from .balance import Balance
from .bank import Bank
from .give import Give

# We need to remove gambling in order to comply with the Discord Guidelines for App Directory
# Our plan is to make a seperate bot for gambling, that will have shared data with this bot
# from .gamble import Gamble


async def setup(bot):
    await bot.add_cog(Balance(bot))
    await bot.add_cog(Bank(bot))
    await bot.add_cog(Give(bot))


#   await bot.add_cog(Gamble(bot))
