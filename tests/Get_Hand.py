import unittest
from bblib.CardGames import Card


def get_hand(list_of_cards):
    total, has_ace = 0, 0
    for card in list_of_cards:
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


class GetHand(unittest.TestCase):

    def test_one_ace(self):
        list_of_cards = [Card(10, "Spades"), Card(10, "Clubs"), Card(1, "Hearts")]
        self.assertEqual(get_hand(list_of_cards), 21)

    def test_two_ace(self):
        list_of_cards = [Card(10, "Spades"), Card(9, "Clubs"), Card(2, "Hearts"), Card(1, "Hearts"), Card(1, "Diamonds")]
        self.assertEqual(get_hand(list_of_cards), 23)

    def test_three_ace(self):
        list_of_cards = [Card(10, "Spades"), Card(9, "Clubs"), Card(2, "Hearts"), Card(1, "Hearts"),
                         Card(1, "Diamonds"), Card(1, "Clubs")]
        self.assertEqual(get_hand(list_of_cards), 24)

    def test_one_ace_under_21(self):
        list_of_cards = [Card(10, "Spades"), Card(1, "Clubs")]
        self.assertEqual(get_hand(list_of_cards), 21)

    def test_two_aces(self):
        list_of_cards = [Card(1, "Spades"), Card(1, "Clubs")]
        self.assertEqual(get_hand(list_of_cards), 12)


if __name__ == '__main__':
    unittest.main()
