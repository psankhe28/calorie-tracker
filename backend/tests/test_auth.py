def test_signup_and_login(client):
    resp = client.post("/api/auth/signup", json={"email": "a@example.com", "password": "password123"})
    assert resp.status_code == 201
    assert "access_token" in resp.json()

    resp = client.post("/api/auth/login", json={"email": "a@example.com", "password": "password123"})
    assert resp.status_code == 200

    resp = client.post("/api/auth/login", json={"email": "a@example.com", "password": "wrong"})
    assert resp.status_code == 401


def test_signup_duplicate_email_rejected(client):
    client.post("/api/auth/signup", json={"email": "dup@example.com", "password": "password123"})
    resp = client.post("/api/auth/signup", json={"email": "dup@example.com", "password": "password123"})
    assert resp.status_code == 409


def test_protected_route_requires_token(client):
    resp = client.get("/api/food-entries")
    assert resp.status_code == 401


def test_me_returns_current_user(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "user@example.com"
