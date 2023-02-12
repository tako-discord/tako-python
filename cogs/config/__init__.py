from .autojoin import Autojoin
from .color import Color
from .crosspost import Crosspost
from .selfroles import Selfroles


async def setup(bot):
    await bot.add_cog(Autojoin(bot))
    await bot.add_cog(Color(bot))
    await bot.add_cog(Crosspost(bot))
    await bot.add_cog(Selfroles(bot))
