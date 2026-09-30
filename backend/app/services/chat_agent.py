import json
from datetime import date, datetime, timedelta

from supabase import Client

from app.core.config import get_settings
from app.core.errors import AppError, ExternalServiceError, LimitExceededError
from app.schemas.chat import ChatMessage
from app.schemas.food_entry import FoodEntryCreate, MealType
from app.schemas.goal import GoalUpsert
from app.services import food_service, goal_service, report_service
from app.services.openai_client import get_client

settings = get_settings()

# Max user messages per chat; assistant replies don't count toward it.
_MAX_USER_MESSAGES = 5

_SYSTEM_PROMPT = """You are the in-app assistant for a personal calorie tracker. You can log meals, \
read and update goals, list past food entries, and summarize a user's week — all via the tools \
provided. Always use a tool instead of guessing when the user asks you to change or read their data. \
When logging a new meal and no date is given, assume today. Keep replies short and conversational. \
Calories and macros you invent for a logged meal should be reasonable estimates unless the user gives \
exact numbers.

When the user asks about patterns in what they've eaten — e.g. cuisine type ("how many times did I eat \
North Indian food"), ingredients, or favorite dishes — call get_food_analysis. Do NOT assume "today" or \
"this week" for these questions: unless the user names a specific period, omit start_date/end_date \
entirely so the whole meal history is searched. get_food_analysis returns raw food names, meal types, \
and timestamps with no cuisine or category field, so classify each food item yourself using your own \
knowledge (e.g. dal, roti, paneer, rajma, chole are North Indian) and summarize the count/dates back \
to the user."""

_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "log_meal",
            "description": "Log a food entry for the current user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "meal_type": {"type": "string", "enum": [m.value for m in MealType]},
                    "food_name": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit": {"type": "string"},
                    "calories": {"type": "number"},
                    "protein_g": {"type": "number"},
                    "carbs_g": {"type": "number"},
                    "fat_g": {"type": "number"},
                    "logged_at": {"type": "string", "description": "ISO datetime; omit for now"},
                },
                "required": ["meal_type", "food_name", "quantity", "calories"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_goals",
            "description": "Get the current user's health goals.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_goals",
            "description": "Set or update the current user's health goals.",
            "parameters": {
                "type": "object",
                "properties": {
                    "calorie_target": {"type": "number"},
                    "protein_target_g": {"type": "number"},
                    "carb_target_g": {"type": "number"},
                    "fat_target_g": {"type": "number"},
                    "weight_goal_kg": {"type": "number"},
                },
                "required": ["calorie_target", "protein_target_g", "carb_target_g", "fat_target_g"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_food_entries",
            "description": "List the current user's food entries in a date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "meal_type": {"type": "string", "enum": [m.value for m in MealType]},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "weekly_summary",
            "description": "Get the current user's weekly calorie trend, macro breakdown, and goal-vs-actual comparison.",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_food_analysis",
            "description": "Get the current user's meal log (food name, meal type, timestamp) for a date range, with no cuisine or category labels attached. Use this to answer questions about food patterns — e.g. cuisine type, ingredients, or favorite dishes — by classifying the returned food names yourself.",
            "parameters": {
                "type": "object", 
                "properties": {
                    "start_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "end_date": {"type": "string", "description": "YYYY-MM-DD"},
                    "meal_type": {"type": "string", "enum": [m.value for m in MealType]},
            },},
        },
    },
]


def _parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _dispatch_tool(supabase: Client, user_id: int, name: str, tool_input: dict) -> dict:
    if name == "log_meal":
        logged_at = (
            datetime.fromisoformat(tool_input["logged_at"]) if tool_input.get("logged_at") else datetime.now()
        )
        payload = FoodEntryCreate(
            meal_type=MealType(tool_input["meal_type"]),
            food_name=tool_input["food_name"],
            quantity=tool_input["quantity"],
            unit=tool_input.get("unit", "serving"),
            calories=tool_input["calories"],
            protein_g=tool_input.get("protein_g", 0),
            carbs_g=tool_input.get("carbs_g", 0),
            fat_g=tool_input.get("fat_g", 0),
            logged_at=logged_at,
        )
        entry = food_service.create_entry(supabase, user_id, payload)
        return {"id": entry["id"], "food_name": entry["food_name"], "calories": entry["calories"]}

    if name == "get_goals":
        goal = goal_service.get_goal(supabase, user_id)
        return {
            "calorie_target": goal["calorie_target"],
            "protein_target_g": goal["protein_target_g"],
            "carb_target_g": goal["carb_target_g"],
            "fat_target_g": goal["fat_target_g"],
            "weight_goal_kg": goal["weight_goal_kg"],
        }

    if name == "set_goals":
        payload = GoalUpsert(**tool_input)
        goal = goal_service.upsert_goal(supabase, user_id, payload)
        return {"calorie_target": goal["calorie_target"], "protein_target_g": goal["protein_target_g"]}

    if name == "list_food_entries":
        result = food_service.list_entries(
            supabase,
            user_id,
            datetime.combine(_parse_date(tool_input.get("start_date")) or date.today() - timedelta(days=7), datetime.min.time()),
            datetime.combine(_parse_date(tool_input.get("end_date")) or date.today(), datetime.max.time()),
            MealType(tool_input["meal_type"]) if tool_input.get("meal_type") else None,
            None,
            page=1,
            page_size=50,
        )
        return {
            "total": result.total,
            "entries": [
                {"food_name": e["food_name"], "meal_type": e["meal_type"], "calories": e["calories"], "logged_at": e["logged_at"]}
                for e in result.items
            ],
        }

    if name == "weekly_summary":
        start = _parse_date(tool_input.get("start_date"))
        end = _parse_date(tool_input.get("end_date"))
        trend = report_service.weekly_calorie_trend(supabase, user_id, start, end)
        macros = report_service.macro_breakdown(supabase, user_id, start, end)
        try:
            comparison = report_service.goal_vs_actual(supabase, user_id, start, end)
        except AppError:
            comparison = None
        return {
            "calorie_trend": [d.model_dump() for d in trend.days],
            "macro_breakdown": [d.model_dump() for d in macros.days],
            "goal_vs_actual": [m.model_dump() for m in comparison.metrics] if comparison else None,
        }

    if name == "get_food_analysis":
        start = _parse_date(tool_input.get("start_date"))
        end = _parse_date(tool_input.get("end_date"))
        analysis = report_service.analyze_food_group(supabase, user_id, start, end)
        return {"food": [d.model_dump() for d in analysis.food_list]}

    raise ValueError(f"Unknown tool: {name}")


def handle_chat(supabase: Client, user_id: int, message: str, history: list[ChatMessage]) -> tuple[str, list[ChatMessage]]:
    # The client resends the whole conversation each request, so count its user turns plus this one.
    user_message_count = sum(1 for m in history if m.role == "user") + 1
    if user_message_count > _MAX_USER_MESSAGES:
        raise LimitExceededError(
            f"This chat has reached its limit of {_MAX_USER_MESSAGES} messages. Start a new chat to continue."
        )

    client = get_client()

    messages: list[dict] = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    messages.append({"role": "user", "content": message})

    for _ in range(5):  # bound the tool-use loop
        try:
            response = client.chat.completions.create(
                model=settings.openai_model,
                max_tokens=1024,
                tools=_TOOLS,
                messages=messages,
            )
        except Exception as exc:
            raise ExternalServiceError(f"Chat assistant failed: {exc}") from exc

        choice = response.choices[0]
        assistant_message = choice.message

        if choice.finish_reason != "tool_calls" or not assistant_message.tool_calls:
            reply = assistant_message.content or ""
            updated_history = history + [ChatMessage(role="user", content=message), ChatMessage(role="assistant", content=reply)]
            return reply, updated_history

        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [tc.model_dump() for tc in assistant_message.tool_calls],
            }
        )

        for tool_call in assistant_message.tool_calls:
            tool_input = json.loads(tool_call.function.arguments or "{}")
            try:
                result = _dispatch_tool(supabase, user_id, tool_call.function.name, tool_input)
                content = json.dumps(result)
            except AppError as exc:
                content = json.dumps({"error": exc.message})
            messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": content})

    raise ExternalServiceError("Chat assistant did not produce a final response in time")
