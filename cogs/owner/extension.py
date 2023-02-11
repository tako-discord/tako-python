import i18n
import discord
from discord import app_commands
from discord.ext import commands
from utils import add_extension, error_embed, get_language


class Extension(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.is_owner()
    @commands.hybrid_group()
    async def extension(self, ctx: commands.Context):
        return ctx.send(
            "Please use a subcommand.\nRun `k!help extension` for more information."
        )

    @commands.is_owner()
    @extension.command(description="Add an extension from Git")
    @app_commands.describe(url="The url of the repository to add")
    async def add(self, ctx: commands.Context, url: str):
        installing = discord.Embed(
            title="📥 Installing",
            description=f"Installing [the extension]({url})...\nThis may take a while depending on the extension's size",
            color=discord.Color.light_gray(),
        )
        msg = await ctx.send(embed=installing, ephemeral=True)
        adder = add_extension(url)
        if adder == 0:
            embed = discord.Embed(
                title="✅ Installed",
                description=f"[The extension]({url}) has been installed!",
                color=discord.Color.green(),
            )
        if adder == 1:
            embed = discord.Embed(
                title="❌ Invalid url",
                description=f"[The extension]({url}) could not be installed!",
                color=discord.Color.red(),
            )
        if adder != 0 or adder != 1:
            embed = discord.Embed(
                title="❌ Unknown error",
                description=f"[The extension]({url}) could not be installed!",
                color=discord.Color.red(),
            )
        await msg.edit(embed=embed)

    @commands.is_owner()
    @extension.command(description="Reload a specific extension")
    @app_commands.describe(extension="The extension to reload")
    async def reload(self, ctx, extension: str):
        await self.bot.reload_extension(f"cogs.{extension.lower()}")
        embed = discord.Embed(
            title="Reload",
            description=f"Category `{extension.lower()}` successfully reloaded",
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed, ephemeral=True)

    @add.error
    @reload.error
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.NotOwner):
            language = get_language(self.bot, ctx.guild.id if ctx.guild else None)
            embed, file = error_embed(
                i18n.t("errors.not_owner_title", locale=language),
                i18n.t("errors.not_owner", locale=language),
                footer=i18n.t("errors.error_occured", locale=language),
            )
            return await ctx.reply(embed=embed, file=file, ephemeral=True)
