import i18n
import discord
from typing import List
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import get_color, get_language


def handle_flags(flags: discord.UserFlags, language: str):
    flags_array = []
    flag_dict = {
        "staff": i18n.t("info.staff", locale=language),
        "partner": i18n.t("info.partner", locale=language),
        "bug_hunter": i18n.t("info.bug_hunter", locale=language),
        "hypesquad": i18n.t("info.hypesquad", locale=language),
        "hypesquad_bravery": i18n.t("info.hypesquad_bravery", locale=language),
        "hypesquad_brilliance": i18n.t("info.hypesquad_brilliance", locale=language),
        "hypesquad_balance": i18n.t("info.hypesquad_balance", locale=language),
        "early_supporter": i18n.t("info.early_supporter", locale=language),
        "team_user": i18n.t("info.team_user", locale=language),
        "system": i18n.t("info.system", locale=language),
        "bug_hunter_level_2": i18n.t("info.bug_hunter_level_2", locale=language),
        "verified_bot": i18n.t("info.verified_bot", locale=language),
        "verified_bot_developer": i18n.t(
            "info.verified_bot_developer", locale=language
        ),
        "early_verified_bot_developer": i18n.t(
            "info.early_verified_bot_developer", locale=language
        ),
        "discord_certified_moderator": i18n.t(
            "info.discord_certified_moderator", locale=language
        ),
        "bot_http_interactions": i18n.t("info.bot_http_interactions", locale=language),
        "spammer": i18n.t("info.spammer", locale=language),
        "active_developer": i18n.t("info.active_developer", locale=language),
    }
    for flag in flags:
        flag_for_dict = str(flag).replace("UserFlags.", "")
        if flags.index(flag) == len(flags) - 2:
            flags_array.append(flag_dict[flag_for_dict] + " & ")
            continue
        if flags.index(flag) == len(flags) - 1:
            flags_array.append(flag_dict[flag_for_dict])
            continue
        flags_array.append(flag_dict[flag_for_dict] + ", ")
    return "".join(flags_array)


def handle_roles(roles: List[discord.Role]):
    final_roles_list = []
    roles_list = list(reversed(roles[1:]))
    for role in roles_list:
        if roles_list.index(role) == len(roles_list) - 2:
            final_roles_list.append(role.mention + " & ")
            continue
        if roles_list.index(role) == len(roles_list) - 1:
            final_roles_list.append(role.mention)
            continue
        final_roles_list.append(role.mention + ", ")
    return "".join(final_roles_list)


# ankucken
def handle_badge_users(bot: TakoBot, users: List[int]):
    final_users_list = []
    for user in users:
        user = bot.get_user(user)
        if users.index(user.id) == len(users) - 2:
            final_users_list.append(user.mention + " & ")
            continue
        if users.index(user.id) == len(users) - 1:
            final_users_list.append(user.mention)
            continue
        final_users_list.append(user.mention + ", ")
    return (
        f"{''.join(final_users_list[:50])}{'...' if len(final_users_list) > 50 else ''}"
    )


class InfoGroup(commands.GroupCog, group_name="info"):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Get information about a user or yourself")
    @app_commands.describe(user="The user to get information about")
    async def user(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member = None,
    ):
        if user == None:
            user = interaction.user
        language = get_language(self.bot, interaction.guild.id)
        user_flags = user.public_flags.all()
        general = [
            "",
            i18n.t(
                "info.username_discrim",
                name=str(user),
                locale=language,
            ),
            f"**ID**: {user.id}",
            f"**Flags**: {handle_flags(user_flags, language) if len(user_flags) else i18n.t('info.no_flags', locale=language)}",
            i18n.t(
                "info.created_on",
                locale=language,
                date=user.created_at.strftime(
                    i18n.t("info.date_format", locale=language)
                ),
            ),
            i18n.t(
                "info.avatar",
                avatar=f"[PNG]({user.avatar.replace(size=512, format='png').url}), [JPG]({user.avatar.replace(size=512, format='jpg').url}), [{'GIF' if user.avatar.is_animated() else 'WEBP'}]({user.avatar.replace(size=512, format='gif', static_format='webp').url})",
                locale=language,
            ),
        ]
        if hasattr(user, "guild"):
            server = [
                "",
                i18n.t(
                    "info.joined_on",
                    date=user.joined_at.strftime(
                        i18n.t("info.date_format", locale=language)
                    ),
                    locale=language,
                ),
                i18n.t(
                    "info.top_role",
                    role=user.top_role.mention
                    if len(user.roles) > 1
                    else i18n.t("info.no_roles", locale=language),
                    locale=language,
                ),
                i18n.t(
                    "info.hoist_role",
                    role=discord.utils.get(reversed(user.roles), hoist=True).mention
                    if discord.utils.get(reversed(user.roles), hoist=True)
                    else i18n.t("info.no_roles", locale=language),
                    locale=language,
                ),
                i18n.t(
                    "info.roles",
                    roles=handle_roles(user.roles)
                    if len(user.roles) > 1
                    else i18n.t("info.no_roles", locale=language),
                    locale=language,
                ),
            ]
        embed = discord.Embed(
            title=i18n.t("info.title", name=user.display_name, locale=language),
            description=i18n.t("info.infos_about", name=user.mention, locale=language),
            color=user.color if hasattr(user, "guild") else user.accent_color,
        )
        embed.add_field(
            name=i18n.t("info.general", locale=language),
            value="\n**❯** ".join(general),
            inline=False,
        )
        embed.add_field(
            name=i18n.t("info.server", locale=language),
            value="\n**❯** ".join(server)
            if hasattr(user, "guild")
            else i18n.t("info.not_in_server", locale=language),
            inline=False,
        )
        embed.set_thumbnail(url=user.display_avatar)
        badges_list = []
        badges = await self.bot.db_pool.fetch("SELECT emoji, users FROM badges")
        for badge in badges:
            if badge["users"] is None:
                continue
            for id in badge["users"]:
                if user.id == id:
                    badges_list.append(badge["emoji"])
        if len(badges_list):
            embed.add_field(
                name="Badges",
                value=i18n.t("info.more_badge_info", locale=language)
                + " ".join(badges_list),
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Get some infos about a badge")
    async def badge(self, interaction: discord.Interaction, badge: str):
        badge = await self.bot.db_pool.fetchrow(
            "SELECT * FROM badges WHERE name = $1", badge
        )
        locale = get_language(self.bot, interaction.guild.id)
        if badge is None:
            return await interaction.response.send_message(
                i18n.t(
                    "info.badge_not_found",
                    locale=locale,
                ),
                ephemeral=True,
            )
        embed = discord.Embed(
            title=badge["emoji"]
            + " "
            + i18n.t(f"badges.{badge['name']}_title", locale=locale),
            description=i18n.t(f"badges.{badge['name']}_desc", locale=locale),
            color=(await get_color(self.bot, interaction.guild.id)),
        )
        if badge["users"]:
            embed.add_field(
                name=i18n.t(
                    "info.users_with_badge",
                    amount=len(badge["users"]),
                    locale=get_language(self.bot, interaction.guild.id),
                ),
                value=handle_badge_users(self.bot, badge["users"]),
            )
        await interaction.response.send_message(embed=embed)

    @badge.autocomplete("badge")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        def localized_badge_name(badge: str, locale: str):
            return i18n.t(f"badges.{badge}_title", locale=locale)

        current = current.lower()
        badges = await self.bot.db_pool.fetch("SELECT * FROM badges")
        locale = get_language(self.bot, interaction.guild.id)
        return [
            app_commands.Choice(
                name=f"{localized_badge_name(badge['name'], locale)} ({badge['emoji']})",
                value=badge["name"],
            )
            for badge in badges
            if current.lower() in badge["name"].lower()
            or current in badge["emoji"].lower()
        ]
