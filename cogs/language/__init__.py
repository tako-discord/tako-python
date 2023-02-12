from .autotranslate import AutoTranslate
from .language import Language
from .reaction_translate import ReactionTranslate
from .translate import Translate


async def setup(bot):
    await bot.add_cog(AutoTranslate(bot))
    await bot.add_cog(Language(bot))
    await bot.add_cog(ReactionTranslate(bot))
    await bot.add_cog(Translate(bot))
