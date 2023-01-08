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
    async def addrole(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
        role: discord.Role = None,
        reason=None,
    ):
        language = get_language(self.bot, interaction.guild.id)

        if member is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_member", locale=language)
            )
        if role is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_role", locale=language)
            )
        if reason is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_reason", locale=language)
            )

        member_top = member.top_role
        interaction_top = interaction.user.top_role
        role_list = interaction.guild.roles
        bot_top = interaction.bot.top_role  # not correct, change it!
        """
        new
        """
        if roleList[member_top] > roleList[bot_top]:
            await interaction.reply(
                f"I have no perms to manage the roles of that user."
            )
        if roleList[role] > roleList[bot_top]:
            await interaction.reply(f"I have no perms to manage the role {role.name}.")
        if roleList[member_top] > roleList[interaction_top]:
            await member.add_roles(
                role, reason=f"Role added by {interaction.user}, reason: {reason}"
            )
            await interaction.reply(
                f"{member.name} has been given the role {role.name}."
            )
        else:
            await interaction.reply(f"You cant add a role to that user!")

    @app_commands.command(description="Removes a role from the provided member.")
    @app_commands.checks.has_permissions(manage_members=True)
    @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(member="The member to remove the role from.")
    @app_commands.describe(role="The role to remove from the member.")
    @app_commands.describe(reason="Why are you removing the role?")
    async def removerole(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None,
        role: discord.Role = None,
        reason=None,
        aliases=["remrole"],
    ):
        language = get_language(self.bot, interaction.guild.id)

        if member is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_member", locale=language)
            )
        if role is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_role", locale=language)
            )
        if reason is None:

            return interaction.reply(
                i18n.t("moderation.roles_provide_reason", locale=language)
            )

        member_top = member.top_role
        interaction_top = interaction.user.top_role
        role_list = interaction.guild.roles
        if roleList[member_top] > roleList[interaction_top]:
            await member.remove_roles(
                role, reason=f"Role removed by {interaction.user}, reason: {reason}"
            )
            await interaction.reply(f"{role.name} has been removed from {member.name}.")
        else:
            await interaction.reply(f"You can't remove a role from that user!")

    @app_commands.command(description="Adds a role to every member")
    @app_commands.checks.has_permissions(manage_members=True)
    @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(role="The role to add to everyone.")
    @app_commands.describe(reason="Why are you adding the role?")
    @app_commands.describe(option="[1] Everyone  [2] Only Humans  [3] Only Bots")
    async def addroletoeveryone(
        self,
        interaction: discord.Interaction,
        role: discord.Role = None,
        reason=None,
        option=1,
    ):
        language = get_language(self.bot, interaction.guild.id)
        if role is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_role", locale=language)
            )
        if reason is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_reason", locale=language)
            )

        interaction_top = interaction.user.top_role
        role_list = interaction.guild.roles
        if roleList[role] > roleList[interaction_top]:
            pass
        else:
            return await interaction.reply(f"You can't add this role to the members!")

        all_members = interaction.guild.members(limit=None)
        counter = 0
        blocked = []  # above the user
        failed = []  # above the bot
        """
        NEUES VON OPTION 1 AUF ALLES ÜBERTRAGEN!!!
        """
        if option == 1:
            # @everyone
            for user in all_members:
                user_top = user.top_role
                bot_top = interaction.bot.top_role  # not correct, change it!
                interaction_top = interaction.user.top_role
                role_list = interaction.guild.roles
                if roleList[user_top] > roleList[bot_top]:
                    failed.append(str(user.name))
                elif roleList[user_top] > roleList[interaction_top]:
                    blocked.append(str(user.name))
                else:
                    counter = +1
                    await user.add_roles(
                        role,
                        reason=f"Role added by {interaction.user}, reason: {reason}",
                    )
            if len(blocked) > 5:
                lblocked = len(blocked)
                del blocked[10 : len(blocked)]
            if len(failed) > 5:
                lfailed = len(failed)
                del failed[10 : len(failed)]
            await interaction.reply(
                f"__You tried to add the role {role.name} to {len(all_members)} Members.__\n {counter} Succesful\n {lblocked} Blocked (above you): {', '.join(blocked),', ...'}\n {lfailed} Failed (above the bot): {', '.join(failed),', ...'}"
            )

        elif option == 2:
            # @humans
            for user in all_members:
                if not user.bot:
                    counter = +1
                    await user.add_roles(
                        role,
                        reason=f"Role added by {interaction.user}, reason: {reason}",
                    )
            await interaction.reply(f"{role.name} has been given to {counter} Humans.")

        elif option == 3:
            # @bots
            for user in all_members:
                if user.bot:
                    counter = +1
                    await user.add_roles(
                        role,
                        reason=f"Role added by {interaction.user}, reason: {reason}",
                    )
            await interaction.reply(f"{role.name} has been given to {counter} Bots.")

    @app_commands.command(description="Removes a role from every member")
    @app_commands.checks.has_permissions(manage_members=True)
    @app_commands.checks.bot_has_permissions(manage_members=True)
    @app_commands.describe(role="The role to remove from everyone.")
    @app_commands.describe(reason="Why are you removing the role?")
    @app_commands.describe(option="[1] Everyone  [2] Only Humans  [3] Only Bots")
    async def removerolefromeveryone(
        self,
        interaction: discord.Interaction,
        role: discord.Role = None,
        reason=None,
        option=1,
    ):
        language = get_language(self.bot, interaction.guild.id)
        if role is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_role", locale=language)
            )
        if reason is None:
            return interaction.reply(
                i18n.t("moderation.roles_provide_reason", locale=language)
            )

        all_members = interaction.guild.members(limit=None)
        counter = 0
        if option == 1:
            # @everyone
            for user in all_members:
                counter = +1
                await user.remove_roles(
                    role, reason=f"Role removed by {interaction.user}, reason: {reason}"
                )
            await interaction.reply(
                f"{role.name} has been removed from {counter} Members."
            )
        elif option == 2:
            # @humans
            for user in all_members:
                if not user.bot:
                    counter = +1
                    await user.remove_roles(
                        role,
                        reason=f"Role removed by {interaction.user}, reason: {reason}",
                    )
            await interaction.reply(
                f"{role.name} has been removed from {counter} Humans."
            )
        elif option == 3:
            # @bots
            for user in all_members:
                if user.bot:
                    counter = +1
                    await user.remove_roles(
                        role,
                        reason=f"Role removed by {interaction.user}, reason: {reason}",
                    )
            await interaction.reply(
                f"{role.name} has been removed from {counter} Bots."
            )
