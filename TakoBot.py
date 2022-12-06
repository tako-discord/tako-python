import json
import os
import i18n
import config
import random
import discord
import aiohttp
import requests
import bot_secrets
from discord.ext import commands, tasks
trimmer = "----------"


class TakoBot(commands.Bot):
    async def on_ready(self):
        print(trimmer)
        print(f"Logged in as {self.user} ({self.user.id})\n{trimmer}")

    async def setup_hook(self):
        for category in os.listdir("cogs"):
            await self.load_extension(f"cogs.{category}")
        i18n.set("filename_format", "{locale}.{format}")
        i18n.set("fallback", "en")
        i18n.load_path.append(f"i18n")
        self.update_phishing_list.start()
        if hasattr(bot_secrets, "UPTIME_KUMA"):
            self.uptime_kuma.start()
        self.presence_update.start()
        self.postgre_guilds = await self.db_pool.fetch("SELECT * FROM guilds")
        self.badges_update.start()

    @tasks.loop(seconds=55)
    async def uptime_kuma(self):
        async with aiohttp.ClientSession() as cs:
            await cs.get(bot_secrets.UPTIME_KUMA + str(round(self.latency * 1000)))
            return

    @uptime_kuma.before_loop
    async def before_uptime_kuma(self):
        await self.wait_until_ready()

    @tasks.loop(hours=1)
    async def update_phishing_list(self):
        self.sussy_domains = []
        if hasattr(config, "ANTI_PHISHING_LIST"):
            for list in config.ANTI_PHISHING_LIST:
                self.sussy_domains.extend(requests.get(list).json()["domains"])

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
