import time


class Lobby:
    def __init__(self, ctx, game, description, number, duration):
        self._ctx = ctx
        self._lobby = [ctx.author.name]
        self._lobby_channel = ctx.channel
        self._lobby_owner = ctx.author.name
        self._game_name = game
        self._description = description
        self._capacity = int(number)
        self._lobby_duration = int(duration) * 60
        self._start_time = time.time()
        self._full = None
        self._message_id = None
        self._previous_duration = None

    def add_member(self, member_to_add):
        if len(self._lobby) == self._capacity:
            return "full"
        elif member_to_add not in self._lobby:
            self._lobby.append(member_to_add)
            if len(self._lobby) == self._capacity:
                self._previous_duration = ((self._start_time + self._lobby_duration) - time.time())
                self._start_time = time.time()
                self._lobby_duration = 60
                return None
            else:
                return True
        else:
            return False

    def remove_member(self, member_to_remove):
        if len(self._lobby) != 1:
            if member_to_remove in self._lobby:
                self._lobby.remove(member_to_remove)
                if member_to_remove == self.return_owner():
                    self._lobby_owner = self._lobby[0]
                return [True, f"{member_to_remove} has been removed from {self._lobby_owner}'s' lobby."]
            else:
                return [False, "You were never in a lobby."]
        elif member_to_remove not in self.return_player_list():
            return [False, "Mentioned player is not in the lobby."]
        else:
            return [None, "You have deleted your own lobby."]

    def to_delete_check(self):
        return (self._start_time + self._lobby_duration) > time.time()

    def return_owner(self):
        return self._lobby_owner

    def return_game(self):
        return self._game_name

    def return_player_count(self):
        return len(self._lobby)

    def return_time(self):
        base_time = ((self._start_time + self._lobby_duration) - time.time())
        return time.strftime('%H:%M:%S', time.gmtime(base_time))

    def update_time(self, message):
        self._lobby_duration = message * 60

    def return_channel(self):
        return self._lobby_channel

    def return_player_list(self):
        return self._lobby

    def return_capacity(self):
        return self._capacity

    def update_capacity(self, new_capacity):
        if new_capacity <= self._capacity:
            self._previous_duration = ((self._start_time + self._lobby_duration) - time.time())
            self._start_time = time.time()
            self._lobby_duration = 60
        elif new_capacity > self._capacity:
            self._lobby_duration = self._lobby_duration
        else:
            self._capacity = new_capacity

    def return_players(self):
        string = ""
        for player in self._lobby:
            string += player + ", "
        return string

    def return_ctx(self):
        return self._ctx

    def return_message(self):
        return self._message_id

    def update_message(self, message):
        self._message_id = message

    def return_description(self):
        return self._description

    def update_description(self, message):
        self._description = message

    def __str__(self):
        return f'{self._lobby_owner}, {self._game_name}, {self.return_player_count()}/{self._capacity + 1}, {self.return_time()}, {self.return_players()}'
