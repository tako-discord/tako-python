import i18n
import discord
from main import TakoBot
from discord.ext import commands
from utils import get_language


# TODO: Add actual working regex instead of just checking whether it contains something from the list
# TODO: See https://github.com/nikolaischunk/stop-discord-phishing for reference
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
                        locale=get_language(
                            self.bot, message.guild.id if message.guild else None
                        ),
                    )
                )
