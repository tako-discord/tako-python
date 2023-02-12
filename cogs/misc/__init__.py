from .affirmations import Affirmations
from .auto_react import AutoReact
from .embed import Embed
from .emoji import Emoji
from .image import ImageGen
from .ip import IP
from .media import Media
from .polls import Poll
from .reddit import Reddit
from .revive import Revive
from .show_tag import ShowTag
from .tag import Tag
from .uwu import UwU
from .youtube import Youtube


async def setup(bot):
    await bot.add_cog(Affirmations(bot))
    await bot.add_cog(AutoReact(bot))
    await bot.add_cog(Embed(bot))
    await bot.add_cog(Emoji(bot))
    await bot.add_cog(ImageGen(bot))
    await bot.add_cog(IP(bot))
    await bot.add_cog(Media(bot))
    await bot.add_cog(Poll(bot))
    await bot.add_cog(Reddit(bot))
    await bot.add_cog(Revive(bot))
    await bot.add_cog(ShowTag(bot))
    await bot.add_cog(Tag(bot))
    await bot.add_cog(UwU(bot))
    await bot.add_cog(Youtube(bot))
