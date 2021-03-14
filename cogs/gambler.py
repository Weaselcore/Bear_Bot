from discord.ext.commands import cooldown
from discord.ext import commands

# Import SQLITE3 wrapper for db functions.


class GamblerCog(commands.Cog, name='gambler'):
    def __init__(self, bot):
        self.bot = bot


def cog_unload(self):
    pass


def setup(bot):
    bot.add_cog(GamblerCog(bot))


def teardown(bot):
    bot.remove_cog(GamblerCog(bot))
