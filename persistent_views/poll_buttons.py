import json
import discord
from uuid import UUID
from utils import poll_embed


class PollButtons(discord.ui.View):
    def __init__(self, uuid: UUID, question: str, answers: list[str], bot):
        super().__init__(timeout=None)

        for answer in answers:
            self.add_item(self.PollButton(uuid, question, answer, answers, bot))

    class PollButton(discord.ui.Button):
        def __init__(
            self, uuid: UUID, question: str, answer: str, answers: list[str], bot
        ):
            super().__init__(label=answer, custom_id=answer)
            self.uuid = uuid
            self.question = question
            self.answer = answer
            self.answers = answers
            self.bot = bot

        async def callback(self, interaction: discord.Interaction):
            async with self.bot.db_pool.acquire() as conn:
                async with conn.transaction():
                    data = (
                        await conn.fetch("SELECT * FROM polls WHERE id = $1", self.uuid)
                    )[0]
                    votes = json.loads(data["votes"])

                    if interaction.user.id in votes:
                        if votes[interaction.user.id] == self.answer:
                            return
                    votes[interaction.user.id] = self.answer
                    votes = json.dumps(votes)
                    await conn.execute(
                        "UPDATE polls SET votes = $1 WHERE id = $2", votes, self.uuid
                    )

            embed = await poll_embed(
                self.question,
                self.answers,
                votes,
                self.bot,
                interaction.guild_id,
                self.uuid,
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
