import i18n
import json
import discord
from utils import new_meme, thumbnail, get_color


class MemeButtons(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="Another one", style=discord.ButtonStyle.blurple, custom_id="next_meme"
    )
    async def next_meme(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        embed, file = await new_meme(
            interaction.guild.id, interaction.user.id, self.bot, self.bot.db_pool
        )

        await interaction.response.edit_message(
            embed=embed, attachments=[file], view=self
        )

    @discord.ui.button(
        label="Share it",
        style=discord.ButtonStyle.grey,
        custom_id="share_meme",
    )
    async def share_meme(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        data = await self.bot.db_pool.fetchval(
            "SELECT last_meme FROM users WHERE user_id = $1;", interaction.user.id
        )
        if not data:
            return await interaction.response.send_message(
                "We couldn't share this meme!", ephemeral=True
            )

        data = json.loads(data)
        thumbnail_path = await thumbnail(interaction.guild.id, "reddit", self)
        file = discord.File(thumbnail_path, filename="thumbnail.png")

        embed = discord.Embed(
            title=f"{data['title']}",
            description=data["postLink"],
            color=await get_color(self, interaction.guild.id),
        )
        embed.set_author(
            name=data["author"],
            url=f"https://reddit.com/u/{data['author']}",
            icon_url="https://www.redditstatic.com/avatars/defaults/v2/avatar_default_1.png",
        )
        embed.set_thumbnail(url="attachment://thumbnail.png")
        embed.set_image(url=data["url"])
        embed.set_footer(text=f"r/{data['subreddit']} • {data['ups']} 👍")

        await interaction.response.send_message(
            i18n.t("misc.meme_share", user=interaction.user.display_avatar),
            embed=embed,
            file=file,
        )
