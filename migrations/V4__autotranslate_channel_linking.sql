-- Revises: V4
-- Creation Date: 2023-10-01 12:59:52.869202 UTC
-- Reason: Autotranslate Channel Linking
ALTER TABLE
    channels
ADD
    COLUMN IF NOT EXISTS autotranslate_link TEXT [];