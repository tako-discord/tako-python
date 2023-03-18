import i18n
import random

import discord
from utils import get_language, error_embed
from discord import app_commands
from discord.ext import commands


class Random(commands.GroupCog, group_name="random"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        description="Provide a list of choices and get one of them back"
    )
    @app_commands.describe(
        choices="The choices to choose from", splitter="The splitter to use"
    )
    async def choose(
        self,
        interaction: discord.Interaction,
        choices: str,
        splitter: str | None = None,
    ):
        choices_list = []  # This is to store the actual choices
        splitted = False  # This is to prevent the bot from splitting the choices multiple times

        # Check for custom splitter
        if splitter:
            choices_list = choices.split(splitter)
            splitted = True
        # Standard splitters
        if choices.__contains__(",") and not splitted:
            choices_list = choices.split(",")
            splitted = True
        if choices.__contains__(" ") and not splitted:
            choices_list = choices.split(" ")
            splitted = True
        if choices.__contains__("|") and not splitted:
            choices_list = choices.split("|")
            splitted = True

        # Check if there are enough choices, if not, send an error message
        # This also works if the user didn't provide a valid splitter
        if len(choices_list) < 2:
            language = get_language(self.bot, interaction.guild_id)
            embed, file = error_embed(
                self.bot,
                i18n.t("misc.random_choice_error_title", locale=language),
                i18n.t("misc.random_choice_error", locale=language),
                interaction.guild_id,
            )
            await interaction.response.send_message(embed=embed, file=file)
            return

        # Choose a random choice and send it
        random_choice = random.choice(choices_list)
        await interaction.response.send_message(random_choice)
