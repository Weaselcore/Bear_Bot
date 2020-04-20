# UoA Helper Bot by WhackaWeasel

import json
import discord
import time
import random
from discord.ext import commands

# Set a prefix which allows the bot to recognise its own commands/help command is disabled to implement a custom one.
bot = commands.Bot(command_prefix='#', help_command=None)

# Bot reads an external file for the token.

with open('token.json', 'r') as file_to_read:
    token = json.load(file_to_read)


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


@bot.command()
async def bamboozle(ctx):
    voice_channel_list, member_list, current_channel = [], [], ctx.author.voice.channel
    if ctx.author.guild_permissions.administrator is True:
        for channel in ctx.guild.channels:
            if channel.type == discord.ChannelType.voice and channel is not current_channel:
                voice_channel_list.append(channel)
        number_of_channels = len(voice_channel_list)
        for member in current_channel.members:
            member_list.append(member)
        for member_to_move in member_list:
            random_number = random.randrange(0, number_of_channels)
            await member_to_move.move_to(voice_channel_list[random_number])
        for member_to_move in member_list:
            await member_to_move.move_to(current_channel)
    else:
        print(f'{ctx.author.name} tried to use this command.')

client = discord.Client()
# This is for your bot's token. Please keep this secure and hidden for security purposes.
bot.run(token)
