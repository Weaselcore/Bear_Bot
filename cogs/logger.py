import asyncio
import datetime

import discord
# An asynchronous way of using MongoDB.
import motor.motor_asyncio
# needed to parse passwords with @ symbols.
import urllib
from discord.ext import commands, tasks
from bblib.ConfigUtil import *

# Default interval is 15 minutes.
# Initialised outside of class as a constant.
INTERVAL = get_config_option("logger", "interval")
print(f"* Interval loaded from config: {INTERVAL} minutes")


class LoggerCog(commands.Cog, name='logger'):
    def __init__(self, bot):
        self.bot = bot
        self.log_count = 0
        self.document_to_send = {}
        self.now, self.date, self.time = None, None, None
        self.last_log = None
        self.string_prefix = "[Logger]"

        token = json_load('mongodb_token.json')
        client = motor.motor_asyncio.AsyncIOMotorClient(
            f"mongodb+srv://{token['user']}:{urllib.parse.quote(token['password'])}@log-database-6fo4z.mongodb.net"
            f"/test?retryWrites=true&w=majority")
        self.db = client.discord_member_log

        self.log.start()

    # Create a generator function to give a member asynchronously.
    async def get_member_generator(self):
        for member in self.bot.guilds[0].members:
            yield member

    async def send_to_database(self):
        self.now = datetime.datetime.now().isoformat()
        self.date = datetime.date.today().strftime("%d/%m/%Y")
        self.time = datetime.datetime.now().strftime("%H:%M")
        self.document_to_send = {self.time: {}}
        collection = self.db[self.date]

        generator = self.get_member_generator()
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
        self.last_log = self.now
        change_config_option("logger", "last_log", self.last_log)
        print(f"* {self.string_prefix} A document with a dict length of {len(self.document_to_send[self.time])} has "
              f"been send to server.")

        if not result.acknowledged:
            print(" {self.string_prefix} Insertion of document failed.")
            return False
        else:
            self.last_log = self.now.__str__()
            return True

    @tasks.loop(reconnect=True, minutes=INTERVAL)
    async def log(self):
        print(self.log.next_iteration)
        result = await self.send_to_database()
        if result:
            # TODO fix logging checks in config file.
            change_config_option("logger", "last_log", self.last_log)
            print(f"* {self.string_prefix} Writing last log in configs.")

    @log.before_loop
    async def before_log(self):
        print(f'* {self.string_prefix} Waiting... Before collecting data.\n')
        time_to_log = await self.improved_check_time()
        time_difference = await self.return_difference(time_to_log)
        await self.bot.wait_until_ready()
        await asyncio.sleep(time_difference+1.5)

    @staticmethod
    async def improved_check_time():
        next_to_log_time = datetime.datetime.now()
        now = datetime.datetime.now()
        upper_boundary = 60
        steps = upper_boundary/INTERVAL
        result = (now.minute//INTERVAL) + 1

        if result == steps:
            next_to_log_time = now.replace(hour=now.hour+1, minute=0, second=0, microsecond=0)
        elif result < steps:
            next_to_log_time = now.replace(minute=result * INTERVAL, second=0, microsecond=0)

        change_config_option("logger", "next_log", next_to_log_time.isoformat())
        change_config_option("logger", "last_check", now.isoformat())
        return next_to_log_time

    async def return_difference(self, to_log_time):
        difference = to_log_time - datetime.datetime.now()
        print(f'** {self.string_prefix} Re-adjusting logging time by {difference.seconds} seconds.')
        return difference.seconds

    def cog_unload(self):
        self.log.cancel()


def setup(bot):
    bot.add_cog(LoggerCog(bot))


def teardown(bot):
    bot.remove_cog(LoggerCog(bot))
