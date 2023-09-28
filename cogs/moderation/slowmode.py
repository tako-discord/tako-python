import i18n
import discord
from utils import get_language
from discord import app_commands
from discord.ext import commands


class Slowmode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Set the slowmode of a channel")
    @app_commands.default_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.guild_only()
    @app_commands.describe(
        seconds="The amount of seconds to set the slowmode to",
        channel="The channel to set the slowmode of (defaults to the current channel)",
    )
    async def slowmode(
        self,
        interaction: discord.Interaction,
        seconds: app_commands.Range[int, 0, 21600],
        channel: discord.TextChannel | discord.Thread | discord.ForumChannel = None,
    ):
        locale = get_language(self.bot, interaction.guild_id)

        if not channel:
            channel = interaction.channel

        await channel.edit(slowmode_delay=seconds)
        await interaction.response.send_message(
            i18n.t(
                "moderation.slowmode_set",
                channel=channel.mention,
                t=seconds,
                locale=locale,
            ),
            ephemeral=True,
        )
