-- 10 years of food_entries for alice@example.com
-- Covers Jan 1 of the year 10 years ago  →  current_date - 14 days
-- (seed.sql already covers the last 13 days)
-- Meals rotate by day-of-week (0=Sun … 6=Sat) for natural variety.
--
-- If re-running after a partial load, delete alice's old entries first:
--   delete from food_entries
--   where user_id = (select id from users where email = 'alice@example.com');

with u as (
    select id from users where email = 'alice@example.com'
),
dates as (
    select d::date
    from generate_series(
        date_trunc('year', current_date - interval '10 years')::date,
        current_date - interval '14 days',
        interval '1 day'
    ) as gs(d)
),
patterns (dow, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, micros, time_of_day) as (
    values
    -- Sunday ---------------------------------------------------------------
    (0, 'breakfast', 'Pancakes & Maple Syrup',      2, 'pieces',   420, 12, 65, 14, '{}',                                      time '09:00'),
    (0, 'lunch',     'Caesar Salad with Chicken',   1, 'bowl',     480, 35, 22, 26, '{"vitamin_k_mcg": 150}',                  time '13:30'),
    (0, 'snack',     'Orange & Walnuts',            1, 'serving',  210,  5, 28, 11, '{"vitamin_c_mg": 70}',                    time '16:00'),
    (0, 'dinner',    'Beef Stir Fry & Rice',        1, 'plate',    620, 35, 65, 22, '{"iron_mg": 3.5}',                        time '19:00'),
    -- Monday ---------------------------------------------------------------
    (1, 'breakfast', 'Greek Yogurt & Berries',      1, 'bowl',     280, 20, 35,  6, '{"vitamin_c_mg": 18, "calcium_mg": 200}', time '07:30'),
    (1, 'lunch',     'Turkey Sandwich',             1, 'sandwich', 460, 30, 42, 16, '{}',                                      time '12:30'),
    (1, 'snack',     'Almonds',                     1, 'handful',  170,  6,  6, 15, '{"vitamin_e_mg": 7}',                     time '15:30'),
    (1, 'dinner',    'Salmon & Quinoa',             1, 'plate',    610, 42, 50, 24, '{"omega3_mg": 1800}',                     time '19:00'),
    -- Tuesday --------------------------------------------------------------
    (2, 'breakfast', 'Scrambled Eggs & Toast',      1, 'plate',    380, 22, 30, 18, '{}',                                      time '07:30'),
    (2, 'lunch',     'Quinoa Salad',                1, 'bowl',     450, 16, 55, 16, '{}',                                      time '12:30'),
    (2, 'dinner',    'Grilled Chicken & Veggies',   1, 'plate',    540, 40, 35, 20, '{}',                                      time '19:00'),
    -- Wednesday ------------------------------------------------------------
    (3, 'breakfast', 'Avocado Toast',               1, 'slice',    280,  8, 28, 16, '{"potassium_mg": 500}',                   time '07:30'),
    (3, 'lunch',     'Grilled Chicken Wrap',        1, 'wrap',     520, 38, 45, 18, '{"iron_mg": 2.5}',                        time '12:30'),
    (3, 'snack',     'Apple & Peanut Butter',       1, 'serving',  200,  6, 25, 10, '{}',                                      time '15:30'),
    (3, 'dinner',    'Veggie Stir Fry & Rice',      1, 'plate',    520, 18, 70, 14, '{"vitamin_c_mg": 40}',                    time '19:00'),
    -- Thursday -------------------------------------------------------------
    (4, 'breakfast', 'Oatmeal & Banana',            1, 'bowl',     340, 10, 60,  6, '{"potassium_mg": 420}',                   time '07:30'),
    (4, 'lunch',     'Lentil Soup',                 1, 'bowl',     380, 18, 55,  8, '{"iron_mg": 4}',                          time '12:30'),
    (4, 'snack',     'Protein Bar',                 1, 'bar',      220, 20, 22,  8, '{}',                                      time '16:00'),
    (4, 'dinner',    'Baked Cod & Sweet Potato',    1, 'plate',    490, 38, 45, 12, '{"vitamin_d_iu": 400}',                   time '19:00'),
    -- Friday ---------------------------------------------------------------
    (5, 'breakfast', 'Banana Smoothie',             1, 'glass',    310, 14, 52,  6, '{"potassium_mg": 600}',                   time '08:00'),
    (5, 'lunch',     'Tuna Salad Wrap',             1, 'wrap',     430, 32, 38, 16, '{"omega3_mg": 900}',                      time '12:30'),
    (5, 'snack',     'Mixed Nuts',                  1, 'handful',  190,  5,  8, 17, '{"vitamin_e_mg": 5}',                     time '16:00'),
    (5, 'dinner',    'Pizza Margherita',            2, 'slices',   560, 22, 72, 20, '{"calcium_mg": 250}',                     time '19:30'),
    -- Saturday -------------------------------------------------------------
    (6, 'breakfast', 'French Toast',               2, 'slices',   440, 14, 58, 18, '{}',                                      time '09:30'),
    (6, 'lunch',     'Burrito Bowl',               1, 'bowl',     590, 28, 70, 18, '{"vitamin_c_mg": 30}',                    time '13:00'),
    (6, 'snack',     'Dark Chocolate',             1, 'square',   170,  2, 20, 10, '{"iron_mg": 2}',                          time '16:00'),
    (6, 'dinner',    'Pasta Bolognese',            1, 'plate',    640, 30, 78, 22, '{}',                                      time '19:30')
)
insert into food_entries (user_id, meal_type, food_name, quantity, unit, calories, protein_g, carbs_g, fat_g, micros, logged_at)
select
    u.id,
    p.meal_type::meal_type,
    p.food_name,
    p.quantity,
    p.unit,
    p.calories,
    p.protein_g,
    p.carbs_g,
    p.fat_g,
    p.micros::jsonb,
    (d.d + p.time_of_day) as logged_at
from u
cross join dates d
join patterns p on p.dow = extract(dow from d.d)::int;
