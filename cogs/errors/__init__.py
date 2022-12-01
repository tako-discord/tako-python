from ._cog import CommandErrorHandler


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))
