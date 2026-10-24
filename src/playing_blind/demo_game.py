import random
import pyspiel

game = pyspiel.load_game("hearts")

state = game.new_initial_state()
HUMAN = 0

while not state.is_terminal():
    if state.is_chance_node():  # dealing / choosing the pass direction
        actions, probs = zip(*state.chance_outcomes())
        state.apply_action(random.choices(actions, probs)[0])
        continue

    player = state.current_player()
    legal = state.legal_actions()
    if player == HUMAN:
        print(state)
        for i, a in enumerate(legal):
            print(f"  [{i}] {state.action_to_string(player, a)}")
        action = legal[int(input("Your move: "))]
    else:
        action = random.choice(legal)
    state.apply_action(action)

print(state)
print("Returns:", state.returns())