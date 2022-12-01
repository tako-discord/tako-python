import discord
from discord import app_commands
from discord.ext import commands


class Cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def example(self, interaction: discord.Interaction):
        return
