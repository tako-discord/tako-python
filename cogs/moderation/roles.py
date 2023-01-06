import i18n
import discord
from utils import get_language
from discord.ext import commands


class Roles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(description="Adds a role to the provided member.")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
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
        
        memberTop = member.top_role
        interactionTop = interaction.user.top_role
        roleList = interaction.guild.roles
        if roleList[memberTop] > roleList[interactionTop]:
            await member.add_roles(role, reason=f"Role added by {interaction.user}, reson: {reason}")
            await interaction.reply(f"{member.name} has been given the role {role.name}.")
        else:
            await interaction.reply(f"You cant add a role to that user!")

    @app_commands.command(description="Adds a role to every member")
    @app_commands.checks.has_permissions(manage_channels=True)
    @app_commands.checks.bot_has_permissions(manage_channels=True)
    @app_commands.describe(role="The role to add to everyone.")
    @app_commands.describe(reason="Why are you adding the role?")
    @app_commands.describe(option="[1] Everyone  [2] Only Human  [3] Only Bots")
    async def addroletoeveryone(self, interaction: discord.Interaction, role: discord.Role = None, reason = None):
        pass
