import i18n
import config
import discord
from random import randint
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from utils import get_color, get_language, thumbnail


class Image(commands.GroupCog, group_name="image"):
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
        user: discord.User = None,
    ):
        if user is None:
            user = interaction.user

        language = get_language(self.bot, interaction.guild.id)
        thumb = await thumbnail(interaction.guild.id, "flag", self.bot)
        thumb = discord.File(thumb, "thumbnail.png")
        embed = discord.Embed(
            color=await get_color(self.bot, interaction.guild.id),
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
    async def jail(self, interaction: discord.Interaction, user: discord.User = None):
        if user is None:
            user = interaction.user

        language = get_language(self.bot, interaction.guild.id)
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
            color=await get_color(self.bot, interaction.guild.id),
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
