from dataclasses import dataclass
from datetime import datetime

from supabase import Client

from app.core.errors import NotFoundError
from app.schemas.food_entry import FoodEntryCreate, FoodEntryUpdate, MealType


@dataclass
class PageResult:
    items: list[dict]
    page: int
    page_size: int
    total: int


def create_entry(supabase: Client, user_id: int, payload: FoodEntryCreate) -> dict:
    row = payload.model_dump(mode="json")
    result = supabase.table("food_entries").insert({"user_id": user_id, **row}).execute()
    return result.data[0]


def get_entry(supabase: Client, user_id: int, entry_id: int) -> dict:
    result = (
        supabase.table("food_entries")
        .select("*")
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if not result.data:
        raise NotFoundError("Food entry not found")
    return result.data[0]


def update_entry(supabase: Client, user_id: int, entry_id: int, payload: FoodEntryUpdate) -> dict:
    get_entry(supabase, user_id, entry_id)  # 404s if missing or not owned by this user

    row = payload.model_dump(mode="json")
    result = (
        supabase.table("food_entries")
        .update(row)
        .eq("id", entry_id)
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0]


def delete_entry(supabase: Client, user_id: int, entry_id: int) -> None:
    get_entry(supabase, user_id, entry_id)  # 404s if missing or not owned by this user
    supabase.table("food_entries").delete().eq("id", entry_id).eq("user_id", user_id).execute()


def list_entries(
    supabase: Client,
    user_id: int,
    start_date: datetime | None,
    end_date: datetime | None,
    meal_type: MealType | None,
    q: str | None,
    page: int,
    page_size: int,
) -> PageResult:
    query = supabase.table("food_entries").select("*", count="exact").eq("user_id", user_id)
    if start_date is not None:
        query = query.gte("logged_at", start_date.isoformat())
    if end_date is not None:
        query = query.lte("logged_at", end_date.isoformat())
    if meal_type is not None:
        query = query.eq("meal_type", meal_type.value)
    if q is not None:
        query = query.ilike("food_name", f"%{q}%")

    range_start = (page - 1) * page_size
    range_end = range_start + page_size - 1
    result = query.order("logged_at", desc=True).range(range_start, range_end).execute()

    return PageResult(items=result.data, page=page, page_size=page_size, total=result.count or 0)
