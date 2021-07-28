import discord
from bblib.Util import get_member_str, get_member_object
from bblib.core.player_database_info import PlayerDatabaseInfo


class GamblerEmbed:

    @staticmethod
    def gambler_stats(player_info: PlayerDatabaseInfo, ctx):

        embed = discord.Embed(title="GAMBLER STATISTICS", color=0x009dd5)
        embed.add_field(name="Balance " + u"\U0001F3E6", value=f'${player_info.money_amount}', inline=False)
        embed.add_field(name="Bank " + u"\U0001F911", value=f'${player_info.bank_amount}', inline=False)

        last_stolen_member = get_member_str(get_member_object(ctx, player_info.last_stolen_id))

        embed.add_field(name="Who Mugged Last " + u"\U0001F575",
                        value=f'{"None" if last_stolen_member is None else last_stolen_member}', inline=False)
        embed.add_field(
            name="When Last Mugged " + u"\u231A",
            value=f'{player_info.last_stolen_time.strftime("%d/%m/%y | %X") if player_info.last_stolen_time is not None else "None"}',
            inline=False)
        embed.add_field(
            name="Last Time Redeemed " + u"\U0001F305",
            value=f'{player_info.last_redeemed.strftime("%d/%m/%y | %X") if player_info.last_redeemed is not None else "None"}',
            inline=False)
        embed.add_field(name="Total Gained " + u"\U0001F4B0", value=f'${player_info.total_gained}', inline=False)
        embed.add_field(name="Total Lost " + u"\U0001F4B8", value=f'${player_info.total_lost}', inline=False)
        embed.set_footer(text=f"Stats for {get_member_str(get_member_object(ctx, player_info.id))}")
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
                embed.add_field(name=f'#{count}', value=f'```{element[0]}```', inline=True)
                embed.add_field(name="Wallet:", value=f'```${element[1]}```', inline=True)
                embed.add_field(name="Bank:", value=f'```${element[2]}```', inline=True)
                count += 1
            return embed
        else:
            return None


class BlackJackEmbed:

    @staticmethod
    def generated_image(title: str, description: str, footer: str, hidden=True, dealer=False):
        if hidden and dealer:
            embed = discord.Embed(title=f"{title}", color=0x016d03)
        else:
            embed = discord.Embed(title=f"{title}", color=0x016d03, description=description)

        embed.set_image(url="attachment://image.png")
        embed.set_footer(text=footer)
        return embed
