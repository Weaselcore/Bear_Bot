import discord
from bblib import Util


class GamblerEmbed:

    @staticmethod
    def gambler_stats(
            balance=0,
            bank=0,
            last_mugged=None,
            when_mugged=None,
            last_redeemed=None,
            total_gained=0,
            total_lost=0,
            member=None):

        embed = discord.Embed(title="GAMBLER STATISTICS", color=0x009dd5)
        embed.add_field(name="Balance " + u"\U0001F3E6", value=f'${balance}', inline=False)
        embed.add_field(name="Bank " + u"\U0001F911", value=f'${bank}', inline=False)
        embed.add_field(name="Who Mugged Last " + u"\U0001F575",
                        value=f'{last_mugged}', inline=False)
        embed.add_field(
            name="When Last Mugged " + u"\u231A",
            value=f'{when_mugged.strftime("%d/%m/%y | %X") if when_mugged is not None else "None"}',
            inline=False)
        embed.add_field(
            name="Last Time Redeemed " + u"\U0001F305",
            value=f'{last_redeemed.strftime("%d/%m/%y | %X") if last_redeemed is not None else "None"}',
            inline=False)
        embed.add_field(name="Total Gained " + u"\U0001F4B0", value=f'${total_gained}', inline=False)
        embed.add_field(name="Total Lost " + u"\U0001F4B8", value=f'${total_lost}', inline=False)
        embed.set_footer(text=f"Stats for {member}")
        return embed

    @staticmethod
    def general(list_of_args):
        embed = discord.Embed(title=f"{list_of_args[0]}", color=0x006d03, description=f"{list_of_args[1]}")
        embed.set_footer(text=f"{list_of_args[2]}")
        return embed

    @staticmethod
    def leaderboard(list_of_args):
        number_of_fields = len(list_of_args)
        if number_of_fields > 0:
            embed = discord.Embed(title="LEADERBOARD - TOP 5", color=0x047dd5)
            count = 1
            for element in list_of_args:
                embed.add_field(name='*Rank*:  ', value=f'```#{count}```', inline=True)
                embed.add_field(name="*Name*: ", value=f'```   {element[0]}   ```', inline=True)
                embed.add_field(
                    name="*Amount*: ", value=f'Wallet: ```${element[1]}```Bank: ```${element[2]}```', inline=True
                )
                count += 1
            return embed
        else:
            return None
