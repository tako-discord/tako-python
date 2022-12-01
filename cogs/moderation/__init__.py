from .anti_phishing import AntiPhishing
from .ban_game import BanGame
from .clear import Clear


async def setup(bot):
    await bot.add_cog(AntiPhishing(bot))
    await bot.add_cog(BanGame(bot))
    await bot.add_cog(Clear(bot))
