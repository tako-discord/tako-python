import os
import i18n
import json
import config
import random
import logging
import discord
import aiohttp
import bot_secrets
import persistent_views
from datetime import datetime
from discord.ext import commands, tasks


trimmer = "----------"
start_time = datetime.now()
ascii_art = """
$$$$$$$$\        $$\                 
\__$$  __|       $$ |                
   $$ | $$$$$$\  $$ |  $$\  $$$$$$\  
   $$ | \____$$\ $$ | $$  |$$  __$$\ 
   $$ | $$$$$$$ |$$$$$$  / $$ /  $$ |
   $$ |$$  __$$ |$$  _$$<  $$ |  $$ |
   $$ |\$$$$$$$ |$$ | \$$\ \$$$$$$  |
   \__| \_______|\__|  \__| \______/
"""


class TakoBot(commands.Bot):
    async def on_ready(self):
        print(f"🔓 | Logged in as {self.user.name} (ID: {self.user.id})")
        print(trimmer)
        print(f"🕐 Startup took {(datetime.now() - start_time).total_seconds()}s")
        print("> Now running and listening to commands")
        print("> Everything will be logged to discord.log")
        print("> Press CTRL+C to exit")
        print(trimmer)

    async def setup_hook(self):
        print(ascii_art)
        logger = logging.getLogger("startup")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "{status} | {message}",
            style="{",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        logger.info("Loading cogs", extra={"status": f"{trimmer}\n🔄"})
        categories = 0
        for category in os.listdir("cogs"):
            categories += 1
            await self.load_extension(f"cogs.{category}")
        logger.info(f"Loaded {len(self.cogs)} cogs from {categories} categories", extra={"status": "✅"})
        logger.info("Loading i18n", extra={"status": f"{trimmer}\n🔄"})
        i18n.set("filename_format", "{locale}.{format}")
        i18n.set("fallback", "en")
        i18n.load_path.append(f"i18n")
        locales = []
        for locale in os.listdir("i18n/misc"):
            locales.append(locale.split(".")[0])
        logger.info(f"Loaded i18n", extra={"status": "✅"})
        logger.info(f"Available locales ({len(locales)}): {', '.join(locales)}", extra={"status": "✅"})
        self.update_phishing_list.start(logger=logger)
        if hasattr(bot_secrets, "UPTIME_KUMA"):
            self.uptime_kuma.start()
        self.postgre_guilds = await self.db_pool.fetch("SELECT * FROM guilds")
        logger.info("Adding persistent views", extra={"status": f"{trimmer}\n🔄"})
        await persistent_views.setup(self)
        logger.info("Added persistent views", extra={"status": "✅"})
        self.presence_update.start()
        self.badges_update.start()
        logger.info("Logging in...", extra={"status": f"{trimmer}\n🔄"})

    @tasks.loop(seconds=55)
    async def uptime_kuma(self):
        async with aiohttp.ClientSession() as cs:
            await cs.get(bot_secrets.UPTIME_KUMA + str(round(self.latency * 1000)))
            return

    @uptime_kuma.before_loop
    async def before_uptime_kuma(self):
        await self.wait_until_ready()

    @tasks.loop(hours=1)
    async def update_phishing_list(self, logger: logging.Logger):
        self.sussy_domains = []
        if hasattr(config, "ANTI_PHISHING_LIST"):
            logger.info("Updating suspicious domains", extra={"status": f"{trimmer}\n🔄"})
            async with aiohttp.ClientSession() as cs:
                for list in config.ANTI_PHISHING_LIST:
                    async with cs.get(list) as r:
                        r = await r.read()
                        r = json.loads(r)
                        self.sussy_domains.extend(r["domains"])
            logger.info(f"Updated suspicious domains ({len(self.sussy_domains)})", extra={"status": "✅"})

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
                        "UPDATE badges SET users = $1 WHERE name = 'Donator';", users
                    )
                    continue
                if role.id == config.TRANSLATOR_ROLE:
                    users = []
                    for member in role.members:
                        users.append(member.id)
                    await self.db_pool.execute(
                        "UPDATE badges SET users = $1 WHERE name = 'Translator';", users
                    )
                    continue
                if role.id == config.ALPHA_TESTER_ROLE:
                    users = []
                    for member in role.members:
                        users.append(member.id)
                    await self.db_pool.execute(
                        "UPDATE badges SET users = $1 WHERE name = 'Alpha Tester';",
                        users,
                    )
                    continue
                if role.id == config.DEV_ROLE:
                    users = []
                    for member in role.members:
                        users.append(member.id)
                    await self.db_pool.execute(
                        "UPDATE badges SET users = $1 WHERE name = 'Core Developer';",
                        users,
                    )
                    continue

    @badges_update.before_loop
    async def before_badges_update(self):
        await self.wait_until_ready()
