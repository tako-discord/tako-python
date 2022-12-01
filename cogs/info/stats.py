import sys
import time
import psutil
import config
import discord
import datetime
from discord import app_commands
from discord.ext import commands
from cpuinfo import get_cpu_info
from utils import format_bytes, get_color


class Stats(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(description="Get some stats about me")
    async def stats(self, interaction):
        await interaction.response.defer()
        # latest_version = requests.get("https://raw.githubusercontent.com/kayano-bot/kayano-rewrite/master/cz.json").json()["commitizen"]["version"]
        operating_systems = {
            "aix": "AIX",
            "darwin": "MacOS",
            "linux": "Linux",
            "win32": "Windows",
        }
        general = [
            f"**<:server:950769912958320680> Server count**: {len(self.bot.guilds)}",
            f"**<:users:950777719417876502> User count**: {len(self.bot.users)}",
            f"**<:channel:951127622820171846> Channel count**: {len(list(self.bot.get_all_channels()))}",
            f"**<:slash_command:951124330459328553> Commands**: {len(self.bot.tree.get_commands())}",
            f"**<:server:950769912958320680> Current Shard**: {self.bot.shard_id if self.bot.shard_id else 'No shard'}",
            f"**🏷️ Version**: {self.bot.version}",
            f"**<:discordpy:968192318836465714> Discord.py Version**: {discord.__version__}",
            f"**<:python:968192022232055808> Python Version**: {sys.version.split(' ', 1)[0]}",
            f"**🏓 Ping**: {round(self.bot.latency * 1000)} ms.",
        ]
        cpu_info = get_cpu_info()
        system = [
            f"**🖥️ Platform**: {operating_systems[sys.platform]}",
            f"**🕐 Uptime**: {str(datetime.timedelta(seconds=time.time() - psutil.boot_time())).split('.')[0]}",
            f"**⚡ CPU**:",
            f"\u3000*Model*: {cpu_info['brand_raw']}",
            f"\u3000*Cores*: {cpu_info['count']}",
            f"\u3000*Speed*: {cpu_info['hz_advertised_friendly'][0]} GHz",
            f"\u3000*Usage (Systemwide)*: {psutil.cpu_percent()}%",
            f"**🗄️ Memory**:",
            f"\u3000*Total*: {format_bytes(psutil.virtual_memory().total)}",
            f"\u3000*Available*: {format_bytes(psutil.virtual_memory().available)}",
        ]
        social_media = []
        if hasattr(config, "TWITTER_LINK"):
            social_media.append(
                f"**{config.EMOJI_TWITTER if hasattr(config, 'EMOJI_TWITTER') else ''} Twitter**: [@DiscordTako]({config.TWITTER_LINK})"
            )
        if hasattr(config, "YOUTUBE_LINK"):
            social_media.append(
                f"**{config.EMOJI_YT if hasattr(config, 'EMOJI_YT') else ''} Youtube**: [Tako]({config.YOUTUBE_LINK})"
            )

        embed = discord.Embed(
            title="📊 Stats",
            description="Here are some stats about me",
            color=await get_color(self.bot, interaction.guild.id),
        )
        embed.set_author(
            name=self.bot.user.name + "#" + self.bot.user.discriminator,
            icon_url=self.bot.user.avatar.url,
        )
        embed.add_field(name="General", value="\n".join(general))
        embed.add_field(name="System", value="\n".join(system))
        if hasattr(config, "YOUTUBE_LINK") or hasattr(config, "TWITTER_LINK"):
            embed.add_field(
                name="Social Media", value="\n".join(social_media), inline=False
            )

        await interaction.followup.send(embed=embed)
