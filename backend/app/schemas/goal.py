from datetime import datetime

from pydantic import BaseModel, Field


class GoalUpsert(BaseModel):
    calorie_target: float = Field(gt=0)
    protein_target_g: float = Field(ge=0)
    carb_target_g: float = Field(ge=0)
    fat_target_g: float = Field(ge=0)
    weight_goal_kg: float | None = Field(default=None, gt=0)


class GoalResponse(GoalUpsert):
    id: int
    user_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
