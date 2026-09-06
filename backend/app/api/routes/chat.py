from fastapi import APIRouter, Depends
from supabase import Client

from app.api.deps import get_current_user
from app.core.auth_user import AuthUser
from app.core.supabase import get_supabase
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_agent import handle_chat

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    supabase: Client = Depends(get_supabase),
    current_user: AuthUser = Depends(get_current_user),
) -> ChatResponse:
    reply, history = handle_chat(supabase, current_user.id, payload.message, payload.history)
    return ChatResponse(reply=reply, history=history)
