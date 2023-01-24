from .sync import Sync
from .extension import Extension
from .manage_announcements import ManageAnnouncements


async def setup(bot):
    await bot.add_cog(Sync(bot))
    await bot.add_cog(Extension(bot))
    await bot.add_cog(ManageAnnouncements(bot))
