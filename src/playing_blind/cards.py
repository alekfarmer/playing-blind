CLUBS = 0
DIAMONDS = 1
HEARTS = 2
SPADES = 3
Q_SPADES = 43
NUM_SUITS = 4


def is_suit(card, suit):
    return (card % NUM_SUITS) == suit


def get_cards_of_suit(cards, suit):
    return [c for c in cards if is_suit(c, suit)]


def get_suit_of_card(card):
    return card % NUM_SUITS


def get_points_in_trick(trick):
    points = len(get_cards_of_suit(trick, HEARTS))
    if Q_SPADES in trick:
        points += 13
    return points


def will_card_win_trick(trick, card):
    if trick == []:
        return True
    leading_suit = get_suit_of_card(trick[0])
    if get_suit_of_card(card) != leading_suit:
        return False

    potential_winners = get_cards_of_suit(trick, leading_suit)
    if card < max(potential_winners):
        return False
    return True
