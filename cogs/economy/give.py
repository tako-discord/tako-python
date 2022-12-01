import i18n
import config
import discord
from discord import app_commands
from discord.ext import commands
from utils import fetch_cash, get_color, get_language, is_owner_func


class Give(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Give other users money from your wallet")
    @app_commands.describe(
        user="The user to give the money to", amount="The amount of money to give away"
    )
    async def give(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member,
        amount: int,
    ):
        language = get_language(self.bot, interaction.guild.id)
        if user.bot:
            return await interaction.response.send_message(
                i18n.t("economy.not_bot", locale=language), ephemeral=True
            )
        if user == interaction.user and not await self.bot.is_owner(interaction.user):
            return await interaction.response.send_message(
                i18n.t("economy.not_self", locale=language), ephemeral=True
            )
        if amount <= 0:
            return await interaction.response.send_message(
                i18n.t(
                    "economy.more_than", amount=f"0{config.CURRENCY}", locale=language
                ),
                ephemeral=True,
            )
        cash = await fetch_cash(self.bot.db_pool, interaction.user)
        is_owner = await is_owner_func(self.bot, interaction.user)
        if cash[0] < amount and not is_owner:
            return await interaction.response.send_message(
                i18n.t("economy.not_enough", locale=language), ephemeral=True
            )

        target_cash = await fetch_cash(self.bot.db_pool, user)
        async with self.bot.db_pool.acquire() as conn:
            async with conn.transaction():
                if not is_owner:
                    await conn.execute(
                        "UPDATE users SET wallet = $1 WHERE user_id = $2;",
                        cash[0] - amount,
                        interaction.user.id,
                    )
                await conn.execute(
                    "UPDATE users SET wallet = $1 WHERE user_id = $2",
                    target_cash[0] + amount,
                    user.id,
                )

        embed = discord.Embed(
            description=f"", color=await get_color(self.bot, interaction.guild.id)
        )
        if not is_owner:
            embed.add_field(
                name=str(interaction.user),
                value=f"{cash[0]} → {cash[0] - amount}{config.CURRENCY}",
                inline=False,
            )
        embed.add_field(
            name=str(user),
            value=f"{target_cash[0]} → {target_cash[0] + amount}{config.CURRENCY}",
        )

        await interaction.response.send_message(
            i18n.t(
                "economy.give",
                user=interaction.user.mention,
                target=user.mention,
                amount=f"**{amount}{config.CURRENCY}**",
                locale=language,
            ),
            embed=embed,
        )
