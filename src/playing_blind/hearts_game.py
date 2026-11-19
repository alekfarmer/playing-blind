from playing_blind.agents import (
    Agent,
    RandomAgent,
    ConservativeAgent,
    FunctionApproximationQLearningAgent,
)
import pyspiel
import random
from collections import defaultdict
import numpy as np
from copy import copy
from playing_blind.cards import *
import sys

DEBUGGING = False
NUM_PLAYERS = 4

MAX_SCORE = 26
NUM_TRICKS = 13


class State:
    def __init__(self, game) -> None:
        self.pyspiel_state = game.new_initial_state()
        self.cards_played = []
        self.scores = [0, 0, 0, 0]
        self.leading_suit = None
        self.current_trick = []

    def current_player(self):
        return self.pyspiel_state.current_player()

    def legal_actions(self):
        return self.pyspiel_state.legal_actions()

    def take_action(self, action):
        player_num = self.pyspiel_state.current_player()
        self.pyspiel_state.apply_action(action)
        self.parse_trick(action, player_num)

    def parse_trick(self, action, player_num):
        def get_trick_winner(trick):
            lead_suit = get_suit_of_card(trick[0])
            leading_suit_cards = get_cards_of_suit(trick, lead_suit)
            winner_index = trick.index(np.max(leading_suit_cards))
            return (winner_index + player_num + 1) % NUM_PLAYERS

        self.current_trick.append(action)
        if len(self.current_trick) < NUM_PLAYERS:
            if len(self.current_trick) == 1:
                self.leading_suit = action % NUM_SUITS
            return
        trick_cards = copy(self.current_trick)
        self.current_trick = []
        self.cards_played.extend(trick_cards)
        winner = get_trick_winner(trick_cards)
        self.scores[winner] += get_points_in_trick(trick_cards)
        # Check for shooting the moon
        if len(self.cards_played) == 52 and MAX_SCORE in self.scores:
            self.scores = [MAX_SCORE if s == 0 else 0 for s in self.scores]


class Hearts:

    def __init__(self, agents: list[Agent], seed=None, starting_index=None) -> None:
        self.seeded_random = random.Random(seed)
        self.agents: list[Agent] = [Agent("") for _ in range(NUM_PLAYERS)]
        if starting_index is None:
            player_order = self.seeded_random.sample(range(NUM_PLAYERS), NUM_PLAYERS)
        else:
            player_order = [(i + starting_index) % 4 for i in range(NUM_PLAYERS)]

        for player_num, agent in zip(player_order, agents):
            agent.set_player_num(player_num)
            self.agents[player_num] = agent

        game = pyspiel.load_game("hearts", {"pass_cards": False})
        self.state = State(game)
        self.deal_hand()

    def deal_hand(self):
        while self.state.pyspiel_state.is_chance_node():
            # AI-GENERATED (Claude): filter chance outcomes to legal actions and sample one
            legal = set(self.state.pyspiel_state.legal_actions())
            outcomes = [
                (a, p)
                for a, p in self.state.pyspiel_state.chance_outcomes()
                if a in legal
            ]
            actions, probs = zip(*outcomes)
            action = self.seeded_random.choices(actions, weights=probs)[0]
            self.state.pyspiel_state.apply_action(action)
        if DEBUGGING:
            print(self.state)

    def play_hand(self, training):
        while not self.state.pyspiel_state.is_terminal():
            player_num = self.state.pyspiel_state.current_player()
            agent = self.agents[player_num]
            action = agent.choose_action(self.state, training)
            if DEBUGGING:
                print(
                    f"{self.state.pyspiel_state.action_to_string(player_num, action)}"
                )
            self.state.take_action(action)
        for a in self.agents:
            a.end_hand(self.state, training)
        if DEBUGGING:
            print(self.state)
            print("---------Hand Over---------")
        score_dict = {}
        best_score = 0
        winners = []
        pyspiel_scores = self.state.pyspiel_state.returns()
        for pyspiel_score, state_score in zip(pyspiel_scores, self.state.scores):
            try:
                assert (MAX_SCORE - pyspiel_score) == state_score
            except AssertionError:
                print(f"pyspiel: {MAX_SCORE - pyspiel_score} != {state_score}")
                raise

        for player_num, score in enumerate(pyspiel_scores):
            agent = self.agents[player_num]
            if DEBUGGING:
                print(f"{agent.name}: {score}")
            score_dict[agent.name] = MAX_SCORE - score
            if score > best_score:
                winners = [agent.name]
                best_score = score
            elif score == best_score:
                winners.append(agent.name)

        if DEBUGGING:
            print("---------------------------")
        return score_dict, winners


def play_all_seats(agents, seed, training):
    mean_scores = {}
    mean_wins = {}
    for a in agents:
        mean_scores[a.name] = 0
        mean_wins[a.name] = 0

    for i in range(NUM_PLAYERS):
        game = Hearts(agents, seed=seed, starting_index=i)
        scores, winners = game.play_hand(training)
        for a in agents:
            mean_scores[a.name] += scores[a.name] / NUM_PLAYERS
        for winner in winners:
            mean_wins[winner] += 1 / (NUM_PLAYERS * len(winners))

    return mean_scores, mean_wins


def evaluate(agents, num_training, num_eval, seed=0):
    total_wins = defaultdict(list)
    total_score = defaultdict(list)

    for i in range(num_training):
        if DEBUGGING:
            print(f"-------Game {seed}--------")
        scores, wins = play_all_seats(agents, 1_000_000 + seed + i, True)

        for a in agents:
            total_wins[a.name].append(wins[a.name])
            total_score[a.name].append(scores[a.name])
    if num_training > 0:
        for a in agents:
            print(f"{a.name:20}", end="| ")
            mean = np.mean(total_wins[a.name])
            std = np.std(total_wins[a.name], ddof=1)
            ci = 1.96 * std / np.sqrt(num_training)
            print(f"win %: {mean:.1%} | +/- {ci:.2%}", end="| ")

            mean = np.mean(total_score[a.name])
            std = np.std(total_score[a.name], ddof=1)
            ci = 1.96 * std / np.sqrt(num_training)
            print(f"score: {mean:.2f} | +/- {ci:.3f}")
        print()

    total_wins = defaultdict(list)
    total_score = defaultdict(list)
    for i in range(num_eval):
        if DEBUGGING:
            print(f"-------Game {seed}--------")
        scores, wins = play_all_seats(agents, seed + i, False)

        for a in agents:
            total_wins[a.name].append(wins[a.name])
            total_score[a.name].append(scores[a.name])

    for a in agents:
        print(f"{a.name:20}", end="| ")
        mean = np.mean(total_wins[a.name])
        std = np.std(total_wins[a.name], ddof=1)
        ci = 1.96 * std / np.sqrt(num_eval)
        print(f"win %: {mean:.1%} | +/- {ci:.2%}", end="| ")

        mean = np.mean(total_score[a.name])
        std = np.std(total_score[a.name], ddof=1)
        ci = 1.96 * std / np.sqrt(num_eval)
        print(f"score: {mean:.2f} | +/- {ci:.3f}")


def baseline(num_iterations):
    ConservativeAgent1 = ConservativeAgent("ConservativeAgent1")
    RandomAgent1 = RandomAgent("RandomAgent1", 1)
    RandomAgent2 = RandomAgent("RandomAgent2", 2)
    RandomAgent3 = RandomAgent("RandomAgent3", 3)
    agents = [
        ConservativeAgent1,
        RandomAgent1,
        RandomAgent2,
        RandomAgent3,
    ]
    evaluate(agents, 0, num_iterations)


def q_learning():
    QLearningAgent = FunctionApproximationQLearningAgent("QLearningAgent1", 2)
    RandomAgent1 = RandomAgent("RandomAgent1", 1)
    RandomAgent2 = RandomAgent("RandomAgent2", 2)
    RandomAgent3 = RandomAgent("RandomAgent3", 3)
    agents = [
        QLearningAgent,
        RandomAgent1,
        RandomAgent2,
        RandomAgent3,
    ]
    evaluate(agents, 3000, 800)


if __name__ == "__main__":
    iterations = 100
    if len(sys.argv) < 2:
        iterations = 100
    elif len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    else:
        raise RuntimeError("Too many arguments")
    baseline(iterations)
    print()
    q_learning()
