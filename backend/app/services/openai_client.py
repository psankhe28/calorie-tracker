import json
import re

from openai import OpenAI

from app.core.config import get_settings
from app.core.errors import ExternalServiceError, ServiceUnavailableError

settings = get_settings()

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if not settings.openai_api_key:
        raise ServiceUnavailableError(
            "AI features require OPENAI_API_KEY to be set on the backend. "
            "Set it in your .env file and restart the server."
        )
    if _client is None:
        extra_headers = None
        if settings.openai_base_url and "openrouter.ai" in settings.openai_base_url:
            # Optional but recommended by OpenRouter for attribution/rate-limit purposes.
            extra_headers = {
                "HTTP-Referer": "http://localhost:5173",
                "X-Title": "Personal Calorie Tracker",
            }
        _client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url or None,
            default_headers=extra_headers,
        )
    return _client


_JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)
_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


def extract_json_object(text: str) -> dict:
    """Pull the first JSON object out of a model response, tolerating markdown fences."""
    match = _JSON_OBJECT.search(text)
    if match is None:
        raise ExternalServiceError("The AI response did not contain valid JSON")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ExternalServiceError(f"The AI response contained malformed JSON: {exc}") from exc


def extract_json_array(text: str) -> list:
    """Pull the first JSON array out of a model response, tolerating markdown fences."""
    match = _JSON_ARRAY.search(text)
    if match is None:
        raise ExternalServiceError("The AI response did not contain a valid JSON array")
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError as exc:
        raise ExternalServiceError(f"The AI response contained malformed JSON: {exc}") from exc
