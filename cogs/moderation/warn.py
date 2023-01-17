"""
Commands:
- /warn
- /delwarn
- /warnings
...

"""

import i18n
import discord
from utils import get_language
from discord.ext import commands, tasks
from discord import app_commands


class WarnSystem(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Sends a warning to the provided member.")
    # @app_commands.checks.has_permissions(manage_members=True)
    # @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(member="The member to warn")
    @app_commands.describe(msg="Your warning")
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
        msg: str = None,
    ):
        language = get_language(self.bot, interaction.guild.id)

        if member is None:
            interaction.reply(
                i18n.t("moderation.roles_provide_member", locale=language)
            )
            return
        if msg is None:
            interaction.reply(
                i18n.t("moderation.roles_provide_reason", locale=language)
            )
            return

        await member.send(f"You recieved a warning in {interaction.guild} for: {msg}")
        await interaction.reply("Warning sent!")
        # store in db with (id)

    @app_commands.command(description="Removes a warning from the provided member.")
    # @app_commands.checks.has_permissions(manage_members=True)
    # @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(member="The member")
    @app_commands.describe(id="Your warning id to remove")
    async def delwarn(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
        id: int = None,
    ):
        language = get_language(self.bot, interaction.guild.id)

        if id is None:
            interaction.reply("Please provide an id.")
            return
        if member is None:
            interaction.reply(
                i18n.t("moderation.roles_provide_member", locale=language)
            )
            return
        # get warning (id) info & remove warning (id) from db

        await interaction.reply(f"Warning '{id.text}' successfully deleted.")

    @app_commands.command(description="Lists all warnings")
    # @app_commands.checks.has_permissions(manage_members=True)
    # @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(member="The member to warn")
    @app_commands.describe(msg="Your warning")
    async def warnings(
        self, interaction: discord.Interaction, member: discord.Member = None
    ):
        language = get_language(self.bot, interaction.guild.id)
        if member is None:
            interaction.reply(
                i18n.t("moderation.roles_provide_member", locale=language)
            )
            return
        # get warnings from user

        await interaction.reply(f"Warnings: {warnings}")
