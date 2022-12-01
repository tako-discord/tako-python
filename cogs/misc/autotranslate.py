import i18n
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from utils import get_language, translate


class AutoTranslate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(description="Disable or enable auto translate")
    @app_commands.describe(value="Wheter to enable or disable auto translate")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def auto_translate(self, interaction: discord.Interaction, value: bool):
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
            ephemeral=True
        )


    @app_commands.command(description="Adjust the confidence threshold for auto translate")
    @app_commands.describe(value="The confidence threshold for auto translate.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def auto_translate_confidence(self, interaction: discord.Interaction, value: app_commands.Range[int, 0, 100]):
        await self.bot.db_pool.execute(
            "INSERT INTO guilds (guild_id, auto_translate_confidence) VALUES ($1, $2) ON CONFLICT(guild_id) DO UPDATE SET auto_translate_confidence = $2;",
            interaction.guild.id,
            value,
        )
        return await interaction.response.send_message(i18n.t("misc.auto_translate_confidence_set", value=value, locale=get_language(self.bot, interaction.guild.id)), ephemeral=True)


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        state = await self.bot.db_pool.fetchval(
            "SELECT auto_translate FROM guilds WHERE guild_id = $1", message.guild.id
        )
        if not message.content or not state or message.author.id == self.bot.user.id:
            return

        headers = {
            "accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://translate.argosopentech.com/detect",
                data=f"q={message.content.replace('&', '%26')}",
                headers=headers,
            ) as r:
                data = await r.json()
                data = data[0]
                confidence = await self.bot.db_pool.fetchval("SELECT auto_translate_confidence FROM guilds WHERE guild_id = $1", message.guild.id)
                guild_language = get_language(self.bot, message.guild.id)
                if confidence >= data["confidence"]:
                    return
                if data["language"] != guild_language:
                    try:
                        await message.reply(
                            f"> {await translate(message.content, guild_language)}\n\n` {data['language']} ➜ {guild_language} | {round(data['confidence'])} `"
                        )
                    except discord.Forbidden:
                        return
