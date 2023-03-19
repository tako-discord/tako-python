-- Revises: V0
-- Creation Date: 2023-03-19 14:32:53.438135 UTC
-- Reason: Initial migration

-- Badges
CREATE TABLE IF NOT EXISTS badges (
    name TEXT PRIMARY KEY,
    emoji TEXT NOT NULL,
    users BIGINT ARRAY
);

INSERT INTO badges (name, emoji) VALUES ('alpha_tester', '🧪') ON CONFLICT DO NOTHING;
INSERT INTO badges (name, emoji) VALUES ('donator', '💖') ON CONFLICT DO NOTHING;
INSERT INTO badges (name, emoji) VALUES ('translator', '🌐') ON CONFLICT DO NOTHING;
INSERT INTO badges (name, emoji) VALUES ('core_developer', '💻') ON CONFLICT DO NOTHING;

-- Other
CREATE TABLE IF NOT EXISTS channels (
    channel_id BIGINT PRIMARY KEY,
    crosspost BOOLEAN NOT NULL DEFAULT FALSE,
    synced BOOLEAN,
    locked BOOLEAN,
    auto_react TEXT ARRAY
);

CREATE TABLE IF NOT EXISTS permissions (
    channel_id BIGINT,
    target_id BIGINT,
    allow INT,
    deny INT,
    type TEXT,
    UNIQUE (channel_id, target_id)
);

CREATE TABLE IF NOT EXISTS guilds (
    guild_id BIGINT PRIMARY KEY,
    banned_games TEXT ARRAY,
    join_roles_user BIGINT ARRAY,
    join_roles_bot BIGINT ARRAY,
    language TEXT,
    reaction_translate BOOLEAN,
    auto_translate BOOLEAN DEFAULT FALSE,
    color TEXT,
    auto_translate_confidence INTEGER DEFAULT 50,
    auto_translate_reply_style TEXT DEFAULT 'min_webhook',
    auto_translate_delete_original BOOLEAN DEFAULT TRUE
);

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tags (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    name TEXT,
    content TEXT,
    thumbnail TEXT,
    image TEXT,
    footer TEXT,
    embed BOOLEAN DEFAULT TRUE,
    guild_id BIGINT
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    wallet BIGINT DEFAULT 1000,
    bank BIGINT DEFAULT 0,
    last_meme TEXT,
    last_reaction_translation TIMESTAMP
);

CREATE TABLE IF NOT EXISTS announcements (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    title TEXT,
    description TEXT,
    type TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS selfroles (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    guild_id BIGINT,
    select_array BIGINT ARRAY,
    min_values INT,
    max_values INT
);

CREATE TABLE IF NOT EXISTS polls (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    question TEXT,
    answers TEXT ARRAY,
    votes TEXT,
    owner BIGINT
);

CREATE TABLE IF NOT EXISTS welcome (
    guild_id BIGINT PRIMARY KEY,
    channel_id BIGINT,
    title TEXT,
    description TEXT,
    style TEXT DEFAULT 'embed',
    mention BOOL DEFAULT FALSE,
    state BOOLEAN
);

CREATE TABLE IF NOT EXISTS warnings (
    id uuid DEFAULT uuid_generate_v4() PRIMARY KEY,
    guild_id BIGINT,
    user_id BIGINT,
    moderator_id BIGINT,
    reason TEXT,
    timestamp TIMESTAMP DEFAULT NOW()
);