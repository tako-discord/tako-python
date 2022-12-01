import i18n
import discord
import requests
from discord import app_commands
from discord.ext import commands
from utils import get_language, get_color, thumbnail, translate


class Translate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Translate something")
    @app_commands.describe(
        text="The text to translate",
        language="The language to translate to (default: server language or en) (examples: de, ch, en, es, ar) (special: morse)",
        source="The source language (default: auto)",
    )
    async def translate(
        self,
        interaction: discord.Interaction,
        text: str,
        language: str = None,
        source: str = "auto",
    ):
        await interaction.response.defer()
        if not language:
            language = get_language(self.bot, interaction.guild.id)
        if language.lower() == "morse":
            request = requests.get(
                f"https://api.funtranslations.com/translate/morse.json?text={text}"
            ).json()
            translation = request["contents"]["translated"]
            source = "any"
        else:
            translation = await translate(text, language, source)
        thumbnail_path = await thumbnail(interaction.user.id, "translation", self.bot)
        file = discord.File(thumbnail_path, filename="thumbnail.png")
        description = [
            translation,
            "",
            i18n.t("misc.source", locale=language, source=source),
            i18n.t("misc.target", locale=language, target=language),
        ]
        embed = discord.Embed(
            title=i18n.t("misc.translation", locale=language),
            description="\n".join(description),
            color=await get_color(self.bot, interaction.guild.id),
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")
        await interaction.followup.send(embed=embed, file=file)
