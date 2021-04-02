import asyncio
from io import BytesIO

import discord
from discord.ext import commands

from bblib import CardGames, Embed
from bblib.Util import message_channel, member_create, get_member_str, get_money


async def generate_image_message(ctx, session_info, dealer=False):
    with BytesIO() as image_binary:
        session_info.construct_image(dealer=dealer).save(image_binary, 'PNG')
        image_binary.seek(0)
        title = "Your Hand:" if dealer is False else "Dealer's Hand:"
        hand_value = session_info.get_hand() if dealer is False else session_info.get_hand(dealer=True)
        image_file = discord.File(fp=image_binary, filename='image.png')

        if session_info.is_stand() or session_info.check_bust():
            hidden = False
        else:
            hidden = True

        embed = Embed.BlackJackEmbed.generated_image(
            title=title,
            description=f'Value: ```{hand_value}```',
            footer=f'Session: {get_member_str(ctx.message.author)} | Jackpot: ${session_info.jackpot}',
            hidden=hidden,
            dealer=dealer)
        await ctx.message.channel.send(file=image_file, embed=embed)


async def send_response(ctx, session_info):
    # Print cards.
    await generate_image_message(ctx, session_info)
    await generate_image_message(ctx, session_info, dealer=True)


async def retrieve_message(ctx, bot, session_info):

    try:
        # Wait for user response.
        msg = await bot.wait_for('message', check=lambda message: message.author == ctx.message.author, timeout=30)

        print(msg)

        try:
            if msg.clean_content.lower() == 'double':
                session_info.set_double()
            elif msg.clean_content.lower() == 'stand':
                session_info.set_stand()
            elif int(msg.clean_content.lower()):
                amount_to_bet = int(msg.clean_content.lower())
                success = session_info.add_jackpot(amount_to_bet)
                if success:
                    await message_channel(ctx, f"```You've added {int(msg.clean_content.lower())} to the jackpot.```")
                else:
                    session_info.set_stand()
                    await message_channel(ctx, "```You've run out of money to add to the jackpot.```")
        except ValueError:
            await message_channel(ctx,
                                  "```Please type an appropriate option. A 'number' to bet, 'double' or 'stand'.```")
            await retrieve_message(ctx, bot, session_info)
    except asyncio.TimeoutError:
        session_info.set_timeout()


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
    
    Initial bet is 25 and then each turn you can bet any amount. When you win you gain double back.
    If you have a soft hand, you can double down once to try to win on the next turn.
    """

    @commands.command(aliases=['bj', 'black', 'jack'])
    @commands.check(member_create)
    @commands.max_concurrency(1, per=commands.BucketType.default, wait=False)
    async def blackjack(self, ctx):

        bank = get_money(ctx.author.id)
        if get_money(ctx.author.id) >= 25:
            # Create a blackjack session.
            blackjack_session = CardGames.BlackJackSession(ctx.message.author)

            # Recursive function that will loop till an outcome is created.
            async def return_outcome(session) -> str:

                # Start function with dealing.
                session.deal()
                session.deal(dealer=True)

                # If the previous input is a certain condition, this will cut the flow early.
                if session.get_double():
                    session.double_down()
                    await send_response(ctx, session)
                    return session.check_condition()
                elif session.check_bust():
                    session.lose_money()
                    await send_response(ctx, session)
                    return session.check_condition()
                elif session.get_timeout():
                    session.lose_money()
                    return "```Your session has timed out. Jackpot was removed from your wallet as penalty.```"
                else:
                    # Print card result.
                    await send_response(ctx, session)
                    # Get user input.
                    await retrieve_message(ctx, self.bot, session)

                # Put base condition here. Natural, Five Card Charlie, Push or Bust.
                if session.is_stand():
                    await send_response(ctx, session)
                    return session.check_condition()
                else:
                    return await return_outcome(session)

            await message_channel(ctx, await return_outcome(blackjack_session))
        else:
            await message_channel(ctx, "```You must have $25 or more to play Blackjack.```")


def setup(bot):
    bot.add_cog(BlackJackCog(bot))


def teardown(bot):
    bot.remove_cog(BlackJackCog(bot))
