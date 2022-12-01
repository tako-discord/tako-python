import i18n
import discord
from TakoBot import TakoBot
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from utils import get_color, get_language, thumbnail


async def announcement_embed(
    bot: TakoBot,
    guild_id: int,
    title: str,
    description: str,
    type: str,
    timestamp: datetime,
    id: str,
):
    thumbnail_path = await thumbnail(
        guild_id, "megaphone" if type == "general" else "tag", bot
    )
    file = discord.File(thumbnail_path, filename="thumbnail.png")

    embed = discord.Embed(
        title=title,
        description=description,
        color=await get_color(bot, guild_id),
        timestamp=timestamp,
    )
    embed.set_footer(text=id)
    embed.set_author(name=type.capitalize())
    embed.set_thumbnail(url="attachment://thumbnail.png")
    return embed, file


class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot: TakoBot = bot

    class AnnouncementPaginator(discord.ui.View):
        def __init__(self, bot: TakoBot, index: int):
            super().__init__(timeout=None)
            self.bot = bot
            self.index = index

        @discord.ui.button(emoji="◀", style=discord.ButtonStyle.blurple, row=1)
        async def prev(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            if self.index == 0:
                return await interaction.response.send_message(
                    i18n.t(
                        "info.no_more_announcements",
                        locale=get_language(self.bot, interaction.guild.id),
                    ),
                    ephemeral=True,
                )
            self.index -= 1
            announcements = await self.bot.db_pool.fetch("SELECT * FROM announcements")
            announcement = announcements[self.index]
            embed, file = await announcement_embed(
                self.bot,
                interaction.guild.id,
                announcement["title"] + " (Latest)"
                if self.index == len(announcements) - 1
                else announcement["title"],
                announcement["description"],
                announcement["type"],
                announcement["timestamp"],
                announcement["id"],
            )
            await interaction.response.edit_message(
                embed=embed, attachments=[file], view=self
            )

        @discord.ui.button(emoji="▶", style=discord.ButtonStyle.blurple, row=1)
        async def next(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            announcements = await self.bot.db_pool.fetch("SELECT * FROM announcements")
            if self.index == len(announcements) - 1:
                return await interaction.response.send_message(
                    i18n.t(
                        "info.no_more_announcements",
                        locale=get_language(self.bot, interaction.guild.id),
                    ),
                    ephemeral=True,
                )
            self.index += 1
            announcement = announcements[self.index]
            embed, file = await announcement_embed(
                self.bot,
                interaction.guild.id,
                announcement["title"] + " (Latest)"
                if self.index == len(announcements) - 1
                else announcement["title"],
                announcement["description"],
                announcement["type"],
                announcement["timestamp"],
                announcement["id"],
            )
            await interaction.response.edit_message(
                embed=embed, attachments=[file], view=self
            )

        @discord.ui.button(label="Latest", style=discord.ButtonStyle.green)
        async def latest(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            announcements = await self.bot.db_pool.fetch("SELECT * FROM announcements")
            self.index = len(announcements) - 1
            announcement = announcements[self.index]
            embed, file = await announcement_embed(
                self.bot,
                interaction.guild.id,
                announcement["title"] + " (Latest)",
                announcement["description"],
                announcement["type"],
                announcement["timestamp"],
                announcement["id"],
            )
            await interaction.response.edit_message(
                embed=embed, attachments=[file], view=self
            )

        @discord.ui.button(label="Remove Controls", style=discord.ButtonStyle.red)
        async def remove_controls(
            self, interaction: discord.Interaction, button: discord.ui.Button
        ):
            announcements = await self.bot.db_pool.fetch("SELECT * FROM announcements")
            announcement = announcements[self.index]
            embed, file = await announcement_embed(
                self.bot,
                interaction.guild.id,
                announcement["title"],
                announcement["description"],
                announcement["type"],
                announcement["timestamp"],
                announcement["id"],
            )
            await interaction.response.edit_message(
                embed=embed, attachments=[file], view=None
            )

    @app_commands.command(
        description="View announcements from the developers of the bot"
    )
    async def announcements(self, interaction: discord.Interaction):
        announcements = await self.bot.db_pool.fetch("SELECT * FROM announcements;")
        if not announcements:
            return await interaction.response.send_message(
                i18n.t(
                    "info.no_announcements",
                    locale=get_language(self.bot, interaction.guild.id),
                ),
                ephemeral=True,
            )
        index = len(announcements) - 1
        announcement = announcements[index]
        embed, file = await announcement_embed(
            self.bot,
            interaction.guild.id,
            announcement["title"] + " (Latest)",
            announcement["description"],
            announcement["type"],
            announcement["timestamp"],
            announcement["id"],
        )
        await interaction.response.send_message(
            embed=embed, file=file, view=self.AnnouncementPaginator(self.bot, index)
        )
