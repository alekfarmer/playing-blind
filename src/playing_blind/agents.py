import random
from playing_blind.cards import *
import numpy as np
from playing_blind.features import *


class Agent:
    def __init__(self, name) -> None:
        self.player_num = -1
        self.name = name

    def set_player_num(self, player_num):
        self.player_num = player_num

    def choose_action(self, state, training):
        raise NotImplementedError("choose_action not implemented")

    def end_hand(self, state, trainging):
        pass


class RandomAgent(Agent):
    def __init__(self, name, seed=None) -> None:
        super().__init__(name)
        self.seeded_random = random.Random(seed)

    def choose_action(self, state, training):
        assert state.current_player() == self.player_num
        legal_actions = state.legal_actions()
        return self.seeded_random.choice(legal_actions)


class ConservativeAgent(Agent):
    def choose_action(self, state, training):
        assert state.current_player() == self.player_num
        legal_actions = sorted(state.legal_actions())

        # If leading, play your lowest card
        curr_trick = state.current_trick
        if curr_trick == []:
            return legal_actions[0]

        lead_suit = state.leading_suit
        assert lead_suit is not None

        leading_suit_cards = get_cards_of_suit(legal_actions, lead_suit)
        if leading_suit_cards:
            # If you have the suit, play your highest that will lose
            lead_suit_played_cards = get_cards_of_suit(curr_trick, lead_suit)
            for action in reversed(leading_suit_cards):
                if action < max(lead_suit_played_cards):
                    return action
            # Else, play your lowest
            return leading_suit_cards[0]

        # Else, get rid of the Q of spades
        if Q_SPADES in legal_actions:
            return Q_SPADES

        # Else, get rid of your highest hearts
        hearts = get_cards_of_suit(legal_actions, HEARTS)
        if hearts:
            return hearts[-1]

        # else get rid of your highest card
        return legal_actions[-1]


class FunctionApproximationQLearningAgent(Agent):
    def __init__(
        self,
        name,
        seed=None,
        feature_extractor=starter_features,
        discount: float = 1,
        exploration_prob: float = 0.2,
    ) -> None:
        super().__init__(name)
        self.seeded_random = random.Random(seed)
        self.feature_extractor = feature_extractor
        self.w = np.zeros(NUM_FEATURES)
        self.exploration_prob = exploration_prob
        self.discount = discount
        self.last_feature_vector = None
        self.last_points = 0
        self.step_size = 0.01

    def max_a_over_q(self, state):
        q_values = []
        features = []
        for a in state.legal_actions():
            feature = self.feature_extractor(state, a)
            q_value = feature @ self.w
            q_values.append(q_value)
            features.append(feature)
        best_a_index = np.argmax(q_values)
        action = state.legal_actions()[best_a_index]
        feature = features[best_a_index]
        q_value = q_values[best_a_index]
        return (action, feature, q_value)

    def end_hand(self, state, training):
        reward = -(state.scores[self.player_num] - self.last_points) / 26
        target = reward
        if training and self.last_feature_vector is not None:
            past_q_value = self.w @ self.last_feature_vector
            self.w += (
                self.step_size * (target - past_q_value) * self.last_feature_vector
            )
        self.last_points = 0
        self.last_feature_vector = None

    def choose_action(self, state, training) -> int:
        reward = -(state.scores[self.player_num] - self.last_points) / 26
        exploration_prob = self.exploration_prob

        action, feature, q_value = self.max_a_over_q(state)
        if training and self.seeded_random.random() < exploration_prob:
            action = self.seeded_random.choice(state.legal_actions())
            feature = self.feature_extractor(state, action)
        target = reward + self.discount * q_value

        if training and self.last_feature_vector is not None:
            past_q_value = self.w @ self.last_feature_vector
            self.w += (
                self.step_size * (target - past_q_value) * self.last_feature_vector
            )

        self.last_feature_vector = feature
        self.last_points = state.scores[self.player_num]
        return action
