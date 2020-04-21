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

# Default interval is 15 minutes.
with open('config.json', 'r') as file_to_read:
    config_dict = json.load(file_to_read)
    interval = config_dict["logger"]["interval"]
    print(f"* Interval: {interval}")


class LoggerCog(commands.Cog, name='logger'):
    def __init__(self, bot):
        self.bot = bot
        self.log_count = 0
        self.document_to_send = {}
        self.now = None
        self.date = None
        self.time = None

        config = self.json_load('config.json')
        self.last_log = config["logger"]["last_log"]

        token = self.json_load('mongodb_token.json')
        client = motor.motor_asyncio.AsyncIOMotorClient(
            f"mongodb+srv://{token['user']}:{urllib.parse.quote(token['password'])}@log-database-6fo4z.mongodb.net"
            f"/test?retryWrites=true&w=majority")
        self.db = client.discord_member_log

        self.log.start()

    @staticmethod
    def json_load(file):
        with open(file, 'r') as file_handler:
            data = json.load(file_handler)
        return data

    @staticmethod
    def json_dump(file, payload):
        with open(file, 'w+') as file_to_write:
            json.dump(payload, file_to_write, indent=4)

    @tasks.loop(minutes=interval, reconnect=True)
    async def log(self):
        to_log = await self.check_last_update()
        if to_log:
            result = await self.send_to_database()
            if result:
                config = self.json_load('config.json')
                config["logger"]["last_log"] = self.last_log
                self.json_dump("config.json", config)
                print("* Writing last log in configs.")

    async def check_last_update(self):
        present_time_obj = datetime.datetime.now()
        last_log_time_obj = datetime.datetime.fromisoformat(self.last_log)
        time_delta = present_time_obj - last_log_time_obj
        if 900 < time_delta.total_seconds():
            print("* Proceeding to log. \n")
            return True
        else:
            print(f"* It's been less than {interval} minutes since last log. \n")
            return False

    # Create a generator function to give a member asynchronously.
    async def get_member(self):
        for member in self.bot.guilds[0].members:
            yield member

    async def send_to_database(self):
        self.now = datetime.datetime.now().isoformat()
        self.date = datetime.date.today().strftime("%d/%m/%Y")
        self.time = datetime.datetime.now().strftime("%H:%M:%S")
        collection = None
        self.document_to_send[self.time] = {}

        if self.db.list_collection_names(filter={"name": self.now}):
            collection = self.db[self.date]

        generator = self.get_member()
        async for member in generator:
            if member.status != discord.Status.offline and member.bot is False:
                member_dict = {"id": member.id,
                               "name": f'{member.name}#{member.discriminator}',
                               "nickname": member.nick,
                               "status": member.status.name}
                self.document_to_send[self.time][member.name + '#' + member.discriminator] = member_dict

        self.document_to_send['length'] = len(self.document_to_send[self.time])
        self.document_to_send['datetime'] = self.now
        result = await collection.insert_one(self.document_to_send)
        print(f"A document with a dict length of {len(self.document_to_send[self.time])} has been send to server.")

        if not result.acknowledged:
            print("Insertion of document failed.")
            return False
        else:
            self.last_log = self.now.__str__()
            return True

    @log.before_loop
    async def before_log(self):
        print('* Waiting... Before collecting data.\n')
        await self.bot.wait_until_ready()

    def cog_unload(self):
        self.log.cancel()


def setup(bot):
    bot.add_cog(LoggerCog(bot))


def teardown(bot):
    bot.remove_cog(LoggerCog(bot))
