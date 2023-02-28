import discord
from millify import millify
from main import youtube_api
from discord import app_commands
from discord.ext import commands
from utils import get_color


class Youtube(commands.GroupCog, group_name="youtube"):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(description="Search a video on YouTube")
    @app_commands.describe(query="The query for the YouTube Search")
    async def search(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer()
        results = youtube_api.search_by_keywords(q=query, count=3).items
        embed = discord.Embed(
            title="YouTube Search",
            color=await get_color(self.bot, interaction.guild_id),
            description=f"Top {len(results)} Search results for *{query}*",
        )

        if not results:
            embed.description = f"No results found for *{query}*"
        for result in results:
            video = youtube_api.get_video_by_id(video_id=result.id.videoId).items[0]
            precision = 2
            field_value = [
                f"[__Video Link__](https://youtube.com/watch?v={result.id.videoId})",
                f"*Channel*: {video.snippet.channelTitle}",
                f"👀 {millify(video.statistics.viewCount, precision=precision)}",
                f"👍 {millify(video.statistics.likeCount, precision=precision)}",
                f"💬 {millify(video.statistics.commentCount, precision=precision)}",
            ]
            embed.add_field(
                name=video.snippet.title, value="\n".join(field_value), inline=False
            )
        await interaction.followup.send(embed=embed)
