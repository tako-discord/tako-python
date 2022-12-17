import i18n
import discord
import logging
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
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

            language = get_language(bot, interaction.guild.id)

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
                    self.bot,
                    i18n.t("errors.bot_missing_perms_title", locale=language),
                    i18n.t("errors.bot_missing_perms", perms=fmt, locale=language),
                    interaction.guild.id,
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
                    self.bot,
                    i18n.t("errors.user_missing_perms_title", locale=language),
                    i18n.t("errors.user_missing_perms", perms=fmt, locale=language),
                    interaction.guild.id,
                )
                return await interaction.response.send_message(
                    embed=embed, file=file, ephemeral=True
                )

            if isinstance(error, app_commands.CommandOnCooldown):
                embed, file = error_embed(
                    self.bot,
                    i18n.t("errors.cooldown_title", locale=language),
                    i18n.t("errors.cooldown", perms=fmt, locale=language),
                    interaction.guild.id,
                )
                return await interaction.response.send_message(
                    embed=embed, file=file, ephemeral=True
                )

            if isinstance(error, app_commands.NoPrivateMessage):
                try:
                    embed, file = error_embed(
                        self.bot,
                        i18n.t("errors.no_pm_title", locale=language),
                        i18n.t("errors.no_pm", perms=fmt, locale=language),
                        interaction.guild.id,
                    )
                    return await interaction.response.send_message(
                        embed=embed, file=file, ephemeral=True
                    )
                except discord.Forbidden:
                    pass
                return

            if isinstance(error, app_commands.CheckFailure):
                embed, file = error_embed(
                    self.bot,
                    i18n.t("errors.check_failure_title", locale=language),
                    i18n.t("errors.check_failure", perms=fmt, locale=language),
                    interaction.guild.id,
                )
                return await interaction.response.send_message(
                    embed=embed, file=file, ephemeral=True
                )

            logger = logging.getLogger("discord")
            logger.error(error)
