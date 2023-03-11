import io
import re
import i18n
import aiohttp
import discord
from TakoBot import TakoBot
from utils import get_language
from discord.ext import commands
from discord import HTTPException, NotFound, app_commands


class Emoji(commands.GroupCog, group_name="emoji"):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(
        description="Add an an emoji with an ID from emoji.gg or url pointing to an image"
    )
    @app_commands.default_permissions(manage_emojis=True)
    async def add(self, interaction: discord.Interaction, emoji: str, name: str = None):
        if name is None:
            name = emoji
        if (
            emoji.startswith("http://") is False
            and emoji.startswith("https://") is False
        ):
            emoji = f"https://cdn3.emoji.gg/emojis/{emoji}.png"
        match = re.match(
            "^https?:\/\/cdn3.emoji.gg\/|^https?:\/\/i[.]imgur[.]com\/|^https?:\/\/raw[.]githubusercontent[.]com\/|http[s]?:\/\/cdn[.]betterttv[.]net\/emote|^https?:\/\/cdn[.]discordapp[.]com\/emojis\/",
            emoji,
        )
        if not match:
            return await interaction.response.send_message(
                i18n.t(
                    "misc.not_emoji",
                    locale=get_language(self.bot, interaction.guild_id),
                ),
                ephemeral=True,
            )
        emoji_dict = {"title": name, "image": emoji}
        title = emoji_dict["title"].replace(" ", "").replace("-", "_")
        title = (
            f"{title[:27 if len(title) < 2 else 32]}{'_tako' if len(title) < 2 else ''}"
        )
        async with aiohttp.ClientSession() as cs:
            async with cs.get(emoji_dict["image"]) as r:
                res = await r.read()
        try:
            added_emoji = await interaction.guild.create_custom_emoji(
                name=title, image=res
            )
        except ValueError:
            return await interaction.response.send_message(
                i18n.t(
                    "misc.not_emoji",
                    locale=get_language(self.bot, interaction.guild_id),
                ),
                ephemeral=True,
            )
        except HTTPException:
            return await interaction.response.send_message(
                i18n.t(
                    "misc.too_big",
                    locale=get_language(self.bot, interaction.guild_id),
                ),
                ephemeral=True,
            )
        embed = discord.Embed(
            title="Emoji added",
            description=i18n.t(
                "misc.added_emoji",
                emoji=added_emoji.name,
                locale=get_language(self.bot, interaction.guild_id),
            ).replace("\n", "\n"),
            color=discord.Color.green(),
        )
        embed.set_thumbnail(url=emoji_dict["image"])
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command()
    @app_commands.default_permissions(manage_emojis=True)
    async def remove(self, interaction: discord.Interaction, emoji: str):
        try:
            emoji = int(emoji)
        except:
            return await interaction.response.send_message(
                i18n.t(
                    "misc.not_id", locale=get_language(self.bot, interaction.guild_id)
                ),
                ephemeral=True,
            )
        try:
            fetched_emoji = await interaction.guild.fetch_emoji(emoji)
        except NotFound:
            return await interaction.response.send_message(
                i18n.t(
                    "misc.not_id", locale=get_language(self.bot, interaction.guild_id)
                ),
                ephemeral=True,
            )
        await fetched_emoji.delete(
            reason=i18n.t(
                "misc.deleted_emoji_log",
                user=str(interaction.user),
                locale=get_language(self.bot, interaction.guild_id),
            )
        )
        embed = discord.Embed(
            title="Emoji removed",
            description=i18n.t(
                "misc.deleted_emoji",
                emoji=fetched_emoji.name,
                locale=get_language(self.bot, interaction.guild_id),
            ),
            color=discord.Color.red(),
        )
        image_bytes = await fetched_emoji.read()
        image = discord.File(io.BytesIO(image_bytes), "thumbnail.png")
        embed.set_thumbnail(url="attachment://thumbnail.png")
        await interaction.response.send_message(embed=embed, file=image, ephemeral=True)

    @remove.autocomplete(name="emoji")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        current = current.lower()
        emojis = await interaction.guild.fetch_emojis()
        return [
            app_commands.Choice(name=f"{emoji.name} ({emoji.id})", value=str(emoji.id))
            for emoji in emojis
            if current in emoji.name.lower() or current in str(emoji.id)
        ]
