import i18n
import discord
from utils import get_language
from discord.ext import commands


class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Adds a role to the provided member.")
    @app_commands.checks.has_permissions(manage_members=True)
    @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(member="The member to add the role to.")
    @app_commands.describe(role="The role to add to the member.")
    @app_commands.describe(reason="Why are you adding the role?")
    async def addrole(self, interaction: discord.Interaction, member: discord.Member = None, role: discord.Role = None, reason = None):
        language = get_language(self.bot, interaction.guild.id)

        if member is None:
            interaction.reply(i18n.t("moderation.roles_provide_member", locale=language))
            return
        if role is None:
            interaction.reply(i18n.t("moderation.roles_provide_role", locale=language))
            return
        if reason is None:
            interaction.reply(i18n.t("moderation.roles_provide_reason", locale=language))
            return
        
        member_top = member.top_role
        interaction_top = interaction.user.top_role
        role_list = interaction.guild.roles
        if roleList[member_top] > roleList[interaction_top]:
            await member.add_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
            await interaction.reply(f"{member.name} has been given the role {role.name}.")
        else:
            await interaction.reply(f"You cant add a role to that user!")


    @app_commands.command(description="Removes a role from the provided member.")
    @app_commands.checks.has_permissions(manage_members=True)
    @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(member="The member to remove the role from.")
    @app_commands.describe(role="The role to remove from the member.")
    @app_commands.describe(reason="Why are you removing the role?")
    async def removerole(self, interaction: discord.Interaction, member: discord.Member = None, role: discord.Role = None, reason = None, aliases=["remrole"]):
        language = get_language(self.bot, interaction.guild.id)

        if member is None:
            interaction.reply(i18n.t("moderation.roles_provide_member", locale=language))
            return
        if role is None:
            interaction.reply(i18n.t("moderation.roles_provide_role", locale=language))
            return
        if reason is None:
            interaction.reply(i18n.t("moderation.roles_provide_reason", locale=language))
            return
        
        member_top = member.top_role
        interaction_top = interaction.user.top_role
        role_list = interaction.guild.roles
        if roleList[member_top] > roleList[interaction_top]:
            await member.remove_roles(role, reason=f"Role removed by {interaction.user}, reason: {reason}")
            await interaction.reply(f"{role.name} has been removed from {member.name}.")
        else:
            await interaction.reply(f"You can't remove a role from that user!")

    @app_commands.command(description="Adds a role to every member")
    @app_commands.checks.has_permissions(manage_members=True)
    @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(role="The role to add to everyone.")
    @app_commands.describe(reason="Why are you adding the role?")
    @app_commands.describe(option="[1] Everyone  [2] Only Humans  [3] Only Bots")
    async def addroletoeveryone(self, interaction: discord.Interaction, role: discord.Role = None, reason = None, option = 1):
        language = get_language(self.bot, interaction.guild.id)
        if role is None:
            interaction.reply(i18n.t("moderation.roles_provide_role", locale=language))
            return
        if reason is None:
            interaction.reply(i18n.t("moderation.roles_provide_reason", locale=language))
            return
        
        all_members = interaction.guild.members(limit=None)
        counter = 0
        if option == 1:
            # @everyone
            for user in all_members:
                counter =+ 1
                await user.add_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
            await interaction.reply(f"{role.name} has been given to {counter} Members.")
        elif option == 2:
            # @humans
            for user in all_members:
                if not user.bot:
                    counter =+ 1
                    await user.add_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
            await interaction.reply(f"{role.name} has been given to {counter} Humans.")      
        elif option == 3:
            # @bots
            for user in all_members:
                if user.bot:
                    counter =+ 1
                    await user.add_roles(role, reason=f"Role added by {interaction.user}, reason: {reason}")
            await interaction.reply(f"{role.name} has been given to {counter} Bots.")
        
    

    @app_commands.command(description="Removes a role from every member")
    @app_commands.checks.has_permissions(manage_members=True)
    @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(role="The role to remove from everyone.")
    @app_commands.describe(reason="Why are you removing the role?")
    @app_commands.describe(option="[1] Everyone  [2] Only Humans  [3] Only Bots")
    async def removerolefromeveryone(self, interaction: discord.Interaction, role: discord.Role = None, reason = None, option = 1):
        language = get_language(self.bot, interaction.guild.id)
        if role is None:
            interaction.reply(i18n.t("moderation.roles_provide_role", locale=language))
            return
        if reason is None:
            interaction.reply(i18n.t("moderation.roles_provide_reason", locale=language))
            return
        
        all_members = interaction.guild.members(limit=None)
        counter = 0
        if option == 1:
            # @everyone
            for user in all_members:
                counter =+ 1
                await user.remove_roles(role, reason=f"Role removed by {interaction.user}, reason: {reason}")
            await interaction.reply(f"{role.name} has been removed from {counter} Members.")
        elif option == 2:
            # @humans
            for user in all_members:
                if not user.bot:
                    counter =+ 1
                    await user.remove_roles(role, reason=f"Role removed by {interaction.user}, reason: {reason}")
            await interaction.reply(f"{role.name} has been removed from {counter} Humans.")      
        elif option == 3:
            # @bots
            for user in all_members:
                if user.bot:
                    counter =+ 1
                    await user.remove_roles(role, reason=f"Role removed by {interaction.user}, reason: {reason}")
            await interaction.reply(f"{role.name} has been removed from {counter} Bots.")