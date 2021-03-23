import discord


class GamblerEmbed:

    @staticmethod
    def gambler_stats(list_of_args):
        embed = discord.Embed(title="GAMBLER STATISTICS", color=0x009dd5)
        embed.add_field(name="Balance " + u"\U0001F3E6", value=f'${list_of_args[0]}', inline=False)
        embed.add_field(name="Who Mugged Last " + u"\U0001F575", value=f'{list_of_args[1]}', inline=False)
        embed.add_field(
            name="When Last Mugged " + u"\u231A",
            value=f'{list_of_args[2].strftime("%d/%m/%y | %X") if list_of_args[2] is not None else "None"}',
            inline=False)
        embed.add_field(
            name="Last Time Redeemed " + u"\U0001F305",
            value=f'{list_of_args[3].strftime("%d/%m/%y | %X") if list_of_args[3] is not None else "None"}',
            inline=False)
        embed.add_field(name="Total Gained " + u"\U0001F4B0", value=f'${list_of_args[4]}', inline=False)
        embed.add_field(name="Total Lost " + u"\U0001F4B8", value=f'${list_of_args[5]}', inline=False)
        embed.set_footer(text=f"Stats for {list_of_args[6]}")
        return embed

    @staticmethod
    def general(list_of_args):
        embed = discord.Embed(title=f"{list_of_args[0]}", color=0x006d03, description=f"{list_of_args[1]}")
        embed.set_footer(text=f"{list_of_args[2]}")
        return embed

    @staticmethod
    def steal(list_of_args):
        embed = discord.Embed(title="OOOH YOU STEALIN'", color=0xd50000, description=f"{list_of_args[0]}")
        embed.set_footer(text=f"{list_of_args[1]}")
        return embed
