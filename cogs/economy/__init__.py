from .balance import Balance
from .bank import Bank
from .gamble import Gamble
from .give import Give


async def setup(bot):
    await bot.add_cog(Balance(bot))
    await bot.add_cog(Bank(bot))
    await bot.add_cog(Gamble(bot))
    await bot.add_cog(Give(bot))
