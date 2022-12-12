import os
import i18n
import json
import config
import discord
import asyncpg
import aiohttp
from uuid import UUID
from datetime import datetime
from urllib.parse import quote
from config import REPO, RAW_GH
from discord import app_commands
from PIL import Image, ImageColor


def clear_console():
    """Clears the console (Supported: Windows & Unix)"""
    command = "clear"
    if os.name in ("nt", "dos"):
        command = "cls"
    return os.system(command)


def format_bytes(size: int):
    """:class:`str`: Returns given bytes into human readable text.
    Supported Range: Bytes -> TB

    Parameters
    -----------
    size: :class:`int`
        Size in bytes to convert
    """
    power = 2**10
    n = 0
    power_labels = ["Bytes", "KB", "MB", "GB", "TB"]
    while size > power and n != 4:
        size /= power
        n += 1
    return str(round(size)) + power_labels[n]


async def get_color(bot, guild_id: int, integer: bool = True):
    """:class:`str` or :class:`int`: Returns the set color of a guild (Default: config.DEFAULT_COLOR)

    Parameters
    -----------
    guild_id: :class:`int`
        The id of the guild you want the color from
    integer: :class:`bool`
        Whetever you want to get the color as an integer or as a string
    """
    color = None
    try:
        color = await bot.db_pool.fetchval(
            "SELECT color FROM guilds WHERE guild_id = $1", guild_id
        )
    except:
        pass
    if integer:
        return int(color, 16) if color is not None else config.DEFAULT_COLOR
    return color if color is not None else config.DEFAULT_COLOR_STR


def color_check(color: str):
    """:class:`bool`: Checks if black or white has more contrast to the input color.

    Parameters
    -----------
    color: :class:`str`
        The color to check (#HEXCOLOR)

    Returns
    --------
    :class:`bool`
        True = White has more contrast

        False = Black has more contrast
    """
    value = True
    rgb = ImageColor.getcolor(color, "RGB")
    value = True if (rgb[0] * 0.299 + rgb[1] * 0.587 + rgb[2] * 0.114) < 143 else False
    return value


async def thumbnail(id: int, icon_name: str, bot):
    """:class:`str`: Creates a thumbnail and returns the filepath of the image.
    Parameters
    -----------
    id: :class:`int`
        The id of the guild to create the thumbnail for.
    icon_name: :class:`str`
        The name of the icon used for the thumbnail. Needs to be in the assets directory and have a `name.png` and `name_dark.png` variant.
    """
    color = await get_color(bot, id, False)
    img = Image.new("RGB", (512, 512), color=color.replace("0x", "#"))
    icon = Image.open(
        f"assets/{icon_name}{'' if color_check(color.replace('0x', '#')) or icon_name is 'reddit' else '_dark'}.png"
    )
    img.paste(icon, (56, 56), mask=icon)
    img.save(f"assets/thumbnails/{icon_name}_{id}.png")
    return f"assets/thumbnails/{icon_name}_{id}.png"


def delete_thumbnail(id: int, icon: str):
    """Deletes a thumbnail (mostly created with the thumbnail() function).

    Parameters
    -----------
    id: :class:`int`
        The id of the guild the thumbnail should be deleted for.
    icon: :class:`str`
        The name of the icon that was used for the thumbnail creation. Needs to be in the assets directory and have a `name.png` and `name_dark.png` variant.
    """
    if config.DELETE_THUMBNAILS == False:
        return
    if os.path.exists(f"assets/thumbnails/{icon}_{id}.png"):
        os.remove(f"assets/thumbnails/{icon}_{id}.png")


def get_language(bot, guild_id: int | None = None):
    """:class:`str`: Get the language of a guild.

    Parameters
    -----------
    bot: :class:`TakoBot`
    guild_id: :class:`int`
        The id of the guild to get the language from.
    """
    language = "en"
    for guild in bot.postgre_guilds:
        if guild["guild_id"] == guild_id:
            language = guild["language"]
    return language if language else "en"


def number_of_pages_needed(elements_per_page: int, total_elements: int):
    """:class:`int`: Returns the number of pages needed if elements per page are limited.

    Parameters
    -----------
    elements_per_page: :class:`int`
        The maximum amount of elements per page.
    total_element: :class:`int`
        The total elements.
    """
    q, r = divmod(total_elements, elements_per_page)
    if r > 0:
        return q + 1
    return q


async def create_user(
    pool: asyncpg.Pool | asyncpg.Connection,
    user: discord.User,
    wallet: int = config.DEFAULT_WALLET,
    bank: int = config.DEFAULT_BANK,
):
    """
    Creates an user in the database.

    Parameters
    -----------
    pool: :class:`asyncpg.Pool`
        The PostgreSQL pool to use.
    user: :class:`discord.User`
        The user to create a row for.
    wallet: :class:`int`
        The amount of money the user has in it's wallet. (Default: config.DEFAULT_WALLET)
    bank: :class:`int`
        The amount of money the user has in it's bank. (Default: config.DEFAULT_BANK)
    """
    await pool.execute(
        "INSERT INTO users (user_id, wallet, bank) VALUES ($1, $2, $3)",
        user.id,
        wallet,
        bank,
    )


def add_extension(url: str):
    """Add an extension from git to the bot.

    Parameters
    -----------
    url: :class:`str`
        The url pointing to the git repository the extension is located at.
    """
    valid_url = os.system(f"git ls-remote {url} > /dev/null 2>&1")
    if valid_url != 0:
        return 1
    cloning = os.system(
        f"cd extensions > /dev/null && git submodule add {url} > /dev/null 2>&1"
    )
    if cloning != 0:
        return 2
    return 0


async def fetch_cash(pool: asyncpg.Pool | asyncpg.Connection, user: discord.User):
    """list[`int`, `int`]: Returns the amount of money a user has in a list where the first value is the money
    in the wallet and the second value is the money in the bank of the user. It will also create a user if it doesn't exist yet.

    Parameters
    -----------
    pool: :class:`asyncpg.Pool` | :class:`asyncpg.Connection`
        The PostgreSQL pool to use. Generally `bot.db_pool`.
    user: :class:`discord.User`
        The user to get the current balance from."""
    data = await pool.fetchrow(
        "SELECT wallet, bank FROM users WHERE user_id = $1;", user.id
    )
    if not data:
        await create_user(pool, user)
    return list(data) if data else [config.DEFAULT_WALLET, config.DEFAULT_BANK]


async def balance_embed(
    bot, user: discord.User | discord.Member, guild_id: int, cash: list[int]
):
    """tuple[:class:`discord.Embed`, :class:`discord.File`]: Returns a tuple of an embed and it's file with the balance of a user.

    Parameters
    -----------
    bot: :class:`TakoBot`
    user: :class:`discord.User` | :class:`discord.Member`
        The user to get the balance from.
    guild_id: :class:`int`
        The id of the guild where the language and color is getting fetched from.
    cash: :class:`list[:class:`int`]`
        The amount of money the user has in it's wallet and bank. (Use the fetch_cash() function to get this)"""
    thumbnail_path = await thumbnail(guild_id, "money", bot)
    file = discord.File(thumbnail_path, filename="thumbnail.png")

    embed = discord.Embed(
        title=i18n.t("economy.balance", locale=get_language(bot, guild_id)),
        color=await get_color(bot, guild_id),
    )
    embed.add_field(
        name=i18n.t("economy.wallet", locale=get_language(bot, guild_id)),
        value=f"{cash[0]:,}{config.CURRENCY}",
    )
    embed.add_field(
        name=i18n.t("economy.bank", locale=get_language(bot, guild_id)),
        value=f"{cash[1]:,}{config.CURRENCY}",
    )
    embed.set_author(name=str(user), icon_url=user.display_avatar.url)
    embed.set_thumbnail(url="attachment://thumbnail.png")

    return embed, file


def error_embed(
    bot,
    title: str,
    description: str,
    guild_id: int,
    footer: str = None,
    style: str = "error",
):
    """tuple[:class:`discord.Embed`, :class:`discord.File`]: Returns an error embed and a file for it's Thumbnail.
    The first value is the embed and the second value is the file.

    Parameters
    -----------
    title: :class:`str`
        The title of the embed.
    description: :class:`str`
        The description of the embed.
    footer: :class:`str` = "An error occured"
        The footer of the embed. (Mostly just the translation of "An error occured")
    style: :class:`str` = "error"
        The style of the embed. (Either 'error' or 'warning')
    """
    match style:
        case "error":
            file = discord.File("assets/alert.png", filename="thumbnail.png")
            if not footer:
                footer = (
                    i18n.t("errors.error_occured", locale=get_language(bot, guild_id))
                    if not footer
                    else footer
                )
        case _:
            file = discord.File("assets/warning.png", filename="thumbnail.png")
            footer = (
                i18n.t("errors.warning_occured", locale=get_language(bot, guild_id))
                if not footer
                else footer
            )
    embed = discord.Embed(
        title=f"**{title}**",
        description=description,
        color=discord.Color.red() if style == "error" else discord.Color.yellow(),
        timestamp=datetime.now(),
    )
    embed.set_thumbnail(url="attachment://thumbnail.png")
    embed.set_footer(text=footer)
    return embed, file


async def get_latest_version():
    """Returns the latest version of the bot."""
    async with aiohttp.ClientSession() as session:
        async with session.get(RAW_GH + REPO + "/master/.gitmoji-changelogrc") as r:
            data = await r.read()
            data = json.loads(data)
            return data["project"]["version"]


async def translate(text: str, target: str, source: str = "auto"):
    """Translates a given string to a specified language.

    Parameters
    -----------
    text: :class:`str`
        The text to translate.
    target: :class:`str`
        The language to translate to.
    source: :class:`str` (Default: "auto")
        The language to translate from."""
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{config.SIMPLY_TRANSLATE}/api/translate/?engine=google&text={quote(text)}&from={source}&to={target}"
        ) as r:
            data = await r.json()
            return data["translated-text"]


async def new_meme(guild_id: int, user_id: int, bot, db_pool: asyncpg.Pool):
    """Returns a new meme embed and it's file from reddit.

    Parameters
    -----------
    guild_id: :class:`int`
        The id of the guild where the language and color is getting fetched from.
    user_id: :class:`int`
        The id of the user who requested the meme.
    bot: :class:`TakoBot`
    db_pool: :class:`asyncpg.Pool`
        The PostgreSQL pool to use. Generally `bot.db_pool`.

    Returns
    --------
    tuple[:class:`discord.Embed`, :class:`discord.File`]"""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.herokuapp.com/gimme/") as r:
            thumbnail_path = await thumbnail(guild_id, "reddit", bot)
            file = discord.File(thumbnail_path, filename="thumbnail.png")

            data = await r.json()
            embed = discord.Embed(
                title=f"{data['title']}",
                description=data["postLink"],
                color=await get_color(bot, guild_id),
            )
            embed.set_author(
                name=data["author"],
                url=f"https://reddit.com/u/{data['author']}",
                icon_url="https://www.redditstatic.com/avatars/defaults/v2/avatar_default_1.png",
            )
            embed.set_thumbnail(url="attachment://thumbnail.png")
            embed.set_image(url=data["url"])
            embed.set_footer(text=f"r/{data['subreddit']} • {data['ups']} 👍")

            async with db_pool.acquire() as con:
                user_data = await con.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1;", user_id
                )
                data = (
                    str(data)
                    .replace("'", '"')
                    .replace("True", "true")
                    .replace("False", "false")
                )
                if user_data:
                    await con.execute(
                        "UPDATE users SET last_meme = $1 WHERE user_id = $2;",
                        data,
                        user_id,
                    )
                else:
                    await con.execute(
                        "INSERT INTO users (user_id, last_meme) VALUES ($1, $2);",
                        user_id,
                        data,
                    )

            return embed, file


async def is_owner_func(bot, user: discord.User | discord.Member):
    """
    Checks if the given user is the owner of the bot.

    Parameters
    -----------
    bot: :class:`TakoBot`
        The bot instance.
    user: :class:`discord.User` | :class:`discord.Member`
        The user to check.
    """
    app_info = await bot.application_info()
    if hasattr(app_info, "team") and hasattr(app_info.team, "members"):
        owners = []
        for member in app_info.team.members:
            if member.membership_state == discord.TeamMembershipState.accepted:
                owners.append(member.id)
        return True if user.id in owners else False
    return True if user.id == bot.owner_id else False


def owner_only():
    """
    An :class:`app_commands.check()` that checks if the user is the owner of the bot.
    """

    async def check(interaction: discord.Interaction):
        return await is_owner_func(interaction.client, interaction.user)

    return app_commands.check(check)


async def poll_embed(
    question: str, asnwers: list, votes: str, bot, guild_id: int, uuid: UUID
):
    """Returns a poll embed.

    Parameters
    -----------
    question: :class:`str`
        The question of the poll.
    asnwers: :class:`list`
        The answers of the poll.
    votes: :class:`str`
        A stringified dictonary from the votes of the poll.
    guild_id: :class:`int`
        The id of the guild where the color is getting fetched from.

    Returns
    --------
    :class:`discord.Embed`"""
    votes = json.loads(votes)
    total_votes = len(votes)
    embed = discord.Embed(
        title=f"**{question}**",
        color=await get_color(bot, guild_id),
    )
    embed.set_footer(text=uuid)

    count = {}
    for answer in asnwers:
        count[f"{answer}"] = 0

    for user in votes:
        value = votes[user]
        count[value] += 1

    percentages = {}
    results = {}
    for answer in count:
        if total_votes != 0:
            percentages[answer] = round(count[answer] / total_votes * 100)
        else:
            percentages[answer] = 0
        progress = []
        for i in range(1, 11):
            if i <= percentages[answer] // 10:
                progress.append(config.EMOJI_MIDDLE_BAR_FULL)
            else:
                progress.append(config.EMOJI_MIDDLE_BAR)
        end = config.EMOJI_END_BAR
        if percentages[answer] >= 90:
            end = config.EMOJI_END_BAR_FULL
        start = config.EMOJI_START_BAR_FULL
        if percentages[answer] < 1:
            start = config.EMOJI_START_BAR
        results[answer] = f"{start}{''.join(progress)}{end} {percentages[answer]}%"
    for result in results:
        embed.add_field(
            name=f"{result} ({count[result]})", value=results[result], inline=False
        )

    return embed
