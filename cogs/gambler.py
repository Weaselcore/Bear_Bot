import datetime
import logging

from discord.ext.commands import cooldown
from discord.ext import commands
from database.DatabaseWrapper import DatabaseWrapper

# TODO to fix the parsing of datetime.

create_guild_table = """CREATE TABLE guild(
                            guild_id integer PRIMARY KEY,
                            name text NOT NULL,
                            creation_date timestamp,
                            last_used timestamp);"""

create_member_table = """CREATE TABLE member(
                            _id integer PRIMARY KEY,
                            name text NOT NULL,
                            creation_date timestamp,
                            last_used timestamp);"""

create_gambler_stat_table = """CREATE TABLE gambler_stat(
                            _id integer PRIMARY KEY,
                            member_id REFERENCES member(_id),
                            money_amount integer,
                            last_stolen_id text,
                            last_redeemed timestamp,
                            last_stolen_datetime timestamp,
                            total_gained integer,
                            total_lost integer);"""


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

        table_name_tuple = ('guild', 'member', 'gambler_stat')
        table_create_tuple = (create_guild_table, create_member_table, create_gambler_stat_table)
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
            self.database.execute(f"""INSERT OR REPLACE INTO guild (guild_id, name, creation_date) values({guild.id}, "{guild.name}", "{str(datetime.datetime.utcnow())}");""")

    @commands.command()
    async def redeem(self, ctx):
        member = ctx.message.author
        self.database.execute(
            f"""INSERT OR REPLACE INTO member (_id, name, creation_date, last_used) values({member.id}, "{member.name}", null, "{str(datetime.datetime.utcnow())}");""")
        curr_object = self.database.execute(
            f"SELECT money_amount FROM gambler_stat WHERE _id={member.id}")

        money_retrieved = curr_object.fetchall()

        money_amount = money_retrieved[0][0] if len(money_retrieved) > 0 else 0

        self.database.execute(
            f"""INSERT OR REPLACE INTO gambler_stat (_id, money_amount, last_redeemed, total_gained) values({member.id}, {money_amount + 100}, "{str(datetime.datetime.utcnow())}", {money_amount + 100});""")

        await ctx.message.channel.send("You have redeemed $100.")


def cog_unload(self):
    self.database.close()


def setup(bot):
    bot.add_cog(GamblerCog(bot))


def teardown(bot):
    bot.remove_cog(GamblerCog(bot))
