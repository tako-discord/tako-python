import discord
from discord.ext import commands
'''
from .affirmation_buttons import AffirmationButtons
from .meme_buttons import MemeButtons
from .self_menu import SelfMenu
from .poll_buttons import PollButtons
'''


async def setup(bot: commands.Bot):
    '''
    bot.add_view(AffirmationButtons())
    bot.add_view(MemeButtons(bot))
    '''
    bot.loop.create_task(selfrole_setup(bot))
    bot.loop.create_task(poll_setup(bot))


async def selfrole_setup(bot):
    '''
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
    '''


async def poll_setup(bot):
    await bot.wait_until_ready()
    '''
    polls = await bot.db_pool.fetch("SELECT * FROM polls;")
    for poll in polls:
        view = PollButtons(
            poll["id"],
            poll["question"],
            poll["answers"],
            bot,
        )
        bot.add_view(view)
    '''
