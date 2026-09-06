def _create_entry(client, headers, **overrides):
    payload = {
        "meal_type": "breakfast",
        "food_name": "Oatmeal",
        "quantity": 1,
        "unit": "bowl",
        "calories": 300,
        "protein_g": 10,
        "carbs_g": 50,
        "fat_g": 5,
        "micros": {},
        "logged_at": "2026-01-01T08:00:00",
    }
    payload.update(overrides)
    return client.post("/api/food-entries", json=payload, headers=headers)


def test_create_and_get_entry(client, auth_headers):
    resp = _create_entry(client, auth_headers)
    assert resp.status_code == 201
    entry_id = resp.json()["id"]

    resp = client.get(f"/api/food-entries/{entry_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["food_name"] == "Oatmeal"


def test_update_and_delete_entry(client, auth_headers):
    entry_id = _create_entry(client, auth_headers).json()["id"]

    resp = client.put(
        f"/api/food-entries/{entry_id}",
        json={
            "meal_type": "lunch",
            "food_name": "Updated",
            "quantity": 2,
            "unit": "plate",
            "calories": 400,
            "protein_g": 20,
            "carbs_g": 40,
            "fat_g": 10,
            "micros": {},
            "logged_at": "2026-01-01T13:00:00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["food_name"] == "Updated"

    resp = client.delete(f"/api/food-entries/{entry_id}", headers=auth_headers)
    assert resp.status_code == 204

    resp = client.get(f"/api/food-entries/{entry_id}", headers=auth_headers)
    assert resp.status_code == 404


def test_pagination(client, auth_headers):
    for i in range(3):
        _create_entry(client, auth_headers, food_name=f"Item {i}", logged_at=f"2026-01-0{i + 1}T08:00:00")

    resp = client.get("/api/food-entries?page=1&page_size=2", headers=auth_headers)
    body = resp.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2
    assert body["page"] == 1
    assert body["page_size"] == 2

    resp = client.get("/api/food-entries?page=2&page_size=2", headers=auth_headers)
    body = resp.json()
    assert len(body["items"]) == 1


def test_filter_by_meal_type_and_date_range(client, auth_headers):
    _create_entry(client, auth_headers, meal_type="breakfast", logged_at="2026-01-01T08:00:00")
    _create_entry(client, auth_headers, meal_type="lunch", logged_at="2026-01-02T13:00:00")

    resp = client.get("/api/food-entries?meal_type=lunch", headers=auth_headers)
    body = resp.json()
    assert body["total"] == 1
    assert body["items"][0]["meal_type"] == "lunch"

    resp = client.get(
        "/api/food-entries?start_date=2026-01-02T00:00:00&end_date=2026-01-02T23:59:59",
        headers=auth_headers,
    )
    body = resp.json()
    assert body["total"] == 1


def test_users_cannot_see_each_others_entries(client, auth_headers):
    _create_entry(client, auth_headers)

    client.post("/api/auth/signup", json={"email": "other@example.com", "password": "password123"})
    other_token = client.post(
        "/api/auth/login", json={"email": "other@example.com", "password": "password123"}
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    resp = client.get("/api/food-entries", headers=other_headers)
    assert resp.json()["total"] == 0


def test_invalid_entry_rejected(client, auth_headers):
    resp = _create_entry(client, auth_headers, calories=-10)
    assert resp.status_code == 422
