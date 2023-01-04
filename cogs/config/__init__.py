from .autojoin import Autojoin
from .color import Color
from .crosspost import Crosspost
from .language import Language
from .selfroles import Selfroles
from .welcome import Welcome


async def setup(bot):
    await bot.add_cog(Autojoin(bot))
    await bot.add_cog(Color(bot))
    await bot.add_cog(Crosspost(bot))
    await bot.add_cog(Language(bot))
    await bot.add_cog(Selfroles(bot))
    await bot.add_cog(Welcome(bot))
