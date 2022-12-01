import i18n
import random
import config
import discord
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import get_color, create_user, get_language


class Gamble(commands.GroupCog, group_name="gamble"):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Play head or tail")
    @app_commands.describe(
        bet="The amount of TK to bet", guess="The guess you want to make"
    )
    @app_commands.choices(
        guess=[
            app_commands.Choice(name="Head", value=1),
            app_commands.Choice(name="Tail", value=2),
        ]
    )
    async def flip(self, interaction: discord.Interaction, bet: int, guess: int):
        language = get_language(self.bot, interaction.guild.id)
        wallet = await self.bot.db_pool.fetchval(
            "SELECT wallet FROM users WHERE user_id = $1;", interaction.user.id
        )
        if not wallet:
            await create_user(self.bot.db_pool, interaction.user)
        if bet > wallet:
            return await interaction.response.send_message(
                i18n.t("economy.not_enough", locale=language), ephemeral=True
            )
        result = random.randint(1, 2)
        embed = discord.Embed(
            title=i18n.t("economy.ht", locale=language),
            color=await get_color(self.bot, interaction.guild.id),
            description=i18n.t(
                "economy.ht_won", locale=language, amount=str(bet) + config.CURRENCY
            )
            if result == guess
            else i18n.t(
                "economy.ht_lost", locale=language, amount=str(bet) + config.CURRENCY
            ),
        )
        embed.add_field(
            name=i18n.t("economy.bet", locale=language),
            value=str(bet) + config.CURRENCY,
        )
        embed.add_field(
            name=i18n.t("economy.guess", locale=language),
            value=i18n.t("economy.head", locale=language)
            if guess == 1
            else i18n.t("economy.tail", locale=language),
        )
        embed.add_field(
            name=i18n.t("economy.new_balance", locale=language),
            value=str(wallet + bet) + config.CURRENCY
            if result == guess
            else str(wallet - bet) + config.CURRENCY,
            inline=False,
        )
        if result == guess:
            await self.bot.db_pool.execute(
                "UPDATE users SET wallet = wallet + $1 WHERE user_id = $2;",
                bet,
                interaction.user.id,
            )
        else:
            await self.bot.db_pool.execute(
                "UPDATE users SET wallet = wallet - $1 WHERE user_id = $2;",
                bet,
                interaction.user.id,
            )
        await interaction.response.send_message(embed=embed)
