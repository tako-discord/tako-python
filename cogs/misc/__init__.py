from .tag import Tag
from .polls import Poll
from .embed import Embed
from .emoji import Emoji
from .image import Image
from .media import Media
from .reddit import Reddit
from .youtube import Youtube
from .show_tag import ShowTag
from .translate import Translate
from .affirmations import Affirmations
from .autotranslate import AutoTranslate
from .reaction_translate import ReactionTranslate


async def setup(bot):
    await bot.add_cog(Tag(bot))
    await bot.add_cog(Poll(bot))
    await bot.add_cog(Embed(bot))
    await bot.add_cog(Emoji(bot))
    await bot.add_cog(Image(bot))
    await bot.add_cog(Media(bot))
    await bot.add_cog(Reddit(bot))
    await bot.add_cog(Youtube(bot))
    await bot.add_cog(ShowTag(bot))
    await bot.add_cog(Translate(bot))
    await bot.add_cog(Affirmations(bot))
    await bot.add_cog(ReactionTranslate(bot))
    await bot.add_cog(AutoTranslate(bot))
