import i18n
import config
import discord
import aiohttp
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from persistent_views.meme_buttons import MemeButtons
from utils import delete_thumbnail, new_meme, thumbnail, get_color, get_language


class Reddit(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(
        description="Get a random meme from the subreddits: memes, me_irl or dankmemes"
    )
    async def meme(self, interaction: discord.Interaction):
        embed, file = await new_meme(
            interaction.guild_id if interaction.guild_id else interaction.user.id,
            interaction.user.id,
            self.bot,
            self.bot.db_pool,
        )

        await interaction.response.send_message(
            embed=embed, file=file, view=MemeButtons(self.bot), ephemeral=True
        )
        delete_thumbnail(
            interaction.guild_id if interaction.guild_id else interaction.user.id,
            "reddit",
        )

    @app_commands.command(description="Get a random post from a subreddit")
    @app_commands.guild_only()
    @app_commands.describe(subreddit="The subreddit to get a random post from")
    async def reddit(self, interaction: discord.Interaction, subreddit: str):
        await interaction.response.defer()
        language = get_language(self.bot, interaction.guild_id)
        if subreddit.startswith("r/"):
            subreddit = subreddit[2:]
        session_timeout = aiohttp.ClientTimeout(total=None, sock_connect=1, sock_read=1)
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            async with session.get(
                f"https://meme-api.com/gimme/{subreddit}/", timeout=1
            ) as r:
                data = await r.json()
                try:
                    if data["code"] == 404:
                        return await interaction.followup.send(
                            i18n.t("misc.reddit_not_found", locale=language),
                            ephemeral=True,
                        )
                    if data["code"] == 400:
                        return await interaction.followup.send(
                            i18n.t("misc.reddit_no_images", locale=language),
                            ephemeral=True,
                        )
                except KeyError:
                    pass
                if hasattr(interaction.channel, "nsfw"):
                    if not interaction.channel.nsfw:  # type: ignore
                        if data["nsfw"]:
                            return await interaction.followup.send(
                                i18n.t("misc.reddit_nsfw", locale=language),
                                ephemeral=True,
                            )
                if hasattr(interaction.channel, "parent"):
                    if not interaction.channel.parent.nsfw:  # type: ignore
                        if data["nsfw"]:
                            return await interaction.followup.send(
                                i18n.t("misc.reddit_nsfw", locale=language),
                                ephemeral=True,
                            )
                embed = discord.Embed(
                    title=data["title"],
                    url=data["postLink"],
                    description=f"{config.EMOJI_UPVOTE if hasattr(config, 'EMOJI_UPVOTE') else '👍'} {data['ups']}",
                    color=await get_color(self.bot, interaction.guild_id),  # type: ignore
                )
                embed.set_image(url=data["url"])
                embed.set_footer(text=f"r/{data['subreddit']}")
                embed.set_author(
                    name=f"u/{data['author']}",
                    url=f"https://reddit.com/u/{data['author']}",
                )

                path = await thumbnail(interaction.guild_id, "reddit", self.bot)
                file = discord.File(path, filename="reddit.png")
                embed.set_thumbnail(url="attachment://reddit.png")

                await interaction.followup.send(embed=embed, file=file)
