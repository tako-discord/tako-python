import discord
from discord import app_commands
from discord.ext import commands

import i18n
from TakoBot import TakoBot
from utils import get_language


class Crosspost(commands.Cog):
    def __init__(self, bot: TakoBot) -> None:
        self.bot = bot

    @app_commands.command(
        description="Set a channel where the messages automatically will be published"
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(
        channel="The news channel auto-crossposting should be enabled in",
        state="Whetever auto-crossposting should be activated (True) or deactivated (False) (Default: True)",
    )
    async def crosspost(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel = None,
        state: bool = True,
    ):
        language = get_language(self.bot, interaction.guild_id)
        if not channel:
            channel = interaction.channel
        if channel.type is discord.ChannelType.news:
            await self.bot.db_pool.execute(
                "INSERT INTO channels (channel_id, crosspost) VALUES ($1, $2) ON CONFLICT(channel_id) DO UPDATE SET crosspost = $2",
                channel.id,
                state,
            )
            await interaction.response.send_message(
                i18n.t(
                    f"config.crossposting_{'activated' if state else 'deactivated'}",
                    channel=channel.mention,
                    locale=language,
                ),
                ephemeral=True,
            )
        else:
            await interaction.response.send_message(
                i18n.t(
                    "config.crossposting_not_news",
                    channel=channel.mention,
                    locale=language,
                ),
                ephemeral=True,
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.type is discord.ChannelType.news:
            crosspost = await self.bot.db_pool.fetchval(
                "SELECT crosspost FROM channels WHERE channel_id = $1",
                message.channel.id,
            )
            if not crosspost:
                return
            if crosspost:
                try:
                    return await message.publish()
                except discord.HTTPException:
                    return
