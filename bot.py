# Christian Plus Server by WhackaWeasel

import json
import discord
import time
import random
import logging

from discord.ext import commands

# Added in 1.5 to enable members cache.
intents = discord.Intents.default()
intents.members = True

# Set a prefix which allows the bot to recognise its own commands/help command is disabled to implement a custom one.
bot = commands.Bot(command_prefix='#', help_command=None, intents=intents)

# Bot reads an external file for the token.

with open('token.json', 'r') as file_to_read:
    token = json.load(file_to_read)

# Sick of lack of warnings, this initialises logging to file.
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
console.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# Allow logs to print to console.
logging.getLogger('discord').addHandler(console)


# First thing the bot runs.
@bot.event
async def on_ready():
    name, identity = bot.user.name, bot.user.id
    print(f"Logged in as - Name: {name}; ID: {identity}\n\nReady when you are.")
    # This is to see if you're running the correct version of discord.py.
    print("Using version: ", discord.__version__, "\n")
    # Loads the handler for the config and will load the appropriate extensions.
    bot.load_extension("cogs.condler")


@bot.command(aliases=["quit", "shutdown"])
@commands.has_permissions(administrator=True)
async def close(ctx):
    logger.info('Close function invoked. Shutting down and logging out gracefully.')
    await ctx.bot.logout()


@bot.command()
async def ping(ctx):
    await ctx.channel.send(f'PONG: {time.ctime()} ')


# Rewrite this function. You're better than this.
"""
@bot.command()
async def bamboozle(ctx):

    # Use first order functions to zip and move members.

    voice_channel_list, member_list, current_channel = [], [], ctx.author.voice.channel
    if ctx.author.guild_permissions.administrator is True:
        for channel in ctx.guild.channels:
            if channel.type == discord.ChannelType.voice and (channel is not current_channel and channel.name != "Bear's Secret Hidey Hole"):
                voice_channel_list.append(channel)
        number_of_channels = len(voice_channel_list)
        for member in current_channel.members:
            member_list.append(member)
        for member_to_move in member_list:
            random_number = random.randrange(0, number_of_channels)
            await member_to_move.move_to(voice_channel_list[random_number])
            print(f"{member_to_move.name} has been moved to {voice_channel_list[random_number].name}")
        for member_to_move in member_list:
            await member_to_move.move_to(current_channel)
            print(f"{member_to_move.name} has returned to {current_channel.name}.")
    else:
        print(f'{ctx.author.name} tried to use this command.')
    """

client = discord.Client()
# This is for your bot's token. Please keep this secure and hidden for security purposes.
bot.run(token)
