import discord
from uwuipy import uwuipy
from main import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import get_language, translate


class UwU(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="uwuify t~text uwu")
    @app_commands.describe(
        message="Your message",
        stutter_chance="Chance of s~s~stuttering (in %, default: 10%)",
        face_chance="Chance of adding a face ^w^ (in %, default: 0%)",
        action_chance="Chance of adding an action *blushes* (in %, default: 5%)",
        exclamation_chance="Chance of adding an exclamation!1!! (in %, default: 25%)",
    )
    async def uwuify(
        self,
        interaction: discord.Interaction,
        message: str,
        stutter_chance: app_commands.Range[int, 0, 100] = 10,
        face_chance: app_commands.Range[int, 0, 100] = 0,
        action_chance: app_commands.Range[int, 0, 100] = 5,
        exclamation_chance: app_commands.Range[int, 0, 100] = 25,
    ):
        await interaction.response.defer()
        if interaction.guild_id:
            locale = get_language(self.bot, interaction.guild_id)
            translated = (await translate(message, locale))[0]
            if isinstance(translated, str):
                message = translated
        uwu = uwuipy(
            round(interaction.created_at.timestamp()),
            stutter_chance=stutter_chance / 100,
            face_chance=face_chance / 100,
            action_chance=action_chance / 100,
            exclamation_chance=exclamation_chance / 100,
        )
        text = uwu.uwuify(message).replace("-", "~")
        await interaction.edit_original_response(content=text)
