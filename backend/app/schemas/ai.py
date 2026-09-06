from pydantic import BaseModel, Field


class NutritionExtraction(BaseModel):
    food_name: str
    quantity: float = Field(gt=0)
    unit: str = "serving"
    calories: float = Field(ge=0)
    protein_g: float = Field(ge=0)
    carbs_g: float = Field(ge=0)
    fat_g: float = Field(ge=0)
    micros: dict[str, float] = Field(default_factory=dict)
    confidence_note: str | None = None
