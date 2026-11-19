CLUBS = 0
DIAMONDS = 1
HEARTS = 2
SPADES = 3
Q_SPADES = 43
NUM_SUITS = 4


def is_suit(card, suit):
    return (card % NUM_SUITS) == suit


def get_suit(cards, suit):
    return [c for c in cards if is_suit(c, suit)]
