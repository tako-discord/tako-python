import i18n
import discord
import humanize
from main import youtube_api
from discord import app_commands
from discord.ext import commands
from utils import get_color, error_embed, get_language


class Youtube(commands.GroupCog, group_name="youtube"):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(description="Search a video on YouTube")
    @app_commands.describe(query="The query for the YouTube Search")
    async def search(self, interaction: discord.Interaction, query: str) -> None:
        await interaction.response.defer()
        results = youtube_api.search_by_keywords(q=query, count=3).items
        language = get_language(self.bot, interaction.guild_id)
        if not results:
            embed, file = error_embed(
                self.bot,
                i18n.t("misc.no_results_title", locale=language),
                i18n.t("misc.no_results", locale=language, query=query[:1000]),
                guild_id=interaction.guild_id,
            )
            await interaction.followup.send(embed=embed, file=file)
            return
        embed = discord.Embed(
            title="YouTube Search",
            color=await get_color(self.bot, interaction.guild_id),  # type: ignore
            description=f"Top {len(results)} Search results for *{query}*",
        )

        if not results:
            embed.description = f"No results found for *{query}*"
        for result in results:
            video = youtube_api.get_video_by_id(video_id=result.id.videoId).items[0]
            humanize_format = "%0.2f"
            field_value = [
                f"[__Video Link__](https://youtube.com/watch?v={result.id.videoId})",
                f"*Channel*: {video.snippet.channelTitle}",
                f"👀 {humanize.intword(video.statistics.viewCount, humanize_format)}",
                f"👍 {humanize.intword(video.statistics.likeCount, humanize_format)}",
                f"💬 {humanize.intword(video.statistics.commentCount, humanize_format)}",
            ]
            embed.add_field(
                name=video.snippet.title, value="\n".join(field_value), inline=False
            )
        await interaction.followup.send(embed=embed)
        return
