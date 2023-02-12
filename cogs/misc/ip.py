from random import randint
from socket import inet_ntoa
from struct import pack

import discord
from discord import app_commands
from discord.ext import commands
from utils import get_color

class IP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Get the IP of an user")
    @app_commands.describe(user="The user to get the IP from")
    async def ip(self, interaction: discord.Interaction, user: discord.User | discord.Member | None = None):
        if not user:
            user = interaction.user
        ip = inet_ntoa(pack(">I", randint(1, 0xFFFFFFFF)))
        embed = discord.Embed(title=f"{user.display_name}'s IP", description=f"`{ip}`", color=await get_color(self.bot, interaction.guild_id)) # type: ignore
        embed.set_footer(text="For legal reasons, this is a joke.")
        await interaction.response.send_message(embed=embed)
