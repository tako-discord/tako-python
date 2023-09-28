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
    selected = pick(options, "What do you want to do? (Use arrow keys to navigate)")
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
            details="Everything you need",
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

        migration_options = [
            file
            for file in os.listdir("migrations")
            if file.endswith(".sql")
            and os.path.isfile(os.path.join("migrations", file))
        ]
        migration_options.sort()
        migration_options.reverse()

        selected = pick(
            options=["All"] + migration_options,
            title="What migration do you want to run? (Use arrow keys to navigate and space to select)",
            multiselect=True,
        )
        if not len(selected) > 0:
            return print("❌ No migrations selected. Aborting...")

        all_selected = True if ("All", 0) in selected else False
        migration_string = ""  # the string that will be executed

        # read the sql files and add them to the string, that will be exucuted
        for migration in selected if not all_selected else migration_options:
            if not migration[0] == "All":  # type: ignore
                with open(f"migrations/{migration[0] if not all_selected else migration}", "r") as file:  # type: ignore
                    migration_string += file.read()

        # Execute the migration
        conn = await asyncpg.connect(
            database=bot_secrets.DB_NAME,
            host=bot_secrets.DB_HOST,
            port=bot_secrets.DB_PORT if hasattr(bot_secrets, "DB_PORT") else 5432,  # type: ignore
            user=bot_secrets.DB_USER,
            password=bot_secrets.DB_PASSWORD,
        )
        await conn.execute(migration_string)
        await conn.close()
        clear_console()
        return print("✔️  Done with initializing database")
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
