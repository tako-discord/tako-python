import i18n
import discord
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import get_language, error_embed


class ChannelLocking(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Locks a channel by removing every permission")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(channel="The channel to lock (Default: current channel)")
    async def lock(
        self, interaction: discord.Interaction, channel: discord.TextChannel = None
    ):
        if channel is None:
            channel = interaction.channel
        locked = await self.bot.db_pool.fetchval(
            "SELECT locked FROM channels WHERE channel_id = $1", channel.id
        )
        language = get_language(self.bot, interaction.guild.id)
        if locked:
            embed, file = error_embed(
                self.bot,
                i18n.t("errors.already_locked_title", locale=language),
                i18n.t(
                    "errors.already_locked", locale=language, channel=channel.mention
                ),
                interaction.guild.id,
            )
            return await interaction.response.send_message(
                embed=embed, file=file, ephemeral=True
            )
        permissions = channel.overwrites
        permission_list = []
        overwrites = {}
        for key, value in permissions.items():
            overwrites[key] = discord.PermissionOverwrite(
                view_channel=value.view_channel,
                send_messages=False if key.is_default() else None,
            )
            values = list(value.pair())
            index = 0
            for value in values:
                values[index] = value.value
                index += 1
            cls_to_str = {discord.Member: "member", discord.Role: "role"}
            target_type = cls_to_str.get(getattr(key, "type", type(key)))
            permission_list.append(
                (channel.id, key.id, values[0], values[1], target_type)
            )
            await channel.set_permissions(key, overwrite=None)
        async with self.bot.db_pool.acquire() as conn:
            async with conn.transaction():
                await self.bot.db_pool.execute(
                    "INSERT INTO channels (channel_id, synced, locked) VALUES ($1, $2, $3) ON CONFLICT(channel_id) DO UPDATE SET synced = $2, locked = $3",
                    channel.id,
                    channel.permissions_synced,
                    True,
                )
                await self.bot.db_pool.executemany(
                    "INSERT INTO permissions (channel_id, target_id, allow, deny, type) VALUES ($1, $2, $3, $4, $5) ON CONFLICT(channel_id, target_id) DO UPDATE SET allow = $3, deny = $4, type= $5;",
                    permission_list,
                )
        await channel.edit(overwrites=overwrites, sync_permissions=False)
        embed = discord.Embed(
            title=i18n.t(
                "moderation.locked_title", channel=channel.name, locale=language
            ),
            description=i18n.t(
                "moderation.locked_desc", channel=channel.mention, locale=language
            ),
            color=discord.Color.red(),
        )
        return await interaction.response.send_message(embed=embed)

    @app_commands.command(
        description="Unlocks a channel by restoring the permissions before locking"
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(channel="The channel to unlock (Default: current channel)")
    async def unlock(
        self, interaction: discord.Interaction, channel: discord.TextChannel = None
    ):
        if channel is None:
            channel = interaction.channel
        locked = await self.bot.db_pool.fetchval(
            "SELECT locked FROM channels WHERE channel_id = $1", channel.id
        )
        language = get_language(self.bot, interaction.guild.id)
        if not locked:
            embed, file = error_embed(
                self.bot,
                i18n.t("errors.not_locked_title", locale=language),
                i18n.t("errors.not_locked", locale=language, channel=channel.mention),
                interaction.guild.id,
            )
            return await interaction.response.send_message(
                embed=embed, file=file, ephemeral=True
            )
        channel_synced = await self.bot.db_pool.fetchval(
            "SELECT synced FROM channels WHERE channel_id = $1", channel.id
        )
        embed = discord.Embed(
            title=i18n.t(
                "moderation.unlocked_title", channel=channel.name, locale=language
            ),
            description=i18n.t(
                "moderation.unlocked_desc", channel=channel.mention, locale=language
            ),
            color=discord.Color.green(),
        )
        if channel_synced:
            category = channel.category
            if category is not None:
                embed.set_footer(
                    text=i18n.t("moderation.unlocked_footer", locale=language)
                )
                await channel.edit(sync_permissions=True, category=category)
                await self.bot.db_pool.execute(
                    "UPDATE channels SET locked = $1 WHERE channel_id = $2",
                    False,
                    channel.id,
                )
                return await interaction.response.send_message(embed=embed)
        permissions = await self.bot.db_pool.fetch(
            "SELECT target_id, allow, deny, type FROM permissions WHERE channel_id = $1",
            channel.id,
        )
        overwrites = {}
        for permission in permissions:
            allow = discord.Permissions(permission["allow"])
            deny = discord.Permissions(permission["deny"])
            if permission["target_id"] == interaction.guild.id:
                target = interaction.guild.default_role
            else:
                target = discord.Object(
                    id=permission["target_id"],
                    type=discord.Role
                    if permission["type"] == "role"
                    else discord.Member,
                )
            overwrites[target] = discord.PermissionOverwrite.from_pair(allow, deny)
        await channel.edit(overwrites=overwrites)
        await self.bot.db_pool.execute(
            "UPDATE channels SET locked = $1 WHERE channel_id = $2", False, channel.id
        )
        return await interaction.response.send_message(embed=embed)
