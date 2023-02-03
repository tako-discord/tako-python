import discord
from uwuipy import uwuipy
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import get_language, translate


class UwU(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="uwuify text uwu")
    async def uwuify(
        self,
        interaction: discord.Interaction,
        message: str,
        stutter_chance: app_commands.Range[float, 0, 1] = 0.1,
        face_chance: app_commands.Range[float, 0, 1] = 0,
        action_chance: app_commands.Range[float, 0, 1] = 0,
        exclamation_chance: app_commands.Range[float, 0, 1] = 0.5,
    ):
        if interaction.guild_id:
            locale = get_language(self.bot, interaction.guild_id)
            translated = await translate(message, locale)
            if isinstance(translated, str):
                message = translated
        uwu = uwuipy(
            round(interaction.created_at.timestamp()),
            stutter_chance=stutter_chance,
            face_chance=face_chance,
            action_chance=action_chance,
            exclamation_chance=exclamation_chance,
        )
        text = uwu.uwuify(message)
        await interaction.response.send_message(text)
