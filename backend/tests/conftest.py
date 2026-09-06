import pytest
from fastapi.testclient import TestClient

from app.core.supabase import get_supabase
from app.main import app
from tests.fake_supabase import FakeSupabaseClient


@pytest.fixture()
def client():
    fake_supabase = FakeSupabaseClient()

    app.dependency_overrides[get_supabase] = lambda: fake_supabase
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    client.post("/api/auth/signup", json={"email": "user@example.com", "password": "password123"})
    resp = client.post("/api/auth/login", json={"email": "user@example.com", "password": "password123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
