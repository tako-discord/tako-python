import discord
from discord import app_commands
from discord.ext import commands


def get_ping_color(ping: int):
    if ping < 200:
        return discord.Color.green()
    if ping < 500:
        return discord.Color.orange()
    return discord.Color.red()


def get_ping_color_name(ping: int):
    if ping < 200:
        return "green"
    if ping < 500:
        return "orange"
    return "red"


class Ping(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @app_commands.command(description="Get my latency")
    async def ping(self, interaction: discord.Interaction):
        ping = round(self.bot.latency * 1000)
        color = get_ping_color(ping)
        thumbnail = discord.File(
            f"assets/ping/ping_{get_ping_color_name(ping)}.png", "thumbnail.png"
        )
        embed = discord.Embed(title="🏓 Pong!", color=color)
        embed.add_field(name="Latency", value=f"{ping} ms.")
        embed.set_thumbnail(url="attachment://thumbnail.png")
        await interaction.response.send_message(embed=embed, file=thumbnail)
