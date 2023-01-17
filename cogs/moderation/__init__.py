from .anti_phishing import AntiPhishing
from .ban_game import BanGame
from .channel_locking import ChannelLocking
from .clear import Clear
from .roles import Roles
from .warn import WarnSystem


async def setup(bot):
    await bot.add_cog(AntiPhishing(bot))
    await bot.add_cog(BanGame(bot))
    await bot.add_cog(ChannelLocking(bot))
    await bot.add_cog(Clear(bot))
    await bot.add_cog(Roles(bot))
    await bot.add_cog(WarnSystem(bot))
