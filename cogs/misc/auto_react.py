import discord
import emoji
from discord import app_commands
from discord.ext import commands

import i18n
from TakoBot import TakoBot


class EmojiTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str):
        is_emoji = emoji.is_emoji(value)
        return await commands.PartialEmojiConverter().convert((await commands.Context.from_interaction(interaction)), value) if not is_emoji else value  # type: ignore


class AutoReact(commands.GroupCog, group_name="auto_react"):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Add an emoji that will be automatically added to every new message in the channel")
    @app_commands.describe(
        emoji="The emoji to add. Can be a custom emoji or a unicode emoji.",
        channel="The channel to add the emoji to. If not specified, the current channel will be used.",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(add_reactions=True)
    async def add(self, interaction: discord.Interaction, emoji: app_commands.Transform[discord.Emoji | str, EmojiTransformer], channel: discord.TextChannel = None):  # type: ignore
        if not channel:
            channel = interaction.channel  # type: ignore
        if not interaction.guild:
            return app_commands.NoPrivateMessage()
        guild: discord.Guild = interaction.guild
        member: discord.Member = guild.get_member(interaction.user.id)  # type: ignore
        if not channel.permissions_for(member).manage_channels:
            return app_commands.MissingPermissions(["manage_channels"])

        data = await self.bot.db_pool.fetchval(
            "SELECT auto_react FROM channels WHERE channel_id = $1", channel.id
        )
        if not data:
            data = []
        if len(data) >= 20:
            return await interaction.response.send_message(
                i18n.t("misc.auto_react_max", channel=channel.mention), ephemeral=True
            )
        if str(emoji) not in data:
            data.append(str(emoji))
        await self.bot.db_pool.execute(
            "INSERT INTO channels (channel_id, auto_react) VALUES ($1, $2) ON CONFLICT(channel_id) DO UPDATE SET auto_react = $2",
            channel.id,
            data,
        )
        return await interaction.response.send_message(
            i18n.t("misc.auto_react_added", emoji=emoji, channel=channel.mention), ephemeral=True
        )

    @app_commands.command(description="Remove an emoji that will be automatically added to every new message in the channel")
    @app_commands.describe(
        emoji="The emoji to remove. Can be a custom emoji or a unicode emoji.",
        channel="The channel to remove the emoji from. If not specified, the current channel will be used.",
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(add_reactions=True)
    async def remove(self, interaction: discord.Interaction, emoji: app_commands.Transform[discord.Emoji | str, EmojiTransformer], channel: discord.TextChannel = None):  # type: ignore
        if not channel:
            channel = interaction.channel  # type: ignore
        if not interaction.guild:
            return app_commands.NoPrivateMessage()
        guild: discord.Guild = interaction.guild
        member: discord.Member = guild.get_member(interaction.user.id)  # type: ignore
        if not channel.permissions_for(member).manage_channels:
            return app_commands.MissingPermissions(["manage_channels"])

        data = await self.bot.db_pool.fetchval(
            "SELECT auto_react FROM channels WHERE channel_id = $1", channel.id
        )
        if not data:
            data = []
        if str(emoji) in data:  # type: ignore
            data.remove(str(emoji))  # type: ignore
        await self.bot.db_pool.execute(
            "INSERT INTO channels (channel_id, auto_react) VALUES ($1, $2) ON CONFLICT(channel_id) DO UPDATE SET auto_react = $2",
            channel.id,
            data,
        )
        return await interaction.response.send_message(
            i18n.t("misc.auto_react_removed", emoji=emoji, channel=channel.mention), ephemeral=True
        )

    @remove.autocomplete("emoji")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        current = current.lower()
        emojis = await self.bot.db_pool.fetchval("SELECT auto_react FROM channels WHERE channel_id = $1", interaction.channel_id)  # type: ignore
        return [
            app_commands.Choice(
                name=emoji,
                value=emoji,
            )
            for emoji in emojis  # type: ignore
            if current.lower() in emoji
        ]

    @app_commands.command(description="List all emojis that will be automatically added to every new message in the channel")
    @app_commands.describe(
        channel="The channel to list the emojis from. If not specified, the current channel will be used.",
    )
    async def list(self, interaction: discord.Interaction, channel: discord.TextChannel = None):  # type: ignore
        if not channel:
            channel = interaction.channel # type: ignore
        
        data = await self.bot.db_pool.fetchval(
            "SELECT auto_react FROM channels WHERE channel_id = $1", channel.id
        )
        if not data:
            return await interaction.response.send_message(
                i18n.t("misc.auto_react_empty", channel=channel.mention), ephemeral=True
            )
        return await interaction.response.send_message(
            i18n.t("misc.auto_react_list", emojis=", ".join(data), channel=channel.mention), ephemeral=True # type: ignore
        )


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        data = await self.bot.db_pool.fetchval(
            "SELECT auto_react FROM channels WHERE channel_id = $1", message.channel.id
        )
        if data:
            for emoji in data:  # type: ignore
                await message.add_reaction(emoji)
