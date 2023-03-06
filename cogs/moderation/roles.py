import i18n
import discord
from utils import get_language
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import time

error_color = discord.Color(0xD0021B)
success_color = discord.Color.green()
loading_color = discord.Color(0xF5A623)
checkmark = "<:checkmark:1080545976839848048>"
cross = "<:cross:1080545978949566484>"

class Roles(commands.GroupCog, name="role"):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    @app_commands.command(description="Adds a role to the provided member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(member="The member to add the role to.")
    @app_commands.describe(role="The role to add to the member.")
    @app_commands.describe(reason="Why are you adding the role?")
    @app_commands.guild_only()
    async def add(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member = None, reason: str = None):
        if not member: member = interaction.user       
        if role.position >= interaction.user.top_role.position:
            embed = discord.Embed(colour=error_color, description=f"{cross} {role.mention} is either above you or me in the Role list.") # roles_above
            return await interaction.response.send_message(embed=embed)
        if role in member.roles:
            embed = discord.Embed(colour=error_color, description=f"{cross} The user already has the role {role.mention}!") # roles_user_has_role
            return await interaction.response.send_message(embed=embed)
        
        await member.add_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
        
        embed = discord.Embed(colour=success_color, description=f"{checkmark} The role {role.mention} was successfully given to {member.mention}!") # roles_single_add_success
        await interaction.response.send_message(embed=embed)


    @app_commands.command(description="Removes a role from the provided member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(member="The member to remove the role from.")
    @app_commands.describe(role="The role to remove from the member.")
    @app_commands.describe(reason="Why are you removing the role?")
    @app_commands.guild_only()
    async def remove(self, interaction: discord.Interaction, role: discord.Role, member: discord.Member = None, reason: str = None):
        if not member: member = interaction.user
        if role.position >= interaction.user.top_role.position:
            embed = discord.Embed(colour=error_color, description=f"{cross} {role.mention} is either above you or me in the Role list.") # roles_above
            return await interaction.response.send_message(embed=embed)
        if not role in member.roles:
            embed = discord.Embed(colour=error_color, description=f"{cross} The user does not have the role {role.mention}!") # roles_user_has_not_role
            return await interaction.response.send_message(embed=embed)
        
        await member.remove_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
        
        embed = discord.Embed(colour=success_color, description=f"{checkmark} The role {role.mention} was successfully removed from {member.mention}!") # roles_single_remove_success
        await interaction.response.send_message(embed=embed)


    @app_commands.command(description="Adds a role to every member")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(role="The role to add to everyone selected")
    @app_commands.describe(reason="Why are you adding the role")
    @app_commands.describe(option="Select to who the role should be added")
    @app_commands.choices(option=[app_commands.Choice(name="Everyone", value=1), app_commands.Choice(name="Only Humans", value=2), app_commands.Choice(name="Only Bots", value=3),])
    @app_commands.guild_only()
    async def add_all(self, interaction: discord.Interaction, role: discord.Role, option: int = 1, reason: str = None):
        if role.position > interaction.user.top_role.position: return await interaction.response.send_message(f"You can't add this role to the members!")   

        member_list = interaction.guild.members
        counter = 0
        
        bot_top = interaction.guild.get_member(self.bot.user.id).top_role.position
        interaction_top = interaction.user.top_role.position
        if option == 1: #everyone
            embed = discord.Embed(colour=loading_color, description=f"<a:loading:1071777312128905267> Adding the role {role.mention} to {len(member_list)} members...\nTime left: {'<t:'+str(int(time.mktime((datetime.now() + timedelta(seconds=0.96*len(member_list))).timetuple())))+':R>'}") # roles_loading_add_members ## TODO: hier weitermachen
            await interaction.response.send_message(embed=embed)
            for user in member_list:
                user_top = user.top_role.position
                if not role in user.roles:                   
                    if user_top > bot_top:
                        continue
                    if user_top > interaction_top:
                        continue
                    counter += 1
                    await user.add_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
            
            if counter == 0: embed = discord.Embed(colour=error_color, description=f"{cross} All members are already having the role {role.mention}.")
            else: embed = discord.Embed(colour=success_color, description=f"{checkmark} The role {role.mention} was successfully given to {counter} members!")
            return await interaction.edit_original_response(embed=embed)

        if option == 2: # humans
            embed = discord.Embed(colour=loading_color, description=f"<a:loading:1071777312128905267> Adding the role {role.mention} to {len([m for m in member_list if not m.bot])} humans...\nTime left: {'<t:'+str(int(time.mktime((datetime.now() + timedelta(seconds=0.96*len([m for m in member_list if not m.bot]))).timetuple())))+':R>'}") # roles_loading_add_members ## TODO: hier weitermachen
            await interaction.response.send_message(embed=embed)
            for user in member_list:
                if not user.bot:
                    user_top = user.top_role.position
                    if not role in user.roles:
                        if user_top > bot_top: continue
                        if user_top > interaction_top: continue
                        counter += 1
                        await user.add_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
            if counter == 0: embed = discord.Embed(colour=error_color, description=f"{cross} All humans are already having the role {role.mention}.")
            else: embed = discord.Embed(colour=success_color, description=f"{checkmark} The role {role.mention} was successfully given to {counter} humans!")
            return await interaction.edit_original_response(embed=embed)

        if option == 3: # bots
            embed = discord.Embed(colour=loading_color, description=f"<a:loading:1071777312128905267> Adding the role {role.mention} to {len([m for m in member_list if m.bot])} bots...\nTime left: {'<t:'+str(int(time.mktime((datetime.now() + timedelta(seconds=0.96*len([m for m in member_list if m.bot]))).timetuple())))+':R>'}") # roles_loading_add_members ## TODO: hier weitermachen
            await interaction.response.send_message(embed=embed)
            for user in member_list:      
                if user.bot:
                    user_top = user.top_role.position
                    if not role in user.roles: 
                        if user_top > bot_top: continue
                        if user_top > interaction_top: continue   
                        counter += 1
                        await user.add_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
            if counter == 0: 
                embed = discord.Embed(colour=error_color, description=f"{cross} All bots are already having the role {role.mention}.")
            else: embed = discord.Embed(colour=success_color, description=f"{checkmark} The role {role.mention} was successfully given to {counter} bots!")
            return await interaction.edit_original_response(embed=embed)


    @app_commands.command(description="Removes a role from every member")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(role="The role to remove from everyone.")
    @app_commands.describe(reason="Why are you removing the role?")
    @app_commands.describe(option="[1] Everyone  [2] Only Humans  [3] Only Bots")
    @app_commands.choices(option=[app_commands.Choice(name="Everyone", value=1), app_commands.Choice(name="Only Humans", value=2), app_commands.Choice(name="Only Bots", value=3),])
    @app_commands.guild_only()
    async def remove_all(self, interaction: discord.Interaction, role: discord.Role, reason: str = None, option: int = 1):
        member_list = interaction.guild.members
        counter = 0
        
        if option == 1: # everyone
            if len(role.members) == 0: 
                return await interaction.response.send_message(embed=discord.Embed(colour=error_color, description=f"{cross} No one has the role {role.mention}."))
            embed = discord.Embed(colour=loading_color, description=f"<a:loading:1071777312128905267> Removing the role {role.mention} from {len(role.members)} members...\nTime left: {'<t:'+str(int(time.mktime((datetime.now() + timedelta(seconds=0.96*len(role.members))).timetuple())))+':R>'}") 
            await interaction.response.send_message(embed=embed)
            for user in member_list:
                if role in user.roles:
                    counter += 1
                    await user.remove_roles(role, reason=f"Role removed by {interaction.user}, reason: {reason}")
            
            else: embed = discord.Embed(colour=success_color, description=f"{checkmark} The role {role.mention} was successfully removed from {counter} members!")
            return await interaction.edit_original_response(embed=embed)
        
        elif option == 2: # humans
            if len(role.members) == 0: 
                return await interaction.response.send_message(discord.Embed(colour=error_color, description=f"{cross} No one has the role {role.mention}."))
            embed = discord.Embed(colour=loading_color, description=f"<a:loading:1071777312128905267> Removing the role {role.mention} from {len([m for m in role.members if not m.bot])} humans...\nTime left: {'<t:'+str(int(time.mktime((datetime.now() + timedelta(seconds=0.96*len([m for m in role.members if not m.bot]))).timetuple())))+':R>'}") 
            await interaction.response.send_message(embed=embed)
            for user in member_list:
                if not user.bot:
                    counter += 1
                    await user.remove_roles(role, reason=f"Role removed by {interaction.user}, reason: {reason}")
                   
            else: embed = discord.Embed(colour=success_color, description=f"{checkmark} The role {role.mention} was successfully removed from {counter} humans!")
            return await interaction.edit_original_response(embed=embed)   
             
        elif option == 3: #bots
            if len(role.members) == 0:
                return await interaction.response.send_message(discord.Embed(colour=error_color, description=f"{cross} No one has the role {role.mention}."))
            embed = discord.Embed(colour=loading_color, description=f"<a:loading:1071777312128905267> Removing the role {role.mention} from {len([m for m in role.members if m.bot])} humans...\nTime left: {'<t:'+str(int(time.mktime((datetime.now() + timedelta(seconds=0.96*len([m for m in role.members if m.bot]))).timetuple())))+':R>'}") 
            await interaction.response.send_message(embed=embed)
            for user in member_list:
                if user.bot:
                    counter += 1
                    await user.remove_roles(role, reason=f"Role removed by {interaction.user}, reason: {reason}")
            
               
            else: embed = discord.Embed(colour=success_color, description=f"{checkmark} The role {role.mention} was successfully removed from {counter} bots!")
            return await interaction.edit_original_response(embed=embed)
        
        
        
    
