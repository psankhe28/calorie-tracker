import enum
from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, Field


class MealType(str, enum.Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class FoodEntryCreate(BaseModel):
    meal_type: MealType
    food_name: str = Field(min_length=1, max_length=255)
    quantity: float = Field(gt=0)
    unit: str = Field(default="serving", max_length=50)
    calories: float = Field(ge=0)
    protein_g: float = Field(default=0, ge=0)
    carbs_g: float = Field(default=0, ge=0)
    fat_g: float = Field(default=0, ge=0)
    micros: dict[str, float] = Field(default_factory=dict)
    logged_at: datetime


class FoodEntryUpdate(FoodEntryCreate):
    pass


class FoodEntryResponse(FoodEntryCreate):
    id: int
    user_id: int

    model_config = {"from_attributes": True}


T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T]
    page: int
    page_size: int
    total: int
