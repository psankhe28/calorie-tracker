from collections import defaultdict
from datetime import date, datetime, timedelta

from supabase import Client

from app.core.errors import NotFoundError
from app.schemas.report import (
    DailyCalories,
    Food,
    GoalVsActual,
    GoalVsActualReport,
    MacroBreakdown,
    MacroBreakdownReport,
    MicroSummary,
    MicroSummaryReport,
    WeeklyCaloriesReport,
    FoodLog
)


def _default_range(start_date: date | None, end_date: date | None) -> tuple[date, date]:
    end = end_date or date.today()
    start = start_date or end - timedelta(days=6)
    return start, end


def _entry_date(entry: dict) -> date:
    return datetime.fromisoformat(entry["logged_at"]).date()


def _entries_in_range(supabase: Client, user_id: int, start: date, end: date) -> list[dict]:
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.max.time())
    result = (
        supabase.table("food_entries")
        .select("*")
        .eq("user_id", user_id)
        .gte("logged_at", start_dt.isoformat())
        .lte("logged_at", end_dt.isoformat())
        .execute()
    )
    return result.data


def weekly_calorie_trend(
    supabase: Client, user_id: int, start_date: date | None, end_date: date | None
) -> WeeklyCaloriesReport:
    start, end = _default_range(start_date, end_date)
    entries = _entries_in_range(supabase, user_id, start, end)

    totals: dict[str, float] = defaultdict(float)
    cursor = start
    while cursor <= end:
        totals[cursor.isoformat()] = 0.0
        cursor += timedelta(days=1)

    for entry in entries:
        totals[_entry_date(entry).isoformat()] += entry["calories"]

    days = [DailyCalories(date=day, calories=round(cal, 2)) for day, cal in sorted(totals.items())]
    return WeeklyCaloriesReport(days=days)


def macro_breakdown(
    supabase: Client, user_id: int, start_date: date | None, end_date: date | None
) -> MacroBreakdownReport:
    start, end = _default_range(start_date, end_date)
    entries = _entries_in_range(supabase, user_id, start, end)

    totals: dict[str, list[float]] = defaultdict(lambda: [0.0, 0.0, 0.0])
    cursor = start
    while cursor <= end:
        totals.setdefault(cursor.isoformat(), [0.0, 0.0, 0.0])
        cursor += timedelta(days=1)

    for entry in entries:
        key = _entry_date(entry).isoformat()
        totals[key][0] += entry["protein_g"]
        totals[key][1] += entry["carbs_g"]
        totals[key][2] += entry["fat_g"]

    days = [
        MacroBreakdown(date=day, protein_g=round(p, 2), carbs_g=round(c, 2), fat_g=round(f, 2))
        for day, (p, c, f) in sorted(totals.items())
    ]
    return MacroBreakdownReport(days=days)


def micro_summary(
    supabase: Client, user_id: int, start_date: date | None, end_date: date | None
) -> MicroSummaryReport:
    start, end = _default_range(start_date, end_date)
    entries = _entries_in_range(supabase, user_id, start, end)

    totals: dict[str, float] = defaultdict(float)
    for entry in entries:
        for nutrient, amount in (entry.get("micros") or {}).items():
            try:
                totals[nutrient] += float(amount)
            except (TypeError, ValueError):
                continue

    nutrients = [MicroSummary(nutrient=n, total=round(t, 2)) for n, t in sorted(totals.items())]
    return MicroSummaryReport(nutrients=nutrients)


def goal_vs_actual(
    supabase: Client, user_id: int, start_date: date | None, end_date: date | None
) -> GoalVsActualReport:
    start, end = _default_range(start_date, end_date)
    entries = _entries_in_range(supabase, user_id, start, end)

    goal_result = supabase.table("goals").select("*").eq("user_id", user_id).limit(1).execute()
    if not goal_result.data:
        raise NotFoundError("No goal set yet — set a goal before viewing this report")
    goal = goal_result.data[0]

    num_days = max((end - start).days + 1, 1)
    actual_calories = sum(e["calories"] for e in entries) / num_days
    actual_protein = sum(e["protein_g"] for e in entries) / num_days
    actual_carbs = sum(e["carbs_g"] for e in entries) / num_days
    actual_fat = sum(e["fat_g"] for e in entries) / num_days

    metrics = [
        GoalVsActual(metric="calories", goal=goal["calorie_target"], actual=round(actual_calories, 2)),
        GoalVsActual(metric="protein_g", goal=goal["protein_target_g"], actual=round(actual_protein, 2)),
        GoalVsActual(metric="carbs_g", goal=goal["carb_target_g"], actual=round(actual_carbs, 2)),
        GoalVsActual(metric="fat_g", goal=goal["fat_target_g"], actual=round(actual_fat, 2)),
    ]
    return GoalVsActualReport(metrics=metrics)

def analyze_food_group(
    supabase: Client, user_id: int, start_date: date | None, end_date: date | None
) -> FoodLog:
    if start_date is None and end_date is None:
        # No period specified — this tool answers open-ended questions like "how many
        # times have I eaten X", so search the whole log instead of defaulting to a week.
        result = supabase.table("food_entries").select("*").eq("user_id", user_id).execute()
        entries = result.data
    else:
        start, end = _default_range(start_date, end_date)
        entries = _entries_in_range(supabase, user_id, start, end)
    if not entries:
        raise NotFoundError("No food entries found in that date range")

    food_list = [
        Food(name=e["food_name"], meal_type=e["meal_type"], logged_at=e["logged_at"])
        for e in entries
    ]
    return FoodLog(food_list=food_list)
