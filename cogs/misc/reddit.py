import discord
import aiohttp
from discord import app_commands
from discord.ext import commands
from TakoBot import TakoBot, MemeButtons
from utils import delete_thumbnail, new_meme


class Reddit(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(
        description="Get a random meme from the subreddits: memes, me_irl or dankmemes"
    )
    async def meme(self, interaction: discord.Interaction):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://meme-api.herokuapp.com/gimme/") as r:
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
