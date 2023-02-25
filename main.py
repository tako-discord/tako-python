import discord
import asyncio
import logging
import pyyoutube
import bot_secrets
import tmdbsimple as tmdb
from TakoBot import TakoBot
from utils import clear_console

youtube_api = pyyoutube.Api(api_key=bot_secrets.YOUTUBE_API_KEY)
tmdb.API_KEY = bot_secrets.TMDB_API_KEY


async def main():
    clear_console()
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    formatter = logging.Formatter(
        "{asctime} | {levelname: <8} | {module}:{funcName}:{lineno} - {message}",
        style="{",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    intents = discord.Intents.default()
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    intents.reactions = True

    bot: TakoBot = TakoBot(command_prefix="tk!", intents=intents)

    await bot.start(bot_secrets.TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
