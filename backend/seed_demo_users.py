"""One-off script to seed a few demo users with distinct goals and a week of food entries,
so multi-user isolation can be checked by hand in the browser. Not part of the app itself --
run manually with: cd backend && .venv/bin/python seed_demo_users.py
"""

from datetime import datetime, timedelta

from app.core.security import hash_password
from app.core.supabase import get_supabase

supabase = get_supabase()

DEMO_USERS = [
    {
        "email": "alice@example.com",
        "password": "password123",
        "goal": {
            "calorie_target": 2000,
            "protein_target_g": 130,
            "carb_target_g": 200,
            "fat_target_g": 60,
            "weight_goal_kg": 62,
        },
        "entries": [
            {"day_offset": -2, "meal_type": "breakfast", "food_name": "Greek Yogurt & Berries", "quantity": 1, "unit": "bowl", "calories": 280, "protein_g": 20, "carbs_g": 35, "fat_g": 6, "micros": {"vitamin_c_mg": 18, "calcium_mg": 200}},
            {"day_offset": -2, "meal_type": "lunch", "food_name": "Grilled Chicken Wrap", "quantity": 1, "unit": "wrap", "calories": 520, "protein_g": 38, "carbs_g": 45, "fat_g": 18, "micros": {"iron_mg": 2.5}},
            {"day_offset": -2, "meal_type": "dinner", "food_name": "Salmon & Quinoa", "quantity": 1, "unit": "plate", "calories": 610, "protein_g": 42, "carbs_g": 50, "fat_g": 24, "micros": {"omega3_mg": 1800}},
            {"day_offset": -1, "meal_type": "breakfast", "food_name": "Oatmeal & Banana", "quantity": 1, "unit": "bowl", "calories": 340, "protein_g": 10, "carbs_g": 60, "fat_g": 6, "micros": {"potassium_mg": 420}},
            {"day_offset": -1, "meal_type": "lunch", "food_name": "Quinoa Salad", "quantity": 1, "unit": "bowl", "calories": 450, "protein_g": 16, "carbs_g": 55, "fat_g": 16, "micros": {}},
            {"day_offset": -1, "meal_type": "snack", "food_name": "Almonds", "quantity": 1, "unit": "handful", "calories": 170, "protein_g": 6, "carbs_g": 6, "fat_g": 15, "micros": {"vitamin_e_mg": 7}},
            {"day_offset": 0, "meal_type": "breakfast", "food_name": "Scrambled Eggs & Toast", "quantity": 1, "unit": "plate", "calories": 380, "protein_g": 22, "carbs_g": 30, "fat_g": 18, "micros": {}},
            {"day_offset": 0, "meal_type": "lunch", "food_name": "Turkey Sandwich", "quantity": 1, "unit": "sandwich", "calories": 460, "protein_g": 30, "carbs_g": 42, "fat_g": 16, "micros": {}},
        ],
    },
    {
        "email": "bob@example.com",
        "password": "password123",
        "goal": {
            "calorie_target": 2800,
            "protein_target_g": 180,
            "carb_target_g": 300,
            "fat_target_g": 80,
            "weight_goal_kg": 85,
        },
        "entries": [
            {"day_offset": -3, "meal_type": "breakfast", "food_name": "Protein Pancakes", "quantity": 3, "unit": "pancakes", "calories": 520, "protein_g": 40, "carbs_g": 60, "fat_g": 12, "micros": {}},
            {"day_offset": -3, "meal_type": "lunch", "food_name": "Beef & Rice Bowl", "quantity": 1, "unit": "bowl", "calories": 780, "protein_g": 50, "carbs_g": 80, "fat_g": 26, "micros": {"iron_mg": 4.2}},
            {"day_offset": -3, "meal_type": "dinner", "food_name": "Grilled Steak & Potatoes", "quantity": 1, "unit": "plate", "calories": 850, "protein_g": 55, "carbs_g": 65, "fat_g": 38, "micros": {"zinc_mg": 5.5}},
            {"day_offset": -3, "meal_type": "snack", "food_name": "Protein Shake", "quantity": 1, "unit": "shake", "calories": 250, "protein_g": 30, "carbs_g": 15, "fat_g": 5, "micros": {}},
            {"day_offset": -1, "meal_type": "breakfast", "food_name": "Oats & Peanut Butter", "quantity": 1, "unit": "bowl", "calories": 480, "protein_g": 20, "carbs_g": 55, "fat_g": 20, "micros": {}},
            {"day_offset": -1, "meal_type": "dinner", "food_name": "Chicken Stir Fry", "quantity": 1, "unit": "plate", "calories": 700, "protein_g": 48, "carbs_g": 60, "fat_g": 24, "micros": {"vitamin_a_mcg": 300}},
            {"day_offset": 0, "meal_type": "lunch", "food_name": "Tuna Pasta", "quantity": 1, "unit": "plate", "calories": 650, "protein_g": 42, "carbs_g": 75, "fat_g": 18, "micros": {}},
        ],
    },
    {
        "email": "carol@example.com",
        "password": "password123",
        "goal": {
            "calorie_target": 1600,
            "protein_target_g": 100,
            "carb_target_g": 150,
            "fat_target_g": 50,
            "weight_goal_kg": 58,
        },
        "entries": [
            {"day_offset": -1, "meal_type": "breakfast", "food_name": "Green Smoothie", "quantity": 1, "unit": "glass", "calories": 220, "protein_g": 8, "carbs_g": 40, "fat_g": 4, "micros": {"vitamin_c_mg": 60, "vitamin_k_mcg": 200}},
            {"day_offset": -1, "meal_type": "lunch", "food_name": "Lentil Soup", "quantity": 1, "unit": "bowl", "calories": 320, "protein_g": 18, "carbs_g": 45, "fat_g": 7, "micros": {"iron_mg": 3.3, "folate_mcg": 180}},
            {"day_offset": -1, "meal_type": "snack", "food_name": "Apple & Peanut Butter", "quantity": 1, "unit": "serving", "calories": 200, "protein_g": 6, "carbs_g": 25, "fat_g": 10, "micros": {}},
            {"day_offset": 0, "meal_type": "breakfast", "food_name": "Avocado Toast", "quantity": 1, "unit": "slice", "calories": 280, "protein_g": 8, "carbs_g": 28, "fat_g": 16, "micros": {"potassium_mg": 500}},
            {"day_offset": 0, "meal_type": "dinner", "food_name": "Tofu Veggie Stir Fry", "quantity": 1, "unit": "plate", "calories": 420, "protein_g": 22, "carbs_g": 40, "fat_g": 18, "micros": {"vitamin_c_mg": 45}},
        ],
    },
]


def seed():
    for user_spec in DEMO_USERS:
        email = user_spec["email"]
        existing = supabase.table("users").select("id").eq("email", email).execute()
        if existing.data:
            user_id = existing.data[0]["id"]
            print(f"{email}: already exists (id={user_id}), skipping creation, will still (re)seed goal/entries")
            supabase.table("food_entries").delete().eq("user_id", user_id).execute()
        else:
            result = supabase.table("users").insert(
                {"email": email, "hashed_password": hash_password(user_spec["password"])}
            ).execute()
            user_id = result.data[0]["id"]
            print(f"{email}: created (id={user_id})")

        goal_payload = {"user_id": user_id, **user_spec["goal"]}
        existing_goal = supabase.table("goals").select("id").eq("user_id", user_id).execute()
        if existing_goal.data:
            supabase.table("goals").update(user_spec["goal"]).eq("user_id", user_id).execute()
        else:
            supabase.table("goals").insert(goal_payload).execute()

        now = datetime.now()
        for entry in user_spec["entries"]:
            logged_at = (now + timedelta(days=entry["day_offset"])).replace(
                hour=9 if entry["meal_type"] == "breakfast" else 13 if entry["meal_type"] == "lunch" else 19 if entry["meal_type"] == "dinner" else 16,
                minute=0,
                second=0,
                microsecond=0,
            )
            row = {k: v for k, v in entry.items() if k != "day_offset"}
            row["user_id"] = user_id
            row["logged_at"] = logged_at.isoformat()
            supabase.table("food_entries").insert(row).execute()

        print(f"{email}: goal set, {len(user_spec['entries'])} food entries seeded")

    print("\nDemo accounts (all password: password123):")
    for user_spec in DEMO_USERS:
        print(f"  {user_spec['email']}")


if __name__ == "__main__":
    seed()
