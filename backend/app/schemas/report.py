from pydantic import BaseModel


class DailyCalories(BaseModel):
    date: str
    calories: float


class MacroBreakdown(BaseModel):
    date: str
    protein_g: float
    carbs_g: float
    fat_g: float


class MicroSummary(BaseModel):
    nutrient: str
    total: float


class GoalVsActual(BaseModel):
    metric: str
    goal: float
    actual: float


class WeeklyCaloriesReport(BaseModel):
    days: list[DailyCalories]


class MacroBreakdownReport(BaseModel):
    days: list[MacroBreakdown]


class MicroSummaryReport(BaseModel):
    nutrients: list[MicroSummary]


class GoalVsActualReport(BaseModel):
    metrics: list[GoalVsActual]
