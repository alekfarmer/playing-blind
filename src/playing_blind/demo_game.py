# AI-GENERATED (Claude): human-play Hearts demo against random opponents (non-core)
import random
import pyspiel

# game = pyspiel.load_game("hearts")

game = pyspiel.load_game("hearts", {"pass_cards": False})
state = game.new_initial_state()
HUMAN = 0

def cards_played(state):
    # Non-chance actions only; with pass_cards=False these are all card plays
    return [pa.action for pa in state.full_history()
            if pa.player != pyspiel.PlayerId.CHANCE]

def is_leading(state):
    return len(cards_played(state)) % 4 == 0

# C -> D -> H -> S

while not state.is_terminal():
    player = state.current_player()
    if state.is_chance_node():  # dealing / choosing the pass direction
        # actions, probs = zip(*state.chance_outcomes())
        # state.apply_action(random.choices(actions, probs)[0])
        # continue
        legal = set(state.legal_actions())
        outcomes = [(a, p) for a, p in state.chance_outcomes() if a in legal]
        actions, probs = zip(*outcomes)
        action = random.choices(actions, weights=probs)[0]
        print(f"  [{action}] {state.action_to_string(player, action)}")
        state.apply_action(action)



    legal = state.legal_actions()
    # print(state)
    # print(is_leading(state))
    # print(player)
    if player == HUMAN:
        print(state)
        for i, a in enumerate(legal):
            print(a)
            print(f"  [{i}] {state.action_to_string(player, a)}")
        action = legal[int(input("Your move: "))]
    else:
        action = random.choice(legal)
    state.apply_action(action)

print(state)
print("Returns:", state.returns())


