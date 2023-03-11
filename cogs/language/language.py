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
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.describe(language="The language to set the bot to")
    @app_commands.guild_only()
    @app_commands.choices(
        language=[
            Choice(name="English (Default)", value="en"),
            Choice(name="Deutsch (German)", value="de"),
            Choice(name="Español (Spanish)", value="es"),
            Choice(name="Français (French)", value="fr"),
            Choice(name="Hrvatski (Croatian)", value="hr"),
            Choice(name="Indonesia (Indonesian)", value="id"),
            Choice(name="Mga Tagalog (Tagalog)", value="tl"),
            Choice(name="Nederlands (Dutch)", value="nl"),
            Choice(name="Polski (Polish)", value="pl"),
            Choice(name="Português, brasileiro (Portuguese, Brazilian)", value="pt"),
            Choice(name="Svenska (Swedish)", value="sv"),
            Choice(name="עִברִית (Hebrew)", value="he"),
            Choice(name="日本 (Japanese)", value="ja"),
        ]
    )
    async def set_language(self, interaction: discord.Interaction, language: str):
        async with self.bot.db_pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO guilds(guild_id, language) VALUES($1, $2) ON CONFLICT(guild_id) DO UPDATE SET guild_id = $1, language = $2",
                interaction.guild_id,
                language,
            )
            data = await conn.fetch("SELECT * FROM guilds")
            self.bot.postgre_guilds = data
        await interaction.response.send_message(
            i18n.t("config.language_success", language=language, locale=language),
            ephemeral=True,
        )
