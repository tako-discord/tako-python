import discord
from discord import app_commands
from discord.ext import commands
from utils import fetch_cash, balance_embed, get_language


class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Check a users balance")
    @app_commands.describe(user="The user to check the balance of (Default: you)")
    async def balance(
        self, interaction: discord.Interaction, user: discord.User = None
    ):
        if user is None:
            user = interaction.user
        if user.bot:
            import i18n
            import config

            return await interaction.response.send_message(
                i18n.t(
                    "economy.not_bot_balance",
                    locale=get_language(self.bot, interaction.guild_id),
                    currency=config.CURRENCY.replace(" ", "", 1)
                    if hasattr(config, "CURRENCY")
                    else " :coin:",
                ),
                ephemeral=True,
            )

        cash = await fetch_cash(self.bot.db_pool, user)
        embed, file = await balance_embed(self.bot, user, interaction.guild_id, cash)
        await interaction.response.send_message(embed=embed, file=file)
