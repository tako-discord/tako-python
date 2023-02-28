import i18n
import discord
from TakoBot import TakoBot
from datetime import datetime
from .flags import language_dict
from discord import app_commands
from discord.ext import commands
from utils import get_language, get_color, translate, error_embed


class ReactionTranslate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Disable or enable reaction translate")
    @app_commands.describe(value="Wheter to enable or disable reaction translate")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def reaction_translate(self, interaction: discord.Interaction, value: bool):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, reaction_translate) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET reaction_translate = $2",
            interaction.guild_id,
            value,
        )
        return await interaction.response.send_message(
            i18n.t(
                f"misc.reaction_translate_{'activated' if value else 'deactivated'}",
                locale=get_language(self.bot, interaction.guild_id),
            )
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        self.bot: TakoBot = self.bot
        language = get_language(self.bot, payload.guild_id)

        async with self.bot.db_pool.acquire() as conn:
            async with conn.transaction():
                state = await self.bot.db_pool.fetchval(
                    "SELECT reaction_translate FROM guilds WHERE guild_id = $1",
                    payload.guild_id,
                )
                last_reaction_translation = await self.bot.db_pool.fetchval(
                    "SELECT last_reaction_translation FROM users WHERE user_id = $1",
                    payload.user_id,
                )
                last_reaction_translation = (
                    datetime.now() - last_reaction_translation
                    if last_reaction_translation
                    else None
                )
        try:
            if not state or not language_dict[payload.emoji.name] or payload.member.bot:  # type: ignore
                return
        except KeyError:
            return
        cooldown = 10
        if (
            last_reaction_translation
            and last_reaction_translation.total_seconds() < cooldown
        ):
            embed, file = error_embed(
                self.bot,
                i18n.t("errors.cooldown_title", locale=language),
                i18n.t(
                    "errors.reaction_translate_cooldown",
                    locale=language,
                    time=round(cooldown - last_reaction_translation.total_seconds()),
                ),
                payload.guild_id,
            )
            try:
                await payload.member.send(embed=embed, file=file)  # type: ignore
            except discord.Forbidden:
                pass
            return
        channel = await self.bot.fetch_channel(payload.channel_id)
        if not channel.permissions_for(payload.member).send_messages:  # type: ignore
            return

        message: discord.Message = await self.bot.get_channel(
            payload.channel_id
        ).fetch_message( # type: ignore

            payload.message_id
        )
        try:
            language = language_dict[payload.emoji.name]
        except KeyError:
            return
        translation = (await translate(message.content, language))[0]

        if not message.content:
            return

        embed = discord.Embed(
            description=translation, color=await get_color(self.bot, payload.guild_id)  # type: ignore
        )
        embed.set_author(
            name=message.author.display_name, icon_url=message.author.display_avatar.url
        )
        embed.set_footer(
            text=i18n.t(
                "misc.reaction_translate_footer",
                locale=language,
                user=payload.member,
            )
        )

        await self.bot.db_pool.execute(
            "INSERT INTO users(user_id, last_reaction_translation) VALUES($1, $2) ON CONFLICT(user_id) DO UPDATE SET user_id = $1, last_reaction_translation = $2",
            payload.user_id,
            datetime.now(),
        )
        await message.reply(embed=embed, mention_author=False)
