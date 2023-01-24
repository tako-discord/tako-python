import emoji
import discord
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands


class EmojiTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str):
        is_emoji = emoji.is_emoji(value)
        return await commands.PartialEmojiConverter().convert((await commands.Context.from_interaction(interaction)), value) if not is_emoji else value  # type: ignore


class AutoReact(commands.GroupCog, group_name="auto_react"):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command()
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
        if str(emoji) not in data:
            data.append(str(emoji))
        await self.bot.db_pool.execute(
            "INSERT INTO channels (channel_id, auto_react) VALUES ($1, $2) ON CONFLICT(channel_id) DO UPDATE SET auto_react = $2",
            channel.id,
            data,
        )
        return await interaction.response.send_message(
            f"Added {emoji} to {channel.mention}", ephemeral=True
        )

    @app_commands.command()
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
            f"Removed {emoji} from {channel.mention}", ephemeral=True
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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        data = await self.bot.db_pool.fetchval(
            "SELECT auto_react FROM channels WHERE channel_id = $1", message.channel.id
        )
        if data:
            for emoji in data:  # type: ignore
                await message.add_reaction(emoji)
