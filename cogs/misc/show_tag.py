import discord
from utils import get_color
from discord import app_commands
from discord.ext import commands


class ShowTag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Show a tag", name="tag-show")
    async def show(self, interaction: discord.Interaction, tag: str):
        if len(tag) < 32 or len(tag) > 36:
            return await interaction.response.send_message(
                "This tag does not exist!", ephemeral=True
            )
        tag = await self.bot.db_pool.fetchrow(
            "SELECT * FROM tags WHERE id = $1 AND guild_id = $2;",
            tag,
            interaction.guild_id,
        )
        if tag is None:
            return await interaction.response.send_message(
                "This tag does not exist!", ephemeral=True
            )
        if tag["embed"]:
            embed = discord.Embed(
                title=tag["name"],
                description=tag["content"],
                color=await get_color(self.bot, interaction.guild_id),
            )
            embed.set_thumbnail(url=tag["thumbnail"])
            embed.set_image(url=tag["image"])
            embed.set_footer(text=tag["footer"])
            return await interaction.response.send_message(embed=embed)
        await interaction.response.send_message(f"**{tag['name']}**\n{tag['content']}")

    @show.autocomplete(name="tag")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        tags = await self.bot.db_pool.fetch(
            "SELECT * FROM tags WHERE guild_id = $1;", interaction.guild_id
        )
        return [
            app_commands.Choice(
                name=f"{tag['name']} ({str(tag['id'])})", value=str(tag["id"])
            )
            for tag in tags
            if current.lower() in tag["name"].lower()
            or current.lower() in str(tag["id"]).lower()
        ]
