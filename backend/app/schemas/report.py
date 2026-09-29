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

class Food(BaseModel):
    name: str
    meal_type: str
    logged_at: str


class WeeklyCaloriesReport(BaseModel):
    days: list[DailyCalories]


class MacroBreakdownReport(BaseModel):
    days: list[MacroBreakdown]


class MicroSummaryReport(BaseModel):
    nutrients: list[MicroSummary]


class GoalVsActualReport(BaseModel):
    metrics: list[GoalVsActual]

class FoodLog(BaseModel):
    food_list: list[Food]

class YearlyCaloriesReport(BaseModel):
    years: list["YearlyCalories"]

class YearlyCalories(BaseModel):
    year: str
    calories: float

class MonthlyCalories(BaseModel):
    month: str
    calories: float

class MonthlyCaloriesReport(BaseModel):
    months: list[MonthlyCalories]