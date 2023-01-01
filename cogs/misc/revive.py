import i18n
import discord
from random import randint
from .topics import questions
from discord import app_commands
from discord.ext import commands
from utils import get_language, translate, get_color


class Revive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Get a random topic to talk about")
    @app_commands.describe(
        id="The topic to show (If not specified, a random topic will be chosen)"
    )
    async def topic(
        self,
        interaction: discord.Interaction,
        id: app_commands.Range[
            int, 1, 2  # <-- Change the 2 to the amount of topics you have.
        ]
        | None = None,
    ):
        locale = get_language(self.bot, interaction.guild.id)
        id = randint(0, len(questions)) if not id else id
        index = id - 1

        embed = discord.Embed(
            title=i18n.t("misc.topic_title", locale=locale),
            description=await translate(questions[index], locale),
            color=await get_color(self.bot, interaction.guild.id),
        )
        embed.set_footer(text=i18n.t("misc.topic_footer", locale=locale, id=id))

        await interaction.response.send_message(embed=embed)
