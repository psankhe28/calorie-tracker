def test_weekly_calories_report(client, auth_headers):
    client.post(
        "/api/food-entries",
        json={
            "meal_type": "breakfast",
            "food_name": "Oatmeal",
            "quantity": 1,
            "unit": "bowl",
            "calories": 300,
            "protein_g": 10,
            "carbs_g": 50,
            "fat_g": 5,
            "micros": {"iron_mg": 2},
            "logged_at": "2026-01-01T08:00:00",
        },
        headers=auth_headers,
    )

    resp = client.get(
        "/api/reports/weekly-calories?start_date=2026-01-01&end_date=2026-01-01", headers=auth_headers
    )
    assert resp.status_code == 200
    days = resp.json()["days"]
    assert days == [{"date": "2026-01-01", "calories": 300.0}]


def test_micro_summary_report(client, auth_headers):
    client.post(
        "/api/food-entries",
        json={
            "meal_type": "breakfast",
            "food_name": "Oatmeal",
            "quantity": 1,
            "unit": "bowl",
            "calories": 300,
            "protein_g": 10,
            "carbs_g": 50,
            "fat_g": 5,
            "micros": {"iron_mg": 2, "vitamin_c_mg": 5},
            "logged_at": "2026-01-01T08:00:00",
        },
        headers=auth_headers,
    )

    resp = client.get(
        "/api/reports/micros?start_date=2026-01-01&end_date=2026-01-01", headers=auth_headers
    )
    nutrients = {n["nutrient"]: n["total"] for n in resp.json()["nutrients"]}
    assert nutrients == {"iron_mg": 2.0, "vitamin_c_mg": 5.0}


def test_goal_vs_actual_requires_goal(client, auth_headers):
    resp = client.get(
        "/api/reports/goal-vs-actual?start_date=2026-01-01&end_date=2026-01-01", headers=auth_headers
    )
    assert resp.status_code == 404


def test_goal_vs_actual_with_goal_set(client, auth_headers):
    client.put(
        "/api/goals",
        json={"calorie_target": 2000, "protein_target_g": 100, "carb_target_g": 200, "fat_target_g": 60},
        headers=auth_headers,
    )
    client.post(
        "/api/food-entries",
        json={
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
        },
        headers=auth_headers,
    )

    resp = client.get(
        "/api/reports/goal-vs-actual?start_date=2026-01-01&end_date=2026-01-01", headers=auth_headers
    )
    metrics = {m["metric"]: (m["goal"], m["actual"]) for m in resp.json()["metrics"]}
    assert metrics["calories"] == (2000.0, 300.0)
