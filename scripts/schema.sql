-- AI Match Predictor — users table
-- Paste into Supabase → SQL Editor → New query → Run.

create table if not exists public.users (
    id                  uuid primary key default gen_random_uuid(),
    email               text unique not null,
    username            text unique not null,
    total_points        integer not null default 0,
    accuracy_percentage double precision not null default 0,
    current_streak      integer not null default 0,
    best_streak         integer not null default 0,
    rank                integer,
    created_at          timestamptz not null default now(),
    updated_at          timestamptz not null default now()
);

-- Indexes used by leaderboard / stats queries (from db.py)
create index if not exists idx_user_points   on public.users (total_points desc);
create index if not exists idx_user_accuracy on public.users (accuracy_percentage desc);

-- OPTIONAL sample rows so the table isn't empty:
-- insert into public.users (email, username, total_points) values
--   ('demo1@example.com', 'demo1', 120),
--   ('demo2@example.com', 'demo2', 90);
