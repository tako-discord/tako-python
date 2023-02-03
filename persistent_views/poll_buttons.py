import i18n
import json
import discord
from uuid import UUID
from utils import poll_embed, get_language


class PollButtons(discord.ui.View):
    def __init__(self, uuid: UUID, question: str, answers: list[str], bot, user_id: int | None = None):
        super().__init__(timeout=None)

        for answer in answers:
            self.add_item(self.PollButton(uuid, question, answer, answers, bot))
        if user_id:
            self.add_item(self.StopButton(uuid, question, answers, bot, user_id))

    class PollButton(discord.ui.Button):
        def __init__(
            self, uuid: UUID, question: str, answer: str, answers: list[str], bot
        ):
            super().__init__(label=answer, custom_id=str(bot.user.id)+"_poll_"+answer)
            self.uuid = uuid
            self.question = question
            self.answer = answer
            self.answers = answers
            self.bot = bot

        async def callback(self, interaction: discord.Interaction):
            if not interaction.guild_id:
                return
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
            )
            await interaction.response.edit_message(embed=embed, view=self.view)
            
    class StopButton(discord.ui.Button):
        def __init__(self, uuid: UUID, question: str, answers: list[str], bot, user_id: int):
            super().__init__(label="Stop", custom_id=str(bot.user.id)+"poll_stop", style=discord.ButtonStyle.red, row=4)
            self.uuid = uuid
            self.question = question
            self.answers = answers
            self.bot = bot
            self.user_id = user_id
            
        async def callback(self, interaction: discord.Interaction):
            if not interaction.guild_id:
                return
            if not interaction.user.id == self.user_id:
                await interaction.response.send_message(i18n.t("misc.poll_owner", locale=get_language(self.bot, interaction.guild_id)), ephemeral=True)
                return
            async with self.bot.db_pool.acquire() as conn:
                async with conn.transaction():
                    data = (
                        await conn.fetch("SELECT * FROM polls WHERE id = $1", self.uuid)
                    )[0]
            await self.bot.db_pool.execute("DELETE FROM polls WHERE id = $1", self.uuid)
            view = PollButtons(self.uuid, self.question, self.answers, self.bot, self.user_id)
            stop_index = len(view.children) - 1
            view.remove_item(view.children[stop_index])
            for item in view.children:
                item.disabled = True # type: ignore
            await interaction.response.edit_message(embed=(await poll_embed(self.question, self.answers, data["votes"], self.bot, interaction.guild_id)), view=view)
