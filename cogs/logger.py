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

        with open('mongodb_token.json', 'r') as file_to_read:
            token = json.load(file_to_read)
        client = motor.motor_asyncio.AsyncIOMotorClient(
            f"mongodb+srv://{token['user']}:{urllib.parse.quote(token['password'])}@log-database-6fo4z.mongodb.net/test?retryWrites=true&w=majority")
        self.db = client.discord_member_log

        self.log.start()

    # TODO: Create a function that can read the log and display it in a suitable format.
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

    async def get_member(self):
        for member in self.bot.guilds[0].members:
            yield member

    async def send_to_database(self):
        now = datetime.datetime.utcnow()
        generator = self.get_member()
        async for member in generator:
            print(member.name)
            if member.status != discord.Status.offline and member.bot is False:
                self.db.logs.insert_one({"date": str(now),
                                               "id": member.id,
                                               "name": f'{member.name}#{member.discriminator}',
                                               "nickname": member.nick,
                                               "status": member.status.name})

    async def do_log(self):
        online_count, total_count, bot_count = 0, 0, 0
        self.log_count = self.log_count + 1
        print(f'Log: {self.log_count}')
        log_list, data, now, guild = [], [], datetime.datetime.utcnow(), self.bot.get_guild(299536709778014210)
        date, current_time = now.strftime('%d/%m/%y'), now.strftime('%H:%M')
        for member in self.bot.get_all_members():
            total_count = total_count + 1
            if member.bot is True:
                bot_count = bot_count + 1
            elif member.status != discord.Status.offline:
                online_count = online_count + 1
                data.append([date, current_time, member.id])
                result = await self.db.logs.insert_one({"date": str(now),
                                                        "id": member.id,
                                                        "name": f'{member.name}#{member.discriminator}',
                                                        "nickname": member.nick,
                                                        "status": member.status.name})
                print(result)
        self.csv_file_write(data)

        print(f'{current_time} - {date}:')
        print(
            f'* Data written, {online_count}/{total_count} online out of total members, with {bot_count} bot excluded.\n')

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


def setup(bot):
    bot.add_cog(LoggerCog(bot))


def teardown(bot):
    bot.remove_cog(LoggerCog(bot))
