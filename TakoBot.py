import os
import i18n
import json
import config
import random
import logging
import discord
import aiohttp
import asyncpg
import bot_secrets
import persistent_views
from datetime import datetime
from discord.ext import commands, tasks

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

start_time = datetime.now()

reset = "\033[0m"
gray = "\033[90m"
green = "\033[92m"
blue = "\033[94m"
yellow = "\033[93m"
trimmer = f"{gray}----------{reset}"

tako_ascii_art = f"""
{yellow}
$$$$$$$$\        $$\                 
\__$$  __|       $$ |                
   $$ | $$$$$$\  $$ |  $$\  $$$$$$\  
   $$ | \____$$\ $$ | $$  |$$  __$$\ 
   $$ | $$$$$$$ |$$$$$$  / $$ /  $$ |
   $$ |$$  __$$ |$$  _$$<  $$ |  $$ |
   $$ |\$$$$$$$ |$$ | \$$\ \$$$$$$  |
   \__| \_______|\__|  \__| \______/
{reset}
"""


class TakoBot(commands.Bot):
    async def on_ready(self):
        if self.initialized:
            return
        print(f"\033[1F\033[2K🔓 {gray}|{reset} {yellow}Logged in as {self.user.name} (ID: {self.user.id}){reset}")  # type: ignore
        print(trimmer)
        print(
            f"{gray}>{reset} Startup took {round((datetime.now() - start_time).total_seconds(), 2)}s"
        )
        print(f"{gray}>{reset} Now running and listening to commands")
        print(f"{gray}>{reset} Everything will be logged to discord.log")
        print(f"{gray}>{reset} Press CTRL+C to exit")
        print(trimmer)
        self.initialized = True  # type: ignore

    async def setup_hook(self):
        print(tako_ascii_art)
        print(trimmer)
        self.initialized = False
        self.db_pool: asyncpg.Pool = await asyncpg.create_pool(
            database=bot_secrets.DB_NAME,
            host=bot_secrets.DB_HOST,
            port=bot_secrets.DB_PORT if hasattr(bot_secrets, "DB_PORT") else 5432,  # type: ignore
            user=bot_secrets.DB_USER,
            password=bot_secrets.DB_PASSWORD,
        )
        logger = logging.getLogger("startup")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "{status} \033[90m|\033[0m {message}",
            style="{",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.info(f"{blue}Loading cogs{reset}", extra={"status": "🔄"})
        categories = 0
        for category in os.listdir("cogs"):
            categories += 1
            await self.load_extension(f"cogs.{category}")
        logger.info(
            f"{green}Loaded {len(self.cogs)} cogs from {categories} categories{reset}",
            extra={"status": "\033[1F\033[2K✅"},
        )
        logger.info(f"{blue}Loading i18n{reset}", extra={"status": "🔄"})
        i18n.set("filename_format", "{locale}.{format}")
        i18n.set("fallback", "en")
        i18n.load_path.append("i18n")
        locales = []
        for locale in os.listdir("i18n/misc"):
            locales.append(locale.split(".")[0])
        logger.info(f"{green}Loaded i18n{reset}", extra={"status": "\033[1F\033[2K✅"})
        logger.info(
            f"{green}Available locales ({len(locales)}): {', '.join(locales)}{reset}",
            extra={"status": "✅"},
        )
        logger.info(f"{blue}Updating suspicious domains{reset}", extra={"status": "🔄"})
        self.update_phishing_list.start()
        logger.info(
            f"{green}Updated suspicious domains{reset}",
            extra={"status": "\033[1F\033[2K✅"},
        )
        if hasattr(bot_secrets, "UPTIME_KUMA"):
            self.uptime_kuma.start()
        self.postgre_guilds = await self.db_pool.fetch("SELECT * FROM guilds")  # type: ignore
        logger.info(f"{blue}Adding persistent views{reset}", extra={"status": "🔄"})
        await persistent_views.setup(self)
        logger.info(
            f"{green}Added persistent views{reset}", extra={"status": "\033[1F\033[2K✅"}
        )
        self.presence_update.start()
        self.badges_update.start()
        self.update_version.start()
        logger.info(f"{blue}Logging in...{reset}", extra={"status": f"{trimmer}\n🔄"})

    @tasks.loop(seconds=55)
    async def uptime_kuma(self):
        async with aiohttp.ClientSession() as cs:
            await cs.get(bot_secrets.UPTIME_KUMA + str(round(self.latency * 1000)))  # type: ignore
            return

    @uptime_kuma.before_loop
    async def before_uptime_kuma(self):
        await self.wait_until_ready()

    @tasks.loop(hours=1)
    async def update_version(self):
        with open("pyproject.toml", "rb") as f:
            self.version = tomllib.load(f)["tool"]["commitizen"]["version"]

    @tasks.loop(hours=1)
    async def update_phishing_list(self):
        self.sussy_domains = []
        if hasattr(config, "ANTI_PHISHING_LIST"):
            async with aiohttp.ClientSession() as cs:
                for list in config.ANTI_PHISHING_LIST:
                    async with cs.get(list) as r:
                        r = await r.read()
                        r = json.loads(r)
                        self.sussy_domains.extend(r["domains"])

    @tasks.loop(seconds=7.5)
    async def presence_update(self):
        presences = [
            {"name": "with the new rewrite", "type": discord.ActivityType.playing},
            {
                "name": f"over {len(self.guilds)} server{'s' if len(self.guilds) > 1 else ''}",
                "type": discord.ActivityType.watching,
            },
            {
                "name": f"{len(self.users)} user{'s' if len(self.users) > 1 else ''}",
                "type": discord.ActivityType.listening,
            },
            {
                "name": f"{len(self.tree.get_commands())} {'commands' if len(self.tree.get_commands()) > 1 else 'command'}",
                "type": discord.ActivityType.listening,
            },
            {
                "name": "/ commands",
                "type": discord.ActivityType.listening,
            },
            {
                "name": f"with version {self.version}",
                "type": discord.ActivityType.playing,
            },
            {
                "name": "translate at translate.tako-bot.com",
                "type": discord.ActivityType.playing,
            },
        ]
        random_presence = random.choice(presences)
        await self.change_presence(
            activity=discord.Activity(
                type=random_presence["type"], name=random_presence["name"]
            )
        )

    @presence_update.before_loop
    async def before_presence_update(self):
        await self.wait_until_ready()

    @tasks.loop(hours=1)
    async def badges_update(self):
        for guild in self.guilds:
            for role in guild.roles:
                if role.id == config.DONATOR_ROLE:
                    users = []
                    for member in role.members:
                        users.append(member.id)
                    await self.db_pool.execute(
                        "UPDATE badges SET users = $1 WHERE name = 'donator';", users
                    )
                    continue
                if role.id == config.TRANSLATOR_ROLE:
                    users = []
                    for member in role.members:
                        users.append(member.id)
                    await self.db_pool.execute(
                        "UPDATE badges SET users = $1 WHERE name = 'translator';", users
                    )
                    continue
                if role.id == config.ALPHA_TESTER_ROLE:
                    users = []
                    for member in role.members:
                        users.append(member.id)
                    await self.db_pool.execute(
                        "UPDATE badges SET users = $1 WHERE name = 'alpha_tester';",
                        users,
                    )
                    continue
                if role.id == config.DEV_ROLE:
                    users = []
                    for member in role.members:
                        users.append(member.id)
                    await self.db_pool.execute(
                        "UPDATE badges SET users = $1 WHERE name = 'core_developer';",
                        users,
                    )
                    continue

    @badges_update.before_loop
    async def before_badges_update(self):
        await self.wait_until_ready()
