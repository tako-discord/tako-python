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
        # language = get_language(self.bot, interaction.guild.id)

        if not member:
            member = interaction.user

        if role.position >= interaction.user.top_role.position:
            embed = discord.Embed(
                colour=discord.Colour(error_color),
                description=f"{role.mention} is either above you or me in the Role list.",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await member.add_roles(
            role, reason=f"Role added by {interaction.user}, reason: {reason}"
        )

        embed = discord.Embed(
            colour=discord.Colour(success_color),
            description=f"The role {role.mention} was successfully **given** to {member.mention}!",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
        # language = get_language(self.bot, interaction.guild.id)

        if not member:
            member = interaction.user

        if role.position >= interaction.user.top_role.position:
            embed = discord.Embed(
                colour=discord.Colour(error_color),
                description=f"{role.mention} is either above you or me in the Role list.",
            )
            return await interaction.response.send_message(embed=embed, ephemeral=True)

        await member.remove_roles(
            role, reason=f"Role added by {interaction.user}, reason: {reason}"
        )

        embed = discord.Embed(
            colour=discord.Colour(success_color),
            description=f"The role {role.mention} was successfully **removed** from {member.mention}!",
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

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
            app_commands.Choice(name="Only self.bots", value=3),
        ]
    )
    async def add_all(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        option: int = 1,
        reason: str = None,
    ):
        # language = get_language(self.bot, interaction.guild.id)
        if role is None:
            return await interaction.response.send_message(
                "Provide the role"
                # i18n.t("moderation.roles_provide_role", locale=language)
            )

        interaction_top = interaction.user.top_role
        role_list = interaction.guild.roles
        # if not role.position > interaction_top.position:
        # return await interaction.response.send_message(f"You can't add this role to the members!")

        all_members = interaction.guild.members
        counter = 0
        have = 0  # ppl that arl have the role assigned
        blocked = []  # above the user
        failed = []  # above the bot

        # TODO: Add failed and blocked to 2nd and 3rd option
        if option == 1:
            # @everyone
            for user in all_members:
                if not role in user.roles:
                    user_top = user.top_role

                    member = interaction.guild.get_member(1061216305040064532)
                    self.bot_top = member.top_role

                    interaction_top = interaction.user.top_role
                    role_list = interaction.guild.roles
                    if user.top_role >= self.bot_top:
                        failed.append(user.name)
                        continue
                    if user.top_role >= interaction.user.top_role:
                        blocked.append(user.name)
                        continue

                    await user.add_roles(
                        role,
                        reason=f"Role added by {interaction.user}, reason: {reason}",
                    )
                    counter += 1
                else:
                    have += 1
            lblocked = len(blocked)
            if len(blocked) > 5:
                del blocked[10 : len(blocked)]
            lfailed = len(failed)
            if len(failed) > 5:
                del failed[10 : len(failed)]
            return await interaction.response.send_message(
                f"__You tried to add the role `{role.name}` to {len(all_members)} Members.__\n {counter} Succesful\n {lblocked} Blocked (above you)\n {lfailed} Failed (above me)\n {have} are already having the role"
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
            return await interaction.response.send_message(
                f"{role.name} has been given to {counter} Humans."
            )

        if option == 3:
            # @self.bots
            for user in all_members:
                if user.self.bot:
                    counter = +1
                    await user.add_roles(
                        role,
                        reason=f"Role added by {interaction.user}, reason: {reason}",
                    )
            return await interaction.response.send_message(
                f"{role.name} has been given to {counter} Bots."
            )

    @app_commands.command(description="Removes a role from every member")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.describe(role="The role to remove from everyone.")
    @app_commands.describe(reason="Why are you removing the role?")
    @app_commands.describe(option="[1] Everyone  [2] Only Humans  [3] Only Bots")
    async def remove_all(
        self,
        interaction: discord.Interaction,
        role: discord.Role,
        reason: str = None,
        option: int = 1,
    ):
        # language = get_language(self.bot, interaction.guild.id)
        if role is None:
            return interaction.response.send_message(
                "Provide the role"
                # i18n.t("moderation.roles_provide_role", locale=language)
            )

        all_members = interaction.guild.members
        counter = 0
        if option == 1:
            # @everyone
            for user in all_members:
                if role in user.roles:
                    counter += 1
                    await user.remove_roles(
                        role,
                        reason=f"Role removed by {interaction.user}, reason: {reason}",
                    )
            await interaction.response.send_message(
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
            await interaction.response.send_message(
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
            await interaction.response.send_message(
                f"{role.name} has been removed from {counter} self.bots."
            )
