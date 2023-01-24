import i18n
import config
import discord
from random import randint
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from utils import get_color, get_language, thumbnail


class ImageGen(commands.GroupCog, group_name="image"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Put a flag behind an avatar")
    @app_commands.describe(
        type="The flag to use", user="The avatar to use (Default: Your Avatar)"
    )
    @app_commands.choices(
        type=[
            Choice(name="Rainbow (Default)", value="lgbtq"),
            Choice(name="Agender", value="agender"),
            Choice(name="Ally", value="ally"),
            Choice(name="Aromantic", value="aromantic"),
            Choice(name="Asexual", value="asexual"),
            Choice(name="Bisexual", value="bi"),
            Choice(name="Butch Lesbian", value="butch-lesbian"),
            Choice(name="Demiromantic", value="demiromantic"),
            Choice(name="Demisexual", value="demisexual"),
            Choice(name="Genderfluid", value="genderfluid"),
            Choice(name="Genderqueer", value="genderqueer"),
            Choice(name="Intersex", value="intersex"),
            Choice(name="Labrys Lesbian", value="labrys-lesbian"),
            Choice(name="Lesbian", value="lesbian"),
            Choice(name="Non-Binary", value="non-binary"),
            Choice(name="Pansexual", value="pan"),
            Choice(name="Polyamorous", value="polyamorous"),
            Choice(name="Polysexual", value="polysexual"),
            Choice(name="Progress", value="progress"),
            Choice(name="Transgender", value="trans"),
        ]
    )
    async def lgbtq(
        self,
        interaction: discord.Interaction,
        type: str = "lgbtq",
        user: discord.User | discord.Member | None = None,
    ):
        if user is None:
            user = interaction.user

        language = get_language(self.bot, interaction.guild_id)
        thumb = await thumbnail(interaction.guild_id, "flag", self.bot)
        thumb = discord.File(thumb, "thumbnail.png")
        embed = discord.Embed(
            color=await get_color(self.bot, interaction.guild.id),  # type: ignore
            title="LGBTQ+ Avatar",
            description=i18n.t("misc.lgbtq_tip", locale=language)
            + f"\n\n{i18n.t('misc.no_gif_support', locale=language)}"
            if user.display_avatar.is_animated
            else "",
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")
        embed.set_image(
            url=f"{config.IMGEN}/pride?type={type}&avatar={user.display_avatar.replace(size=512, format='png').url}"
        )
        return await interaction.response.send_message(embed=embed, file=thumb)

    @app_commands.command(description="Put jail bars over an avatar (Black & White)")
    @app_commands.describe(user="The avatar to use (Default: Your Avatar)")
    async def jail(
        self,
        interaction: discord.Interaction,
        user: discord.User | discord.Member | None = None,
    ):
        if user is None:
            user = interaction.user

        language = get_language(self.bot, interaction.guild_id)
        rand = randint(1, 100)
        new_rand = 1
        if rand <= 70:
            new_rand = 2
        if rand <= 50:
            new_rand = 3
        if rand <= 20:
            new_rand = 4
        if rand == 1:
            new_rand = 5
        embed = discord.Embed(
            color=await get_color(self.bot, interaction.guild_id),  # type: ignore
            title=f"{str(user)} is now in jail!",
            description=i18n.t(
                f"misc.jail_desc_{new_rand}",
                user=user.display_name,
                officer=interaction.user.display_name,
                locale=language,
            ),
        )
        embed.set_image(
            url=f"{config.IMGEN}/jail?avatar={user.display_avatar.replace(size=512, format='png').url}"
        )
        return await interaction.response.send_message(embed=embed)

    #
    # @app_commands.describe(prompt="The prompt to generate an image from")
    # @app_commands.command(description="Generate an image using Craiyon (Formerly known as Dall-E Mini)")
    # async def craiyon(self, interaction: discord.Interaction, prompt: str):
    #     embed1 = discord.Embed(title="Generating...", description="This might take up to 2 minutes", color=await get_color(self.bot, interaction.guild_id)) # type: ignore
    #     await interaction.response.send_message(embed=embed1)

    #     generator = Craiyon()
    #     result = await generator.async_generate(prompt)
    #     if not result:
    #         embed2 = discord.Embed(title="Error", description="An error occured while generating the image", color=await get_color(self.bot, interaction.guild_id)) # type: ignore
    #         return await interaction.response.edit_message(embed=embed2)
    #     files = []
    #     for i in result.images: # type: ignore
    #         image = base64.decodebytes(i.encode("utf-8"))
    #         files.append(discord.File(image))
    #     embed3 = discord.Embed(title="Generated Image", description=prompt, color=await get_color(self.bot, interaction.guild_id)) # type: ignore
    #     await interaction.response.edit_message(embed=embed3, attachments=files)
    #
    #
