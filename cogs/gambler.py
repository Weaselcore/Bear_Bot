from discord.ext.commands import cooldown
from discord.ext import commands, tasks


class GamblerCog(commands.Cog, name='gambler'):
    def __init__(self, bot):
        self.bot = bot

    

def setup(bot):
    bot.add_cog(GamblerCog(bot))


def teardown(bot):
    bot.remove_cog(GamblerCog(bot))
