from datetime import datetime, timezone

from supabase import Client

from app.core.errors import NotFoundError
from app.schemas.goal import GoalUpsert


def get_goal(supabase: Client, user_id: int) -> dict:
    """Return the user's current (most recently set) goal."""
    result = (
        supabase.table("goals")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise NotFoundError("No goal set yet")
    return result.data[0]


def list_goal_history(supabase: Client, user_id: int) -> list[dict]:
    """Return all goals ever set by the user, most recent first."""
    result = (
        supabase.table("goals")
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def upsert_goal(supabase: Client, user_id: int, payload: GoalUpsert) -> dict:
    """Record a new goal for the user, preserving prior goals as history."""
    row = {"user_id": user_id, "created_at": datetime.now(timezone.utc).isoformat(), **payload.model_dump()}
    result = supabase.table("goals").insert(row).execute()
    return result.data[0]
