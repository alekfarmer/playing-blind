from playing_blind.agents import Agent, RandomAgent, ConservativeAgent
import pyspiel
import random
from collections import defaultdict
import numpy as np

DEBUGGING = False
NUM_PLAYERS = 4

MAX_SCORE = 26


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

        self.game = pyspiel.load_game("hearts", {"pass_cards": False})
        self.state = self.game.new_initial_state()
        self.deal_hand()

    def deal_hand(self):
        while self.state.is_chance_node():
            # AI-GENERATED (Claude): filter chance outcomes to legal actions and sample one
            legal = set(self.state.legal_actions())
            outcomes = [(a, p) for a, p in self.state.chance_outcomes() if a in legal]
            actions, probs = zip(*outcomes)
            action = self.seeded_random.choices(actions, weights=probs)[0]
            self.state.apply_action(action)
        if DEBUGGING:
            print(self.state)

    def play_hand(self):
        while not self.state.is_terminal():
            player_num = self.state.current_player()
            agent = self.agents[player_num]
            action = agent.choose_action(self.state)
            if DEBUGGING:
                print(f"{self.state.action_to_string(player_num, action)}")
            self.state.apply_action(action)
        if DEBUGGING:
            print(self.state)
            print("---------Hand Over---------")
        score_dict = {}
        best_score = 0
        winners = []
        for player_num, score in enumerate(self.state.returns()):
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


def play_all_seats(agents, seed):
    mean_scores = {}
    mean_wins = {}
    for a in agents:
        mean_scores[a.name] = 0
        mean_wins[a.name] = 0

    for i in range(NUM_PLAYERS):
        game = Hearts(agents, seed=seed, starting_index=i)
        scores, winners = game.play_hand()
        for a in agents:
            mean_scores[a.name] += scores[a.name] / NUM_PLAYERS
        for winner in winners:
            mean_wins[winner] += 1 / (NUM_PLAYERS * len(winners))

    return mean_scores, mean_wins


def baseline():
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
    total_wins = defaultdict(list)
    total_score = defaultdict(list)
    num_games = 10000
    for seed in range(num_games):
        if DEBUGGING:
            print(f"-------Game {seed}--------")
        scores, wins = play_all_seats(agents, seed)

        for a in agents:
            total_wins[a.name].append(wins[a.name])
            total_score[a.name].append(scores[a.name])

    for a in agents:
        print(f"{a.name:20}", end="| ")
        mean = np.mean(total_wins[a.name])
        std = np.std(total_wins[a.name], ddof=1)
        ci = 1.96 * std / np.sqrt(num_games)
        print(f"win %: {mean:.1%} | +/- {ci:.4%}", end="| ")

        mean = np.mean(total_score[a.name])
        std = np.std(total_score[a.name], ddof=1)
        ci = 1.96 * std / np.sqrt(num_games)
        print(f"score: {mean:.2f} | +/- {ci:.4f}")


if __name__ == "__main__":
    baseline()
