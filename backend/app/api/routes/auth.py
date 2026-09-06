from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client

from app.api.deps import get_current_user
from app.core.auth_user import AuthUser
from app.core.supabase import get_supabase
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, supabase: Client = Depends(get_supabase)) -> TokenResponse:
    user = auth_service.signup(supabase, payload.email, payload.password)
    return TokenResponse(access_token=auth_service.issue_token(user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, supabase: Client = Depends(get_supabase)) -> TokenResponse:
    user = auth_service.authenticate(supabase, payload.email, payload.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    return TokenResponse(access_token=auth_service.issue_token(user))


@router.get("/me", response_model=UserResponse)
def me(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    return current_user
