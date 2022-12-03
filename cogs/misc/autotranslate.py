import i18n
import aiohttp
import discord
import config
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from utils import get_language, translate


class AutoTranslate(commands.GroupCog, name="auto_translate"):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Disable or enable auto translate")
    @app_commands.describe(value="Whether to enable or disable auto translate")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle(self, interaction: discord.Interaction, value: bool):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, auto_translate) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET auto_translate = $2",
            interaction.guild.id,
            value,
        )
        return await interaction.response.send_message(
            i18n.t(
                f"misc.auto_translate_{'activated' if value else 'deactivated'}",
                locale=get_language(self.bot, interaction.guild.id),
            ),
            ephemeral=True,
        )

    @app_commands.command(description="Set the style of the auto translated message")
    @app_commands.describe(style="The style of the auto translated message")
    @app_commands.checks.has_permissions(manage_guild=True)
    @app_commands.choices(
        style=[
            Choice(name="Default", value="default"),
            Choice(name="Webhook", value="webhook"),
            Choice(name="Minimal Webhook", value="min_webhook"),
        ]
    )
    async def style(self, interaction: discord.Interaction, style: str):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, auto_translate_reply_style) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET auto_translate_reply_style = $2",
            interaction.guild.id,
            style,
        )
        return await interaction.response.send_message(
            i18n.t(
                "misc.auto_translate_reply_style_set",
                style=style,
                locale=get_language(self.bot, interaction.guild.id),
            ),
            ephemeral=True,
        )

    @app_commands.command(
        description="Adjust the confidence threshold for auto translate"
    )
    @app_commands.describe(value="The confidence threshold for auto translate.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def sensitivity(
        self, interaction: discord.Interaction, value: app_commands.Range[int, 0, 100]
    ):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, auto_translate_confidence) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET auto_translate_confidence = $2;",
            interaction.guild.id,
            value,
        )
        return await interaction.response.send_message(
            i18n.t(
                "misc.auto_translate_confidence_set",
                value=value,
                locale=get_language(self.bot, interaction.guild.id),
            ),
            ephemeral=True,
        )

    @app_commands.command(
        description="Toggle original message deletion for auto translate"
    )
    @app_commands.describe(value="Whether to delete the original message or not")
    async def delete_original(self, interaction: discord.Interaction, value: bool):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, auto_translate_delete_original) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET auto_translate_delete_original = $2;",
            interaction.guild.id,
            value,
        )
        return await interaction.response.send_message(
            i18n.t(
                "misc.auto_translate_delete_original",
                value=value,
                locale=get_language(self.bot, interaction.guild.id),
            ),
            ephemeral=True,
        )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        state = await self.bot.db_pool.fetchval(
            "SELECT auto_translate FROM guilds WHERE guild_id = $1", message.guild.id
        )
        if (
            not message.content
            or not state
            or message.author.id == self.bot.user.id
            or message.webhook_id
        ):
            return
        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{config.LIBRE_TRANSLATE}/detect",
                data=f"q={message.content.replace('&', '%26')}",
                headers=headers,
            ) as r:
                data = await r.json()
                data = data[0]
                confidence = await self.bot.db_pool.fetchval(
                    "SELECT auto_translate_confidence FROM guilds WHERE guild_id = $1",
                    message.guild.id,
                )
                reply_style = await self.bot.db_pool.fetchval(
                    "SELECT auto_translate_reply_style FROM guilds WHERE guild_id = $1",
                    message.guild.id,
                )
                delete_original = await self.bot.db_pool.fetchval(
                    "SELECT auto_translate_delete_original FROM guilds WHERE guild_id = $1",
                    message.guild.id,
                )
                guild_language = get_language(self.bot, message.guild.id)
                if confidence >= data["confidence"]:
                    return
                webhook_id = None
                for webhook in await message.channel.webhooks():
                    if webhook.name == "AutoTranslate":
                        webhook_id = webhook.id
                if not webhook_id:
                    webhook = await message.channel.create_webhook(
                        name="AutoTranslate"
                    )
                else:
                    webhook = await self.bot.fetch_webhook(webhook_id)
                if data["language"] != guild_language:
                    try:
                        match reply_style:
                            case "webhook":
                                await webhook.send(
                                    username=f"{message.author.display_name} ({data['language']} ➜ {guild_language})",
                                    avatar_url=message.author.display_avatar.url,
                                    embed=discord.Embed(
                                        description=await translate(
                                            message.content, guild_language
                                        ),
                                        color=0x2F3136,
                                    ).set_footer(
                                        text=f"Confidence: {round(data['confidence'])}%"
                                    ),
                                )
                                if delete_original or delete_original is None:
                                    await message.delete()
                            case "min_webhook":
                                await webhook.send(
                                    username=f"{message.author.display_name} ({data['language']} ➜ {guild_language})",
                                    avatar_url=message.author.display_avatar.url,
                                    content=await translate(
                                        message.content, guild_language
                                    ),
                                )
                                if delete_original:
                                    await message.delete()
                            case _:
                                if delete_original:
                                    await message.channel.send(
                                        f"{message.author.mention}:\n> "
                                        + (
                                            await translate(
                                                message.content, guild_language
                                            )
                                        ).replace("\n", "\n> ")
                                        + f"\n\n` {data['language']} ➜ {guild_language} | {round(data['confidence'])} `",
                                        allowed_mentions=discord.AllowedMentions.none(),
                                    )
                                    await message.delete()
                                    return
                                await message.reply(
                                    "> "
                                    + (
                                        await translate(message.content, guild_language)
                                    ).replace("\n", "\n> ")
                                    + f"\n\n` {data['language']} ➜ {guild_language} | {round(data['confidence'])} `",
                                    allowed_mentions=discord.AllowedMentions.none(),
                                    mention_author=False,
                                )
                    except discord.Forbidden:
                        return
