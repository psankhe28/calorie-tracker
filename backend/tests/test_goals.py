def test_get_goal_requires_goal_set(client, auth_headers):
    resp = client.get("/api/goals", headers=auth_headers)
    assert resp.status_code == 404


def test_upsert_goal_preserves_history(client, auth_headers):
    first = client.put(
        "/api/goals",
        json={"calorie_target": 1800, "protein_target_g": 90, "carb_target_g": 180, "fat_target_g": 55},
        headers=auth_headers,
    )
    assert first.status_code == 200

    second = client.put(
        "/api/goals",
        json={"calorie_target": 2000, "protein_target_g": 100, "carb_target_g": 200, "fat_target_g": 60},
        headers=auth_headers,
    )
    assert second.status_code == 200

    current = client.get("/api/goals", headers=auth_headers)
    assert current.json()["calorie_target"] == 2000

    history = client.get("/api/goals/history", headers=auth_headers)
    calorie_targets = [g["calorie_target"] for g in history.json()]
    assert calorie_targets == [2000, 1800]
