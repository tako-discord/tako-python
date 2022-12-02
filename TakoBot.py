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
from utils import new_meme, thumbnail, get_color, get_language

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
        self.add_view(MemeButtons(self))
        self.add_view(AffirmationButtons())
        self.loop.create_task(self.selfrole_setup())

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

    async def selfrole_setup(self):
        await self.wait_until_ready()
        selfrole_menus = await self.db_pool.fetch("SELECT * FROM selfroles")
        for item in selfrole_menus:
            view = discord.ui.View(timeout=None)
            menu = SelfMenu(
                self,
                item["select_array"],
                item["min_values"],
                item["max_values"],
                str(item["id"]),
            )
            view.add_item(menu)
            self.add_view(view)


class AffirmationButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Another one",
        style=discord.ButtonStyle.blurple,
        emoji="❤️",
        custom_id="next_affirmation",
    )
    async def next_affirmation(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://affirmations.dev/") as r:
                data = await r.json()
                await interaction.response.edit_message(
                    content=data["affirmation"], view=self
                )


class MemeButtons(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="Another one", style=discord.ButtonStyle.blurple, custom_id="next_meme"
    )
    async def next_meme(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed, file = await new_meme(
            interaction.guild.id, interaction.user.id, self.bot, self.bot.db_pool
        )

        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )

    @discord.ui.button(
        label="Share it",
        style=discord.ButtonStyle.grey,
        custom_id="share_meme",
    )
    async def share_meme(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        data = await self.bot.db_pool.fetchval(
            "SELECT last_meme FROM users WHERE user_id = $1;", interaction.user.id
        )
        if not data:
            return await interaction.response.send_message(
                "We couldn't share this meme!", ephemeral=True
            )

        data = json.loads(data)
        thumbnail_path = await thumbnail(interaction.guild.id, "reddit", self)
        file = discord.File(thumbnail_path, filename="thumbnail.png")

        embed = discord.Embed(
            title=f"{data['title']}",
            description=data["postLink"],
            color=await get_color(self, interaction.guild.id),
        )
        embed.set_author(
            name=data["author"],
            url=f"https://reddit.com/u/{data['author']}",
            icon_url="https://www.redditstatic.com/avatars/defaults/v2/avatar_default_1.png",
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")
        embed.set_image(url=data["url"])
        embed.set_footer(text=f"r/{data['subreddit']} • {data['ups']} 👍")

        await interaction.response.send_message(
            i18n.t("misc.meme_share", user=interaction.user.display_avatar),
            embed=embed,
            file=file,
        )


class SelfMenu(discord.ui.Select):
    def __init__(
        self, bot, select_array: list, min_values: int, max_values: int, uuid: str
    ):
        options = []
        for role_id in select_array:
            for guild in bot.guilds:
                for role in guild.roles:
                    if role.id == role_id:
                        options.append(
                            discord.SelectOption(label=role.name, value=str(role_id))
                        )
        super().__init__(
            custom_id=uuid,
            placeholder="No roles selected",
            options=options,
            min_values=min_values,
            max_values=max_values,
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        for option in self.options:
            role = discord.utils.get(interaction.guild.roles, id=int(option.value))
            if str(role.id) in self.values:
                await interaction.user.add_roles(role)
            else:
                await interaction.user.remove_roles(role)
        await interaction.followup.send(
            content=i18n.t(
                "config.selfroles_updated",
                locale=get_language(self.bot, interaction.guild.id),
            ),
            ephemeral=True,
        )
