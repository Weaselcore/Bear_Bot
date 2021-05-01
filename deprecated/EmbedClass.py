import discord


class GameEmbed:
    def __init__(self, game, description, current_players, max_players, time, players_list):
        self._apex_keywords = ["apex"]
        self._league_keywords = ["lol", "legend", "league"]
        self._csgo_keywords = ["csgo", "cs:go", "cs", "cs go"]
        self._overwatch_keywords = ["ow", "overwatch"]
        self._title = game
        self._description = description
        self._current_players = current_players
        self._maximum_players = max_players
        self._time = time
        self._players_list = players_list
        self._game_guess = self.guess_game()

    def guess_game(self):
        clean_string = (str(self._title.lower())).strip()
        name_list = clean_string.split(" ")
        for element in name_list:
            if element in self._apex_keywords:
                return 'apex'
            elif element in self._league_keywords:
                return 'league'
            elif element in self._csgo_keywords:
                return 'csgo'
            elif element in self._overwatch_keywords:
                return 'overwatch'
            else:
                return self._title

    def get_colour(self):
        game_guess = self._game_guess
        if game_guess == "apex":
            return discord.Colour.dark_red()
        elif game_guess == "league":
            return discord.Colour.dark_blue()
        elif game_guess == "csgo":
            return discord.Colour.gold()
        elif game_guess == "overwatch":
            return discord.Colour.greyple()
        else:
            return discord.Colour.default()

    def get_game(self):
        game_guess = self._game_guess
        if game_guess == 'apex':
            return 'Apex Legends'
        elif game_guess == 'league':
            return 'League of Legends'
        elif game_guess == 'csgo':
            return 'CS:GO'
        elif game_guess == 'overwatch':
            return 'Overwatch'
        else:
            return self._game_guess

    def analyse_time(self):
        time = self._time
        time = time.split(":")
        if time[0] == "00" and time[1] == "00":
            return f'{self._time} seconds remaining'
        elif time[0] == "00":
            return f'{self._time} minutes remaining'
        else:
            return f'{self._time} hours remaining'

    def get_url(self):
        game_guess = self._game_guess
        if game_guess in self._league_keywords:
            return "https://res.cloudinary.com/teepublic/image/private/s--SRABn1B---/t_Preview/b_rgb:191919,c_limit,f_jpg,h_630,q_90,w_630/v1539296610/production/designs/3303813_0.jpg"
        elif game_guess in self._apex_keywords:
            return "https://ih0.redbubble.net/image.747405197.6265/flat,550x550,075,f.u1.jpg"
        elif game_guess in self._csgo_keywords:
            return "https://images-wixmp-ed30a86b8c4ca887773594c2.wixmp.com/f/f6fd9b7b-364e-4cae-ac0a-cd5f7cd9781c/dbxa6pu-12dd02d0-7975-4894-b81b-2a7a6ae15a04.png?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1cm46YXBwOjdlMGQxODg5ODIyNjQzNzNhNWYwZDQxNWVhMGQyNmUwIiwiaXNzIjoidXJuOmFwcDo3ZTBkMTg4OTgyMjY0MzczYTVmMGQ0MTVlYTBkMjZlMCIsIm9iaiI6W1t7InBhdGgiOiJcL2ZcL2Y2ZmQ5YjdiLTM2NGUtNGNhZS1hYzBhLWNkNWY3Y2Q5NzgxY1wvZGJ4YTZwdS0xMmRkMDJkMC03OTc1LTQ4OTQtYjgxYi0yYTdhNmFlMTVhMDQucG5nIn1dXSwiYXVkIjpbInVybjpzZXJ2aWNlOmZpbGUuZG93bmxvYWQiXX0.pODiEmXBuPbHAb8g3mZleYnFpnvR6_1ZW3xW7AhZT8E"
        elif game_guess in self._overwatch_keywords:
            return "https://i.imgur.com/0RIw2RB.png"
        else:
            return 'https://via.placeholder.com/300'

    def get_slots(self):
        current = self._current_players
        maximum = self._maximum_players
        return (u"\U0001F535" * current) + (u"\u26AA" * (maximum - current))

    def create_game_embed(self):
        embed = discord.Embed(title=f'Game:       {self.get_game()}', color=self.get_colour())
        embed.set_author(name=f'Owner:   {self._players_list[0].upper()}')
        embed.set_thumbnail(url=self.get_url())
        embed.add_field(
            name=f'Slots:        {self._current_players} {self.get_slots()} {self._maximum_players - self._current_players}',
            value=f'\n_________________________________________', inline=False)
        embed.add_field(name=f'Description: \n{self._description.upper()}', value=self.analyse_time(), inline=True)
        embed.set_footer(text=f"Currently in lobby: {self._players_list}")
        return embed


class ResponseEmbed:
    def __init__(self, title, description):
        self._title = title
        self._description = description

    def create_embed(self):
        embed = discord.Embed(title=self._title,
                              description=self._description,
                              color=discord.Color.orange())
        return embed
