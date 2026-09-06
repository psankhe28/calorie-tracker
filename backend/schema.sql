-- Personal Calorie Tracker schema.
-- Run this once in the Supabase dashboard: Project -> SQL Editor -> New query -> paste -> Run.
-- There is no migration tool in this project (Alembic/SQLAlchemy were intentionally removed
-- in favor of talking to Supabase directly) -- this file is the source of truth for the schema,
-- applied by hand. If you change it later, write the ALTER statements yourself and run them too.

create table if not exists users (
    id bigint generated always as identity primary key,
    email text unique not null,
    hashed_password text not null,
    created_at timestamptz not null default now()
);

-- Every goal change is inserted as a new row (history is preserved); the current goal for a
-- user is simply the most recent row by created_at. If you already ran an earlier version of
-- this schema, apply this migration by hand:
--   alter table goals drop constraint if exists goals_user_id_key;
--   alter table goals rename column updated_at to created_at;
--   create index if not exists idx_goals_user_id_created_at on goals (user_id, created_at desc);
create table if not exists goals (
    id bigint generated always as identity primary key,
    user_id bigint not null references users (id) on delete cascade,
    calorie_target double precision not null,
    protein_target_g double precision not null,
    carb_target_g double precision not null,
    fat_target_g double precision not null,
    weight_goal_kg double precision,
    created_at timestamptz not null default now()
);

create index if not exists idx_goals_user_id_created_at on goals (user_id, created_at desc);

do $$
begin
    if not exists (select 1 from pg_type where typname = 'meal_type') then
        create type meal_type as enum ('breakfast', 'lunch', 'dinner', 'snack');
    end if;
end$$;

create table if not exists food_entries (
    id bigint generated always as identity primary key,
    user_id bigint not null references users (id) on delete cascade,
    meal_type meal_type not null,
    food_name text not null,
    quantity double precision not null,
    unit text not null default 'serving',
    calories double precision not null,
    protein_g double precision not null default 0,
    carbs_g double precision not null default 0,
    fat_g double precision not null default 0,
    micros jsonb not null default '{}'::jsonb,
    logged_at timestamptz not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_food_entries_user_id on food_entries (user_id);
create index if not exists idx_food_entries_logged_at on food_entries (logged_at);

-- One row per uploaded food-diary PDF: the original file lives in Supabase Storage (bucket
-- "pdf-imports", auto-created by the backend on first upload -- see app/services/pdf_import.py);
-- this row is the "receipt" -- what got extracted from it, so a user can revisit an old upload
-- and see both the source file and what was imported/skipped from it.
create table if not exists pdf_imports (
    id bigint generated always as identity primary key,
    user_id bigint not null references users (id) on delete cascade,
    file_name text not null,
    storage_path text not null,
    imported_count integer not null default 0,
    extracted_entries jsonb not null default '[]'::jsonb,
    skipped_rows jsonb not null default '[]'::jsonb,
    created_at timestamptz not null default now()
);

create index if not exists idx_pdf_imports_user_id_created_at on pdf_imports (user_id, created_at desc);

-- The backend authenticates with the service_role key and enforces per-user access itself
-- (every query is filtered by the authenticated user's id in application code), so RLS is
-- left disabled here. If you ever query these tables from the frontend directly with the
-- anon/publishable key, enable RLS and add policies first -- do not skip that step in that case.
