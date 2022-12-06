import discord
import aiohttp
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from persistent_views.affirmation_buttons import AffirmationButtons


class Affirmations(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Feel bad? Get some affirmations!")
    async def affirmation(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://affirmations.dev/") as r:
                data = await r.json()
                await interaction.response.send_message(
                    data["affirmation"], view=AffirmationButtons(), ephemeral=True
                )
