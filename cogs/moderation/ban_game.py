import i18n
import discord
from utils import get_language
from discord.ext import commands


class BanGame(commands.Cog):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @commands.hybrid_command(
        description="Automatically ban an user if they're playing a specific game"
    )
    @commands.has_guild_permissions(ban_members=True, manage_guild=True)
    @commands.bot_has_guild_permissions(ban_members=True)
    async def ban_game(self, ctx: commands.Context, game: str):
        game = game.lower()
        data = await self.bot.db_pool.fetchrow(
            "SELECT * FROM guilds WHERE guild_id = $1;", ctx.author.guild.id
        )
        if data is None:
            data = await self.bot.db_pool.execute(
                "INSERT INTO guilds (guild_id, banned_games) VALUES ($1, $2);",
                ctx.author.guild.id,
                [game],
            )
        else:
            array = data["banned_games"]
            if array is None:
                array = []
            if game not in array:
                array.append(game.lower())
                data = await self.bot.db_pool.execute(
                    "UPDATE guilds SET banned_games = $1 WHERE guild_id = $2",
                    array,
                    ctx.author.guild.id,
                )
                await ctx.reply(
                    f"✅ Added *{game}* to the banned games list",
                    ephemeral=True,
                    delete_after=5,
                )
                await ctx.message.delete(delay=5)
                return
            else:
                array.remove(game.lower())
                data = await self.bot.db_pool.execute(
                    "UPDATE guilds SET banned_games = $1 WHERE guild_id = $2",
                    array,
                    ctx.author.guild.id,
                )
                await ctx.reply(
                    f"🗑️ Removed *{game}* from the banned games list",
                    ephemeral=True,
                    delete_after=5,
                )
                await ctx.message.delete(delay=5)
                return

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        if before.bot:
            return
        if before.activities != after.activities:
            data = await self.bot.db_pool.fetchrow(
                "SELECT * FROM guilds WHERE guild_id = $1;", after.guild.id
            )
            if not data or not hasattr(data, "banned_games"):
                return
            for activity in after.activities:
                activity_name = activity
                if hasattr(activity, "name"):
                    activity_name = activity.name
                if activity_name.lower() in data["banned_games"]:
                    language = get_language(self.bot, after.guild.id)
                    try:
                        await after.ban(
                            reason=i18n.t(
                                "moderation.ban_game_log",
                                game=activity_name,
                                locale=language,
                            ),
                            delete_message_days=0,
                        )
                        await after.send(
                            i18n.t(
                                "moderation.ban_game_dm",
                                guild=after.guild.id,
                                game=activity_name,
                                locale=language,
                            )
                        )
                    except:
                        pass
