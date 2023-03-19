from random import choices, randint

import discord
from discord import app_commands
from discord.ext import commands

import i18n
import config
from main import TakoBot
from utils import fetch_cash, get_language, get_color, thumbnail


class Beg(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.cooldown(1, 60 * 60 * 3)
    async def beg(self, interaction: discord.Interaction):
        received = choices([True, False], weights=[0.9, 0.1])[0]
        over_100 = choices([True, False], weights=[0.1, 0.9])[0]
        amount = randint(10, 100) if not over_100 else randint(100, 1000)
        balance = await fetch_cash(self.bot.db_pool, interaction.user)

        embed = discord.Embed(
            color=await get_color(self.bot, interaction.guild_id),  # type: ignore
            title=f"\n{balance[0]} → {balance[0] + amount}" + config.CURRENCY
            if config.CURRENCY
            else "TK"
            if received
            else i18n.t(
                "economy.begging_failed" + str(randint(1, 4)),
                locale=get_language(self.bot, interaction.guild_id),
            ),
            description=i18n.t(
                "economy.begged_" + str(received).lower(),
                locale=get_language(self.bot, interaction.guild_id),
                amount=str(amount) + config.CURRENCY if config.CURRENCY else "TK",
            ),
        )

        thumbnail_path = await thumbnail(interaction.guild_id, "money", self.bot)
        embed.set_thumbnail(url="attachment://thumbnail.png")
        file = discord.File(thumbnail_path, filename="thumbnail.png")

        await self.bot.db_pool.execute(
            "UPDATE users SET wallet = wallet + $1 WHERE user_id = $2",
            amount,
            interaction.user.id,
        )

        await interaction.response.send_message(embed=embed, file=file)
