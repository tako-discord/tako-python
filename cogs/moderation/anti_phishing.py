from re import findall

import discord
from discord.ext import commands

import i18n
from main import TakoBot
from utils import get_language


class AntiPhishing(commands.Cog):
    def __init__(self, bot: TakoBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        url_extract_pattern = "[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]*)"

        urls = findall(
            url_extract_pattern,
            message.content.lower(),
        )
        for domain in self.bot.sussy_domains:
            for url in urls:
                if url == domain:
                    await message.delete()
                    await message.channel.send(
                        i18n.t(
                            "moderation.malicious_link",
                            user=message.author.mention,
                            locale=get_language(
                                self.bot, message.guild.id if message.guild else None
                            ),
                        )
                    )
