import i18n
import discord
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import get_color, get_language, thumbnail, delete_thumbnail


async def autojoin_logic(
    bot: TakoBot, interaction: discord.Interaction, role: discord.Role, column: str
):
    language = get_language(bot, interaction.guild_id)
    if (
        role.is_default()
        or role.is_bot_managed()
        or role.managed
        or not role.is_assignable()
        or role >= interaction.user.top_role # type: ignore
        and interaction.guild.owner_id != interaction.user.id if interaction.guild else True
    ):
        return await interaction.response.send_message(
            i18n.t("config.invalid_role", locale=language), ephemeral=True
        )
    data = await bot.db_pool.fetchrow(
        "SELECT * FROM guilds WHERE guild_id = $1", interaction.guild_id
    )
    if not data:
        if column == "join_roles_user":
            await bot.db_pool.execute(
                "INSERT INTO guilds (guild_id, join_roles_user) VALUES ($1, $2)",
                interaction.guild_id,
                [role.id],
            )
        else:
            await bot.db_pool.execute(
                "INSERT INTO guilds (guild_id, join_roles_bot) VALUES ($1, $2)",
                interaction.guild_id,
                [role.id],
            )
        return await interaction.response.send_message(
            i18n.t("config.autojoinroles_added", role=role.name, locale=language),
            ephemeral=True,
        )
    array = data[column]
    if array is None:
        array = []
    if role.id not in array:
        array.append(role.id)
        if column == "join_roles_user":
            await bot.db_pool.execute(
                "UPDATE guilds SET join_roles_user = $1 WHERE guild_id = $2",
                array,
                interaction.guild_id,
            )
        else:
            await bot.db_pool.execute(
                "UPDATE guilds SET join_roles_bot = $1 WHERE guild_id = $2",
                array,
                interaction.guild_id,
            )
        return await interaction.response.send_message(
            i18n.t("config.autojoinroles_added", role=role.name, locale=language),
            ephemeral=True,
        )
    array.remove(role.id)
    if column == "join_roles_user":
        await bot.db_pool.execute(
            "UPDATE guilds SET join_roles_user = $1 WHERE guild_id = $2",
            array,
            interaction.guild_id,
        )
    else:
        await bot.db_pool.execute(
            "UPDATE guilds SET join_roles_bot = $1 WHERE guild_id = $2",
            array,
            interaction.guild_id,
        )
        return await interaction.response.send_message(
            i18n.t("config.autojoinroles_removed", role=role.name, locale=language),
            ephemeral=True,
        )


def no_roles_field(embed: discord.Embed, type: str, language: str = "en"):
    embed.add_field(
        name=i18n.t("config.autojoinroles_empty_title", type=type, locale=language),
        value=i18n.t("config.autojoinroles_empty", type=type, locale=language),
        inline=False,
    )


class Autojoin(commands.GroupCog, group_name="autojoinroles"):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(
        description="Toggle a role that will be automatically added to new users"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(
        role="The role that should be toggled in the autojoinrole list"
    )
    async def user(self, interaction: discord.Interaction, role: discord.Role):
        await autojoin_logic(self.bot, interaction, role, "join_roles_user")

    @app_commands.command(
        description="Toggle a role that will be automatically added to new bots"
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.guild_only()
    @app_commands.describe(
        role="The role that should be toggled in the autojoinrole list"
    )
    async def bot(self, interaction: discord.Interaction, role: discord.Role):
        await autojoin_logic(self.bot, interaction, role, "join_roles_bot")

    @app_commands.command(
        description="List all roles that will be automatically added to new members"
    )
    async def list(self, interaction: discord.Interaction):
        await interaction.response.defer()
        language = get_language(self.bot, interaction.guild.id)
        data = await self.bot.db_pool.fetchrow(
            "SELECT * FROM guilds WHERE guild_id = $1", interaction.guild_id
        )
        thumbnail_path = await thumbnail(interaction.guild.id, "role", self.bot)
        file = discord.File(thumbnail_path, filename="thumbnail.png")
        embed = discord.Embed(
            title=i18n.t(
                "config.autojoinroles_title",
                guild=interaction.guild.name,
                locale=language,
            ),
            description=i18n.t("config.autojoinroles_desc", locale=language),
            color=await get_color(self.bot, interaction.guild.id), # type: ignore
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")
        if not data:
            no_roles_field(embed, "users", language)
            no_roles_field(embed, "bots", language)
        else:
            user_array = data["join_roles_user"]
            bot_array = data["join_roles_bot"]
            # Adding User field
            if not user_array:
                no_roles_field(embed, "users", language)
            else:
                embed.add_field(
                    name=i18n.t("config.autojoinroles_users", locale=language),
                    value="\n".join([f"<@&{role}> ({role})" for role in user_array]),
                    inline=False,
                )
            # Adding Bot field
            if not bot_array:
                no_roles_field(embed, "bots", language)
            else:
                embed.add_field(
                    name=i18n.t("config.autojoinroles_bots", locale=language),
                    value="\n".join([f"<@&{role}> ({role})" for role in bot_array]),
                    inline=False,
                )
        await interaction.followup.send(embed=embed, file=file)
        delete_thumbnail(interaction.guild_id, "role") # type: ignore

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        data = await self.bot.db_pool.fetchrow(
            "SELECT * FROM guilds WHERE guild_id = $1", member.guild.id
        )
        if not data:
            return
        if member.bot:
            try:
                for role in data["join_roles_bot"]:
                    role = member.guild.get_role(int(role))
                    if role:
                        await member.add_roles(role)
                return
            except TypeError:
                return
        if "MEMBER_VERIFICATION_GATE_ENABLED" in member.guild.features:
            return
        for role in data["join_roles_user"]:
            try:
                role = member.guild.get_role(int(role))
                if role:
                    await member.add_roles(role)
            except TypeError:
                return

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.pending and not after.pending:
            data = await self.bot.db_pool.fetchval(
                "SELECT join_roles_user FROM guilds WHERE guild_id = $1", after.guild.id
            )
            if not data:
                return
            for role in data:
                role = after.guild.get_role(int(role))
                if role:
                    await after.add_roles(role)
