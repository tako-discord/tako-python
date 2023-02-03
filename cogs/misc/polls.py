import json
import discord
from uuid import uuid4
from utils import poll_embed
from discord import app_commands
from discord.ext import commands
from persistent_views.poll_buttons import PollButtons


class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Create a poll")
    @app_commands.describe(
        question="The question to ask",
    )
    @app_commands.guild_only()
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        answer1: str,
        answer2: str,
        answer3: str | None = None,
        answer4: str | None = None,
        answer5: str | None = None,
        answer6: str | None = None,
        answer7: str | None = None,
        answer8: str | None = None,
        answer9: str | None = None,
        answer10: str | None = None,
    ):
        if not interaction.guild_id:
            return
        answers = [
            answer1,
            answer2,
            answer3,
            answer4,
            answer5,
            answer6,
            answer7,
            answer8,
            answer9,
            answer10,
        ]
        new_answers = []
        for answer in answers:
            if answer:
                new_answers.append(answer)
        answers = new_answers
        votes = json.dumps({})

        uuid = uuid4()
        await self.bot.db_pool.execute(
            "INSERT INTO polls (id, question, answers, votes, owner) VALUES ($1, $2, $3, $4, $5)",
            uuid,
            question,
            answers,
            votes,
            interaction.user.id,
        )
        embed = await poll_embed(
            question, answers, votes, self.bot, interaction.guild_id
        )

        await interaction.response.send_message(
            embed=embed, view=PollButtons(uuid, question, answers, self.bot, interaction.user.id)
        )
