-- Dummy data seed for the Personal Calorie Tracker.
-- Run this in the Supabase dashboard: Project -> SQL Editor -> New query -> paste -> Run.
-- This WIPES all existing data (pdf_imports, food_entries, goals, users) and replaces it
-- with 3 demo accounts, each with a goal and ~2 weeks of food entries.
--
-- Demo accounts (all password: password123):
--   alice@example.com
--   bob@example.com
--   carol@example.com

-- ---------------------------------------------------------------------------
-- 1. Clear existing data (children first, respecting foreign keys)
-- ---------------------------------------------------------------------------
truncate table pdf_imports, food_entries, goals, users restart identity cascade;

-- ---------------------------------------------------------------------------
-- 2. Users
-- password for all three: "password123"
-- ---------------------------------------------------------------------------
insert into users (email, hashed_password) values
    ('alice@example.com', '$2b$12$HtrCzaaOyTreL2V4v0nqrOeod5LIFRTpnYrh0TwDQqUw/4l4djxVK'),
    ('bob@example.com',   '$2b$12$HtrCzaaOyTreL2V4v0nqrOeod5LIFRTpnYrh0TwDQqUw/4l4djxVK'),
    ('carol@example.com', '$2b$12$HtrCzaaOyTreL2V4v0nqrOeod5LIFRTpnYrh0TwDQqUw/4l4djxVK');

-- ---------------------------------------------------------------------------
-- 3. Goals (one current goal per user)
-- ---------------------------------------------------------------------------
insert into goals (user_id, calorie_target, protein_target_g, carb_target_g, fat_target_g, weight_goal_kg)
select id, 2000, 130, 200, 60, 62 from users where email = 'alice@example.com'
union all
select id, 2800, 180, 300, 80, 85 from users where email = 'bob@example.com'
union all
select id, 1600, 100, 150, 50, 58 from users where email = 'carol@example.com';

-- ---------------------------------------------------------------------------
-- 4. Food entries -- two weeks of history per user, logged relative to today
-- ---------------------------------------------------------------------------

-- Alice: moderate, balanced diet
with u as (select id from users where email = 'alice@example.com')
insert into food_entries (user_id, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, micros, logged_at)
select u.id, v.meal_type::meal_type, v.food_name, v.quantity, v.unit, v.calories, v.protein_g, v.carbs_g, v.fat_g, v.micros::jsonb,
       (current_date + v.day_offset) + v.time_of_day
from u, (values
    (-13, 'breakfast', 'Greek Yogurt & Berries',   1, 'bowl',     280, 20, 35,  6, '{"vitamin_c_mg": 18, "calcium_mg": 200}', time '08:00'),
    (-13, 'lunch',     'Grilled Chicken Wrap',     1, 'wrap',     520, 38, 45, 18, '{"iron_mg": 2.5}',                        time '13:00'),
    (-13, 'dinner',    'Salmon & Quinoa',          1, 'plate',    610, 42, 50, 24, '{"omega3_mg": 1800}',                     time '19:00'),
    (-12, 'breakfast', 'Oatmeal & Banana',         1, 'bowl',     340, 10, 60,  6, '{"potassium_mg": 420}',                   time '08:00'),
    (-12, 'lunch',     'Quinoa Salad',             1, 'bowl',     450, 16, 55, 16, '{}',                                      time '13:00'),
    (-12, 'snack',     'Almonds',                  1, 'handful',  170,  6,  6, 15, '{"vitamin_e_mg": 7}',                     time '16:00'),
    (-11, 'breakfast', 'Scrambled Eggs & Toast',   1, 'plate',    380, 22, 30, 18, '{}',                                      time '08:00'),
    (-11, 'lunch',     'Turkey Sandwich',          1, 'sandwich', 460, 30, 42, 16, '{}',                                      time '13:00'),
    (-11, 'dinner',    'Veggie Stir Fry & Rice',   1, 'plate',    520, 18, 70, 14, '{"vitamin_c_mg": 40}',                    time '19:00'),
    (-9,  'breakfast', 'Greek Yogurt & Berries',   1, 'bowl',     280, 20, 35,  6, '{"vitamin_c_mg": 18, "calcium_mg": 200}', time '08:00'),
    (-9,  'lunch',     'Grilled Chicken Wrap',     1, 'wrap',     520, 38, 45, 18, '{"iron_mg": 2.5}',                        time '13:00'),
    (-9,  'snack',     'Apple & Peanut Butter',    1, 'serving',  200,  6, 25, 10, '{}',                                      time '16:00'),
    (-8,  'breakfast', 'Oatmeal & Banana',         1, 'bowl',     340, 10, 60,  6, '{"potassium_mg": 420}',                   time '08:00'),
    (-8,  'dinner',    'Salmon & Quinoa',          1, 'plate',    610, 42, 50, 24, '{"omega3_mg": 1800}',                     time '19:00'),
    (-6,  'breakfast', 'Avocado Toast',            1, 'slice',    280,  8, 28, 16, '{"potassium_mg": 500}',                   time '08:00'),
    (-6,  'lunch',     'Quinoa Salad',             1, 'bowl',     450, 16, 55, 16, '{}',                                      time '13:00'),
    (-6,  'dinner',    'Grilled Chicken & Veggies',1, 'plate',    540, 40, 35, 20, '{}',                                      time '19:00'),
    (-5,  'breakfast', 'Scrambled Eggs & Toast',   1, 'plate',    380, 22, 30, 18, '{}',                                      time '08:00'),
    (-5,  'lunch',     'Turkey Sandwich',          1, 'sandwich', 460, 30, 42, 16, '{}',                                      time '13:00'),
    (-5,  'snack',     'Almonds',                  1, 'handful',  170,  6,  6, 15, '{"vitamin_e_mg": 7}',                     time '16:00'),
    (-3,  'breakfast', 'Greek Yogurt & Berries',   1, 'bowl',     280, 20, 35,  6, '{"vitamin_c_mg": 18, "calcium_mg": 200}', time '08:00'),
    (-3,  'lunch',     'Grilled Chicken Wrap',     1, 'wrap',     520, 38, 45, 18, '{"iron_mg": 2.5}',                        time '13:00'),
    (-3,  'dinner',    'Salmon & Quinoa',          1, 'plate',    610, 42, 50, 24, '{"omega3_mg": 1800}',                     time '19:00'),
    (-1,  'breakfast', 'Oatmeal & Banana',         1, 'bowl',     340, 10, 60,  6, '{"potassium_mg": 420}',                   time '08:00'),
    (-1,  'lunch',     'Quinoa Salad',             1, 'bowl',     450, 16, 55, 16, '{}',                                      time '13:00'),
    (-1,  'snack',     'Apple & Peanut Butter',    1, 'serving',  200,  6, 25, 10, '{}',                                      time '16:00'),
    (0,   'breakfast', 'Scrambled Eggs & Toast',   1, 'plate',    380, 22, 30, 18, '{}',                                      time '08:00'),
    (0,   'lunch',     'Turkey Sandwich',          1, 'sandwich', 460, 30, 42, 16, '{}',                                      time '13:00')
) as v(day_offset, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, micros, time_of_day);

-- Bob: higher-calorie, high-protein diet
with u as (select id from users where email = 'bob@example.com')
insert into food_entries (user_id, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, micros, logged_at)
select u.id, v.meal_type::meal_type, v.food_name, v.quantity, v.unit, v.calories, v.protein_g, v.carbs_g, v.fat_g, v.micros::jsonb,
       (current_date + v.day_offset) + v.time_of_day
from u, (values
    (-13, 'breakfast', 'Protein Pancakes',          3, 'pancakes', 520, 40, 60, 12, '{}',                     time '07:30'),
    (-13, 'lunch',     'Beef & Rice Bowl',          1, 'bowl',     780, 50, 80, 26, '{"iron_mg": 4.2}',       time '12:30'),
    (-13, 'dinner',    'Grilled Steak & Potatoes',  1, 'plate',    850, 55, 65, 38, '{"zinc_mg": 5.5}',       time '19:30'),
    (-13, 'snack',     'Protein Shake',             1, 'shake',    250, 30, 15,  5, '{}',                     time '16:00'),
    (-11, 'breakfast', 'Oats & Peanut Butter',      1, 'bowl',     480, 20, 55, 20, '{}',                     time '07:30'),
    (-11, 'dinner',    'Chicken Stir Fry',          1, 'plate',    700, 48, 60, 24, '{"vitamin_a_mcg": 300}', time '19:30'),
    (-10, 'breakfast', 'Protein Pancakes',          3, 'pancakes', 520, 40, 60, 12, '{}',                     time '07:30'),
    (-10, 'lunch',     'Tuna Pasta',                1, 'plate',    650, 42, 75, 18, '{}',                     time '12:30'),
    (-10, 'dinner',    'Grilled Steak & Potatoes',  1, 'plate',    850, 55, 65, 38, '{"zinc_mg": 5.5}',       time '19:30'),
    (-9,  'breakfast', 'Oats & Peanut Butter',      1, 'bowl',     480, 20, 55, 20, '{}',                     time '07:30'),
    (-9,  'lunch',     'Beef & Rice Bowl',          1, 'bowl',     780, 50, 80, 26, '{"iron_mg": 4.2}',       time '12:30'),
    (-9,  'snack',     'Protein Shake',             1, 'shake',    250, 30, 15,  5, '{}',                     time '16:00'),
    (-7,  'breakfast', 'Protein Pancakes',          3, 'pancakes', 520, 40, 60, 12, '{}',                     time '07:30'),
    (-7,  'dinner',    'Chicken Stir Fry',          1, 'plate',    700, 48, 60, 24, '{"vitamin_a_mcg": 300}', time '19:30'),
    (-6,  'lunch',     'Tuna Pasta',                1, 'plate',    650, 42, 75, 18, '{}',                     time '12:30'),
    (-6,  'dinner',    'Grilled Steak & Potatoes',  1, 'plate',    850, 55, 65, 38, '{"zinc_mg": 5.5}',       time '19:30'),
    (-4,  'breakfast', 'Oats & Peanut Butter',      1, 'bowl',     480, 20, 55, 20, '{}',                     time '07:30'),
    (-4,  'lunch',     'Beef & Rice Bowl',          1, 'bowl',     780, 50, 80, 26, '{"iron_mg": 4.2}',       time '12:30'),
    (-4,  'snack',     'Protein Shake',             1, 'shake',    250, 30, 15,  5, '{}',                     time '16:00'),
    (-2,  'breakfast', 'Protein Pancakes',          3, 'pancakes', 520, 40, 60, 12, '{}',                     time '07:30'),
    (-2,  'dinner',    'Chicken Stir Fry',          1, 'plate',    700, 48, 60, 24, '{"vitamin_a_mcg": 300}', time '19:30'),
    (0,   'breakfast', 'Oats & Peanut Butter',      1, 'bowl',     480, 20, 55, 20, '{}',                     time '07:30'),
    (0,   'lunch',     'Tuna Pasta',                1, 'plate',    650, 42, 75, 18, '{}',                     time '12:30')
) as v(day_offset, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, micros, time_of_day);

-- Carol: lower-calorie, plant-forward diet
with u as (select id from users where email = 'carol@example.com')
insert into food_entries (user_id, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, micros, logged_at)
select u.id, v.meal_type::meal_type, v.food_name, v.quantity, v.unit, v.calories, v.protein_g, v.carbs_g, v.fat_g, v.micros::jsonb,
       (current_date + v.day_offset) + v.time_of_day
from u, (values
    (-13, 'breakfast', 'Green Smoothie',            1, 'glass',   220,  8, 40,  4, '{"vitamin_c_mg": 60, "vitamin_k_mcg": 200}', time '08:00'),
    (-13, 'lunch',     'Lentil Soup',               1, 'bowl',    320, 18, 45,  7, '{"iron_mg": 3.3, "folate_mcg": 180}',        time '12:30'),
    (-13, 'snack',     'Apple & Peanut Butter',     1, 'serving', 200,  6, 25, 10, '{}',                                        time '15:30'),
    (-12, 'breakfast', 'Avocado Toast',             1, 'slice',   280,  8, 28, 16, '{"potassium_mg": 500}',                     time '08:00'),
    (-12, 'dinner',    'Tofu Veggie Stir Fry',      1, 'plate',   420, 22, 40, 18, '{"vitamin_c_mg": 45}',                      time '19:00'),
    (-10, 'breakfast', 'Green Smoothie',            1, 'glass',   220,  8, 40,  4, '{"vitamin_c_mg": 60, "vitamin_k_mcg": 200}', time '08:00'),
    (-10, 'lunch',     'Lentil Soup',               1, 'bowl',    320, 18, 45,  7, '{"iron_mg": 3.3, "folate_mcg": 180}',        time '12:30'),
    (-9,  'breakfast', 'Avocado Toast',             1, 'slice',   280,  8, 28, 16, '{"potassium_mg": 500}',                     time '08:00'),
    (-9,  'dinner',    'Tofu Veggie Stir Fry',      1, 'plate',   420, 22, 40, 18, '{"vitamin_c_mg": 45}',                      time '19:00'),
    (-9,  'snack',     'Apple & Peanut Butter',     1, 'serving', 200,  6, 25, 10, '{}',                                        time '15:30'),
    (-7,  'breakfast', 'Green Smoothie',            1, 'glass',   220,  8, 40,  4, '{"vitamin_c_mg": 60, "vitamin_k_mcg": 200}', time '08:00'),
    (-7,  'lunch',     'Lentil Soup',               1, 'bowl',    320, 18, 45,  7, '{"iron_mg": 3.3, "folate_mcg": 180}',        time '12:30'),
    (-5,  'breakfast', 'Avocado Toast',             1, 'slice',   280,  8, 28, 16, '{"potassium_mg": 500}',                     time '08:00'),
    (-5,  'dinner',    'Tofu Veggie Stir Fry',      1, 'plate',   420, 22, 40, 18, '{"vitamin_c_mg": 45}',                      time '19:00'),
    (-4,  'snack',     'Apple & Peanut Butter',     1, 'serving', 200,  6, 25, 10, '{}',                                        time '15:30'),
    (-3,  'breakfast', 'Green Smoothie',            1, 'glass',   220,  8, 40,  4, '{"vitamin_c_mg": 60, "vitamin_k_mcg": 200}', time '08:00'),
    (-3,  'lunch',     'Lentil Soup',               1, 'bowl',    320, 18, 45,  7, '{"iron_mg": 3.3, "folate_mcg": 180}',        time '12:30'),
    (-1,  'breakfast', 'Avocado Toast',             1, 'slice',   280,  8, 28, 16, '{"potassium_mg": 500}',                     time '08:00'),
    (-1,  'dinner',    'Tofu Veggie Stir Fry',      1, 'plate',   420, 22, 40, 18, '{"vitamin_c_mg": 45}',                      time '19:00'),
    (0,   'breakfast', 'Green Smoothie',            1, 'glass',   220,  8, 40,  4, '{"vitamin_c_mg": 60, "vitamin_k_mcg": 200}', time '08:00'),
    (0,   'lunch',     'Lentil Soup',               1, 'bowl',    320, 18, 45,  7, '{"iron_mg": 3.3, "folate_mcg": 180}',        time '12:30')
) as v(day_offset, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, micros, time_of_day);
