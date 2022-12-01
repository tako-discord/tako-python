import i18n
import uuid
import discord
from TakoBot import TakoBot, SelfMenu
from discord import app_commands
from discord.ext import commands
from utils import get_language, thumbnail, get_color


class Selfroles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Create a role selection menu")
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.checks.bot_has_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def selfroles(
        self,
        interaction: discord.Interaction,
        title: str,
        description: str,
        role_1: discord.Role,
        embed_state: bool = True,
        min_values: int = None,
        max_values: int = None,
        role_2: discord.Role = None,
        role_3: discord.Role = None,
        role_4: discord.Role = None,
        role_5: discord.Role = None,
        role_6: discord.Role = None,
        role_7: discord.Role = None,
        role_8: discord.Role = None,
        role_9: discord.Role = None,
        role_10: discord.Role = None,
        role_11: discord.Role = None,
        role_12: discord.Role = None,
        role_13: discord.Role = None,
        role_14: discord.Role = None,
        role_15: discord.Role = None,
        role_16: discord.Role = None,
        role_17: discord.Role = None,
        role_18: discord.Role = None,
        role_19: discord.Role = None,
        role_20: discord.Role = None,
    ):
        role_array = [role_1]

        if role_2:
            role_array.append(role_2)
        if role_3:
            role_array.append(role_3)
        if role_4:
            role_array.append(role_4)
        if role_5:
            role_array.append(role_5)
        if role_6:
            role_array.append(role_6)
        if role_7:
            role_array.append(role_7)
        if role_8:
            role_array.append(role_8)
        if role_9:
            role_array.append(role_9)
        if role_10:
            role_array.append(role_10)
        if role_11:
            role_array.append(role_11)
        if role_12:
            role_array.append(role_12)
        if role_13:
            role_array.append(role_13)
        if role_14:
            role_array.append(role_14)
        if role_15:
            role_array.append(role_15)
        if role_16:
            role_array.append(role_16)
        if role_17:
            role_array.append(role_17)
        if role_18:
            role_array.append(role_18)
        if role_19:
            role_array.append(role_19)
        if role_20:
            role_array.append(role_20)

        select_array = []
        language = get_language(self.bot, interaction.guild.id)

        for role in role_array:
            if (
                role.is_default()
                or role.is_bot_managed()
                or role.managed
                or not role.is_assignable()
                or role >= interaction.user.top_role
            ):
                continue
            select_array.append(role.id)
        if not select_array:
            return await interaction.response.send_message(
                i18n.t("config.invalid_role", locale=language), ephemeral=True
            )

        if max_values is None:
            max_values = len(select_array)
        if max_values > len(select_array):
            max_values = len(select_array)

        id = uuid.uuid4()
        await self.bot.db_pool.execute(
            "INSERT INTO selfroles (id, guild_id, select_array, min_values, max_values) VALUES ($1, $2, $3, $4, $5);",
            id,
            interaction.guild.id,
            select_array,
            min_values,
            max_values,
        )
        view = discord.ui.View(timeout=None)
        menu = SelfMenu(self.bot, select_array, min_values, max_values, str(id))
        view.add_item(menu)

        file = discord.File(
            await thumbnail(interaction.guild.id, "role", self.bot),
            filename="thumbnail.png",
        )

        if embed_state:
            embed = discord.Embed(
                title=title,
                description=description,
                color=await get_color(self.bot, interaction.guild.id),
            )
            embed.set_thumbnail(url="attachment://thumbnail.png")
            await interaction.channel.send(embed=embed, view=view, file=file)
        else:
            await interaction.channel.send(
                content=f"**{title}**\n{description}", view=view
            )
        await interaction.response.send_message(
            content=i18n.t(
                "config.selfrole_created",
                locale=language,
            ),
            ephemeral=True,
        )
