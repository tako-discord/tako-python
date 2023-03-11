import re
import discord
from discord import app_commands
from discord.ext import commands


class Color(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Set the color of your embeds")
    @app_commands.describe(
        color="A valid 6 character HEX code. (Example: #FFFFFF, 0xFFFFFF, FFFFFF (White), None (Default))"
    )
    @app_commands.default_permissions(manage_guild=True)
    async def set_color(self, interaction: discord.Interaction, color: str):
        if color.lower() == "none":
            await self.bot.db_pool.execute(
                "INSERT INTO guilds(guild_id, color) VALUES($1, $2) ON CONFLICT(guild_id) DO UPDATE SET guild_id = $1, color = $2",
                interaction.guild_id,
                None,
            )
            return await interaction.response.send_message(
                "Your personal embed color is now back to default.", ephemeral=True
            )
        if color.startswith("#"):
            color = color.replace("#", "0x")
        if not color.startswith("0x"):
            color = f"0x{color}"
        match = re.search(r"^0x([A-Fa-f0-9]{6})$", color)
        if not match:
            return await interaction.response.send_message(
                "That's not a valid (*6* character) hex color.", ephemeral=True
            )

        await self.bot.db_pool.execute(
            "INSERT INTO guilds(guild_id, color) VALUES($1, $2) ON CONFLICT(guild_id) DO UPDATE SET guild_id = $1, color = $2",
            interaction.guild_id,
            color,
        )
        await interaction.response.send_message(
            f"Your personal embed color is now `{color}`.", ephemeral=True
        )
