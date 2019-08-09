class Deck:
    def __init__(self):
        self.deck = []
        self.burned = []
        self.played = []
        suit_list = ["spades", "clubs", "diamonds", "hearts"]
        value_list = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king", "ace"]
        for value in value_list:
            for suit in suit_list:
                self.deck.append(value + "_of_" + suit)

    def print_deck(self):
        return self.deck
