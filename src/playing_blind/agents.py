import random
import pyspiel
from playing_blind.cards import *


class Agent:
    def __init__(self, name) -> None:
        self.player_num = -1
        self.name = name

    def set_player_num(self, player_num):
        self.player_num = player_num

    def choose_action(self, state):
        raise NotImplementedError("choose_action not implemented")

    def end_hand(self, state):
        pass


class RandomAgent(Agent):
    def __init__(self, name, seed=None) -> None:
        super().__init__(name)
        self.seeded_random = random.Random(seed)

    def choose_action(self, state):
        assert state.pyspiel_state.current_player() == self.player_num
        legal_actions = state.pyspiel_state.legal_actions()
        return self.seeded_random.choice(legal_actions)


class ConservativeAgent(Agent):
    def choose_action(self, state):
        assert state.pyspiel_state.current_player() == self.player_num
        legal_actions = sorted(state.pyspiel_state.legal_actions())

        # If leading, play your lowest card
        curr_trick = state.current_trick
        if curr_trick == []:
            return legal_actions[0]

        lead_suit = state.leading_suit
        assert lead_suit is not None

        leading_suit_cards = get_suit(legal_actions, lead_suit)
        if leading_suit_cards:
            # If you have the suit, play your highest that will lose
            lead_suit_played_cards = get_suit(curr_trick, lead_suit)
            for action in reversed(leading_suit_cards):
                if action < max(lead_suit_played_cards):
                    return action
            # Else, play your lowest
            return leading_suit_cards[0]

        # Else, get rid of the Q of spades
        if Q_SPADES in legal_actions:
            return Q_SPADES

        # Else, get rid of your highest hearts
        hearts = get_suit(legal_actions, HEARTS)
        if hearts:
            return hearts[-1]

        # else get rid of your highest card
        return legal_actions[-1]


class QLearningAgent(Agent):
    def choose_action(self, state):
        return super().choose_action(state)
