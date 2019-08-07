# UoA Helper Bot by WhackaWeasel

import json
import discord
from discord.ext import commands

# Set a prefix which allows the bot to recognise its own commands/help command is disabled to implement a custom one.
bot = commands.Bot(command_prefix='#', help_command=None)


def json_load(file):
    with open(file, 'r') as file_to_read:
        data = json.load(file_to_read)
    file_to_read.close()
    return data


def json_dump(file, payload):
    with open(file, 'w+') as file_to_write:
        json.dump(payload, file_to_write)
    file_to_write.close()


token = json_load("token.json")


# A list to store the created cogs to load sequentially on startup.
extensions = []
config_dictionary = json_load('config.json')
for key, value in config_dictionary.items():
    if value is True:
        extensions.append(key)
        print(f'{key} has been added to the extension list.')


# The function to load the cogs on event: startup.
def load_extension():
    if len(extensions) == 0:
        print("* No extensions were loaded.")
    else:
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


@bot.command()
async def unload(ctx, cog):
    cog = "cogs." + cog
    if cog in extensions:
        bot.unload_extension(cog)
        extensions.remove(cog)
        await ctx.channel.send(f'Extension "{cog}" has been unloaded.')
        print(f'* Extension "{cog}" has been unloaded.')
        cog_config_dict = json_load('config.json')
        for config, config_value in cog_config_dict.items():
            if config == cog:
                cog_config_dict[config] = False
        json_dump('config.json', cog_config_dict)
    else:
        await ctx.channel.send('This extension is not currently running or does not exist.')


@bot.command()
async def load(ctx, cog):
    cog = "cogs." + cog
    if cog not in extensions:
        bot.load_extension(cog)
        extensions.append(cog)
        await ctx.channel.send(f'Extension "{cog}" has been loaded.')
        print(f'* Extension "{cog}" has been loaded.')
        cog_config_dict = json_load('config.json')
        for config, config_value in cog_config_dict.items():
            if config == cog:
                cog_config_dict[config] = True
        json_dump('config.json', cog_config_dict)
    else:
        await ctx.channel.send('This extension is currently running or does not exist.')


@bot.command()
async def reload(ctx, cog):
    cog = "cogs." + cog
    try:
        bot.reload_extension(cog)
    except commands.ExtensionNotLoaded:
        await ctx.channel.send("Extension is currently not running.")
        print("* Extension reload failed. Reason: Extension not running.")

client = discord.Client()
# This is for your bot's token. Please keep this secure and hidden for security purposes.
bot.run(token)
