from supabase import Client, create_client

from app.core.config import get_settings
from app.core.errors import ServiceUnavailableError

settings = get_settings()

_client: Client | None = None


def get_supabase() -> Client:
    """Server-side Supabase client, authenticated with the service_role key.

    The backend enforces per-user authorization itself (every query is scoped by the
    authenticated user's id), so it talks to Supabase with the service_role key rather
    than relying on Postgres Row-Level Security policies. Never expose this key to the
    frontend.
    """
    global _client
    if not settings.supabase_url or not settings.supabase_service_key:
        raise ServiceUnavailableError(
            "SUPABASE_URL and SUPABASE_SERVICE_KEY must be set on the backend. "
            "Set them in your .env file and restart the server."
        )
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _client
