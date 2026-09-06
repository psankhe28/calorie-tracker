from fastapi import APIRouter, Depends
from supabase import Client

from app.api.deps import get_current_user
from app.core.auth_user import AuthUser
from app.core.supabase import get_supabase
from app.schemas.goal import GoalResponse, GoalUpsert
from app.services import goal_service

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.get("", response_model=GoalResponse)
def read_goal(
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    return goal_service.get_goal(supabase, current_user.id)


@router.put("", response_model=GoalResponse)
def upsert_goal(
    payload: GoalUpsert,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> dict:
    return goal_service.upsert_goal(supabase, current_user.id, payload)


@router.get("/history", response_model=list[GoalResponse])
def read_goal_history(
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> list[dict]:
    return goal_service.list_goal_history(supabase, current_user.id)
