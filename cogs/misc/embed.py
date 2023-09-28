import re
import discord
from utils import get_color
from datetime import datetime
from discord import app_commands
from discord.ext import commands


class EmbedModal(discord.ui.Modal, title="Embed Creator"):
    def __init__(self, embed: discord.Embed):
        super().__init__()
        self.embed = embed

    embed_title = discord.ui.TextInput(label="Title", required=False)
    description = discord.ui.TextInput(
        label="Description",
        max_length=1024,
        placeholder="Enter a description",
        style=discord.TextStyle.long,
    )
    thumbnail = discord.ui.TextInput(label="Thumbnail", required=False)
    image = discord.ui.TextInput(label="Image", required=False)
    footer = discord.ui.TextInput(label="Footer", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        embed = self.embed
        embed.title = self.embed_title.value
        embed.description = self.description.value
        embed.set_thumbnail(url=self.thumbnail.value)
        embed.set_image(url=self.image.value)
        embed.set_footer(text=self.footer.value)
        await interaction.channel.send(embed=self.embed)
        await interaction.response.send_message(
            content="Succesfully send your embed!", ephemeral=True
        )


class Embed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Create an embed")
    async def embed(
        self,
        interaction: discord.Interaction,
        color: str = None,
        timestamp: bool = False,
    ):
        if color is None:
            color = await get_color(self.bot, interaction.guild_id, False)
        if color.startswith("#"):
            color = color.replace("#", "0x")
        if not color.startswith("0x"):
            color = f"0x{color}"
        match = re.search(r"^0x([A-Fa-f0-9]{6})$", color)
        if not match:
            return await interaction.response.send_message(
                f"Your color (`{color}`) is not a valid (*6* character) hex color.",
                ephemeral=True,
            )
        if timestamp:
            timestamp = datetime.now()
        else:
            timestamp = None
        embed = discord.Embed(
            color=color if isinstance(color, int) else int(color, 16),
            timestamp=timestamp,
        )
        embed.set_author(
            name=interaction.user.name + "#" + interaction.user.discriminator,
            icon_url=interaction.user.display_avatar,
            url=f"https://discord.com/users/{interaction.user.id}",
        )
        await interaction.response.send_modal(EmbedModal(embed))
