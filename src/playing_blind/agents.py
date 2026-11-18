import random
import pyspiel

CLUBS = 0
DIAMONDS = 1
HEARTS = 2
SPADES = 3
NUM_SUITS = 4
Q_SPADES = 43


class Agent:
    def __init__(self, name) -> None:
        self.player_num = -1
        self.name = name

    def set_player_num(self, player_num):
        self.player_num = player_num

    def choose_action(self, state):
        raise NotImplementedError("choose_action not implemented")

    # AI-GENERATED (Claude): cards_played, is_leading, current_trick helpers
    def cards_played(self, state):
        # Non-chance actions only; with pass_cards=False these are all card plays
        return [
            pa.action
            for pa in state.full_history()
            if pa.player != pyspiel.PlayerId.CHANCE
        ]

    def is_leading(self, state):
        return len(self.cards_played(state)) % 4 == 0

    def current_trick(self, state):
        played = self.cards_played(state)
        n = len(played) % 4  # cards already played in this trick
        return played[len(played) - n :] if n else []

    def is_suit(self, action, suit):
        return (action % NUM_SUITS) == suit

    def get_suit(self, actions, suit):
        return [a for a in actions if self.is_suit(a, suit)]


class RandomAgent(Agent):
    def __init__(self, name, seed=None) -> None:
        super().__init__(name)
        self.seeded_random = random.Random(seed)

    def choose_action(self, state):
        assert state.current_player() == self.player_num
        legal_actions = state.legal_actions()
        return self.seeded_random.choice(legal_actions)


class ConservativeAgent(Agent):
    def choose_action(self, state):
        assert state.current_player() == self.player_num
        legal_actions = sorted(state.legal_actions())

        # If leading, play your lowest card
        if self.is_leading(state):
            return legal_actions[0]
        curr_trick = self.current_trick(state)

        lead_suit = curr_trick[0] % NUM_SUITS
        leading_suit_cards = self.get_suit(legal_actions, lead_suit)
        if leading_suit_cards:
            # If you have the suit, play your highest that will lose
            lead_suit_played_cards = self.get_suit(curr_trick, lead_suit)
            for action in reversed(leading_suit_cards):
                if action < max(lead_suit_played_cards):
                    return action
            # Else, play your lowest
            return leading_suit_cards[0]

        # Else, get rid of the Q of spades
        if Q_SPADES in legal_actions:
            return Q_SPADES

        # Else, get rid of your highest hearts
        hearts = self.get_suit(legal_actions, HEARTS)
        if hearts:
            return hearts[-1]

        # else get rid of your highest card
        return legal_actions[-1]
