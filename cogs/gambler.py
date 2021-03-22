import datetime
import logging
from random import random

from discord.ext.commands import cooldown
from discord.ext import commands
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


async def message(ctx, incoming_message) -> None:
    await ctx.message.channel.send(incoming_message)


def fifty() -> bool:
    float_number = random()
    return True if float_number < 0.5 else False


class GamblerCog(commands.Cog, name='gambler'):
    def __init__(self, bot):
        self.bot = bot
        self.database = DatabaseWrapper()
        self.cursor = self.database.cursor
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
            check_format = f''' SELECT count(name) FROM sqlite_master WHERE type="table" AND name="{tuple_data[0]}"'''
            self.database.execute(check_format)
            if self.cursor.fetchone()[0] == 1:
                self.logger.info((tuple_data[0]).upper() + " table exists.")
            else:
                self.logger.info((tuple_data[0]).upper() + " table does not exists. Creating now.")
                self.database.create_table(tuple_data[1])

    def register_guild(self) -> None:
        list_of_guilds = self.bot.guilds
        for guild in list_of_guilds:
            self.database.execute(
                f"""INSERT OR REPLACE INTO guild (guild_id, name, creation_date) values({guild.id}, "{guild.name}", "{datetime.datetime.utcnow()}");""")

    def get_money(self, member) -> int:
        cursor = self.database.execute(
            f"SELECT money_amount FROM gambler_stat WHERE _id={member.id}")
        # fetchall returns a tuple in a list.
        money_list = cursor.fetchall()
        money = 0 if len(money_list) == 0 else money_list[0][0]
        return money

    def member_exists(self, member):
        cursor = self.database.execute(
            f"SELECT _id FROM gambler_stat WHERE _id={member.id}")
        result = cursor.fetchall()
        if len(result) == 0:
            self.database.execute(
                f"""INSERT INTO gambler_stat (_id, money_amount) values({member.id}, 0);""")

    def update(self, list_to_change, member_id):
        # nickname, money_amount, last_stolen_id, last_redeemed, last_stolen_datetime, total_gained, total_lost
        values = list(zip(*list_to_change))
        cursor = self.database.execute(
            f'''UPDATE gambler_stat SET {values[0]} = {values[1]} WHERE _id = {member_id};'''
        )

    def add_money(self, member, money_amount) -> None:
        old_amount = self.get_money(member)
        # Add money_amount to previous amount, add money gained.
        self.update([('nickname', member.nick), ('money_amount', old_amount + money_amount), ('total_gained', old_amount + money_amount)], member_id=member.id)

    def remove_money(self, member, money_amount) -> None:
        old_amount = self.get_money(member)
        # Subtract money_amount to previous amount, add money lost.
        self.update([('nickname', member.nick), ('money_amount', old_amount - money_amount), ('total_lost', old_amount + money_amount)], member_id=member.id)

    @commands.command(aliases=['balance', 'bal'])
    async def money(self, ctx):
        self.member_exists(ctx.message.author)
        if len(ctx.message.mentions) > 0:
            member = ctx.message.mentions[0]
            money = self.get_money(member)
        else:
            member = ctx.message.author
            cursor = self.database.execute(
                f"SELECT money_amount FROM gambler_stat WHERE _id={member.id}")
            money = cursor.fetchall()[0][0]
        await message(ctx, f'Member: {member.nick if member.nick is not None else member.name} has ${money}.')

    # TODO check timestamp from db instead using cool down from memory.
    @commands.command()
    async def redeem(self, ctx):
        member = ctx.message.author
        self.member_exists(ctx.message.author)

        # TODO make it consistent with add_money.
        money_retrieved = self.get_money(member)

        self.update([('nickname', member.nick), ('money_amount', money_retrieved + 100), ('last_redeemed', str(datetime.datetime.utcnow())), ('total_gained', money_retrieved + 100)], member_id=member.id)
        await ctx.message.channel.send(f"You have redeemed $100. Balance is now ${money_retrieved + 100}.")

    @commands.command(aliases=['double'])
    async def gamble(self, ctx):
        self.member_exists(ctx.message.author)
        member = ctx.message.author
        money = self.get_money(member)
        if money != 0:
            if fifty():
                self.add_money(member, money)
                await ctx.message.channel.send(f"You have successfully doubled your money: ${self.get_money(member)}")
            else:
                self.remove_money(member, money)
                await ctx.message.channel.send(f"You have lost all your money: -${money}")
        else:
            await message(ctx, "Your balance is $0. Get a job.")

    @commands.command()
    async def steal(self, ctx):
        self.member_exists(ctx.message.author)
        member = ctx.message.author
        mention = ctx.message.mentions
        if len(mention) == 0:
            await message(ctx, "You have to mention someone to steal.")
        elif mention[0] == member:
            await message(ctx, "You just stole from yourself, idiot.")
        elif mention[0].id == 450904080211116032:
            money = self.get_money(member)
            self.remove_money(member, money)
            await message(ctx, "You tried to mug Bear Bot?!? Reverse card! You're now naked, penniless and homeless.")
        else:
            self.member_exists(mention[0])
            target_money = self.get_money(mention[0])
            if target_money is not None and target_money != 0:
                if fifty():
                    self.remove_money(mention[0], target_money)
                    self.add_money(member, target_money)
                    await message(ctx, f"You have stolen from {mention[0].nick if mention[0].nick is not None else mention[0].name}. New balance: ${self.get_money(member)}")
                else:
                    money = self.get_money(member)
                    self.remove_money(member, round(money * 0.25))
                    await message(ctx,
                                  f"You have been caught. You've been fined ${round(money * 0.25)}. Balance: ${round(money * 0.75)} ")
            else:
                await message(ctx, "You cannot steal from people who have nothing. How heartless.")


def cog_unload(self):
    self.database.close()


def setup(bot):
    bot.add_cog(GamblerCog(bot))


def teardown(bot):
    bot.remove_cog(GamblerCog(bot))
