from playing_blind.cards import *

import numpy as np

NUM_FEATURES = 8


def starter_features(state, action):
    bias = 1
    current_trick = state.current_trick + [action]
    wins_trick = int(will_card_win_trick(current_trick, action))
    points = wins_trick * get_points_in_trick(current_trick) / 26
    win_likelihood = len(current_trick) / 4 * wins_trick
    playing_q_spades = int(action == Q_SPADES and not wins_trick)
    dumping_points = int(is_suit(action, HEARTS) and not wins_trick)
    high_spade = int(
        is_suit(action, SPADES)
        and action > Q_SPADES
        and Q_SPADES not in state.cards_played
    )
    card_rank = (action // NUM_SUITS) / 12
    return np.array(
        [
            bias,
            wins_trick,
            points,
            win_likelihood,
            playing_q_spades,
            dumping_points,
            high_spade,
            card_rank,
        ]
    )
