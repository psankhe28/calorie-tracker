from datetime import date

from fastapi import APIRouter, Depends, Query
from supabase import Client

from app.api.deps import get_current_user
from app.core.auth_user import AuthUser
from app.core.supabase import get_supabase
from app.schemas.report import (
    GoalVsActualReport,
    MacroBreakdownReport,
    MicroSummaryReport,
    WeeklyCaloriesReport,
)
from app.services import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/weekly-calories", response_model=WeeklyCaloriesReport)
def weekly_calories(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> WeeklyCaloriesReport:
    return report_service.weekly_calorie_trend(supabase, current_user.id, start_date, end_date)


@router.get("/macros", response_model=MacroBreakdownReport)
def macros(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> MacroBreakdownReport:
    return report_service.macro_breakdown(supabase, current_user.id, start_date, end_date)


@router.get("/micros", response_model=MicroSummaryReport)
def micros(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> MicroSummaryReport:
    return report_service.micro_summary(supabase, current_user.id, start_date, end_date)


@router.get("/goal-vs-actual", response_model=GoalVsActualReport)
def goal_vs_actual(
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> GoalVsActualReport:
    return report_service.goal_vs_actual(supabase, current_user.id, start_date, end_date)
