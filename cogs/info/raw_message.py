import i18n
import discord
from utils import get_language
from discord import app_commands
from discord.ext import commands


class RawMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Get Raw Message",
            callback=self.raw_message,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    async def raw_message(
        self, interaction: discord.Interaction, message: discord.Message
    ):
        language = get_language(self.bot, interaction.guild.id)
        if not message.content and not message.embeds:
            return await interaction.response.send_message(
                i18n.t("info.no_content", locale=language), ephemeral=True
            )
        if message.embeds:
            embed = i18n.t("info.embed", locale=language)
            embeds = [""]
            embed_count = 0
            for embed in message.embeds:
                embed_count += 1
                embeds.append(
                    f"{i18n.t('info.embed', count=embed_count, locale=language)}\n```\n{embed.description}```"
                )
            return await interaction.response.send_message(
                f"{i18n.t('info.message')} ```"
                + "\n"
                + message.content
                + "```"
                + "\n".join(embeds),
                ephemeral=True,
            )
        await interaction.response.send_message(
            "```" + "\n" + message.content + "```", ephemeral=True
        )
