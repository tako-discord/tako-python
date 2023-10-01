import i18n
import discord
import bot_secrets
from main import TakoBot
from discord.ext import commands
from utils import error_embed, get_language


class Sync(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @commands.hybrid_command(description="Sync all slash commands")
    @commands.is_owner()
    async def sync(self, ctx):
        await ctx.defer(ephemeral=True)
        if hasattr(bot_secrets, "TEST_GUILD"):
            self.bot.tree.copy_global_to(
                guild=discord.Object(id=bot_secrets.TEST_GUILD)  # type: ignore
            )
            await self.bot.tree.sync(guild=discord.Object(id=bot_secrets.TEST_GUILD))  # type: ignore
        else:
            await self.bot.tree.sync()
        await ctx.followup.send("Successfully synced!", ephemeral=True)

    @sync.error
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.NotOwner):
            language = get_language(self.bot, ctx.guild.id if ctx.guild else None)
            embed, file = error_embed(
                self.bot,
                i18n.t("errors.not_owner_title", locale=language),
                i18n.t("errors.not_owner", locale=language),
                footer=i18n.t("errors.error_occured", locale=language),
            )
            return await ctx.reply(embed=embed, file=file, ephemeral=True)
