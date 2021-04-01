from io import BytesIO

import discord
from discord.ext import commands

from bblib import Cards, Embed
from bblib.Util import message_channel, member_create


async def generate_image_message(ctx, session_info, dealer=False):
    with BytesIO() as image_binary:
        session_info.construct_image(dealer=dealer).save(image_binary, 'PNG')
        image_binary.seek(0)
        title = "Your Hand:" if dealer is False else "Dealer's Hand:"
        hand_value = session_info.get_hand() if dealer is False else session_info.get_hand(dealer=True)
        image_file = discord.File(fp=image_binary, filename='image.png')
        embed = Embed.BlackJackEmbed.generated_image(
            title=title,
            description=f'Value: ```{hand_value}```')
        await ctx.message.channel.send(file=image_file, embed=embed)


class BlackJackCog(commands.Cog, name='blackjack'):
    def __init__(self, bot):
        self.bot = bot

    """
    There are many outcomes for black jack:
    
    A natural where cards adding up to 21 gives a Blackjack/win.
    Five Card Charlie where having 5 cards in hand without busting will grant a win.
    Push where the player and dealer have the same value that's under 21. No one wins.
    Bust where a hand is over 21 resulting in a lose.
    Split will not be handled.
    
    Betting Rules:
    
    You can bet 25, 50, 75 each turn. When you win you gain double back.
    If you have a soft hand, you can double down once to try to win on the next turn.
    """

    @commands.command(aliases=['bj', 'black', 'jack'])
    @commands.check(member_create)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def blackjack(self, ctx):

        # Create a blackjack session.
        blackjack_session = Cards.BlackJackSession()

        # Recursive function that will loop till an outcome is created.
        async def return_outcome(session) -> tuple[bool, str]:

            async def send_response(session_info):
                # Print cards.
                await generate_image_message(ctx, session_info)
                await generate_image_message(ctx, session_info, dealer=True)

            async def retrieve_message(session_info):

                # Wait for user response.
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.message.author)

                if msg.clean_content.lower() == 'hit me':
                    pass
                elif msg.clean_content.lower() == 'stand':
                    session_info.set_stand()
                else:
                    await message_channel(ctx, "Please type an appropriate option.")
                    await retrieve_message(session_info)

            # Start function with dealing.
            session.deal()
            session.deal(dealer=True)

            # Check if bust.
            is_bust = session.check_bust()
            if is_bust:
                await send_response(session)
                return False, "Bust, better luck next time.",

            # Print card result.
            await send_response(session)

            # Get user response.
            await retrieve_message(session)

            # Put base condition here. Natural, Five Card Charlie, Push or Bust.
            if session.is_stand():
                return session.check_condition()
            else:
                return await return_outcome(session)

        final_result = await return_outcome(blackjack_session)
        await message_channel(ctx, final_result[1])


def setup(bot):
    bot.add_cog(BlackJackCog(bot))


def teardown(bot):
    bot.remove_cog(BlackJackCog(bot))
