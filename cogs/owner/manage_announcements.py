import i18n
import discord
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import get_language, owner_only


class AnnouncementModal(discord.ui.Modal, title="Announcement Creator"):
    def __init__(self, bot: TakoBot, type: str):
        super().__init__()
        self.bot = bot
        self.type = type

    annnouncement_title = discord.ui.TextInput(
        label="Title", max_length=256, required=True
    )
    description = discord.ui.TextInput(
        label="Description",
        max_length=4000,
        placeholder="Enter a description",
        style=discord.TextStyle.long,
        required=True,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await self.bot.db_pool.execute(
            "INSERT INTO announcements (title, description, type) VALUES ($1, $2, $3);",
            self.annnouncement_title.value,
            self.description.value,
            self.type,
        )
        await interaction.response.send_message(
            i18n.t(
                "owner.success", locale=get_language(self.bot, interaction.guild_id)
            ),
            ephemeral=True,
        )


class ManageAnnouncements(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(
        description="Create a new global announcement (Bot Owner only)"
    )
    @app_commands.choices(
        type=[
            app_commands.Choice(name="General", value="general"),
            app_commands.Choice(name="Changelog", value="changelog"),
        ]
    )
    @owner_only()
    async def set_announcement(
        self,
        interaction: discord.Interaction,
        type: str = "general",
    ):
        await interaction.response.send_modal(AnnouncementModal(self.bot, type))

    @app_commands.command(description="Delete an announcement (Bot Owner only)")
    @app_commands.describe(id="The id of the announcement to delete")
    @owner_only()
    async def del_announcement(self, interaction: discord.Interaction, id: str):
        announcement = await self.bot.db_pool.fetchrow(
            "SELECT * FROM announcements WHERE id = $1;", id
        )
        if not announcement:
            return await interaction.response.send_message(
                i18n.t(
                    "owner.announcement_not_found",
                    locale=get_language(self.bot, interaction.guild_id),
                )
            )
        await self.bot.db_pool.execute("DELETE FROM announcements WHERE id = $1", id)
        await interaction.response.send_message(
            i18n.t(
                "owner.success", locale=get_language(self.bot, interaction.guild_id)
            ),
            ephemeral=True,
        )

    @del_announcement.autocomplete("id")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        announcements = await self.bot.db_pool.fetch("SELECT * FROM announcements;")
        return [
            app_commands.Choice(
                name=f"{announcement['title']} ({str(announcement['id'])})",
                value=str(announcement["id"]),
            )
            for announcement in announcements
            if current.lower() in announcement["title"].lower()
            or current.lower() in str(announcement["id"]).lower()
        ]
