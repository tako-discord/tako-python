-- Revises: V3
-- Creation Date: 2023-03-19 19:44:05.774548 UTC
-- Reason: last user daily
ALTER TABLE
    users
ADD
    COLUMN IF NOT EXISTS last_daily TIMESTAMP;