import i18n
import discord
from utils import get_language


class SelfMenu(discord.ui.Select):
    def __init__(
        self, bot, select_array: list, min_values: int, max_values: int, uuid: str
    ):
        options = []
        for role_id in select_array:
            for guild in bot.guilds:
                for role in guild.roles:
                    if role.id == role_id:
                        options.append(
                            discord.SelectOption(label=role.name, value=str(role_id))
                        )
        super().__init__(
            custom_id=uuid,
            placeholder="No roles selected",
            options=options,
            min_values=min_values,
            max_values=max_values,
        )
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        for option in self.options:
            role = discord.utils.get(interaction.guild.roles, id=int(option.value))
            if str(role.id) in self.values:
                await interaction.user.add_roles(role)
            else:
                await interaction.user.remove_roles(role)
        await interaction.followup.send(
            content=i18n.t(
                "config.selfroles_updated",
                locale=get_language(self.bot, interaction.guild.id),
            ),
            ephemeral=True,
        )
