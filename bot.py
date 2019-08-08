# UoA Helper Bot by WhackaWeasel

import json
import discord
import time
from discord.ext import commands

# Set a prefix which allows the bot to recognise its own commands/help command is disabled to implement a custom one.
bot = commands.Bot(command_prefix='#', help_command=None)

# Bot reads an external file for the token.
with open('token.json', 'r') as file_to_read:
    token = json.load(file_to_read)
file_to_read.close()

# First thing the bot runs.
@bot.event
async def on_ready():
    name, identity = bot.user.name, bot.user.id
    print(f"Logged in as - Name: {name}; ID: {identity}\n\nReady when you are.")
    # This is to see if you're running the correct version of discord.py.
    print("Using version: ", discord.__version__, "\n")
    # Loads the handler for the config and will load the appropriate extensions.
    bot.load_extension("cogs.condler")


@bot.command()
async def ping(ctx):
    await ctx.channel.send(f'PONG: {time.ctime()} ')

"""
@bot.command()
async def bamboozle(ctx):
    voice_channels = []
    for channel in bot.get_all_channels():
        if channel.type is discord.ChannelType.voice:
            voice_channels.append(channel)
    await ctx.channel.send(voice_channels)
    current_channel = ctx.channel
    for member in current_channel."""


client = discord.Client()
# This is for your bot's token. Please keep this secure and hidden for security purposes.
bot.run(token)
