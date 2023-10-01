import io
import os
import i18n
import json
import discord
from main import TakoBot
from ftlangdetect import detect
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from utils import get_language, translate, error_embed


class AutoTranslate(commands.GroupCog, name="auto_translate"):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Disable or enable auto translate")
    @app_commands.describe(value="Whether to enable or disable auto translate")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def toggle(self, interaction: discord.Interaction, value: bool):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, auto_translate) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET auto_translate = $2",
            interaction.guild_id,
            value,
        )
        return await interaction.response.send_message(
            i18n.t(
                f"misc.auto_translate_{'activated' if value else 'deactivated'}",
                locale=get_language(self.bot, interaction.guild_id),
            ),
            ephemeral=True,
        )

    @app_commands.command(description="Set the style of the auto translated message")
    @app_commands.describe(style="The style of the auto translated message")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.choices(
        style=[
            Choice(name="Default", value="default"),
            Choice(name="Webhook", value="webhook"),
            Choice(name="Minimal Webhook", value="min_webhook"),
        ]
    )
    @app_commands.guild_only()
    async def style(self, interaction: discord.Interaction, style: str):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, auto_translate_reply_style) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET auto_translate_reply_style = $2",
            interaction.guild_id,
            style,
        )
        return await interaction.response.send_message(
            i18n.t(
                "misc.auto_translate_reply_style_set",
                style=style,
                locale=get_language(self.bot, interaction.guild_id),
            ),
            ephemeral=True,
        )

    @app_commands.command(
        description="Adjust the confidence threshold for auto translate"
    )
    @app_commands.describe(value="The confidence threshold for auto translate.")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def sensitivity(
        self, interaction: discord.Interaction, value: app_commands.Range[int, 0, 100]
    ):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, auto_translate_confidence) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET auto_translate_confidence = $2;",
            interaction.guild_id,
            value,
        )
        return await interaction.response.send_message(
            i18n.t(
                "misc.auto_translate_confidence_set",
                value=value,
                locale=get_language(self.bot, interaction.guild_id),
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
            interaction.guild_id,
            value,
        )
        return await interaction.response.send_message(
            i18n.t(
                "misc.auto_translate_delete_original",
                value=value,
                locale=get_language(self.bot, interaction.guild_id),
            ),
            ephemeral=True,
        )

    # TODO: Add descriptions to command and arguments
    @app_commands.command()
    @app_commands.guild_only()
    async def link(
        self,
        interaction: discord.Interaction,
        source_channel: discord.TextChannel | discord.Thread,
        target_channel: discord.TextChannel | discord.Thread,
        source_lang: str = "auto",
        target_lang: str | None = None,
    ):
        if source_lang == target_lang:
            return await interaction.response.send_message(
                i18n.t(
                    "errors.auto_translate_same_lang",
                    locale=get_language(self.bot, interaction.guild_id),
                ),
                ephemeral=True,
            )
        if source_channel == target_channel:
            return await interaction.response.send_message(
                i18n.t(
                    "errors.auto_translate_same_channel",
                    locale=get_language(self.bot, interaction.guild_id),
                ),
                ephemeral=True,
            )
        data = await self.bot.db_pool.fetchval(
            "SELECT autotranslate_link FROM channels WHERE channel_id = $1",
            source_channel.id,
        )
        if not data:
            data = []
        link_data = {
            "target_channel": target_channel.id,
            "source_lang": source_lang,
            "target_lang": target_lang,
        }
        if link_data in data:
            return await interaction.response.send_message(
                i18n.t(
                    "errors.auto_translate_link_exists",
                    locale=get_language(self.bot, interaction.guild_id),
                ),
                ephemeral=True,
            )
        data.append(json.dumps(link_data))
        await self.bot.db_pool.execute(
            "INSERT INTO channels (channel_id, autotranslate_link) VALUES ($1, $2) ON CONFLICT(channel_id) DO UPDATE SET autotranslate_link = $2",
            source_channel.id,
            data,
        )
        await interaction.response.send_message(
            i18n.t(
                "misc.auto_translate_linked",
                locale=get_language(self.bot, interaction.guild_id),
                source_channel=source_channel.mention,
                source_lang=source_lang,
                target_channel=target_channel.mention,
                target_lang=target_lang,
            ),
            ephemeral=True,
        )

    # TODO: Add command to delete links

    @commands.Cog.listener(name="on_message")
    async def on_message_link(self, message: discord.Message):
        try:
            fetched_val = await self.bot.db_pool.fetchval(
                "SELECT autotranslate_link FROM channels WHERE channel_id = $1",
                message.channel.id,
            )
        except AttributeError:
            return
        if not fetched_val:
            return
        for autotranslate_link in fetched_val:
            if (
                not message.content
                or not autotranslate_link
                or message.author.id == self.bot.user.id  # type: ignore
                or message.webhook_id
                or not message.guild
            ):
                continue

            data = json.loads(autotranslate_link)
            source_lang = data["source_lang"]
            target_lang = data["target_lang"]
            target_channel: discord.abc.GuildChannel | discord.Thread = self.bot.get_channel(data["target_channel"])  # type: ignore
            if target_channel == discord.abc.PrivateChannel:
                continue

            attachments: list[dict] = []
            if message.attachments:
                for attachment in message.attachments:
                    bytes = await attachment.read()
                    attachments.append(
                        {
                            "bytes": bytes,
                            "spoiler": attachment.is_spoiler(),
                            "filename": attachment.filename,
                            "description": attachment.description,
                        }
                    )
            size = 0
            boost_level = message.guild.premium_tier if hasattr(message, "guild") else 0
            size_limit = 8000000
            match boost_level:
                case 2:
                    size_limit = 50000000
                case 3:
                    size_limit = 100000000
            new_attachments = []
            attachment_removed = False
            for attachment in attachments:
                file_size = len(attachment["bytes"])
                size += file_size
                if size > size_limit:
                    size -= file_size
                    attachment_removed = True
                    continue
                attachment_bytes = io.BytesIO(attachment["bytes"])
                new_attachments.append(
                    discord.File(
                        attachment_bytes,
                        spoiler=attachment["spoiler"],
                        filename=attachment["filename"],
                        description=attachment["description"],
                    )
                )
            attachments = new_attachments
            too_large_embed, too_large_file = error_embed(
                self.bot,
                i18n.t("errors.too_large_title", locale=source_lang),
                i18n.t("errors.too_large", locale=source_lang),
                message.guild.id,
                style="warning",
            )

            data = await detect(
                message.content.replace("\n", " "),
                path=os.path.join(os.getcwd(), "assets/lid.176.bin"),
            )
            data["score"] = data["score"] * 100
            confidence = await self.bot.db_pool.fetchval(
                "SELECT auto_translate_confidence FROM guilds WHERE guild_id = $1",
                message.guild.id,
            )
            if not confidence:
                confidence = 75
            if confidence >= data["score"]:
                return
            if data["lang"] != source_lang:
                return

            webhook_id = None
            if (
                target_channel.type == discord.ChannelType.public_thread
                or target_channel.type == discord.ChannelType.private_thread
            ):
                for webhook in await target_channel.parent.webhooks():  # type: ignore
                    if webhook.name == f"AutoTranslate ({self.bot.user.id})":  # type: ignore
                        webhook_id = webhook.id
            else:
                for webhook in await target_channel.webhooks():  # type: ignore
                    if webhook.name == f"AutoTranslate ({self.bot.user.id})":  # type: ignore
                        webhook_id = webhook.id
            if not webhook_id:
                if (
                    target_channel.type == discord.ChannelType.public_thread
                    or target_channel.type == discord.ChannelType.private_thread
                ):
                    webhook = await target_channel.parent.create_webhook(name=f"AutoTranslate ({self.bot.user.id})")  # type: ignore
                else:
                    webhook = await target_channel.create_webhook(name=f"AutoTranslate ({self.bot.user.id})")  # type: ignore
            else:
                webhook = await self.bot.fetch_webhook(webhook_id)

            translation = await translate(message.content, target_lang, source_lang)
            try:
                await webhook.send(
                    username=f"{message.author.display_name} ({translation[1]} ➜ {target_lang})",
                    avatar_url=message.author.display_avatar.url,
                    files=attachments,  # type: ignore
                    thread=target_channel if isinstance(target_channel, discord.Thread) else discord.utils.MISSING,  # type: ignore
                    content=translation[0],
                )
            except:
                continue

            if attachment_removed:
                await message.channel.send(
                    message.author.mention,
                    embed=too_large_embed,
                    file=too_large_file,
                    allowed_mentions=discord.AllowedMentions(
                        everyone=False,
                        users=[message.author],
                        roles=False,
                        replied_user=False,
                    ),
                )
            continue

    @commands.Cog.listener(name="on_message")
    async def on_message_autotranslate(self, message: discord.Message):
        if not message.guild:
            return
        try:
            state = await self.bot.db_pool.fetchval(
                "SELECT auto_translate FROM guilds WHERE guild_id = $1",
                message.guild.id,
            )
        except AttributeError:
            return
        if (
            not message.content
            or not state
            or message.author.id == self.bot.user.id  # type: ignore
            or message.webhook_id
        ):
            return
        attachments: list[dict] = []
        if message.attachments:
            for attachment in message.attachments:
                bytes = await attachment.read()
                attachments.append(
                    {
                        "bytes": bytes,
                        "spoiler": attachment.is_spoiler(),
                        "filename": attachment.filename,
                        "description": attachment.description,
                    }
                )
        size = 0
        boost_level = message.guild.premium_tier if hasattr(message, "guild") else 0
        size_limit = 8000000
        match boost_level:
            case 2:
                size_limit = 50000000
            case 3:
                size_limit = 100000000
        new_attachments = []
        attachment_removed = False
        for attachment in attachments:
            file_size = len(attachment["bytes"])
            size += file_size
            if size > size_limit:
                size -= file_size
                attachment_removed = True
                continue
            attachment_bytes = io.BytesIO(attachment["bytes"])
            new_attachments.append(
                discord.File(
                    attachment_bytes,
                    spoiler=attachment["spoiler"],
                    filename=attachment["filename"],
                    description=attachment["description"],
                )
            )
        attachments = new_attachments

        data = await detect(
            message.content.replace("\n", " "),
            path=os.path.join(os.getcwd(), "assets/lid.176.bin"),
        )
        data["score"] = data["score"] * 100
        confidence = await self.bot.db_pool.fetchval(
            "SELECT auto_translate_confidence FROM guilds WHERE guild_id = $1",
            message.guild.id,
        )
        if confidence >= data["score"]:
            return
        reply_style = await self.bot.db_pool.fetchval(
            "SELECT auto_translate_reply_style FROM guilds WHERE guild_id = $1",
            message.guild.id,
        )
        delete_original = await self.bot.db_pool.fetchval(
            "SELECT auto_translate_delete_original FROM guilds WHERE guild_id = $1",
            message.guild.id,
        )
        guild_language = get_language(self.bot, message.guild.id)
        too_large_embed, too_large_file = error_embed(
            self.bot,
            i18n.t("errors.too_large_title", locale=guild_language),
            i18n.t("errors.too_large", locale=guild_language),
            message.guild.id,
            style="warning",
        )
        webhook_id = None
        if (
            message.channel.type == discord.ChannelType.public_thread
            or message.channel.type == discord.ChannelType.private_thread
        ):
            for webhook in await message.channel.parent.webhooks():  # type: ignore
                if webhook.name == f"AutoTranslate ({self.bot.user.id})":  # type: ignore
                    webhook_id = webhook.id
        else:
            for webhook in await message.channel.webhooks():  # type: ignore
                if webhook.name == f"AutoTranslate ({self.bot.user.id})":  # type: ignore
                    webhook_id = webhook.id
        if not webhook_id:
            if (
                message.channel.type == discord.ChannelType.public_thread
                or message.channel.type == discord.ChannelType.private_thread
            ):
                webhook = await message.channel.parent.create_webhook(name=f"AutoTranslate ({self.bot.user.id})")  # type: ignore
            else:
                webhook = await message.channel.create_webhook(name=f"AutoTranslate ({self.bot.user.id})")  # type: ignore
        else:
            webhook = await self.bot.fetch_webhook(webhook_id)
        if data["lang"] != guild_language:
            translation = await translate(message.content, guild_language)
            if not translation:
                return
            if translation[0].lower() == message.content.lower():
                return
            try:
                match reply_style:
                    case "webhook":
                        await webhook.send(
                            username=f"{message.author.display_name} ({translation[1]} ➜ {guild_language})",
                            avatar_url=message.author.display_avatar.url,
                            files=attachments,  # type: ignore
                            thread=message.channel if isinstance(message.channel, discord.Thread) else discord.utils.MISSING,  # type: ignore
                            embed=discord.Embed(
                                description=translation[0],
                                color=0x2F3136,
                            ).set_footer(
                                text=f"Confidence: {round(data['score'])}%"  # type: ignore
                            ),
                        )
                        if delete_original or delete_original is None:
                            await message.delete()
                            if attachment_removed:
                                await message.channel.send(
                                    message.author.mention,
                                    embed=too_large_embed,
                                    file=too_large_file,
                                    allowed_mentions=discord.AllowedMentions(
                                        everyone=False,
                                        users=[message.author],
                                        roles=False,
                                        replied_user=False,
                                    ),
                                )
                            return
                        if attachment_removed:
                            await message.reply(
                                embed=too_large_embed,
                                file=too_large_file,
                                mention_author=True,
                            )
                    case "min_webhook":
                        await webhook.send(
                            username=f"{message.author.display_name} ({translation[1]} ➜ {guild_language})",
                            avatar_url=message.author.display_avatar.url,
                            files=attachments,  # type: ignore
                            thread=message.channel if isinstance(message.channel, discord.Thread) else discord.utils.MISSING,  # type: ignore
                            content=translation[0],
                            allowed_mentions=discord.AllowedMentions.none(),
                        )
                        if delete_original:
                            await message.delete()
                            if attachment_removed:
                                await message.channel.send(
                                    message.author.mention,
                                    embed=too_large_embed,
                                    file=too_large_file,
                                    allowed_mentions=discord.AllowedMentions(
                                        everyone=False,
                                        users=[message.author],
                                        roles=False,
                                        replied_user=False,
                                    ),
                                )
                            return
                        if attachment_removed:
                            await message.reply(
                                embed=too_large_embed,
                                file=too_large_file,
                                mention_author=True,
                            )
                    case _:
                        if delete_original:
                            await message.channel.send(
                                f"{message.author.mention}:\n> "
                                + (translation[0]).replace("\n", "\n> "),
                                allowed_mentions=discord.AllowedMentions.none(),
                                files=attachments,  # type: ignore
                            )
                            if attachment_removed:
                                await message.channel.send(
                                    message.author.mention,
                                    embed=too_large_embed,
                                    file=too_large_file,
                                    allowed_mentions=discord.AllowedMentions(
                                        everyone=False,
                                        users=[message.author],
                                        roles=False,
                                        replied_user=False,
                                    ),
                                )
                            await message.delete()
                            return
                        await message.reply(
                            "> " + (translation[0]).replace("\n", "\n> "),
                            allowed_mentions=discord.AllowedMentions.none(),
                            mention_author=False,
                            files=attachments,
                        )
                        if attachment_removed:
                            await message.reply(
                                embed=too_large_embed,
                                file=too_large_file,
                                mention_author=True,
                            )
            except discord.Forbidden:
                return
