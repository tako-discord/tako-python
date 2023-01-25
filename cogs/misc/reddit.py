import discord
import aiohttp
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import delete_thumbnail, new_meme
from persistent_views.meme_buttons import MemeButtons


class Reddit(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(
        description="Get a random meme from the subreddits: memes, me_irl or dankmemes"
    )
    async def meme(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.herokuapp.com/gimme/"):
                embed, file = await new_meme(
                    interaction.guild.id,
                    interaction.user.id,
                    self.bot,
                    self.bot.db_pool,
                )

                await interaction.response.send_message(
                    embed=embed, file=file, view=MemeButtons(self.bot), ephemeral=True
                )
                delete_thumbnail(interaction.guild.id, "reddit")
