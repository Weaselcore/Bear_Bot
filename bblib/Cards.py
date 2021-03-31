from random import shuffle
from PIL import Image

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

    def get_suit(self):
        return self.suit

    def get_image_name(self):
        value = self.get_name()
        suit = self.get_suit()
        name_tuple = None
        if value == 'Ace':
            name_tuple = ('A', suit[:1],)
        elif value == 'Jack':
            name_tuple = ('J', suit[:1],)
        elif value == 'Queen':
            name_tuple = ('Q', suit[:1],)
        elif value == 'King':
            name_tuple = ('K', suit[:1],)
        else:
            name_tuple = (str(value), suit[:1])
        return '{}{}.png'.format(*name_tuple)

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
        self.stand = False
        self.hand, self.dealer = [], []
        self.deck = [Card(rank, suit) for suit in suits for rank in range(1, 14)] * 8
        for i in range(0, 5):
            shuffle(self.deck)
        self.deal()
        self.deal(dealer=True)

    def deal(self, dealer=False):
        if dealer and self.get_hand(dealer=True) < 17:
            self.dealer.append(self.deck.pop())
        else:
            self.hand.append(self.deck.pop())

    def get_hand(self, dealer=False):
        total, has_ace = 0, 0
        hand_to_check = self.dealer if dealer is True else self.hand
        for card in hand_to_check:
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

    def is_bust(self):
        if self.bust is True:
            return True
        else:
            return False

    def set_stand(self) -> None:
        self.stand = True

    def is_stand(self) -> bool:
        return self.stand

    def conclusion(self) -> tuple[bool, str]:
        if self.get_hand() > self.get_hand(dealer=True) and self.get_hand(dealer=True) < 22:
            return True, "You have beaten the dealer",
        else:
            return False, "You have lost to dealer",

    def get_hand_cards(self):
        return str(self.hand)

    def get_dealer_cards(self):
        return str(self.dealer)

    def construct_image(self):
        # Get base mat design.
        root_path = 'resources/card_images/'
        padding, old_position, card_count = 50, 0, 0
        base_mat = Image.open(root_path + 'card_mat.png')
        base_mat = base_mat.copy()
        for card in self.hand:
            file_name = card.get_image_name()
            card = Image.open(root_path + file_name)
            if card_count == 0:
                position = ((old_position + padding), padding)
            else:
                position = ((old_position + padding + card.width), padding)
            base_mat.paste(card, position)
            old_position = position[0]
            card_count += 1
        return base_mat









