# We want a message queue that's easy to traverse and to search for the data.


class Node:
    def __init__(self, data):
        self._data = data
        self._next = None

    def get_data(self):
        return self._data

    def get_next(self):
        return self._next

    def set_data(self, new_data):
        self._data = new_data

    def set_next(self, new_next):
        self._next = new_next


class UnorderedList:
    def __init__(self):
        self._head = None

    def is_empty(self):
        return self._head is None

    def add(self, item):
        temp = Node(item)
        temp.set_next(self._head)
        self._head = temp

    def index(self, number):
        current = self._head
        count = 0
        while current is not None and count < number:
            current = current.get_next()
            count += 1
        return current.get_data()

    def remove(self, item):
        current = self._head
        previous = None
        found = False
        while not found:
            if current.get_data() == item:
                found = True
            else:
                previous = current
                current = current.get_next()

        if previous is None:
            self._head = current.get_next()
        else:
            previous.set_next(current.get_next())

    def append(self, item):
        current = self._head
        if current is None:
            self._head = Node(item)
        else:
            while current.next:
                current = current.next
            current.next = Node(item)

    def pop(self, position=None):
        if position is None:
            position = len(self)
        elif position < 0 or position >= len(self):
            raise ValueError("Position doesn't exist")
        current_pos = 0
        prev = None
        current = self._head
        while current.next and current_pos < position:
            prev = current
            current = current.next
            current_pos += 1
        if prev is None:
            self._head = current.next
        else:
            prev.next = current.next
        return current.data

    @staticmethod
    def extract_lobby_data(lobby):
        game = lobby.return_game()
        description = lobby.return_description()
        count = lobby.return_player_count()
        capacity = lobby.return_capacity()
        time = lobby.return_time()
        players = lobby.return_player_list()
        return [game, description, count, capacity, time, players]

    def __getitem__(self, index):
        lobby = self.index(index)
        lobby_data_list = self.extract_lobby_data(lobby)
        return lobby_data_list

    def __len__(self):
        current = self._head
        count = 0
        while current is not None:
            count += 1
            current = current.get_next()
        return count
