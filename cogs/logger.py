import asyncio
import csv
import datetime
import json

import discord
import pathlib
# An asynchronous way of using MongoDB.
import motor.motor_asyncio
# needed to parse passwords with @ symbols.
import urllib
from discord.ext import commands, tasks


class LoggerCog(commands.Cog, name='logger'):
    def __init__(self, bot):
        self.bot = bot
        self.log_count = 0
        self.document_to_send = {}
        self.now = None
        self.date = None
        self.time = None

        with open('mongodb_token.json', 'r') as file_to_read:
            token = json.load(file_to_read)
        client = motor.motor_asyncio.AsyncIOMotorClient(
            f"mongodb+srv://{token['user']}:{urllib.parse.quote(token['password'])}@log-database-6fo4z.mongodb.net"
            f"/test?retryWrites=true&w=majority")

        self.db = client.discord_member_log
        self.log.start()

    @staticmethod
    def csv_file_read():
        with open('member_data.csv', newline='') as member_data:
            data_reader = csv.reader(member_data, delimiter=' ', quotechar="'")
            for row in data_reader:
                print(', '.join(row))
        member_data.close()

    @staticmethod
    def csv_file_write(data_dump):
        with open('member_data.csv', 'a', newline="") as member_data:
            data_writer = csv.writer(member_data, delimiter=' ', quotechar="'", quoting=csv.QUOTE_MINIMAL)
            data_writer.writerows(data_dump)
        member_data.close()

    @tasks.loop(minutes=30.0, reconnect=True)
    async def log(self):
        await self.send_to_database()

    # Create a generator function to give a member asynchronously.
    async def get_member(self):
        for member in self.bot.guilds[0].members:
            yield member

    async def send_to_database(self):
        self.now = datetime.datetime.utcnow()
        self.date = datetime.date.today().strftime("%d/%m/%Y")
        self.time = datetime.datetime.now().strftime("%H:%M:%S")
        collection = None
        self.document_to_send[self.time] = {}

        if self.db.list_collection_names(filter={"name": self.now}):
            collection = self.db[self.date]

        generator = self.get_member()
        async for member in generator:
            if member.status != discord.Status.offline and member.bot is False:
                print(member.name)
                member_dict = {"id": member.id,
                               "name": f'{member.name}#{member.discriminator}',
                               "nickname": member.nick,
                               "status": member.status.name}
                self.document_to_send[self.time][member.name + '#' + member.discriminator] = member_dict

        self.document_to_send['length'] = len(self.document_to_send[self.time])
        self.document_to_send['datetime'] = self.now
        result = await collection.insert_one(self.document_to_send)

        if not result.acknowledged:
            print("Insertion of document failed.")

    @log.before_loop
    async def before_log(self):
        print('* Waiting... Before collecting data.\n')
        path = pathlib.Path('member_data.csv')
        if path.exists() is False:
            new_file = open("member_data.csv", 'w')
            new_file.close()
            print("WARNING: Data collection log not found, generating new one.")
        else:
            print("Previous data collection found, new data will append to this file.\n")
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.log.cancel()

    @commands.command()
    async def last_log(self, ctx):
        


def setup(bot):
    bot.add_cog(LoggerCog(bot))


def teardown(bot):
    bot.remove_cog(LoggerCog(bot))
