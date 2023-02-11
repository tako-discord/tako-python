import i18n
import discord
from TakoBot import TakoBot
from discord.ext import commands
from utils import get_language


class AntiPhishing(commands.Cog):
    def __init__(self, bot: TakoBot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        for domain in self.bot.sussy_domains:
            if message.content.lower().__contains__(domain):
                await message.delete()
                await message.channel.send(
                    i18n.t(
                        "moderation.malicious_link",
                        user=message.author.mention,
                        locale=get_language(self.bot, message.guild.id),
                    )
                )
