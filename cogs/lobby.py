import asyncio
import discord
from discord.ext import commands, tasks
from UnorderedListClass import UnorderedList
from LobbyClass import Lobby
from EmbedClass import GameEmbed, ResponseEmbed
from discord.ext.commands import cooldown


class LobbyCog(commands.Cog, name='lobby'):
    def __init__(self, bot):
        self.bot = bot
        self.lobby_list = UnorderedList()
        self.lobby_manager.start()
        self.default_message_lifespan = 30

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await self.manage(message=error, channel=ctx.message.channel)
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.manage(message=f"Please add arguments after this command.", channel=ctx.message.channel)

    @staticmethod
    async def return_embed_elements(lobby):
        embed = GameEmbed(lobby[0], lobby[1], lobby[2], lobby[3], lobby[4], lobby[5])
        return embed.create_game_embed()

    @staticmethod
    async def purge_lobby_thread(channel):
        deleted_messages = await channel.purge(limit=100)
        deletion_count = len(deleted_messages)
        if deletion_count != 0:
            print(f'{deletion_count} messages has been deleted.')

    async def manage(self, message=None, channel=None, embed=None):
        if channel is not None:
            if embed is not None:
                msg = await channel.send(embed=embed)
            else:
                msg = await channel.send(message)
            await msg.delete(delay=self.default_message_lifespan)
        else:
            await message.delete(delay=self.default_message_lifespan)

    async def update_presence(self):
        if len(self.lobby_list) == 1:
            update = f"{len(self.lobby_list)} lobby"
        else:
            update = f"{len(self.lobby_list)} lobbies"
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=update))

    async def update_messages(self, channel):
        for number in range(len(self.lobby_list)):
            print("Now updating")
            lobby = self.lobby_list.index(number)
            lobby_data = self.lobby_list[number]
            result = lobby.to_delete_check()
            if result:
                embed = await self.return_embed_elements(lobby_data)
                await channel.send(embed=embed)
            else:
                channel = lobby.return_channel()
                owner = lobby.return_owner()
                self.lobby_list.remove(lobby)
                await channel.send(f"{owner}'s lobby has expired and will be removed.")

    @tasks.loop(seconds=10.0, reconnect=True)
    async def lobby_manager(self):
        channel = self.bot.get_channel(591832432022388739)
        await self.purge_lobby_thread(channel)
        await self.update_messages(channel)
        await self.update_presence()

    @lobby_manager.before_loop
    async def before_lobby_manager(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @cooldown(1, 10)
    async def show_lobbies(self, ctx):
        await self.manage(message=ctx.message)
        count = len(self.lobby_list)
        if count == 0:
            await ctx.message.channel.send("There are no lobbies to display.")
        for number in range(count):
            lobby = self.lobby_list.index(number)
            owner, player_list = lobby.return_owner(), lobby.return_players()
            await self.manage(message=f"{owner}: [{player_list}]", channel=ctx.message.channel)

    @commands.command()
    @cooldown(1, 5)
    async def create(self, ctx):
        creator_name, channel = ctx.message.author.name, ctx.message.channel
        flag = False
        await self.manage(message=ctx.message)

        # Predicate function checks if input is valid.
        def check_name(user_input):
            return user_input.author.name == creator_name

        if len(self.lobby_list) != 0:
            for number in range(len(self.lobby_list)):
                lobby = self.lobby_list.index(number)
                if lobby.return_owner() == creator_name:
                    await self.manage(message="Sorry. You can only have one lobby running at a time.", channel=channel)
                    flag = True
                    break
                elif creator_name in lobby.return_player_list():
                    await self.manage(message="Sorry. Leave the lobby you're in to create a new lobby.",
                                      channel=channel)
                    flag = True
                    break
        if flag is False:
            bot_response = ResponseEmbed(
                "**Type:**     __Game Name__,      ,__Description__,     __# of People__ (*including you*), "
                "    __Duration__ (*minutes*)  ",
                '**\nExample: ```league of legends, Arams; Anyone welcome, 5, 60```**')
            embed = bot_response.create_embed()
            await self.manage(embed=embed, channel=channel)

            try:
                response_game_name = await self.bot.wait_for('message', check=check_name, timeout=25)
                await self.manage(message=response_game_name)
                message_list = response_game_name.content.split(",")
                count = 0
                if len(message_list) == 4:
                    for element in message_list:
                        new_element = element.strip()
                        if count >= 2:
                            try:
                                new_element = int(new_element)
                            except ValueError:
                                await self.manage(message="Please use numbers appropriately. Creation cancelled.",
                                                  channel=channel)
                                await self.manage(message=ctx.message)
                                break
                        message_list[count] = new_element
                        count += 1
                    if message_list[2] < 2 or message_list[3] < 1:
                        await self.manage(
                            message="Minimum lobby size is 2 and minimum time is 1 minute. Creation cancelled.",
                            channel=channel)
                    else:
                        creator_name = Lobby(ctx, message_list[0], message_list[1], message_list[2], message_list[3])
                        self.lobby_list.add(creator_name)
                        await self.manage(message="Lobby has been created.", channel=channel)
                await self.manage(message=ctx.message)
            except asyncio.TimeoutError:
                await self.manage(message='Creation Timeout', channel=channel)

    @commands.command()
    @cooldown(1, 5)
    async def join(self, ctx):
        await self.manage(message=ctx.message)
        channel = ctx.message.channel
        if len(ctx.message.mentions) == 0:
            await self.manage(message="You need to @ someone to join their lobby.", channel=channel)
        elif len(ctx.message.mentions) == 1:
            member = ctx.message.mentions[0].name
            if ctx.message.author.name == member:
                await self.manage(message="Sorry, you cannot join your own lobby", channel=channel)
            elif len(self.lobby_list) != 0:
                flag = True
                for number in range(len(self.lobby_list)):
                    lobby = self.lobby_list.index(number)
                    player_list = lobby.return_player_list()
                    if ctx.author.name is player_list[0]:
                        await self.manage(message="You cannot join a lobby if you're an owner of one.",
                                          channel=channel)
                        flag = False
                        break
                if flag:
                    for number in range(len(self.lobby_list)):
                        lobby = self.lobby_list.index(number)
                        if lobby.return_owner() == member:
                            result = lobby.add_member(ctx.author.name)
                            if result:
                                await self.manage(message="You've been added to the lobby.", channel=channel)
                            elif result is None:
                                await self.manage(message="Lobby full. Lobby will delete itself in 1 minutes.",
                                                  channel=channel)
                            elif result == "full":
                                await self.manage(message="Sorry. This lobby is full.", channel=channel)
                            elif result is False:
                                await self.manage(message="Sorry. That user does not have a lobby available.",
                                                  channel=channel)
            else:
                await self.manage(message="Sorry. That user does not have a lobby available.", channel=channel)
        else:
            await self.manage(message="You have mentioned too many people, bud.", channel=channel)

    @commands.command()
    @cooldown(1, 5)
    async def leave(self, ctx):
        channel = ctx.message.channel
        for number in range(len(self.lobby_list)):
            lobby = self.lobby_list.index(number)
            if ctx.author.name in lobby.return_player_list():
                result = lobby.remove_member(ctx.author.name)
                await self.manage(message=result[1], channel=channel)
                if result[0] is None:
                    self.lobby_list.remove(lobby)
        await self.manage(message=ctx.message)

    @commands.command()
    @cooldown(1, 5)
    async def size(self, ctx):
        await self.manage(message=ctx.message)
        channel = ctx.message.channel
        if len(self.lobby_list) != 0:
            for number in range(len(self.lobby_list)):
                lobby = self.lobby_list.index(number)
                if ctx.author.name in lobby.return_player_list():
                    msg = ctx.message.content.split()
                    if len(msg) == 2:
                        number = msg[1]
                        try:
                            number = int(number)
                            await self.manage(
                                message=f"Lobby's cap updated from {lobby.return_capacity()} to {number}.",
                                channel=channel)
                            lobby.update_capacity(number)
                        except ValueError:
                            await self.manage(message="Please use numbers.", channel=channel)
                            break
                    else:
                        await self.manage(message="Invalid input. Please try again.", channel=channel)
        else:
            await self.manage(message="You need to be an owner of a lobby to change the size.", channel=channel)

    @commands.command()
    @cooldown(1, 5)
    async def time(self, ctx, amount: int):
        await self.manage(message=ctx.message)
        channel = ctx.message.channel
        for number in range(len(self.lobby_list)):
            lobby = self.lobby_list.index(number)
            if ctx.author.name in lobby.return_player_list():
                await self.manage(
                    message=f"You have updated the lobby's capacity from {lobby.return_time()} to {amount}min.",
                    channel=channel)
                lobby.update_time(number * 60)
            else:
                await self.manage(message="Invalid input. Please try again.", channel=channel)

    @commands.command()
    @cooldown(1, 5)
    async def remove(self, ctx):
        await self.manage(message=ctx.message)
        channel = ctx.message.channel
        if len(ctx.message.mentions) == 1:
            for number in range(len(self.lobby_list)):
                lobby = self.lobby_list.index(number)
                lobby_owner = lobby.return_owner()
                member_to_remove = ctx.message.mentions[0].name
                if lobby_owner != ctx.author.name:
                    await self.manage(message="Sorry you need to be the lobby owner to remove a player.",
                                      channel=channel)
                else:
                    result = lobby.remove_member(member_to_remove)
                    if result[0] is None:
                        self.lobby_list.remove(lobby)
                    await self.manage(result[1], channel=channel)

    @commands.command()
    @cooldown(1, 5)
    async def show_all(self, ctx):
        channel = ctx.message.channel
        if len(self.lobby_list) == 0:
            await self.manage("There are no lobbies present at the moment, why not create one?", channel)
        else:
            for number in range(len(self.lobby_list)):
                lobby_data = self.lobby_list[number]
                embed = await self.return_embed_elements(lobby_data)
                await self.manage(embed=embed, channel=channel)

    @commands.command()
    @cooldown(1, 5)
    async def edit(self, ctx):
        await self.manage(message=ctx.message)
        channel, description = ctx.message.channel, ctx.message.content
        if len(self.lobby_list) == 0:
            await self.manage(message="Create a lobby to edit it's description.", channel=channel)
        else:
            for number in range(len(self.lobby_list)):
                lobby = self.lobby_list.index(number)
                if ctx.author.name == lobby.return_owner():
                    if len(description) > 6:
                        lobby.update_description(description[6:])
                        await self.manage(message="You have successfully updated your description.", channel=channel)
                    else:
                        await self.manage(message="Please type a description to replace your current description.",
                                          channel=channel)
                else:
                    await self.manage(message="Create a lobby first before editing it's description.", channel=channel)

    @commands.command()
    async def purge(self, ctx):
        channel = ctx.message.channel
        await self.manage(message=ctx.message)

        def is_bot(message):
            return message.author == self.bot.user

        deleted_messages = await ctx.channel.purge(limit=50, check=is_bot)

        if len(deleted_messages) != 0:
            await self.manage(message=f"You have delete {len(deleted_messages)} bot messages within this text channel.",
                              channel=channel)
        else:
            await self.manage(message="In the past 50 messages, there have been no bot messages found.",
                              channel=channel)

    @commands.command(name='help')
    async def help(self, ctx):
        await self.manage(message=ctx.message)
        channel = ctx.message.channel
        description = "#create - Command used to start lobby creation.\n" \
                      "#join *@user* - Command used to join someones lobby.\n" \
                      "#leave - Command used to a lobby. \n" \
                      "#size *number* - Command used to change the lobby capacity.\n" \
                      "#time *number* - Command used to change the lobby in minutes. \n" \
                      "#remove *@user* - Command used to remove a user in your lobby.\n"
        embed = ResponseEmbed(title="Help", description=description)
        await self.manage(channel=channel, embed=embed.create_embed())


def cog_unload(self):
    self.lobby_manager.cancel()


def setup(bot):
    bot.add_cog(LobbyCog(bot))


def teardown(bot):
    bot.remove_cog(LobbyCog(bot))
