# UoA Helper Bot by WhackaWeasel

import json
import discord
from discord.ext import commands

with open("token.txt", 'r') as file:
    token = json.load(file)
# Set a prefix which allows the bot to recognise its own commands/help command is disabled to implement a custom one.
bot = commands.Bot(command_prefix='#', help_command=None)
# A list to store the created cogs to load sequentially on startup.
core_extensions = ['cogs.logger', 'cogs.lobby']


# The function to load the cogs on event: startup.
def load_extension():
    for cog in core_extensions:
        bot.load_extension(cog)
        print(f'* Extension {cog} has been loaded.')
    print('\n')


# First thing the bot runs.
@bot.event
async def on_ready():
    name, identity = bot.user.name, bot.user.id
    print(f"Logged in as - Name: {name}; ID: {identity}\n\nReady when you are.")
    # This is to see if you're running the correct version of discord.py.
    print("Using version: ", discord.__version__, "\n")
    # Loads the cogs available on start up.
    load_extension()


client = discord.Client()
# This is for your bot's token. Please keep this secure and hidden for security purposes.
bot.run(token)
