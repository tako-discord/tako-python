import i18n
import discord
from TakoBot import TakoBot
from utils import get_language
from discord import app_commands
from discord.ext import commands

class ChannelLocking(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Locks a channel by removing every permission")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(channel="The channel to lock (Default: current channel)")
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(send_messages=False)}
        permissions = channel.overwrites
        permission_list = []
        for key, value in permissions.items():
            overwrites[key] = discord.PermissionOverwrite(view_channel=value.view_channel)
            values = list(value.pair())
            index = 0
            for value in values:
                values[index] = value.value
                index += 1
            cls_to_str = {
                discord.Member: "member",
                discord.Role: "role"
            }
            target_type = cls_to_str.get(getattr(key, "type", type(key)))
            permission_list.append((channel.id, key.id, values[0], values[1], target_type))
            await channel.set_permissions(key, overwrite=None)
        async with self.bot.db_pool.acquire() as conn:
            async with conn.transaction():
                await self.bot.db_pool.execute("INSERT INTO channels (channel_id, synced) VALUES ($1, $2) ON CONFLICT(channel_id) DO UPDATE SET synced = $2", channel.id, channel.permissions_synced)
                await self.bot.db_pool.executemany("INSERT INTO permissions (channel_id, target_id, allow, deny, type) VALUES ($1, $2, $3, $4, $5) ON CONFLICT(channel_id, target_id) DO UPDATE SET allow = $3, deny = $4, type= $5;", permission_list)
        await channel.edit(overwrites=overwrites, sync_permissions=False)
        await interaction.response.send_message(i18n.t("moderation.locked", channel=channel.mention, locale=get_language(self.bot, interaction.guild.id)))


    @app_commands.command(description="Unlocks a channel by restoring the permissions before locking")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(channel="The channel to unlock (Default: current channel)")
    async def unlock(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        if channel is None:
            channel = interaction.channel
        channel_synced = await self.bot.db_pool.fetchval("SELECT synced FROM channels WHERE channel_id = $1", channel.id)
        if channel_synced:
            category = channel.category
            if category is not None:
                await channel.edit(sync_permissions=True, category=category)
            return await interaction.response.send_message(i18n.t("moderation.locked", channel=channel.mention, locale=get_language(self.bot, interaction.guild.id)))
        permissions = await self.bot.db_pool.fetch("SELECT target_id, allow, deny, type FROM permissions WHERE channel_id = $1", channel.id)        
        overwrites = {}
        for permission in permissions:
            allow = discord.Permissions(permission["allow"])
            deny = discord.Permissions(permission["deny"])
            if permission["target_id"] == interaction.guild.id:
                target = interaction.guild.default_role
            else:
                target = discord.Object(id=permission["target_id"], type=discord.Role if permission["type"] == "role" else discord.Member)
            overwrites[target] = discord.PermissionOverwrite.from_pair(allow, deny)
        await channel.edit(overwrites=overwrites)
        return await interaction.response.send_message(i18n.t("moderation.unlocked", channel=channel.mention, locale=get_language(self.bot, interaction.guild.id)))
