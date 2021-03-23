from random import shuffle

suits = ("Spades", "Hearts", "Clubs", "Diamonds")


class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def get_name(self):
        if self.rank == 1:
            rank = "Ace"
        elif self.rank == 11:
            rank = "Jack"
        elif self.rank == 12:
            rank = "Queen"
        elif self.rank == 13:
            rank = "King"
        else:
            rank = str(self.rank)
        return rank

    def get_value(self):
        return self.rank

    def __repr__(self):
        return str([self.get_name(), self.suit, ])


# Example code to load images into an embed from local file.
# embed = discord.Embed(title="Title", description="Desc", color=0x00ff00) #creates embed
# file = discord.File("path/to/image/file.png", filename="image.png")
# embed.set_image(url="attachment://image.png")
# await ctx.send(file=file, embed=embed)


class BlackJackSession:
    def __init__(self):
        self.bust = False
        self.hand, self.dealer = [], []
        self.deck = [Card(rank, suit) for suit in suits for rank in range(1, 14)]
        for i in range(0, 5):
            shuffle(self.deck)
        self.deal()

    def deal(self):
        self.hand.append(self.deck.pop())
        self.dealer.append(self.deck.pop())
        self.hand.append(self.deck.pop())
        self.dealer.append(self.deck.pop())

    def conclusion(self):
        if self.bust:
            return False
        elif self.get_hand_value() > self.get_dealer_value():
            return True
        else:
            return False

    def get_hand_value(self):
        total = 0
        has_ace = 0
        for card in self.hand:
            name = card.get_name()
            value = card.get_value()
            if name == "Jack" or name == "Queen" or name == "King":
                total += 10
            elif name == "Ace":
                total += 11
                has_ace += 1
            else:
                total += value
        # Adjust for the amount of aces in hand.
        for i in range(1, has_ace):
            if total > 21:
                total -= 10
        if total > 21:
            self.bust = True
        return total

    def get_dealer_value(self):
        total = 0
        has_ace = 0
        for card in self.dealer:
            name = card.get_name()
            value = card.get_value()
            if name == "Jack" or name == "Queen" or name == "King":
                total += 10
            elif name == "Ace":
                total += 11
                has_ace += 1
            else:
                total += value
        # Adjust for the amount of aces in hand.
        for i in range(1, has_ace):
            if total > 21:
                total -= 10
        if total > 21:
            self.bust = True
        return total

    def get_hand_cards(self):
        return str(self.hand)

    def get_dealer_cards(self):
        return str(self.dealer)
