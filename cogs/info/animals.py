import i18n
import discord
import aiohttp
from typing import TypedDict
from discord import app_commands
from discord.ext import commands
from typings.apis import SomeRandomApi
from discord.app_commands import Choice
from utils import error_embed, get_language, translate, get_color


class Animals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Get a random animal image and fact")
    @app_commands.describe(
        animal=[
            Choice("Bird", "bird"),
            Choice("Cat", "cat"),
            Choice("Dog", "dog"),
            Choice("Fox", "fox"),
            Choice("Kangaroo", "kangaroo"),
            Choice("Koala", "koala"),
            Choice("Panda", "panda"),
            Choice("Racoon", "raccoon"),
            Choice("Red Panda", "red_panda"),
        ]
    )
    @app_commands.choices()
    async def animal(self, interaction: discord.Interaction, animal: str):
        url = "https://some-random-api.ml/animal/" + animal
        locale = get_language(self.bot, interaction.guild_id)

        # Initialize the session
        async with aiohttp.ClientSession() as session:
            # Make the request
            async with session.get(url) as response:
                # If not successful, return an error embed
                if not response.status == 200:
                    embed, file = error_embed(
                        self.bot,
                        i18n.t("error.api_error_title", locale=locale),
                        i18n.t(
                            "error.api_error",
                            locale=locale,
                            error=f"SRA ANIMAL: {response.status} {response.reason} ({url})",
                        ),
                        interaction.guild_id,
                    )
                    await interaction.response.send_message(embed=embed, file=file)
                    return

                # Convert the data to a dictionary
                data: SomeRandomApi.Animal = await response.json()
                # Response
                embed = discord.Embed(
                    title=f"{animal.title()}",
                    description=data["fact"],
                    color=await get_color(self.bot, interaction.guild_id),
                )
                embed.set_image(url=data["image"])
                await interaction.response.send_message(embed=embed)
