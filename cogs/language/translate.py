import i18n
import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from utils import get_language, get_color, thumbnail, translate


class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Translate something")
    @app_commands.describe(
        text="The text to translate",
        language="The language to translate to as two letter code (special: morse)",
        source="The source language (default: auto)",
        ephemeral="Whether the response should be ephemeral (default: false)",
    )
    async def translate(
        self,
        interaction: discord.Interaction,
        text: str,
        language: str | None = None,
        source: str = "auto",
        ephemeral: bool = False,
    ):
        await interaction.response.defer(ephemeral=ephemeral)
        if not language:
            language = get_language(self.bot, interaction.guild_id)
        if language.lower() == "morse":
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://api.funtranslations.com/translate/morse.json?text={text}"
                ) as response:
                    request = await response.json(content_type="application/json")
            translation = request["contents"]["translated"], "morse"
            source = "any"
        else:
            translation = await translate(text, language, source)
        thumbnail_path = await thumbnail(interaction.user.id, "translation", self.bot)
        file = discord.File(thumbnail_path, filename="thumbnail.png")
        description = [
            translation[0],
            "",
            i18n.t("misc.source", locale=language, source=translation[1]),
            i18n.t("misc.target", locale=language, target=language),
        ]
        embed = discord.Embed(
            title=i18n.t("misc.translation", locale=language),
            description="\n".join(description),
            color=await get_color(self.bot, interaction.guild_id), # type: ignore
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")
        await interaction.followup.send(embed=embed, file=file, ephemeral=ephemeral)
