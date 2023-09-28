import uuid
import discord
from main import TakoBot
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from utils import get_color, number_of_pages_needed


class TagCreation(discord.ui.Modal, title="Create a Tag"):
    def __init__(self, embed: bool, bot: TakoBot):
        super().__init__()
        self.embed = embed
        self.bot = bot

        self.add_item(
            discord.ui.TextInput(
                label="Name",
                placeholder="Name of the tag",
                max_length=35,
                required=True,
            )
        )
        self.add_item(
            discord.ui.TextInput(
                label="Content",
                placeholder="Content of the tag",
                max_length=4000 if embed else 1950,
                style=discord.TextStyle.long,
                required=True,
            )
        )
        if embed:
            self.add_item(discord.ui.TextInput(label="Thumbnail", required=False))
            self.add_item(discord.ui.TextInput(label="Image", required=False))
            self.add_item(
                discord.ui.TextInput(label="Footer", max_length=1965, required=False)
            )

    async def on_submit(self, interaction: discord.Interaction):
        id = uuid.uuid4()
        if not self.embed:
            await self.bot.db_pool.execute(
                "INSERT INTO tags  (id, name, content, embed, guild_id) VALUES ($1, $2, $3, $4, $5)",
                id,
                self.children[0].value,
                self.children[1].value,
                False,
                interaction.guild_id,
            )
        else:
            await self.bot.db_pool.execute(
                "INSERT INTO tags (id, name, content, thumbnail, image, footer, embed, guild_id) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)",
                id,
                self.children[0].value,
                self.children[1].value,
                self.children[2].value,
                self.children[3].value,
                self.children[4].value,
                True,
                interaction.guild_id,
            )
        await interaction.response.send_message(
            f"Succesfully created the tag! (ID: *{str(id)}*)", ephemeral=True
        )


class TagEdit(discord.ui.Modal, title="Edit a Tag"):
    def __init__(self, tag: str, embed: bool, bot: TakoBot):
        super().__init__()
        self.embed = embed
        self.tag = tag
        self.bot = bot

        self.add_item(
            discord.ui.TextInput(
                label="Name",
                placeholder="Name of the tag",
                max_length=35,
                default=tag["name"],
                required=True,
            )
        )
        self.add_item(
            discord.ui.TextInput(
                label="Content",
                placeholder="Content of the tag",
                max_length=4000 if embed else 1950,
                default=tag["content"],
                style=discord.TextStyle.long,
                required=True,
            )
        )
        if embed:
            self.add_item(
                discord.ui.TextInput(
                    label="Thumbnail", default=tag["thumbnail"], required=False
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label="Image", default=tag["image"], required=False
                )
            )
            self.add_item(
                discord.ui.TextInput(
                    label="Footer",
                    max_length=1965,
                    default=tag["footer"],
                    required=False,
                )
            )

    async def on_submit(self, interaction: discord.Interaction):
        if not self.embed:
            await self.bot.db_pool.execute(
                "UPDATE tags SET name = $1, content = $2 WHERE id = $3;",
                self.children[0].value,
                self.children[1].value,
                self.tag["id"],
            )
        else:
            await self.bot.db_pool.execute(
                "UPDATE tags SET name = $1, content = $2, thumbnail = $3, image = $4, footer = $5 WHERE id = $6;",
                self.children[0].value,
                self.children[1].value,
                self.children[2].value,
                self.children[3].value,
                self.children[4].value,
                self.tag["id"],
            )
        await interaction.response.send_message(
            f"Succesfully edited the tag! (ID: *{self.tag['id']}*)", ephemeral=True
        )


class PaginatorButtons(discord.ui.View):
    def __init__(self, array, total_pages, current_page, bot):
        super().__init__()
        self.array = array
        self.total_pages = total_pages
        self.current_page = current_page
        self.bot = bot

    @discord.ui.button(label="First Page", emoji="⏪")
    async def first_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.current_page = 1
        embed = discord.Embed(
            title="Tags",
            description="\n".join(
                self.array[55 * self.current_page - 55 : 55 * self.current_page]
            ),
            color=await get_color(self.bot, interaction.guild_id),
            timestamp=datetime.now(),
        )
        embed.set_footer(text=f"Page {self.current_page}/{self.total_pages}")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Previous Page", emoji="◀️")
    async def previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page == 1:
            return await interaction.response.send_message(
                "You are already on the first page!", ephemeral=True
            )
        self.current_page = self.current_page - 1
        embed = discord.Embed(
            title="Tags",
            description="\n".join(
                self.array[55 * self.current_page - 55 : 55 * self.current_page]
            ),
            color=await get_color(self.bot, interaction.guild_id),
            timestamp=datetime.now(),
        )
        embed.set_footer(text=f"Page {self.current_page}/{self.total_pages}")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Next Page", emoji="▶️")
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page == self.total_pages:
            return await interaction.response.send_message(
                "You are already on the last page!", ephemeral=True
            )
        self.current_page = self.current_page + 1
        embed = discord.Embed(
            title="Tags",
            description="\n".join(
                self.array[55 * self.current_page - 55 : 55 * self.current_page]
            ),
            color=await get_color(self.bot, interaction.guild_id),
            timestamp=datetime.now(),
        )
        embed.set_footer(text=f"Page {self.current_page}/{self.total_pages}")
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label="Last Page", emoji="⏩")
    async def last_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if self.current_page == self.total_pages:
            return await interaction.response.send_message(
                "You are already on the last page!", ephemeral=True
            )
        self.current_page = self.total_pages
        embed = discord.Embed(
            title="Tags",
            description="\n".join(
                self.array[55 * self.current_page - 55 : 55 * self.current_page]
            ),
            color=await get_color(self.bot, interaction.guild_id),
            timestamp=datetime.now(),
        )
        embed.set_footer(text=f"Page {self.current_page}/{self.total_pages}")
        await interaction.response.edit_message(embed=embed, view=self)


class Tag(commands.GroupCog, group_name="tag"):
    def __init__(self, bot: commands.AutoShardedBot):
        self.bot = bot

    @app_commands.command(description="Create a tag")
    async def create(self, interaction: discord.Interaction, embed: bool = True):
        await interaction.response.send_modal(TagCreation(embed, self.bot))

    @app_commands.command(description="Edit a tag")
    async def edit(self, interaction: discord.Interaction, tag: str):
        if len(tag) < 32 or len(tag) > 36:
            return await interaction.response.send_message(
                "This tag does not exist!", ephemeral=True
            )
        tag = await self.bot.db_pool.fetchrow(
            "SELECT * FROM tags WHERE id = $1 AND guild_id = $2;",
            tag,
            interaction.guild_id,
        )
        if tag is None:
            return await interaction.response.send_message(
                "This tag does not exist!", ephemeral=True
            )
        await interaction.response.send_modal(
            TagEdit(tag=tag, embed=tag["embed"], bot=self.bot)
        )

    @app_commands.command(description="Delete a tag")
    async def delete(self, interaction: discord.Interaction, tag: str):
        if len(tag) < 32 or len(tag) > 36:
            return await interaction.response.send_message(
                "This tag does not exist!", ephemeral=True
            )
        try:
            data = await self.bot.db_pool.fetchrow(
                "SELECT * FROM tags WHERE id = $1 AND guild_id = $2;",
                tag,
                interaction.guild_id,
            )
        except:
            pass
        if data is None:
            return await interaction.response.send_message(
                "This tag does not exist!", ephemeral=True
            )
        else:
            await self.bot.db_pool.execute(
                "DELETE FROM tags WHERE id = $1 AND guild_id = $2;",
                tag,
                interaction.guild_id,
            )
            await interaction.response.send_message(
                "Succesfully deleted the tag!", ephemeral=True
            )

    @app_commands.command(description="List all tags in the current guild")
    async def list(self, interaction: discord.Interaction):
        tags = await self.bot.db_pool.fetch(
            "SELECT * FROM tags WHERE guild_id = $1;", interaction.guild_id
        )
        tags_array = []
        for tag in tags:
            tags_array.append(f"{tag['name']} ({tag['id']})")
        if not tags_array:
            tags_array = ["There are no tags on this server"]
        total_pages = number_of_pages_needed(55, len(tags_array))
        index = 55
        embed = discord.Embed(
            title="Tags",
            description="\n".join(tags_array[:index]),
            timestamp=datetime.now(),
            color=await get_color(self.bot, interaction.guild_id),
        )
        embed.set_footer(text=f"Page 1/{total_pages}")
        if total_pages > 1:
            view = PaginatorButtons(tags_array, total_pages, 1, self.bot)
            await interaction.response.send_message(embed=embed, view=view)
        else:
            await interaction.response.send_message(embed=embed)

    @edit.autocomplete(name="tag")
    @delete.autocomplete(name="tag")
    async def autocomplete_callback(
        self, interaction: discord.Interaction, current: str
    ):
        tags = await self.bot.db_pool.fetch(
            "SELECT * FROM tags WHERE guild_id = $1;", interaction.guild_id
        )
        return [
            app_commands.Choice(
                name=f"{tag['name']} ({str(tag['id'])})", value=str(tag["id"])
            )
            for tag in tags
            if current.lower() in tag["name"].lower()
            or current.lower() in str(tag["id"]).lower()
        ]
