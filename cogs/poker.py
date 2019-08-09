from discord.ext import commands
from PokerClass import Deck
import pathlib
import random
import discord


class PokerCog(commands.Cog, name='poker'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def deck(self, ctx):
        deck = Deck()
        deck_list = deck.print_deck()
        await ctx.channel.send(deck_list)

    @commands.command()
    async def deal(self, ctx):
        hand = []
        final_hand = []
        deck = Deck()
        deck_list = deck.print_deck()
        for number in range(0, 5):
            random.shuffle(deck_list)
            hand.append(random.choice(deck_list))
        for card in hand:
            card_image = self.get_card_image(card)
            final_hand.append(discord.File(card_image, 'rb'))
        await ctx.channel.send(files=final_hand)

    @staticmethod
    def get_card_image(card_name):
        home_file = pathlib.Path.cwd()
        card_name = card_name + ".png"
        file = pathlib.Path(home_file/"card_images"/card_name)
        return file


def setup(bot):
    bot.add_cog(PokerCog(bot))


def teardown(bot):
    bot.remove_cog(PokerCog(bot))
