import i18n
import discord
from utils import get_language
from discord.ext import commands
from discord import app_commands

error_color = discord.Color(0xD0021B)
success_color = discord.Color.green()
loading_color = discord.Color(0xF5A623)
# ONLY A TEST
stickyroles = {
    1071473795740737536: [1071782017273954424, 1071477419510333470]
}

class Stickyroles(commands.GroupCog, name="stickyroles"):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @app_commands.command(description="Adds a role to the stickyroles.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(role="The role")
    @app_commands.guild_only()
    async def add(self, interaction: discord.Interaction, role: discord.Role):
        
        if role.id not in stickyroles[interaction.guild.id]:          
            stickyroles[interaction.guild.id].append(role.id)
            
            embed = discord.Embed(colour=success_color, description=f"✅ The role {role.mention} is now a sticky role.\n"+str(stickyroles))
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(colour=error_color, description=f"❌ The role {role.mention} is already a sticky role.")
            await interaction.response.send_message(embed=embed)
            
            
    @app_commands.command(description="Removes a role from the stickyroles.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(role="The role")
    @app_commands.guild_only()
    async def remove(self, interaction: discord.Interaction, role: discord.Role):
        
        if role.id not in stickyroles[interaction.guild.id]:                      
            embed = discord.Embed(colour=error_color, description=f"❌ The role {role.mention} is not a sticky role.\n")
            await interaction.response.send_message(embed=embed)
        else:
            stickyroles[interaction.guild.id].remove(role.id)
            embed = discord.Embed(colour=success_color, description=f"✅ The role {role.mention} is now no longer a sticky role.\n"+str(stickyroles))
            await interaction.response.send_message(embed=embed)
