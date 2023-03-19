from random import randint

import discord
from datetime import datetime, timedelta
from discord import app_commands
from discord.ext import commands

import i18n
import config
from main import TakoBot
from utils import fetch_cash, get_language, get_color, thumbnail

cooldown = 60 * 60 * 24


class Daily(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command()
    async def daily(self, interaction: discord.Interaction):
        last_daily = await self.bot.db_pool.fetchval(
            "SELECT last_daily FROM users WHERE user_id = $1", interaction.user.id
        )
        if isinstance(last_daily, datetime):
            current_time = datetime.now()
            elapsed_time = current_time - last_daily
            if elapsed_time.total_seconds() < cooldown:
                raise app_commands.CommandOnCooldown(
                    app_commands.Cooldown(1, cooldown),
                    (60 * 60 * 24) - (current_time - last_daily).total_seconds(),
                )

        amount = randint(500, 1500)
        balance = await fetch_cash(self.bot.db_pool, interaction.user)

        embed = discord.Embed(
            color=await get_color(self.bot, interaction.guild_id),  # type: ignore
            title=f"\n{balance[0]} → {balance[0] + amount}" + config.CURRENCY
            if config.CURRENCY
            else "TK",
            description=i18n.t(
                "economy.daily",
                locale=get_language(self.bot, interaction.guild_id),
                user=interaction.user.display_name,
                amount=str(amount) + config.CURRENCY if config.CURRENCY else "TK",
            ),
        )

        thumbnail_path = await thumbnail(interaction.guild_id, "money", self.bot)
        embed.set_thumbnail(url="attachment://thumbnail.png")
        file = discord.File(thumbnail_path, filename="thumbnail.png")

        await self.bot.db_pool.execute(
            "UPDATE users SET wallet = wallet + $1, last_daily = $2 WHERE user_id = $3",
            amount,
            datetime.now(),
            interaction.user.id,
        )

        await interaction.response.send_message(embed=embed, file=file)
