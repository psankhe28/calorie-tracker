from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import Client

from app.core.auth_user import AuthUser
from app.core.security import decode_access_token
from app.core.supabase import get_supabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    supabase: Client = Depends(get_supabase),
) -> AuthUser:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise credentials_error

    subject = decode_access_token(token)
    if subject is None:
        raise credentials_error

    result = supabase.table("users").select("id, email").eq("id", int(subject)).limit(1).execute()
    if not result.data:
        raise credentials_error

    row = result.data[0]
    return AuthUser(id=row["id"], email=row["email"])
