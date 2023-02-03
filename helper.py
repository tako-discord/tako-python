import os
import asyncio
import bot_secrets
from pick import pick
from utils import clear_console, add_extension


async def main():
    clear_console()
    options = [
        "Start the bot",
        "Start RPC",
        "Update",
        "Init Database",
        "Add Extension from Git",
        "Exit",
    ]
    selected = pick(
        options, "What do you want to do? (Use arrow keys to navigate)", "x"
    )
    if selected[1] == len(options) - 1:
        return
    if selected[1] == 0:
        print("Starting the bot...")
        from main import main as bot_main

        await bot_main()

    if selected[1] == 1:
        import DiscordRPC

        buttons = DiscordRPC.button(
            button_one_label="Join Server",
            button_one_url="https://dsc.gg/tako-server",
            button_two_label="View on top.gg",
            button_two_url="https://top.gg/bot/878366398269771847",
        )
        rpc = DiscordRPC.RPC.Set_ID(app_id="878366398269771847")
        rpc.set_activity(
            details="A bot done right",
            large_image="tako",
            buttons=buttons,
        )
        rpc.run()
    if selected[1] == 2:
        print("Pulling latest changes...", end="\r")
        os.system("git pull > /dev/null")
        print("Installing dependencies...", end="\r")
        os.system("pip install -r requirements.txt > /dev/null 2>&1")
        clear_console()
        print("✔️  Done with updating")
    if selected[1] == 3:
        import asyncpg

        conn = await asyncpg.connect(
            database=bot_secrets.DB_NAME,
            host=bot_secrets.DB_HOST,
            port=bot_secrets.DB_PORT if hasattr(bot_secrets, "DB_PORT") else 5432,  # type: ignore
            user=bot_secrets.DB_USER,
            password=bot_secrets.DB_PASSWORD,
        )
        version = await conn.fetch(
            "SELECT version();",
        )
        print(f"Initializing database with {next(version[0].values())}")
        await conn.execute(
            """
            CREATE TABLE IF NOT EXISTS badges (name TEXT PRIMARY KEY, emoji TEXT NOT NULL, users BIGINT ARRAY);
            INSERT INTO badges  (name, emoji) VALUES ('alpha_tester', '🧪') ON CONFLICT DO NOTHING;
            INSERT INTO badges  (name, emoji) VALUES ('donator', '💖') ON CONFLICT DO NOTHING;
            INSERT INTO badges  (name, emoji) VALUES ('translator', '🌐') ON CONFLICT DO NOTHING;
            INSERT INTO badges  (name, emoji) VALUES ('core_developer', '💻') ON CONFLICT DO NOTHING;
            CREATE TABLE IF NOT EXISTS channels (channel_id BIGINT PRIMARY KEY, crosspost BOOLEAN NOT NULL DEFAULT FALSE, synced BOOLEAN, locked BOOLEAN, auto_react TEXT ARRAY);
            CREATE TABLE IF NOT EXISTS permissions (channel_id BIGINT, target_id BIGINT, allow INT, deny INT, type TEXT, UNIQUE (channel_id, target_id));
            CREATE TABLE IF NOT EXISTS guilds (guild_id BIGINT PRIMARY KEY, banned_games TEXT ARRAY, join_roles_user BIGINT ARRAY, join_roles_bot BIGINT ARRAY, language TEXT, reaction_translate BOOLEAN, auto_translate BOOLEAN DEFAULT FALSE, color TEXT, auto_translate_confidence INTEGER DEFAULT 50, auto_translate_reply_style TEXT DEFAULT 'min_webhook', auto_translate_delete_original BOOLEAN DEFAULT TRUE);
            CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
            CREATE TABLE IF NOT EXISTS tags (id uuid DEFAULT uuid_generate_v4() PRIMARY KEY, name TEXT, content TEXT, thumbnail TEXT, image TEXT, footer TEXT, embed BOOLEAN DEFAULT TRUE, guild_id BIGINT);
            CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, wallet BIGINT DEFAULT 1000, bank BIGINT DEFAULT 0, last_meme TEXT, last_reaction_translation TIMESTAMP);
            CREATE TABLE IF NOT EXISTS announcements (id uuid DEFAULT uuid_generate_v4() PRIMARY KEY, title TEXT, description TEXT, type TEXT, timestamp TIMESTAMP DEFAULT NOW());
            CREATE TABLE IF NOT EXISTS selfroles (id uuid DEFAULT uuid_generate_v4() PRIMARY KEY, guild_id BIGINT, select_array BIGINT ARRAY, min_values INT, max_values INT);
            CREATE TABLE IF NOT EXISTS polls (id uuid DEFAULT uuid_generate_v4() PRIMARY KEY, question TEXT, answers TEXT ARRAY, votes TEXT, owner BIGINT);
            CREATE TABLE IF NOT EXISTS welcome (guild_id BIGINT PRIMARY KEY, channel_id BIGINT, title TEXT, description TEXT, style TEXT DEFAULT 'embed', mention BOOL DEFAULT FALSE, state BOOLEAN);
            """
        )
        await conn.close()
        clear_console()
        print("✔️  Done with initializing database")
    if selected[1] == 4:
        url = input("Enter the url of the extension: ")
        print("📥 Installing extension...", end="\r")
        adder = add_extension(url)
        if adder == 0:
            return print("✔️  Done with installing the extension")
        if adder == 1:
            return print("❌ Invalid url")
        if adder == 2:
            print("❌  Failed to install the extension")


if __name__ == "__main__":
    asyncio.run(main())
