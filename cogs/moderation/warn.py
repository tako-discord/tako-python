import i18n
import config
import discord
from time import mktime
from asyncpg import Record
from random import randint
from main import TakoBot
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from utils import error_embed, get_language, get_color, number_of_pages_needed


async def warn_pagination_logic(
    bot: TakoBot,
    warnings: list[Record],
    user: discord.User | discord.Member,
    original_user: discord.User | discord.Member,
    language: str,
    page: int,
    interaction: discord.Interaction,
    state: bool | None = None,  # True = add, False = remove
    interaction_created_at: datetime = datetime.now(),
):
    if not original_user == interaction.user:
        return
    if state:
        page += 1
    if state is False:
        page -= 1
    embed = discord.Embed(
        color=await get_color(bot, interaction.guild_id), timestamp=interaction_created_at  # type: ignore
    )
    embed.set_author(
        name=i18n.t(
            "moderation.warnings_title",
            amount=len(warnings),
            user=str(user),
            count=len(warnings),
        ),
        icon_url=user.display_avatar.url,
    )
    embed.set_footer(
        text=i18n.t(
            "general.page",
            locale=language,
            page=f"{page + 1}/{number_of_pages_needed(5, len(warnings))}",
        )
    )

    for warning in warnings[(5 * page) : (5 * (page + 1))]:
        embed.add_field(
            name=f"{warning['reason'] if warning['reason'] else i18n.t('moderation.no_reason', locale=language)}",
            value=i18n.t(
                "moderation.warned_by",
                locale=language,
                moderator=warning["moderator_id"],
                date=int(mktime(warning["timestamp"].timetuple())),
            )
            + f"\n`{warning['id']}`",
            inline=False,
        )

    if state is not None:
        await interaction.response.edit_message(
            embed=embed,
            view=WarnPagination(
                bot,
                warnings,
                user,
                interaction.user,
                language,
                page,
            ),
        )
        return
    await interaction.response.send_message(
        embed=embed,
        view=WarnPagination(
            bot,
            warnings,
            user,
            interaction.user,
            language,
            page,
        ),
    )


class WarnPagination(discord.ui.View):
    def __init__(
        self,
        bot: TakoBot,
        warnings: list[Record],
        user: discord.User | discord.Member,
        orginal_user: discord.User | discord.Member,
        language: str,
        page: int = 0,
        interaction_created_at: datetime = datetime.now(),
    ):
        super().__init__(timeout=None)
        self.bot = bot
        self.warnings = warnings
        self.user = user
        self.original_user = orginal_user
        self.language = language
        self.page = page

        if len(warnings) > 10:
            self.add_item(
                WarnFirst(
                    bot,
                    warnings,
                    user,
                    orginal_user,
                    language,
                    page,
                    interaction_created_at,
                )
            )
        if len(warnings) > 5:
            self.add_item(
                WarnPrevious(
                    bot,
                    warnings,
                    user,
                    orginal_user,
                    language,
                    page,
                    interaction_created_at,
                )
            )
        if len(warnings) > 5:
            self.add_item(
                WarnNext(
                    bot,
                    warnings,
                    user,
                    orginal_user,
                    language,
                    page,
                    interaction_created_at,
                )
            )
        if len(warnings) > 10:
            self.add_item(
                WarnLast(
                    bot,
                    warnings,
                    user,
                    orginal_user,
                    language,
                    page,
                    interaction_created_at,
                )
            )


class WarnPrevious(discord.ui.Button):
    def __init__(
        self,
        bot: TakoBot,
        warnings: list[Record],
        user: discord.User | discord.Member,
        orginal_user: discord.User | discord.Member,
        language: str,
        page: int = 0,
        interaction_created_at: datetime = datetime.now(),
    ):
        self.bot = bot
        self.warnings = warnings
        self.user = user
        self.original_user = orginal_user
        self.language = language
        self.page = page
        self.interaction_created_at = interaction_created_at
        super().__init__(
            emoji=config.EMOJI_ARROW_LEFT  # type: ignore
            if hasattr(config, "EMOJI_ARROW_LEFT")
            else "⬅️",
            style=discord.ButtonStyle.green,
            disabled=True if page == 0 else False,
        )

    async def callback(self, interaction: discord.Interaction):
        await warn_pagination_logic(
            self.bot,
            self.warnings,
            self.user,
            self.original_user,
            self.language,
            self.page,
            interaction,
            False,
            self.interaction_created_at,
        )


class WarnNext(discord.ui.Button):
    def __init__(
        self,
        bot: TakoBot,
        warnings: list[Record],
        user: discord.User | discord.Member,
        orginal_user: discord.User | discord.Member,
        language: str,
        page: int = 0,
        interaction_created_at: datetime = datetime.now(),
    ):
        self.bot = bot
        self.warnings = warnings
        self.user = user
        self.original_user = orginal_user
        self.language = language
        self.page = page
        self.interaction_created_at = interaction_created_at
        super().__init__(
            emoji=config.EMOJI_ARROW_RIGHT  # type: ignore
            if hasattr(config, "EMOJI_ARROW_RIGHT")
            else "➡️",
            style=discord.ButtonStyle.green,
            disabled=True if int(len(warnings) / 5) - 1 <= page else False,
        )

    async def callback(self, interaction: discord.Interaction):
        await warn_pagination_logic(
            self.bot,
            self.warnings,
            self.user,
            self.original_user,
            self.language,
            self.page,
            interaction,
            True,
            self.interaction_created_at,
        )


class WarnFirst(discord.ui.Button):
    def __init__(
        self,
        bot: TakoBot,
        warnings: list[Record],
        user: discord.User | discord.Member,
        orginal_user: discord.User | discord.Member,
        language: str,
        page: int = 0,
        interaction_created_at: datetime = datetime.now(),
    ):
        self.bot = bot
        self.warnings = warnings
        self.user = user
        self.original_user = orginal_user
        self.language = language
        self.page = page
        self.interaction_created_at = interaction_created_at
        super().__init__(
            emoji=config.EMOJI_ARROW_FIRST  # type: ignore
            if hasattr(config, "EMOJI_ARROW_FIRST")
            else "⏪",
            style=discord.ButtonStyle.green,
            disabled=True if page == 0 else False,
        )

    async def callback(self, interaction: discord.Interaction):
        await warn_pagination_logic(
            self.bot,
            self.warnings,
            self.user,
            self.original_user,
            self.language,
            0,
            interaction,
            None,
            self.interaction_created_at,
        )


class WarnLast(discord.ui.Button):
    def __init__(
        self,
        bot: TakoBot,
        warnings: list[Record],
        user: discord.User | discord.Member,
        orginal_user: discord.User | discord.Member,
        language: str,
        page: int = 0,
        interaction_created_at: datetime = datetime.now(),
    ):
        self.bot = bot
        self.warnings = warnings
        self.user = user
        self.original_user = orginal_user
        self.language = language
        self.page = page
        self.interaction_created_at = interaction_created_at
        super().__init__(
            emoji=config.EMOJI_ARROW_LAST  # type: ignore
            if hasattr(config, "EMOJI_ARROW_LAST")
            else "⏩",
            style=discord.ButtonStyle.green,
            disabled=True if int(len(warnings) / 5) <= page else False,
        )

    async def callback(self, interaction: discord.Interaction):
        await warn_pagination_logic(
            self.bot,
            self.warnings,
            self.user,
            self.original_user,
            self.language,
            number_of_pages_needed(5, len(self.warnings)) - 1,
            interaction,
            None,
            self.interaction_created_at,
        )


class Warn(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Warn a user", name="warn")
    @app_commands.describe(user="The user to warn", reason="The reason for the warning")
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_messages=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member,
        reason: str | None = None,
    ) -> None:
        if not interaction.guild:
            return
        language = get_language(self.bot, interaction.guild_id)

        if interaction.user == user:
            embed, file = error_embed(
                self.bot,
                i18n.t("moderation.warn_self_title", locale=language),
                i18n.t(f"moderation.warn_self_desc{randint(1,5)}", locale=language),
            )
            await interaction.response.send_message(
                embed=embed, file=file, ephemeral=True
            )
            return

        if user.bot:
            embed, file = error_embed(
                self.bot,
                i18n.t("moderation.warn_bot_title", locale=language),
                i18n.t(f"moderation.warn_bot_desc{randint(1,5)}", locale=language),
            )
            await interaction.response.send_message(
                embed=embed, file=file, ephemeral=True
            )
            return

        await self.bot.db_pool.execute(
            "INSERT INTO warnings (guild_id, user_id, moderator_id, reason) VALUES ($1, $2, $3, $4)",
            interaction.guild_id,
            user.id,
            interaction.user.id,
            reason,
        )

        dm_embed = discord.Embed(
            color=discord.Color.red(),
            description=i18n.t(
                "moderation.warned_dm",
                guild=interaction.guild.name,
                user=interaction.user.mention,
                success=config.EMOJI_CHECKMARK
                if hasattr(config, "EMOJI_CROSS")
                else "❌",
                locale=language,
            ),
        )

        return_embed = discord.Embed(
            color=discord.Color.green(),
            description=i18n.t(
                "moderation.warned",
                user=user.mention,
                success=config.EMOJI_CHECKMARK
                if hasattr(config, "EMOJI_CHECKMARK")
                else "✅",
                locale=language,
            ),
        )
        if reason:
            return_embed.add_field(
                name=i18n.t(
                    "moderation.reason",
                    user=user.mention,
                    success=config.EMOJI_CHECKMARK
                    if hasattr(config, "EMOJI_CHECKMARK")
                    else "✅",
                    locale=language,
                ),
                value=reason
                if reason
                else i18n.t("moderation_no_reason", locale=language),
            )
            dm_embed.add_field(
                name=i18n.t("moderation.reason", locale=language),
                value=reason
                if reason
                else i18n.t("moderation_no_reason", locale=language),
            )

        await interaction.response.send_message(embed=return_embed)

    @app_commands.command(description="List all warnings for a user")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(user="The user to list warnings for")
    @app_commands.guild_only()
    async def warnings(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member | None = None,
    ) -> None:
        if not user:
            user = interaction.user
        language = get_language(self.bot, interaction.guild_id)

        warnings = await self.bot.db_pool.fetch(
            "SELECT * FROM warnings WHERE guild_id = $1 AND user_id = $2",
            interaction.guild_id,
            user.id,
        )

        if not warnings:
            embed = discord.Embed(
                color=discord.Color.blue(),
                description=i18n.t(
                    "moderation.no_warnings",
                    locale=language,
                    user=user.mention,
                    info=config.EMOJI_INFO if hasattr(config, "EMOJI_INFO") else "ℹ",
                ),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await warn_pagination_logic(
            self.bot,
            warnings,
            user,
            interaction.user,
            language,
            0,
            interaction,
            None,
            interaction.created_at,
        )

    @app_commands.command(description="Remove all warnings from a user")
    @app_commands.describe(user="The user to remove all warnings from")
    @app_commands.default_permissions(manage_messages=True)
    async def clear_warnings(
        self, interaction: discord.Interaction, user: discord.User | discord.Member
    ) -> None:
        language = get_language(self.bot, interaction.guild_id)

        await self.bot.db_pool.execute(
            "DELETE FROM warnings WHERE guild_id = $1 AND user_id = $2",
            interaction.guild_id,
            user.id,
        )

        embed = discord.Embed(
            color=discord.Color.green(),
            description=i18n.t(
                "moderation.clear_warnings",
                locale=language,
                user=user.mention,
                success=config.EMOJI_CHECKMARK
                if hasattr(config, "EMOJI_CHECKMARK")
                else "✅",
            ),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(description="Delete a specific warning")
    @app_commands.describe(id="The ID of the warning to remove")
    @app_commands.default_permissions(manage_messages=True)
    async def del_warning(
        self,
        interaction: discord.Interaction,
        id: str,
    ) -> None:
        language = get_language(self.bot, interaction.guild_id)

        data = await self.bot.db_pool.fetchrow(
            "SELECT * FROM warnings WHERE id = $1", id
        )
        if not data:
            return

        await self.bot.db_pool.execute(
            "DELETE FROM warnings WHERE id = $1",
            id,
        )

        embed = discord.Embed(
            color=discord.Color.green(),
            description=i18n.t(
                "moderation.deleted_warning",
                locale=language,
                id=id,
                success=config.EMOJI_CHECKMARK
                if hasattr(config, "EMOJI_CHECKMARK")
                else "✅",
            ),
        )
        await interaction.response.send_message(embed=embed)

    @del_warning.autocomplete("id")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        current = current.lower()
        warnings = await self.bot.db_pool.fetch("SELECT * FROM warnings WHERE guild_id = $1", interaction.guild_id)  # type: ignore
        list = []
        for warning in warnings:
            reason = (
                warning["reason"]
                if warning["reason"]
                else i18n.t(
                    "moderation.no_reason",
                    locale=get_language(self.bot, interaction.guild_id),
                )
            )
            if (
                current in str(warning["id"])
                or current in reason
                or current in str(warning["user_id"])
            ):
                list.append(
                    app_commands.Choice(
                        name=f"{str(warning['id'])} - {reason} - {str(warning['user_id'])}",
                        value=str(warning["id"]),
                    )
                )
        return list
