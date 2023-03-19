import i18n
import discord
import logging
from time import time
from main import TakoBot
from discord.ext import commands
from discord import app_commands, Locale
from utils import get_language, error_embed


class CommandErrorHandler(commands.Cog):
    def __init__(self, bot: TakoBot):
        @bot.tree.error
        async def on_app_command_error(
            interaction: discord.Interaction,
            error: app_commands.AppCommandError,
        ):
            if isinstance(error, app_commands.CommandNotFound):
                return

            locale_dict = {
                Locale.german: "de",
                Locale.american_english: "en",
                Locale.british_english: "en",
                Locale.spain_spanish: "es",
                Locale.french: "fr",
                Locale.croatian: "hr",
                Locale.japanese: "ja",
                Locale.dutch: "nl",
                Locale.polish: "pl",
                Locale.brazil_portuguese: "pt",
                Locale.swedish: "sv",
                Locale.chinese: "zh",
            }
            language = get_language(bot, interaction.guild_id)
            try:
                language = locale_dict[interaction.locale]
            except KeyError:
                pass

            if isinstance(error, app_commands.BotMissingPermissions):
                missing = [
                    perm.replace("_", " ").replace("guild", "server").title()
                    for perm in error.missing_permissions
                ]
                if len(missing) > 2:
                    fmt = "{}, & {}".format("**, **".join(missing[:-1]), missing[-1])
                else:
                    fmt = " & ".join(missing)
                embed, file = error_embed(
                    bot,
                    i18n.t("errors.bot_missing_perms_title", locale=language),
                    i18n.t("errors.bot_missing_perms", perms=fmt, locale=language),
                    interaction.guild_id,
                )
                return await interaction.response.send_message(
                    embed=embed, file=file, ephemeral=True
                )

            if isinstance(error, app_commands.MissingPermissions):
                missing = [
                    perm.replace("_", " ").replace("guild", "server").title()
                    for perm in error.missing_permissions
                ]
                if len(missing) > 2:
                    fmt = "{}, & {}".format("**, **".join(missing[:-1]), missing[-1])
                else:
                    fmt = " & ".join(missing)
                embed, file = error_embed(
                    bot,
                    i18n.t("errors.user_missing_perms_title", locale=language),
                    i18n.t("errors.user_missing_perms", perms=fmt, locale=language),
                    interaction.guild_id,
                )
                return await interaction.response.send_message(
                    embed=embed, file=file, ephemeral=True
                )

            if isinstance(error, app_commands.CommandOnCooldown):
                embed, file = error_embed(
                    bot,
                    i18n.t("errors.cooldown_title", locale=language),
                    i18n.t(
                        "errors.cooldown",
                        locale=language,
                        time=int(time()) + int(error.retry_after),
                    ),
                    interaction.guild_id,
                )
                return await interaction.response.send_message(
                    embed=embed, file=file, ephemeral=True
                )

            if isinstance(error, app_commands.NoPrivateMessage):
                try:
                    embed, file = error_embed(
                        bot,
                        i18n.t("errors.no_pm_title", locale=language),
                        i18n.t("errors.no_pm", locale=language),
                    )
                    return await interaction.response.send_message(
                        embed=embed, file=file, ephemeral=True
                    )
                except discord.Forbidden:
                    pass
                return

            if isinstance(error, app_commands.CheckFailure):
                embed, file = error_embed(
                    bot,
                    i18n.t("errors.check_failure_title", locale=language),
                    i18n.t("errors.check_failure", locale=language),
                    interaction.guild_id,
                )
                return await interaction.response.send_message(
                    embed=embed, file=file, ephemeral=True
                )

            logger = logging.getLogger("discord")
            logger.error(error)
