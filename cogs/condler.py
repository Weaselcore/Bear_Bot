from discord.ext import commands
import json
import pathlib


class ConfigCog(commands.Cog, name='cogs.condler'):
    def __init__(self, bot):
        self.bot = bot
        self.ignored = ["__pycache__", "condler.py"]
        self.running = []

        # If config file is not found, it'll be dynamically generated.
        path_to_check = pathlib.Path.cwd() / 'config.json'
        if not pathlib.Path.exists(path_to_check):
            cog_folder = pathlib.Path.cwd()/'cogs'
            config = {}
            config["extension"] = {}
            # This portion will initialise the extension config.
            for file in cog_folder.iterdir():
                file = str(file)
                last_slash = file.rfind("/")
                file = file[last_slash+1:]
                if file not in self.ignored:
                    dot = file.rfind(".")
                    file = "cogs." + file[:dot]
                    config["extension"][file] = False
            # This portion will initialise the logger config.
            config["logger"] = {"interval": 15, "last_log": None}
            # This line will write the config dictionary to file.
            self.json_dump('config.json', config)
        else:
            # If config file is found, it'll see which extensions to run.
            config_dictionary = self.json_load('config.json')
            for key, value in config_dictionary['extension'].items():
                if value is True:
                    self.running.append(key)
                    print(f'{key} has been added to the extension list.')

        # After init, it will run the appropriate extensions.
        if len(self.running) == 0:
            print("* No extensions were loaded.")
        else:
            for cog in self.running:
                bot.load_extension(cog)
                print(f'* Extension "{cog}" has been loaded.')

    @staticmethod
    def json_load(file):
        with open(file, 'r') as file_to_read:
            data = json.load(file_to_read)
        file_to_read.close()
        return data

    @staticmethod
    def json_dump(file, payload):
        with open(file, 'w+') as file_to_write:
            json.dump(payload, file_to_write)
        file_to_write.close()

    @commands.command()
    async def unload(self, ctx, cog):
        cog = "cogs." + cog
        if cog in self.running:
            self.bot.unload_extension(cog)
            self.running.remove(cog)
            await ctx.channel.send(f'Extension "{cog}" has been unloaded.')
            print(f'* Extension "{cog}" has been unloaded.')
            cog_config_dict = self.json_load('config.json')
            for config, config_value in cog_config_dict['extension'].items():
                if config == cog:
                    cog_config_dict['extension'][config] = False
            self.json_dump('config.json', cog_config_dict)
        else:
            await ctx.channel.send('This extension is not currently running or does not exist.')

    @commands.command()
    async def load(self, ctx, cog):
        cog = "cogs." + cog
        if cog not in self.running:
            self.bot.load_extension(cog)
            self.running.append(cog)
            await ctx.channel.send(f'Extension "{cog}" has been loaded.')
            print(f'* Extension "{cog}" has been loaded.')
            cog_config_dict = self.json_load('config.json')
            for config, config_value in cog_config_dict['extension'].items():
                if config == cog:
                    cog_config_dict['extension'][config] = True
            self.json_dump('config.json', cog_config_dict)
        else:
            await ctx.channel.send('This extension is currently running or does not exist.')

    @commands.command()
    async def reload(self, ctx, cog):
        cog = "cogs." + cog
        try:
            self.bot.reload_extension(cog)
        except commands.ExtensionNotLoaded:
            await ctx.channel.send("Extension is currently not running.")
            print("* Extension reload failed. Reason: Extension not running.")


def setup(bot):
    bot.add_cog(ConfigCog(bot))


def teardown(bot):
    bot.remove_cog(ConfigCog(bot))
