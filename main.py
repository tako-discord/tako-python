import asyncio
import json
import logging
import os
import random
from datetime import datetime

import aiohttp
import asyncpg
import discord
import pyyoutube
import tmdbsimple as tmdb
from discord.ext import commands, tasks

import bot_secrets
import config
import views
from translator import TakoTranslator
from utils import clear_console

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

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


youtube_api = pyyoutube.Api(api_key=bot_secrets.YOUTUBE_API_KEY)
tmdb.API_KEY = bot_secrets.TMDB_API_KEY


class TakoBot(commands.AutoShardedBot):
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
        self.initialized = True

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
        await self.tree.set_translator(TakoTranslator())
        locales = []
        for locale in os.listdir("i18n/misc"):
            locales.append(locale.split(".")[0])
        logger.info(f"{green}Loaded i18n{reset}", extra={"status": "\033[1F\033[2K✅"})
        logger.info(
            f"{green}Available locales ({len(locales)}): {', '.join(locales)}{reset}",
            extra={"status": "✅"},
        )
        if hasattr(bot_secrets, "UPTIME_KUMA"):
            self.uptime_kuma.start()
        self.badges_update.start()
        self.postgre_guilds = await self.db_pool.fetch("SELECT * FROM guilds")  # type: ignore
        self.update_phishing_list.start()
        self.update_version.start()
        self.presence_update.start()
        await views.setup(self)
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
            {
                "name": f"over {len(self.guilds)} server{'s' if len(self.guilds) > 1 else ''}",
                "type": discord.ActivityType.watching,
            },
            {
                "name": f"{len(self.users)} user{'s' if len(self.users) > 1 else ''}",
                "type": discord.ActivityType.listening,
            },
            {
                "name": f"{len(self.tree.get_commands())} command{'s' if len(self.tree.get_commands()) > 1 else ''}",
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
        guild = None
        guild = await self.fetch_guild(config.MAIN_GUILD, with_counts=False)
        if not isinstance(guild, discord.Guild):
            return
        query = "UPDATE badges SET users = $1, emoji = $2 WHERE name = $3;"
        for role in guild.roles:
            if role.id == config.DONATOR_ROLE:
                users = []
                for member in role.members:
                    users.append(member.id)
                await self.db_pool.execute(
                    query,
                    users,
                    "💖"
                    if not hasattr(config, "EMOJI_TRANSLATOR")
                    or not config.EMOJI_TRANSLATOR
                    else config.EMOJI_TRANSLATOR,
                    "donator",
                )
                continue
            if role.id == config.TRANSLATOR_ROLE:
                users = []
                for member in role.members:
                    users.append(member.id)
                await self.db_pool.execute(
                    query,
                    users,
                    "🌐"
                    if not hasattr(config, "EMOJI_DONATOR") or not config.EMOJI_DONATOR
                    else config.EMOJI_DONATOR,
                    "translator",
                )
                continue
            if role.id == config.ALPHA_TESTER_ROLE:
                users = []
                for member in role.members:
                    users.append(member.id)
                await self.db_pool.execute(
                    query,
                    users,
                    "🧪"
                    if not hasattr(config, "EMOJI_TRANSLATOR")
                    or not config.EMOJI_TRANSLATOR
                    else config.EMOJI_TRANSLATOR,
                    "alpha_tester",
                )
                continue
            if role.id == config.DEV_ROLE:
                users = []
                for member in role.members:
                    users.append(member.id)
                await self.db_pool.execute(
                    query,
                    users,
                    "💻"
                    if not hasattr(config, "EMOJI_DEV") or not config.EMOJI_DEV
                    else config.EMOJI_DEV,
                    "core_developer",
                )
                continue

    @badges_update.before_loop
    async def before_badges_update(self):
        await self.wait_until_ready()


async def main():
    clear_console()
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    formatter = logging.Formatter(
        "{asctime} | {levelname: <8} | {module}:{funcName}:{lineno} - {message}",
        style="{",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    intents.reactions = True

    bot: TakoBot = TakoBot(command_prefix="tk!", intents=intents)

    await bot.start(bot_secrets.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
