import i18n
import discord
from TakoBot import TakoBot
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from utils import get_language, get_color


class ClearAll(discord.ui.View):
    def __init__(self, bot, channel: discord.TextChannel):
        super().__init__()
        self.bot = bot
        self.channel = channel

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message(
            i18n.t(
                "moderation.deleting",
                locale=get_language(self.bot, interaction.guild.id),
            ),
            ephemeral=True,
        )
        channel = self.channel
        await interaction.guild.create_text_channel(
            name=channel.name,
            position=channel.position,
            category=channel.category,
            topic=channel.topic,
            slowmode_delay=channel.slowmode_delay,
            nsfw=channel.nsfw,
            overwrites=channel.overwrites,
            default_auto_archive_duration=channel.default_auto_archive_duration,
        )
        await channel.delete()
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            i18n.t(
                "moderation.cancelled",
                locale=get_language(self.bot, interaction.guild.id),
            ),
            ephemeral=True,
        )
        self.stop()


class Clear(commands.Cog):
    def __init__(self, bot: TakoBot):
        self.bot = bot

    @app_commands.command(description="Delete multiple messages at once")
    @app_commands.describe(
        amount="The amount of messages to be deleted (0 to delete every message)",
        target="The user to delete the messages from",
        channel="The channel to delete the messages from",
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.checks.bot_has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: int = 1,
        target: discord.User | discord.Member = None,
        channel: discord.TextChannel = None,
    ):
        await interaction.response.defer(ephemeral=True)
        language = get_language(self.bot, interaction.guild.id)
        if not channel:
            channel = interaction.channel
        if amount == 0:
            embed = discord.Embed(
                title=i18n.t(
                    "moderation.sure_to_delete", channel=channel.name, locale=language
                ),
                color=await get_color(self.bot, interaction.guild.id),
            )
            return await interaction.followup.send(
                embed=embed, view=ClearAll(self.bot, channel)
            )
        too_many_messages = False
        if amount > 100:
            amount = 100
            too_many_messages_file = discord.File(
                "assets/warning.png", filename="warning.png"
            )
            too_many_messages_embed = discord.Embed(
                title=f"**{i18n.t('moderation.too_many_messages_title', locale=language)}**",
                description=i18n.t("moderation.too_many_messages", locale=language),
                color=discord.Color.yellow(),
                timestamp=datetime.now(),
            )
            too_many_messages_embed.set_thumbnail(url="attachment://warning.png")
            too_many_messages_embed.set_footer(
                text=i18n.t("errors.warning", locale=language)
            )
            too_many_messages = True
        if not target:
            await interaction.channel.purge(
                limit=amount,
                reason=i18n.t(
                    "moderation.clear_reason", user=interaction.user, locale=language
                ),
            )
        else:
            messages = []
            message_count = 0
            async for msg in channel.history(limit=None):
                if message_count == amount:
                    break
                if msg.author.id == target.id:
                    messages += [msg]
                    message_count += 1
            await interaction.channel.delete_messages(
                messages=messages,
                reason=i18n.t(
                    "moderation.clear_reason", user=interaction.user, locale=language
                ),
            )
        embed = discord.Embed(
            description=i18n.t(
                f"moderation.cleared{'_target' if target else ''}",
                amount=amount,
                channel=channel.mention,
                target=str(target),
                locale=language,
            ),
            color=discord.Color.red(),
            timestamp=datetime.utcnow(),
        )
        embed.set_author(
            name=str(interaction.user),
            url=f"https://discord.com/user/{interaction.user.id}",
            icon_url=interaction.user.display_avatar.url,
        )
        file = discord.File("assets/trash.png", filename="trash.png")
        embed.set_thumbnail(url="attachment://trash.png")
        embeds = [embed]
        files = [file]
        if too_many_messages:
            embeds.append(too_many_messages_embed)
            files.append(too_many_messages_file)
        await interaction.followup.send(embeds=embeds, files=files)
        return
