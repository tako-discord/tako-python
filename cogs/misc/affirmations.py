import discord
import aiohttp
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands


class Affirmations(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Feel bad? Get some affirmations!")
    @app_commands.describe(
        ephemeral="Whether the response should be ephemeral (default: false)",
    )
    async def affirmation(
        self, interaction: discord.Interaction, ephemeral: bool = False
    ):
        await interaction.response.defer(ephemeral=ephemeral)
        async with aiohttp.ClientSession() as session:
            async with session.get("https://affirmations.dev/") as r:
                data = await r.json()
                await interaction.followup.send(data["affirmation"])
