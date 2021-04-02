from random import shuffle
from PIL import Image

from bblib import Util
from bblib.Util import update_money

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


class BlackJackSession:
    def __init__(self, member):
        self.member = member
        self.bust = False
        self.stand = False
        self.double = False
        self.turn = 0
        self.hand, self.dealer = [], []
        self.jackpot = 0
        self.add_jackpot(25)

        self.deck = [Card(rank, suit) for suit in suits for rank in range(1, 14)] * 8
        for i in range(0, 5):
            shuffle(self.deck)

        self.deal()
        self.deal(dealer=True)

    def deal(self, dealer=False):
        if dealer and self.get_hand(dealer=True) < 17:
            self.dealer.append(self.deck.pop())
        elif dealer is False:
            self.hand.append(self.deck.pop())
            self.turn += 1

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
        for i in range(0, has_ace):
            if total > 21:
                total -= 10
        return total

    def add_jackpot(self, bet):
        money_amount = Util.get_money(self.member.id)
        # Member's wallet is updated at the end of the session and so must be checked against the jackpot.
        money_amount = money_amount - self.jackpot
        if money_amount == 0:
            return False
        elif bet > money_amount:
            self.jackpot += money_amount
            return True
        else:
            self.jackpot += bet
            return True

    def gain_money(self):
        update_money(self.member, self.jackpot * 2, add_wallet=True, banking=False)

    def lose_money(self):
        update_money(self.member, self.jackpot, add_wallet=False, banking=False)

    def double_down(self):
        self.jackpot = self.jackpot + 25
        self.stand = True

    def check_bust(self):
        if self.get_hand() > 21:
            self.bust = True
            return True
        else:
            return False

    def set_stand(self) -> None:
        self.stand = True

    def is_stand(self) -> bool:
        return self.stand

    def set_double(self) -> None:
        self.double = True

    def get_double(self) -> bool:
        return self.double

    def get_hand_cards(self):
        return str(self.hand)

    def get_dealer_cards(self):
        return str(self.dealer)

    def construct_image(self, dealer=False):
        # Get base mat design.
        root_path = 'resources/card_images/'
        padding, old_position, card_count = 50, 0, 0
        base_mat = Image.open(root_path + 'card_mat.png')
        base_mat = base_mat.copy()

        hand_to_check = self.hand if dealer is False else self.dealer

        first_card = True

        for card in hand_to_check:
            if dealer and (not self.check_bust() and not self.is_stand()) and first_card:
                file_name = 'red_back.png'
            else:
                file_name = card.get_image_name()
            card = Image.open(root_path + file_name)
            if card_count == 0:
                position = ((old_position + padding), padding)
            else:
                position = ((old_position + padding + card.width), padding)
            base_mat.paste(card, position, card)
            old_position = position[0]
            card_count += 1
            first_card = False
        return base_mat

    def check_condition(self):
        hand_value = self.get_hand()

        # Hand is bigger than 21; bust.
        if hand_value > 21:
            self.lose_money()
            return "Bust, better luck next time."
        # Hand is 21 and lower than dealer.
        elif hand_value == 21 and self.get_hand(dealer=True) < 22:
            self.gain_money()
            return "Blackjack! You win!"
        # Hand is lower than 21 and higher than dealer.
        elif 21 >= hand_value > self.get_hand(dealer=True):
            self.gain_money()
            return "You have beaten the dealer!"
        # Hand is under 21 and has 5 cards.
        elif 21 >= hand_value >= self.get_hand(dealer=True) and len(self.hand) == 5:
            self.gain_money()
            return "Five Card Charlie! You win!"
        # Hand is equal to dealer's, dealer is lower than 22.
        elif self.get_hand() == self.get_hand(dealer=True) and self.get_hand() > 22:
            return "Push, no one wins."
        else:
            self.lose_money()
            return "You have lost against the dealer!"
