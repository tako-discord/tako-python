import i18n
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice


class Language(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        description="Set the language of the bot (in the current server)"
    )
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.describe(language="The language to set the bot to")
    @app_commands.choices(
        language=[
            Choice(name="English", value="en"),
            Choice(name="Deutsch", value="de"),
            Choice(name="Español", value="es"),
            Choice(name="Français", value="fr"),
            Choice(name="עִברִית", value="he"),
            Choice(name="Hrvatski", value="hr"),
            Choice(name="Indonesia", value="id"),
            Choice(name="Nederlands", value="nl"),
            Choice(name="Polski", value="pl"),
            Choice(name="Português (brasileiro)", value="pt"),
            Choice(name="Svenska", value="sv"),
        ]
    )
    async def set_language(self, interaction: discord.Interaction, language: str):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO guilds(guild_id, language) VALUES($1, $2) ON CONFLICT(guild_id) DO UPDATE SET guild_id = $1, language = $2",
                interaction.guild.id,
                language,
            )
            data = await conn.fetch("SELECT * FROM guilds")
            self.bot.postgre_guilds = data
        await interaction.response.send_message(
            i18n.t("config.language_success", language=language, locale=language),
            ephemeral=True,
        )
