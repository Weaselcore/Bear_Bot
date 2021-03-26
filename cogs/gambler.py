import datetime
import logging
from random import choice

from discord.ext import commands

import bblib.Embed
from bblib.Util import get_member_str, get_member_object, message_channel
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
                            last_stolen_datetime timestamp,
                            total_gained integer DEFAULT 0,
                            total_lost integer DEFAULT 0);"""


def fifty() -> bool:
    return choice([True, False])


# TODO short on time, clean below
def get_value_money(column_name: str, filter_str: str):
    with DatabaseWrapper() as database:
        cursor = database.execute(f"SELECT money_amount FROM gambler_stat WHERE ({column_name})={filter_str}")
        result = cursor.fetchall()[0][0]
        return result


def get__value_bank(column_name: str, filter_str: str):
    with DatabaseWrapper() as database:
        cursor = database.execute(f"SELECT bank_amount FROM gambler_stat WHERE ({column_name})={filter_str}")
        result = cursor.fetchall()[0][0]
        return result


def get_value_last_redeemed(column_name: str, filter_str: str):
    with DatabaseWrapper() as database:
        cursor = database.execute(f"SELECT last_redeemed FROM gambler_stat WHERE ({column_name})={filter_str}")
        result = cursor.fetchall()[0][0]
        return result


def get_money(member_id) -> int:
    money = get_value_money(member_id, '_id')
    return money


def get_bank(member_id) -> int:
    bank = get__value_bank(member_id, '_id')
    return bank


def get_last_redeemed(member_id):
    last_redeemed_time = get_value_last_redeemed(member_id, '_id')
    return last_redeemed_time


def member_create(ctx):
    """
    Is a predicate function for the @command.check decorator.
    This ensures that the member that's being queried will have a row available.
    :param ctx:
    :return True: Will always be the case.
    """
    with DatabaseWrapper() as database:
        members_to_check = [ctx.message.author.id]
        members_to_check.extend(ctx.message.raw_mentions)
        for member in members_to_check:  # Deposit amount.
            cursor = database.execute(f"SELECT _id FROM gambler_stat WHERE _id={member}")
            result = cursor.fetchall()
            if not result:
                database.execute(f"""INSERT INTO gambler_stat (_id, money_amount) values({member}, 0);""")
    return True


def update(list_to_change: list, member_id):
    # nickname, money_amount, last_stolen_id, last_redeemed, last_stolen_datetime, total_gained, total_lost
    with DatabaseWrapper() as database:
        values = list(zip(*list_to_change))
        database.execute(f'''UPDATE gambler_stat SET {values[0]} = {values[1]} WHERE _id = {member_id};''')


def update_money(member, money_amount, add=True):
    old_amount = get_money(member.id)
    money_to_add = old_amount + money_amount if add else old_amount - money_amount

    update([('nickname', get_member_str(member)), ('money_amount', money_to_add),
            ('total_gained', old_amount + money_amount)], member_id=member.id)


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
        with DatabaseWrapper() as database:
            if len(ctx.message.mentions) != 0:
                member = ctx.message.mentions[0]
            else:
                member = ctx.message.author

            cursor = database.execute(f"""SELECT money_amount, bank_amount, last_stolen_id, last_stolen_datetime, 
            last_redeemed, total_gained, total_lost FROM gambler_stat WHERE _id = {member.id}""")
            result = cursor.fetchall()[0]

            last_stolen_member_object = get_member_object(ctx, result[2])
            if last_stolen_member_object is not None:
                last_stolen_name = last_stolen_member_object.name if last_stolen_member_object.nick is None else last_stolen_member_object.nick
            else:
                last_stolen_name = "None"

            embed = bblib.Embed.GamblerEmbed.gambler_stats(balance=result[0], bank=result[1],
                                                           last_mugged=last_stolen_name, last_redeemed=result[4],
                                                           total_gained=result[5], total_lost=result[6],
                                                           member=get_member_str(member))
            await message_channel(ctx, embed=embed)

    # TODO Use functions above to simplify this command.
    @commands.command(aliases=['balance', 'bal'])
    @commands.check(member_create)
    async def money(self, ctx):
        """
        Returns information from the database on a specific member's balance.
        Mentioning someone will return theirs, no mention will return your balance.
        :param ctx:
        """
        with DatabaseWrapper() as database:
            member = ctx.message.author

            if len(ctx.message.mentions) > 0:
                member = ctx.message.mentions[0]

            money = get_money(member.id)
            bank = get_bank(member.id)
            title = "FETCHING BALANCE FROM BEAR BANK"
            description = f'Balance: ${money} | Bank: ${bank}'
            footer = f'Member: {get_member_str(member)}'
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
        money = get_money(member.id)
        last_redeemed = get_last_redeemed(member.id)
        now = datetime.datetime.utcnow()

        if last_redeemed is None or (now - last_redeemed) > datetime.timedelta(hours=1):
            update([('nickname', get_member_str(member)), ('money_amount', money + 100),
                    ('last_redeemed', str(datetime.datetime.utcnow())), ('total_gained', money + 100)],
                   member_id=member.id)

            title = ("ANOTHER STIMULUS CHEQUE???",)
            embed = bblib.Embed.GamblerEmbed.general(
                title + ("You have redeemed $100.", f"Balance is now ${money + 100}."))
            await message_channel(ctx, embed=embed)
        else:
            time_remaining = datetime.timedelta(hours=1) - (now - last_redeemed)
            await message_channel(
                ctx,
                f"On cooldown, I don't have infinite money. {round(time_remaining.seconds/60)} minutes remaining.")

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
                update_money(member, money_to_gamble, add=False)
                description_tuple = (f"You have lost ${money_to_gamble}",)
                footer_tuple = (f"Your balance is now ${get_money(member.id)}",)

        title = ("FEELING LUCKY KID?",)
        embed = bblib.Embed.GamblerEmbed.general(title + description_tuple + footer_tuple)
        await message_channel(ctx, embed=embed)

    @commands.command()
    @commands.check(member_create)
    async def steal(self, ctx):
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
            update_money(member, money, add=False)
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
                    update_money(mention[0], target_money, add=False)
                    update_money(member, target_money)
                    description = f"You have stolen ${target_money} from {mention[0].nick if mention[0].nick is not None else mention[0].name}."
                    footer = f"New balance: ${get_money(member.id)}"
                else:
                    money = get_money(member.id)
                    update_money(member, round(money * 0.25), add=False)
                    description = f"You have been caught. You've been fined ${round(money * 0.25)}. "
                    footer = f"Balance: ${round(money * 0.75)} "
                update([("last_stolen_id", mention[0].id), ("last_stolen_datetime", str(datetime.datetime.utcnow()))],
                       member_id=member.id)

                embed = bblib.Embed.GamblerEmbed.general((title, description, footer))
                await message_channel(ctx, embed=embed)
            else:
                await message_channel(ctx,
                                      incoming_message="You cannot steal from people who have nothing. How heartless.")

    # TODO create a function to simplify both commands.
    @commands.command(aliases=['bank'])
    @commands.check(member_create)
    async def deposit(self, ctx):
        number_arg = bblib.Util.get_number_arg(ctx)

        if number_arg is None:
            await message_channel(ctx, incoming_message="Please add amount to deposit.")
        else:
            member = ctx.message.author
            money = get_money(member.id)
            bank = get_bank(member.id)

            if number_arg >= money:
                number_arg = money

            new_money_amount = money - number_arg
            new_bank_amount = bank + number_arg
            update([('bank_amount', new_bank_amount), ('money_amount', new_money_amount)], member.id)

            title = "DEPOSITING TO BEAR BANK..."
            description = f'You have deposited ${number_arg}.'
            footer = f'Balance: ${get_money(member.id)} | Bank: ${get_bank(member.id)}'
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
            money = get_money(member.id)
            bank = get_bank(member.id)

            if number_arg >= bank:
                number_arg = bank

            new_money_amount = money + number_arg
            new_bank_amount = bank - number_arg
            update([('bank_amount', new_bank_amount), ('money_amount', new_money_amount)], member.id)

            title = "WITHDRAWING TO BEAR BANK..."
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

    '''
    @commands.command(aliases=['bj', 'black', 'jack'])
    @commands.check(member_create)
    async def blackjack(self, ctx):
        blackjack_session = Cards.BlackJackSession()
        await message_channel(ctx, incoming_message=f'Your hand: {blackjack_session.get_hand_value()} : {blackjack_session.get_hand_cards()}')
        await message_channel(ctx, incoming_message=f'Dealers hand: {blackjack_session.get_dealer_value()} : {blackjack_session.get_dealer_cards()}')
        await message_channel(ctx, incoming_message=f'Win: {blackjack_session.conclusion()}')
    '''


def setup(bot):
    bot.add_cog(GamblerCog(bot))


def teardown(bot):
    bot.remove_cog(GamblerCog(bot))
