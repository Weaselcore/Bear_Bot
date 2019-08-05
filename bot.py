# UoA Helper Bot by WhackaWeasel

import json
import discord
from discord.ext import commands

# Set a prefix which allows the bot to recognise its own commands/help command is disabled to implement a custom one.
bot = commands.Bot(command_prefix='#', help_command=None)

with open("token.json", 'r') as token_file:
    token = json.load(token_file)

# A list to store the created cogs to load sequentially on startup.
extensions = []
with open('config.json', 'r') as config_file:
    config_dictionary = json.load(config_file)
    for key, value in config_dictionary.items():
        if value is True:
            extensions.append(key)
            print(f'{key} has been added to the extension list.')


# The function to load the cogs on event: startup.
def load_extension():
    for cog in extensions:
        bot.load_extension(cog)
        print(f'* Extension "{cog}" has been loaded.')


# First thing the bot runs.
@bot.event
async def on_ready():
    name, identity = bot.user.name, bot.user.id
    print(f"Logged in as - Name: {name}; ID: {identity}\n\nReady when you are.")
    # This is to see if you're running the correct version of discord.py.
    print("Using version: ", discord.__version__, "\n")
    # Loads the cogs available on start up.
    load_extension()

# TODO: Need to add commands to load/unload cogs and to update the config file.

client = discord.Client()
# This is for your bot's token. Please keep this secure and hidden for security purposes.
bot.run(token)
