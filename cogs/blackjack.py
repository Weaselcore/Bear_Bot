from io import BytesIO

import discord
from discord.ext import commands

from bblib import Cards
from bblib.Util import message_channel, member_create


class BlackJackCog(commands.Cog, name='blackjack'):
    def __init__(self, bot):
        self.bot = bot

    """
    There are many outcomes for black jack.
    
    A natural where cards adding up to 21 gives a Blackjack/win.
    Five Card Charlie where having 5 cards in hand without busting will grant a win.
    Push where the player and dealer have the same value that's under 21. No one wins.
    Bust where a hand is over 21 resulting in a lose.
    """

    @commands.command(aliases=['bj', 'black', 'jack'])
    @commands.check(member_create)
    async def blackjack(self, ctx):

        result = None

        # Create a blackjack session.
        blackjack_session = Cards.BlackJackSession()

        # Recursive function that will loop till an outcome is created.
        async def return_outcome(session):

            async def send_response(session_info):
                # Print cards.
                with BytesIO() as image_binary:
                    session_info.construct_image().save(image_binary, 'PNG')
                    image_binary.seek(0)
                    # TODO Rewrite util message function to take files.
                    await ctx.message.channel.send(file=discord.File(fp=image_binary, filename='image.png'))

                await message_channel(
                    ctx,
                    incoming_message=
                    f'Your hand: {session_info.get_hand()} : {session_info.get_hand_cards()}'
                )
                await message_channel(
                    ctx,
                    incoming_message=
                    f'Dealers hand: {session_info.get_hand(dealer=True)} : {session_info.get_dealer_cards()}'
                )

            async def retrieve_message(session_info):

                # Wait for user response.
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.message.author)

                if msg.clean_content.lower() == 'hit me':
                    session_info.deal()
                    session_info.deal(dealer=True)
                elif msg.clean_content.lower() == 'stand':
                    session_info.set_stand()
                else:
                    await message_channel(ctx, "Please type an appropriate option.")
                    await retrieve_message(session_info)

            # Start function with dealing.
            session.deal()
            session.deal(dealer=True)

            # Check if bust.
            is_bust = session.is_bust()
            if is_bust:
                return False, "Bust, better luck next time.",

            # Print card result.
            await send_response(session)

            # Get user response.
            await retrieve_message(session)

            # Put base condition here. Natural, Five Card Charlie, Push or Bust.
            if session.is_stand():
                return session.conclusion()
            else:
                await return_outcome(session)

        final_result = await return_outcome(blackjack_session)
        await message_channel(ctx, final_result[1])


def setup(bot):
    bot.add_cog(BlackJackCog(bot))


def teardown(bot):
    bot.remove_cog(BlackJackCog(bot))
