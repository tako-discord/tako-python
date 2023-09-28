import i18n
import discord
from asyncio import sleep
from random import randint
from .topics import questions
from discord import app_commands
from discord.ext import commands
from utils import get_language, translate, get_color, error_embed


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
        id: int | None = None,
    ):
        await interaction.response.defer()
        locale = get_language(self.bot, interaction.guild_id)
        id = randint(0, len(questions)) if id is None else id
        index = id - 1
        embeds = []
        files = []
        valid_topic = True

        if id > len(questions) or id <= 0:
            id = randint(0, len(questions))
            index = id - 1
            valid_topic = False

        embed = discord.Embed(
            title=i18n.t("misc.topic_title", locale=locale),
            description=(await translate(questions[index], locale, "en"))[0],
            color=await get_color(self.bot, interaction.guild_id),  # type: ignore
        )
        embed.set_footer(text=i18n.t("misc.topic_footer", locale=locale, id=id))
        embeds.append(embed)

        if not valid_topic:
            embed2, file = error_embed(
                self.bot,
                i18n.t("misc.topic_invalid_title", locale=locale),
                i18n.t("misc.topic_invalid", amount=len(questions), locale=locale),
                interaction.guild_id,
                style="warning",
            )
            embeds = [embed2, embed]
            files.append(file)

        await interaction.followup.send(embeds=embeds, files=files)
        if not valid_topic:
            await sleep(5)
            await interaction.edit_original_response(embed=embed, attachments=[])
