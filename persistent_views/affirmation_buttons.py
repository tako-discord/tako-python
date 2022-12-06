import discord
import aiohttp


class AffirmationButtons(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Another one",
        style=discord.ButtonStyle.blurple,
        emoji="❤️",
        custom_id="next_affirmation",
    )
    async def next_affirmation(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://affirmations.dev/") as r:
                data = await r.json()
                await interaction.response.edit_message(
                    content=data["affirmation"], view=self
                )
