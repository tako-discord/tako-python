import discord
from .affirmation_buttons import AffirmationButtons
from .meme_buttons import MemeButtons
from .self_menu import SelfMenu


async def setup(bot):
    await bot.add_view(AffirmationButtons())
    await bot.add_view(MemeButtons(bot))
    bot.loop.create_task(selfrole_setup(bot))


async def selfrole_setup(bot):
        await bot.wait_until_ready()
        selfrole_menus = await bot.db_pool.fetch("SELECT * FROM selfroles")
        for item in selfrole_menus:
            view = discord.ui.View(timeout=None)
            menu = SelfMenu(
                bot,
                item["select_array"],
                item["min_values"],
                item["max_values"],
                str(item["id"]),
            )
            view.add_item(menu)
            bot.add_view(view)
