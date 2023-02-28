import i18n
import discord
from discord import app_commands
from discord.ext import commands
from utils import fetch_cash, get_language, balance_embed


class Bank(commands.GroupCog, group_name="bank"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Deposit TK on your bank account")
    @app_commands.describe(amount="The amount of TK to deposit")
    async def deposit(self, interaction: discord.Interaction, amount: int):
        cash = await fetch_cash(self.bot.db_pool, interaction.user)
        language = get_language(self.bot, interaction.guild_id)

        if amount > cash[0]:
            return await interaction.response.send_message(
                i18n.t("economy.not_enough", locale=language), ephemeral=True
            )

        async with self.bot.db_pool.acquire() as con:
            async with con.transaction():
                await con.execute(
                    "UPDATE users SET wallet=$2, bank=$3 WHERE user_id=$1",
                    interaction.user.id,
                    cash[0] - amount,
                    cash[1] + amount,
                )
                cash = await fetch_cash(con, interaction.user)
                embed, file = await balance_embed(
                    self.bot, interaction.user, interaction.guild_id, cash
                )
                await interaction.response.send_message(embed=embed, file=file)

    @app_commands.command(description="Withdraw TK from your bank account")
    @app_commands.describe(amount="The amount of TK to withdraw")
    async def withdraw(self, interaction: discord.Interaction, amount: int):
        cash = await fetch_cash(self.bot.db_pool, interaction.user)
        language = get_language(self.bot, interaction.guild_id)

        if amount > cash[1]:
            return await interaction.response.send_message(
                i18n.t("economy.not_enough", locale=language), ephemeral=True
            )

        async with self.bot.db_pool.acquire() as con:
            async with con.transaction():
                await con.execute(
                    "UPDATE users SET wallet=$2, bank=$3 WHERE user_id=$1",
                    interaction.user.id,
                    cash[0] + amount,
                    cash[1] - amount,
                )
                cash = await fetch_cash(con, interaction.user)
                embed, file = await balance_embed(
                    self.bot, interaction.user, interaction.guild_id, cash
                )
                await interaction.response.send_message(embed=embed, file=file)
