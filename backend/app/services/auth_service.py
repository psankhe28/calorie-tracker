from supabase import Client

from app.core.auth_user import AuthUser
from app.core.errors import ConflictError
from app.core.security import create_access_token, hash_password, verify_password


def signup(supabase: Client, email: str, password: str) -> AuthUser:
    existing = supabase.table("users").select("id").eq("email", email).limit(1).execute()
    if existing.data:
        raise ConflictError("An account with this email already exists")

    result = (
        supabase.table("users")
        .insert({"email": email, "hashed_password": hash_password(password)})
        .execute()
    )
    row = result.data[0]
    return AuthUser(id=row["id"], email=row["email"])


def authenticate(supabase: Client, email: str, password: str) -> AuthUser | None:
    result = supabase.table("users").select("id, email, hashed_password").eq("email", email).limit(1).execute()
    if not result.data:
        return None

    row = result.data[0]
    if not verify_password(password, row["hashed_password"]):
        return None

    return AuthUser(id=row["id"], email=row["email"])


def issue_token(user: AuthUser) -> str:
    return create_access_token(subject=str(user.id))
