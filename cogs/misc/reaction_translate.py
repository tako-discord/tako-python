import i18n
import discord
from .flags import language_dict
from discord import app_commands
from discord.ext import commands
from utils import get_language, get_color, translate, thumbnail, delete_thumbnail


class ReactionTranslate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Disable or enable reaction translate")
    @app_commands.describe(value="Wheter to enable or disable reaction translate")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def reaction_translate(self, interaction: discord.Interaction, value: bool):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, reaction_translate) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET reaction_translate = $2",
            interaction.guild.id,
            value,
        )
        return await interaction.response.send_message(
            i18n.t(
                f"misc.reaction_translate_{'activated' if value else 'deactivated'}",
                locale=get_language(self.bot, interaction.guild.id),
            )
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        state = await self.bot.db_pool.fetchval(
            "SELECT reaction_translate FROM guilds WHERE guild_id = $1",
            payload.guild_id,
        )
        try:
            if not state or not language_dict[payload.emoji.name] or payload.member.bot:
                return
        except KeyError:
            return

        message: discord.Message = await self.bot.get_channel(
            payload.channel_id
        ).fetch_message(payload.message_id)
        language = language_dict[payload.emoji.name]
        translation = await translate(message.content, language)

        if not message.content:
            return

        thumbnail_path = await thumbnail(payload.guild_id, "translation", self.bot)
        file = discord.File(thumbnail_path, filename="thumbnail.png")

        embed = discord.Embed(
            description=translation, color=await get_color(self.bot, payload.guild_id)
        )
        embed.set_author(
            name=message.author.display_name, icon_url=message.author.avatar.url
        )
        embed.set_footer(
            text=i18n.t(
                "misc.reaction_translate_footer",
                locale=get_language(self.bot, payload.guild_id),
                user=payload.member.display_name,
            )
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")

        await message.reply(embed=embed, mention_author=False, file=file)
        await delete_thumbnail(payload.guild_id, "translation")
