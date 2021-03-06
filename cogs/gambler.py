import datetime
import logging

from discord.ext import commands

import bblib.Embed
from bblib.Util import get_member_str, get_member_object, message_channel, member_create, fifty, get_money, get_bank, \
    get_last_redeemed, get_total_gained, get_total_lost, get_stolen_id, get_stolen_time, get_last_bank_time, update, \
    update_money
from DatabaseWrapper import DatabaseWrapper

create_guild_table = """CREATE TABLE guild(
                            guild_id integer PRIMARY KEY,
                            name text NOT NULL,
                            creation_date timestamp);"""

create_member_table = """CREATE TABLE member(
                            _id integer NOT NULL PRIMARY KEY,
                            name text NOT NULL,
                            creation_date timestamp);"""

create_gambler_stat_table = """CREATE TABLE gambler_stat(
                            _id integer NOT NULL PRIMARY KEY,
                            nickname text DEFAULT NULL,
                            money_amount integer DEFAULT 0,
                            bank_amount integer DEFAULT 0,
                            last_stolen_id integer,
                            last_redeemed timestamp,
                            last_bank_datetime timestamp,
                            last_stolen_datetime timestamp,
                            total_gained integer DEFAULT 0,
                            total_lost integer DEFAULT 0);"""


class GamblerCog(commands.Cog, name='gambler'):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord')

        """ Check if tables are in the database. """
        global create_gambler_stat_table, create_member_table, create_guild_table

        table_name_tuple = ('guild', 'gambler_stat')
        table_create_tuple = (create_guild_table, create_gambler_stat_table)
        to_unzip = zip(table_name_tuple, table_create_tuple)

        for tuple_data in to_unzip:
            with DatabaseWrapper() as database:
                check_format = f''' SELECT count(name) FROM sqlite_master WHERE type = "table" AND name = "{tuple_data[0]}" '''
                cursor = database.execute(check_format)
                if cursor.fetchone()[0] == 1:
                    self.logger.info((tuple_data[0]).upper() + " table exists.")
                else:
                    self.logger.info((tuple_data[0]).upper() + " table does not exists. Creating now.")
                    database.create_table(tuple_data[1])

        """ Register Guilds. """
        list_of_guilds = self.bot.guilds
        with DatabaseWrapper() as database:
            for guild in list_of_guilds:
                database.execute(
                    f"""INSERT OR REPLACE INTO guild (guild_id, name, creation_date) values({guild.id}, "{guild.name}", "{datetime.datetime.utcnow()}");""")

    @commands.command(aliases=['stat', 'statistic'])
    @commands.check(member_create)
    async def info(self, ctx):
        """
        Returns information from the database on a specific member.
        Mentioning someone will return theirs, no mention will return your information.
        :param ctx:
        """
        if len(ctx.message.mentions) != 0:
            member = ctx.message.mentions[0]
        else:
            member = ctx.message.author

        last_stolen_member_object = get_member_object(ctx, get_stolen_id(member.id))
        if last_stolen_member_object is not None:
            last_stolen_name = last_stolen_member_object.name if last_stolen_member_object.nick is None else last_stolen_member_object.nick
        else:
            last_stolen_name = "None"

        # TODO create a mass query function to make this more efficient.
        embed = bblib.Embed.GamblerEmbed.gambler_stats(balance=get_money(member.id),
                                                       bank=get_bank(member.id),
                                                       last_redeemed=get_last_redeemed(member.id),
                                                       last_mugged=last_stolen_name,
                                                       when_mugged=get_stolen_time(member.id),
                                                       total_gained=get_total_gained(member.id),
                                                       total_lost=get_total_lost(member.id),
                                                       member=get_member_str(member))
        await message_channel(ctx, embed=embed)

    @commands.command(aliases=['balance', 'bal'])
    @commands.check(member_create)
    async def money(self, ctx):
        """
        Returns information from the database on a specific member's balance.
        Mentioning someone will return theirs, no mention will return your balance.
        :param ctx:
        """
        member = ctx.message.author

        if len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]

        money, bank = get_money(member.id), get_bank(member.id)
        title = f"Fetching Balance for {get_member_str(member)}"
        description = f'```Balance: ${money} | Bank: ${bank}```'
        footer = f'Invoked by {get_member_str(ctx.message.author)} '
        embed = bblib.Embed.GamblerEmbed.general((title, description, footer))
        await message_channel(ctx, embed=embed)

    @commands.command()
    @commands.check(member_create)
    async def redeem(self, ctx):
        """
        Will give a member $100 and will update database.
        :param ctx:
        """
        member = ctx.message.author
        money, last_redeemed = get_money(member.id), get_last_redeemed(member.id)
        now = datetime.datetime.utcnow()

        if last_redeemed is None or (now - last_redeemed) > datetime.timedelta(hours=1):
            update_money(member, 100, add_wallet=True, banking=False, redeem=True)

            title = ("THAT'S ANOTHER HUNNIT!",)
            embed = bblib.Embed.GamblerEmbed.general(
                title + (f"```Wallet balance is now ${money + 100}.```", f"Invoked by {get_member_str(member)}"))
            await message_channel(ctx, embed=embed)
        else:
            time_remaining = datetime.timedelta(hours=1) - (now - last_redeemed)
            embed = bblib.Embed.GamblerEmbed.general(
                ("Redeem is on Cooldown",
                 f"```{datetime.datetime.fromtimestamp(time_remaining.seconds).strftime('%M minutes and %S seconds remaining')}```",
                 f"Invoked by {get_member_str(member)}"))
            await message_channel(ctx, embed=embed)

    @commands.command(aliases=['double'])
    @commands.check(member_create)
    async def gamble(self, ctx):
        """
        Will gamble all member's money if no amount is stated.
        :param ctx:
        """
        member = ctx.message.author
        money_to_gamble = bblib.Util.get_number_arg(ctx)
        money = get_money(member.id)

        if money_to_gamble is None or money < money_to_gamble:
            money_to_gamble = money

        description_tuple = ("Your balance is $0. Get a job.",)
        footer_tuple = (f"Your balance is now $0",)

        if money_to_gamble is not None:
            if fifty():
                update_money(member, money_to_gamble)
                description_tuple = (
                    f"You have successfully doubled your money (${money_to_gamble} to ${money_to_gamble * 2}).",)
                footer_tuple = (f"Your balance is now ${get_money(member.id)}",)
            else:
                update_money(member, money_to_gamble, add_wallet=False)
                description_tuple = (f"You have lost ${money_to_gamble}.",)
                footer_tuple = (f"Your balance is now ${get_money(member.id)}.",)

        title = ("FEELING LUCKY KID?",)
        embed = bblib.Embed.GamblerEmbed.general(title + description_tuple + footer_tuple)
        await message_channel(ctx, embed=embed)

    @commands.command()
    @commands.check(member_create)
    async def steal(self, ctx):
        # await message_channel(ctx, "```Function is disabled due to bugs.```")
        """
        Will steal from another member if mentioned, cannot steal from the same member twice.
        If player's are "caught", they will be fined.
        :param ctx:
        :return:
        """

        def get_last_stolen(member_id):
            with DatabaseWrapper() as database:
                cursor = database.execute(f"SELECT last_stolen_id FROM gambler_stat WHERE _id = {member_id}")
                return cursor.fetchall()[0][0]

        member, mention = ctx.message.author, ctx.message.mentions
        last_stolen = get_last_stolen(member.id)

        if len(mention) == 0:
            await message_channel(ctx, incoming_message="You have to mention someone to steal.")
        elif mention[0] == member:
            await message_channel(ctx, incoming_message="You just stole from yourself, idiot.")
        elif get_money(member.id) == 0:
            await message_channel(ctx, incoming_message="You cannot steal if you do not have money!")
            pass
        elif mention[0].id == 450904080211116032:
            money = get_money(member.id)
            update_money(member, money, add_wallet=False)
            await message_channel(ctx,
                                  incoming_message="You tried to mug Bear Bot?!? Reverse card! You're now naked, "
                                                   "penniless and homeless.")
        elif last_stolen is not None and int(last_stolen) == mention[0].id:
            await message_channel(ctx, "You cannot target the same person again!")
            pass
        else:
            # This prevents people with low balance stealing all from high balance people.
            if get_money(member.id) >= get_money(mention[0].id):
                target_money = get_money(mention[0].id)
            else:
                target_money = get_money(member.id)

            title = "OOOH YOU STEALIN"
            if target_money is not None and target_money != 0:
                if fifty():
                    update_money(mention[0], target_money, add_wallet=False)
                    update_money(member, target_money)
                    description = f"You have stolen ${target_money} from {mention[0].nick if mention[0].nick is not None else mention[0].name}."
                    footer = f"New balance: ${get_money(member.id)}"
                else:
                    money = get_money(member.id)
                    update_money(member, round(money * 0.50), add_wallet=False)
                    description = f"You have been caught. You've been fined ${round(money * 0.50)}. "
                    footer = f"Balance: ${round(money * 0.50)} "
                update([("last_stolen_id", mention[0].id), ("last_stolen_datetime", str(datetime.datetime.utcnow()))],
                       member_id=member.id)

                embed = bblib.Embed.GamblerEmbed.general((title, description, footer))
                await message_channel(ctx, embed=embed)
            else:
                await message_channel(ctx,
                                      incoming_message="You cannot steal from people who have nothing. How heartless.")

    # TODO clean up messaging
    @commands.command(aliases=['bank'])
    @commands.check(member_create)
    async def deposit(self, ctx):
        number_arg = bblib.Util.get_number_arg(ctx)
        last_bank = get_last_bank_time(ctx.message.author.id)

        if last_bank is None or (datetime.datetime.utcnow() - last_bank) > datetime.timedelta(hours=12):
            if number_arg is None:
                await message_channel(ctx, incoming_message="Please add amount to deposit.")
            else:
                member = ctx.message.author
                money = get_money(member.id)

                if number_arg >= money:
                    number_arg = money

                update_money(member, number_arg, add_wallet=False, banking=True)

                title = "DEPOSITING TO BEAR BANK..."
                description = f'You have deposited ${number_arg}.'
                footer = f'Balance: ${get_money(member.id)} | Bank: ${get_bank(member.id)}'
                embed = bblib.Embed.GamblerEmbed.general((title, description, footer,))
                await message_channel(ctx, embed=embed)
        else:
            time_remaining = datetime.timedelta(4) - (datetime.datetime.utcnow() - last_bank)
            title = "Bank Command on Cooldown"
            description = f'```{datetime.datetime.fromtimestamp(time_remaining.seconds).strftime("%H hours, %M minutes, %S seconds")} remaining```'
            footer = f'Invoked by {get_member_str(ctx.message.author)}'
            embed = bblib.Embed.GamblerEmbed.general((title, description, footer,))
            await message_channel(ctx, embed=embed)

    @commands.command()
    @commands.check(member_create)
    async def withdraw(self, ctx):
        number_arg = bblib.Util.get_number_arg(ctx)

        if number_arg is None:
            await message_channel(ctx, incoming_message="Please add amount to withdraw.")
        else:
            member = ctx.message.author
            money, bank = get_money(member.id), get_bank(member.id)

            if number_arg >= bank:
                number_arg = bank

            update_money(member, number_arg, add_wallet=True, banking=True)

            title = f"Withdrawing for {get_member_str(member)}..."
            description = f'You have withdrawn ${number_arg}.'
            footer = f'Balance: ${get_money(member.id)} | Bank: ${get_bank(member.id)}'
            embed = bblib.Embed.GamblerEmbed.general((title, description, footer,))
            await message_channel(ctx, embed=embed)

    @commands.command(aliases=['rank'])
    async def leader(self, ctx):
        with DatabaseWrapper() as database:
            cursor = database.execute("SELECT nickname, money_amount, bank_amount FROM gambler_stat ORDER BY "
                                      "money_amount + bank_amount DESC LIMIT 5")
            result = cursor.fetchall()
            embed = bblib.Embed.GamblerEmbed.leaderboard(result)
            if embed:
                await message_channel(ctx, embed=embed)
            else:
                await message_channel(ctx, incoming_message="No big ballers on this server.")

    # TODO Make this not add to stats.
    @commands.command()
    @commands.check(member_create)
    @commands.has_permissions(administrator=True)
    async def give(self, ctx):
        if len(ctx.message.mentions) == 0:
            await message_channel(ctx, '```You need to mention someone to use this command.```')
        else:
            member = ctx.message.mentions[0]
            name = get_member_str(member)
            wallet_before = get_money(member.id)
            update_money(member, int(ctx.message.clean_content.split(" ")[-1]), add_wallet=True, banking=False, redeem=False)
            wallet_after = get_money(member.id)
            await message_channel(ctx, f"```Updated {name}'s wallet: ${wallet_before} -> ${wallet_after}```")


def setup(bot):
    bot.add_cog(GamblerCog(bot))


def teardown(bot):
    bot.remove_cog(GamblerCog(bot))
