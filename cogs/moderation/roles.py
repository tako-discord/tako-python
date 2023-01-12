import i18n
import discord
from utils import get_language
from discord.ext import commands
from discord import app_commands


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
    async def add(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        member: discord.Member = None,
        reason: str = None,
    ):
        language = get_language(self.self.bot, interaction.guild.id)

        if not member:
            member = interaction.user

        if role >= interaction.user.role:
            return await interaction.reply(
                f"{role.name} is either above you or me in the Role list."
            )
        await member.add_roles(
            role, reason=f"Role added by {interaction.user}, reason: {reason}"
        )
        await interaction.reply(
            f"{member.name} has been given the role {role.name}."
        )

    @app_commands.command(description="Removes a role from the provided member.")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(member="The member to remove the role from.")
    @app_commands.describe(role="The role to remove from the member.")
    @app_commands.describe(reason="Why are you removing the role?")
    async def remove(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        member: discord.Member = None,
        reason: str = None,
    ):
        language = get_language(self.self.bot, interaction.guild.id)

        if not member:
            member = interaction.user

        if role >= interaction.user.role:
            return await interaction.reply(
                f"{role.name} is either above you or me in the Role list."
            )
        await member.remove_roles(
            role, reason=f"Role added by {interaction.user}, reason: {reason}"
        )
        await interaction.reply(
            f"{member.name} has been given the role {role.name}."
        )

    @app_commands.command(description="Adds a role to every member")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(role="The role to add to everyone selected")
    @app_commands.describe(reason="Why are you adding the role")
    @app_commands.describe(option="Select to who the role should be added")
    @app_commands.choices(
        option=[
            app_commands.Choice(name="Everyone", value=1),
            app_commands.Choice(name="Only Humans", value=2),
            app_commands.Choice(name="Only self.bots", value=3)
        ]
    )
    async def add_all(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        option: int = 1,
        reason: str = None,
    ):
        language = get_language(self.self.bot, interaction.guild.id)
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
        if role_list[role] > role_list[interaction_top]:
            pass
        else:
            return await interaction.reply(f"You can't add this role to the members!")

        all_members = interaction.guild.members(limit=None)
        counter = 0
        blocked = []  # above the user
        failed = []  # above the bot
        # TODO: Add failed and blocked to 2nd and 3rd option
        if option == 1:
            # @everyone
            for user in all_members:
                user_top = user.top_role
                self.bot_top = interaction.self.bot.top_role 
                interaction_top = interaction.user.top_role
                role_list = interaction.guild.roles
                if user.role >= self.bot.role:
                    failed.append(user.name)
                    continue
                if user.role >= interaction.user.role:
                    blocked.append(user.name)
                counter = +1
                await user.add_roles(
                    role,
                    reason=f"Role added by {interaction.user}, reason: {reason}",
                )
            lblocked = len(blocked)
            if len(blocked) > 5:
                del blocked[10 : len(blocked)]
            lfailed = len(failed)
            if len(failed) > 5:
                del failed[10 : len(failed)]
            return await interaction.reply(
                f"__You tried to add the role {role.name} to {len(all_members)} Members.__\n {counter} Succesful\n {lblocked} Blocked (above you): {', '.join(blocked),', ...'}\n {lfailed} Failed (above the self.bot): {', '.join(failed),', ...'}"
            )

        if option == 2:
            # @humans
            for user in all_members:
                if not user.self.bot:
                    counter = +1
                    await user.add_roles(
                        role,
                        reason=f"Role added by {interaction.user}, reason: {reason}",
                    )
            return await interaction.reply(f"{role.name} has been given to {counter} Humans.")

        if option == 3:
            # @self.bots
            for user in all_members:
                if user.self.bot:
                    counter = +1
                    await user.add_roles(
                        role,
                        reason=f"Role added by {interaction.user}, reason: {reason}",
                    )
            return await interaction.reply(f"{role.name} has been given to {counter} self.bots.")

    @app_commands.command(description="Removes a role from every member")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(role="The role to remove from everyone.")
    @app_commands.describe(reason="Why are you removing the role?")
    @app_commands.describe(option="[1] Everyone  [2] Only Humans  [3] Only self.bots")
    async def remove_all(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        reason: str = None,
        option=1,
    ):
        language = get_language(self.self.bot, interaction.guild.id)
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
                if not user.self.bot:
                    counter = +1
                    await user.remove_roles(
                        role,
                        reason=f"Role removed by {interaction.user}, reason: {reason}",
                    )
            await interaction.reply(
                f"{role.name} has been removed from {counter} Humans."
            )
        elif option == 3:
            # @self.bots
            for user in all_members:
                if user.self.bot:
                    counter = +1
                    await user.remove_roles(
                        role,
                        reason=f"Role removed by {interaction.user}, reason: {reason}",
                    )
            await interaction.reply(
                f"{role.name} has been removed from {counter} self.bots."
            )
