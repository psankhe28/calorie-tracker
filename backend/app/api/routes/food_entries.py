from datetime import datetime

from fastapi import APIRouter, Depends, Query, status
from supabase import Client

from app.api.deps import get_current_user
from app.core.auth_user import AuthUser
from app.core.supabase import get_supabase
from app.schemas.food_entry import FoodEntryCreate, FoodEntryResponse, FoodEntryUpdate, MealType, Page
from app.services import food_service

router = APIRouter(prefix="/api/food-entries", tags=["food-entries"])


@router.post("", response_model=FoodEntryResponse, status_code=status.HTTP_201_CREATED)
def create_food_entry(
    payload: FoodEntryCreate,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    return food_service.create_entry(supabase, current_user.id, payload)


@router.get("", response_model=Page[FoodEntryResponse])
def list_food_entries(
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    meal_type: MealType | None = Query(default=None),
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> Page[FoodEntryResponse]:
    result = food_service.list_entries(supabase, current_user.id, start_date, end_date, meal_type, q, page, page_size)
    return Page[FoodEntryResponse](
        items=[FoodEntryResponse.model_validate(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/{entry_id}", response_model=FoodEntryResponse)
def get_food_entry(
    entry_id: int,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    return food_service.get_entry(supabase, current_user.id, entry_id)


@router.put("/{entry_id}", response_model=FoodEntryResponse)
def update_food_entry(
    entry_id: int,
    payload: FoodEntryUpdate,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    return food_service.update_entry(supabase, current_user.id, entry_id, payload)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_food_entry(
    entry_id: int,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> None:
    food_service.delete_entry(supabase, current_user.id, entry_id)
