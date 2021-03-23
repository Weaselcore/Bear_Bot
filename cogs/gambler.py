import datetime
import logging
from random import random

from discord.ext import commands

import bblib.Embed
from database.DatabaseWrapper import DatabaseWrapper

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
                            last_stolen_id text,
                            last_redeemed timestamp,
                            last_stolen_datetime timestamp,
                            total_gained integer DEFAULT 0,
                            total_lost integer DEFAULT 0);"""


# TODO fix total loss.


async def message(ctx, incoming_message=None, embed=None) -> None:
    if not embed:
        await ctx.message.channel.send(incoming_message)
    else:
        await ctx.message.channel.send(embed=embed)


def fifty() -> bool:
    float_number = random()
    return True if float_number < 0.5 else False


def get_member_name(member) -> str:
    return member.name if member.nick is None else member.nick


def get_money(member) -> int:
    with DatabaseWrapper() as database:
        cursor = database.execute(f"SELECT money_amount FROM gambler_stat WHERE _id={member.id}")
        # fetchall returns a tuple in a list.
        money_list = cursor.fetchall()
        money = 0 if len(money_list) == 0 else money_list[0][0]
        return money


def member_create(ctx):
    with DatabaseWrapper() as database:
        members_to_check = [ctx.message.author.id]
        members_to_check.extend(ctx.message.raw_mentions)
        for member in members_to_check:
            cursor = database.execute(f"SELECT _id FROM gambler_stat WHERE _id={member}")
            result = cursor.fetchall()
            if not result:
                database.execute(f"""INSERT INTO gambler_stat (_id, money_amount) values({member}, 0);""")
    return True


def update(list_to_change, member_id):
    # nickname, money_amount, last_stolen_id, last_redeemed, last_stolen_datetime, total_gained, total_lost
    with DatabaseWrapper() as database:
        values = list(zip(*list_to_change))
        database.execute(f'''UPDATE gambler_stat SET {values[0]} = {values[1]} WHERE _id = {member_id};''')


def add_money(member, money_amount) -> None:
    old_amount = get_money(member)
    # Add money_amount to previous amount, add money gained.
    update([('nickname', get_member_name(member)), ('money_amount', old_amount + money_amount),
            ('total_gained', old_amount + money_amount)], member_id=member.id)


def remove_money(member, money_amount) -> None:
    old_amount = get_money(member)
    # Subtract money_amount to previous amount, add money lost.
    update([('nickname', get_member_name(member)), ('money_amount', old_amount - money_amount),
            ('total_lost', old_amount + money_amount)], member_id=member.id)


class GamblerCog(commands.Cog, name='gambler'):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger('discord')
        self.initialise_tables()
        self.register_guild()

    def initialise_tables(self) -> None:
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

    def register_guild(self) -> None:
        list_of_guilds = self.bot.guilds
        with DatabaseWrapper() as database:
            for guild in list_of_guilds:
                database.execute(
                    f"""INSERT OR REPLACE INTO guild (guild_id, name, creation_date) values({guild.id}, "{guild.name}", "{datetime.datetime.utcnow()}");""")

    @commands.command(aliases=['stat', 'statistic'])
    @commands.check(member_create)
    async def info(self, ctx):
        with DatabaseWrapper() as database:
            member = ctx.message.author
            cursor = database.execute(f"""SELECT money_amount, last_stolen_id, last_stolen_datetime, 
            last_redeemed, total_gained, total_lost FROM gambler_stat WHERE _id = {member.id}""")
            result = cursor.fetchall()
            name_tuple = (get_member_name(member),)
            embed = bblib.Embed.GamblerEmbed.gambler_stats(result[0] + name_tuple)
            await message(ctx, embed=embed)

    @commands.command(aliases=['balance', 'bal', 'bank'])
    @commands.check(member_create)
    async def money(self, ctx):
        with DatabaseWrapper() as database:
            if len(ctx.message.mentions) > 0:
                member = ctx.message.mentions[0]
                money = get_money(member)
            else:
                member = ctx.message.author
                cursor = database.execute(f"SELECT money_amount FROM gambler_stat WHERE _id={member.id}")
                money = cursor.fetchall()[0][0]
            title = "FETCHING BALANCE FROM BEAR BANK"
            description = f'Balance: ${money}'
            footer = f'Member: {get_member_name(member)}'
            embed = bblib.Embed.GamblerEmbed.general((title, description, footer))
            await message(ctx, embed=embed)

    # TODO check timestamp from db instead using cool down from memory.
    @commands.command()
    @commands.check(member_create)
    async def redeem(self, ctx):
        member = ctx.message.author
        title = ("ANOTHER STIMULUS CHEQUE???",)
        # TODO make it consistent with add_money.
        money_retrieved = get_money(member)
        update([('nickname', get_member_name(member)), ('money_amount', money_retrieved + 100),
                ('last_redeemed', str(datetime.datetime.utcnow())), ('total_gained', money_retrieved + 100)],
               member_id=member.id)
        embed = bblib.Embed.GamblerEmbed.general(
            title + ("You have redeemed $100.", f"Balance is now ${money_retrieved + 100}."))
        await ctx.message.channel.send(embed=embed)

    @commands.command(aliases=['double'])
    @commands.check(member_create)
    async def gamble(self, ctx):
        member = ctx.message.author
        money = get_money(member)
        title = ("FEELING LUCKY KID?",)
        if money != 0:
            if fifty():
                add_money(member, money)
                description_tuple = ("You have successfully doubled your money.",)
                footer_tuple = (f"Your balance is now ${money * 2}",)
            else:
                remove_money(member, money)
                description_tuple = (f"You have lost all your money: -${money}",)
                footer_tuple = (f"Your balance is now $0",)
        else:
            description_tuple = ("Your balance is $0. Get a job.",)
            footer_tuple = (f"Your balance is now $0",)

        embed = bblib.Embed.GamblerEmbed.general(title + description_tuple + footer_tuple)
        await message(ctx, embed=embed)

    @commands.command()
    @commands.check(member_create)
    async def steal(self, ctx):

        def get_last_stolen(member_id):
            with DatabaseWrapper() as database:
                cursor = database.execute(f"SELECT last_stolen_id FROM gambler_stat WHERE _id = {member_id}")
                return cursor.fetchall()[0][0]

        member, mention = ctx.message.author, ctx.message.mentions
        last_stolen = get_last_stolen(member.id)

        if len(mention) == 0:
            await message(ctx, incoming_message="You have to mention someone to steal.")
        elif mention[0] == member:
            await message(ctx, incoming_message="You just stole from yourself, idiot.")
        elif get_money(member) == 0:
            await message(ctx, incoming_message="You cannot steal if you do not have money!")
            pass
        elif mention[0].id == 450904080211116032:
            money = get_money(member)
            remove_money(member, money)
            await message(ctx,
                          incoming_message="You tried to mug Bear Bot?!? Reverse card! You're now naked, penniless "
                                           "and homeless.")
        elif last_stolen is not None and int(last_stolen) == mention[0].id:
            await message(ctx, "You cannot target the same person again!")
            pass
        else:
            target_money = get_money(mention[0])
            if target_money is not None and target_money != 0:
                if fifty():
                    remove_money(mention[0], target_money)
                    add_money(member, target_money)

                    await message(ctx,
                                  incoming_message=f"You have stolen from {mention[0].nick if mention[0].nick is not None else mention[0].name}. New balance: ${get_money(member)}")
                else:
                    money = get_money(member)
                    remove_money(member, round(money * 0.25))
                    await message(ctx,
                                  incoming_message=f"You have been caught. You've been fined ${round(money * 0.25)}. "
                                                   f"Balance: ${round(money * 0.75)} ")
                update([("last_stolen_id", mention[0].id), ("last_stolen_datetime", str(datetime.datetime.utcnow()))],
                       member_id=member.id)
            else:
                await message(ctx, incoming_message="You cannot steal from people who have nothing. How heartless.")


def cog_unload(self):
    self.database.close()


def setup(bot):
    bot.add_cog(GamblerCog(bot))


def teardown(bot):
    bot.remove_cog(GamblerCog(bot))
