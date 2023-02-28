import os
import discord
import tmdbsimple as tmdb
from TakoBot import TakoBot
from discord import app_commands
from discord.ext import commands
from utils import get_color, thumbnail


async def button_logic(
    results,
    interaction: discord.Interaction,
    index: int,
    embed: discord.Embed,
    user: discord.User,
    bot: TakoBot,
):
    if interaction.user.id != user.id:
        return await interaction.response.send_message(
            "You cannot interact with this message because it was not invoked by you.",
            ephemeral=True,
        )
    result_id = results[index]["id"]
    view = ReturnButton(bot, results, embed, user, interaction.guild)
    tmdb_logo = discord.File(f"{os.getcwd()}/assets/TMDb.png")
    title = (
        results[index]["title"] if "title" in results[index] else results[index]["name"]
    )
    types = {"movie": "Movie", "tv": "TV", "person": "Person"}
    if results[index]["media_type"] == "movie":
        more_info = tmdb.Movies(result_id).info()
    if results[index]["media_type"] == "tv":
        more_info = tmdb.TV(result_id).info()
    if results[index]["media_type"] == "person":
        more_info = tmdb.People(result_id).info()
    if results[index]["media_type"] == "movie" or results[index]["media_type"] == "tv":
        tagline = (
            f"**{more_info['tagline']}**" if more_info["tagline"] else "**No Tagline**"
        )
        detailed_embed = discord.Embed(
            title=f"{title} ({types[results[index]['media_type']]})",
            description=tagline,
            color=await get_color(bot, interaction.guild_id),
        )
    else:
        biography = more_info["biography"]
        detailed_embed = discord.Embed(
            title=f"{title} ({types[results[index]['media_type']]})",
            description=biography
            if len(biography) <= 1024
            else f"{biography[:1021]}...",
            color=await get_color(bot, interaction.guild_id),
        )
    url = f"https://image.tmdb.org/t/p/original{more_info['backdrop_path'] if 'backdrop_path' in more_info else more_info['profile_path']}"
    detailed_embed.set_image(url=url)
    detailed_embed.set_footer(text="Data by TMDb", icon_url="attachment://TMDb.png")
    await interaction.response.edit_message(
        embed=detailed_embed, attachments=[tmdb_logo], view=view
    )


def remove_items(results, view: discord.ui.View):
    for item in view.children:
        if len(results) < 2 and item.emoji.name == "2️⃣":
            view.remove_item(item)
            continue
        if len(results) < 3 and item.emoji.name == "3️⃣":
            view.remove_item(item)
            continue


class ReturnButton(discord.ui.View):
    def __init__(self, bot, results, embed: discord.Embed, user, guild: discord.Guild):
        super().__init__()
        self.bot = bot
        self.results = results
        self.embed = embed
        self.user = user
        self.guild = guild

    @discord.ui.button(
        label="Back to search results", emoji="⬅️", style=discord.ButtonStyle.primary
    )
    async def close(self, interaction: discord.Interaction, button: discord.Button):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                "You cannot interact with this message because it was not invoked by you.",
                ephemeral=True,
            )
        view = MediaButtons(self.results, self.embed, interaction.user, self.bot)
        remove_items(self.results, view)
        file = discord.File(
            await thumbnail(self.guild.id, "search", self.bot), filename="thumbnail.png"
        )
        tmdb_logo = discord.File(f"{os.getcwd()}/assets/TMDb.png")
        await interaction.response.edit_message(
            embed=self.embed, attachments=[file, tmdb_logo], view=view
        )


class MediaButtons(discord.ui.View):
    def __init__(self, results, embed, user, bot):
        super().__init__()
        self.results = results
        self.embed = embed
        self.user = user
        self.bot = bot

    @discord.ui.button(emoji="1️⃣", style=discord.ButtonStyle.grey)
    async def one(self, interaction: discord.Interaction, button: discord.ui.Button):
        await button_logic(
            results=self.results,
            interaction=interaction,
            index=0,
            embed=self.embed,
            user=self.user,
            bot=self.bot,
        )

    @discord.ui.button(emoji="2️⃣", style=discord.ButtonStyle.grey)
    async def two(self, interaction: discord.Interaction, button: discord.ui.Button):
        await button_logic(
            results=self.results,
            interaction=interaction,
            index=1,
            embed=self.embed,
            user=self.user,
            bot=self.bot,
        )

    @discord.ui.button(emoji="3️⃣", style=discord.ButtonStyle.grey)
    async def three(self, interaction: discord.Interaction, button: discord.ui.Button):
        await button_logic(
            results=self.results,
            interaction=interaction,
            index=2,
            embed=self.embed,
            user=self.user,
            bot=self.bot,
        )


class Media(commands.GroupCog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Search for a movie, TV show or person")
    @app_commands.describe(query="The movie, TV show or person to search for")
    async def search(self, interaction: discord.Interaction, query: str):
        count = 0
        search = tmdb.Search()
        search.multi(query=query)
        search.results = search.results[:3]
        types = {"movie": "Movie", "tv": "TV", "person": "Person"}
        thumbnail_path = await thumbnail(interaction.guild_id, "search", self.bot)
        file = discord.File(thumbnail_path, filename="thumbnail.png")
        tmdb_logo = discord.File(f"{os.getcwd()}/assets/TMDb.png")
        embed = discord.Embed(
            title="Media search",
            description=f"Top {len(search.results[:3])} Search results for *{query}*"
            if len(search.results)
            else "Nothing matched your search",
            color=await get_color(self.bot, interaction.guild_id),
        )
        for s in search.results:
            if s["media_type"] == "movie":
                more_info = tmdb.Movies(s["id"]).info()
            if s["media_type"] == "tv":
                more_info = tmdb.TV(s["id"]).info()
            if s["media_type"] == "person":
                more_info = tmdb.People(s["id"]).info()
            count = count + 1
            if s["media_type"] == "person":
                tagline = f"*Known for department*: {more_info['known_for_department']}"
            else:
                tagline = (
                    f"**{more_info['tagline']}**"
                    if more_info["tagline"]
                    else "**No Tagline**"
                )
            date = f"*Release date*: {more_info['release_date'] if 'release_date' in more_info else 'No release date'}"
            if s["media_type"] == "person":
                date = f"*Birthday*: {more_info['birthday']}"
            score = (
                f"*Score*: {int(float(s['vote_average']) * 10)}%"
                if "vote_average" in s
                else ""
            )
            embed_values = [
                tagline,
                date,
                score,
            ]
            title = s["title"] if "title" in s else s["name"]
            embed.add_field(
                name=f"[{count}] {title} ({types[search.results[count-1]['media_type']]})",
                value="\n".join(embed_values),
                inline=False,
            )
        embed.set_thumbnail(url="attachment://thumbnail.png")
        embed.set_footer(text="Data by TMDb", icon_url="attachment://TMDb.png")

        view = (
            MediaButtons(search.results, embed, interaction.user, self.bot)
            if len(search.results)
            else None
        )
        if view:
            remove_items(search.results, view)
        await interaction.response.send_message(
            embed=embed, files=[file, tmdb_logo], view=view
        )
