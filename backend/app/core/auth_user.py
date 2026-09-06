from dataclasses import dataclass


@dataclass
class AuthUser:
    """The authenticated user, as loaded from Supabase for the current request."""

    id: int
    email: str
