from ._cog import Info
from .info import InfoGroup
from .raw_message import RawMessage


async def setup(bot):
    await bot.add_cog(Info(bot))
    await bot.add_cog(InfoGroup(bot))
    await bot.add_cog(RawMessage(bot))
