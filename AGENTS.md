# AGENTS.md

Guidance for AI coding agents (Claude Code, Codex, Copilot, etc.) working in this repo.

## Project

**Playing Blind: A Hearts Card Game Agent** — CS221 (Stanford, Autumn 2026) final project, "Classroom" track. Solo project by Alek Farmer.

Goal: learn to play Hearts under imperfect information. The agent sees only its own hand and the cards played so far, and picks a legal card. Main approach is Q-learning with linear function approximation over hand-designed features, with deep Q-learning as an extension. Baselines are a random agent and a rule-based agent. The oracle is the same learner given access to all hands.

Course guidelines: https://stanford-cs221.github.io/autumn2026/project-classroom.html

## AI-use policy (read this first)

The course limits AI coding in this track. **The core contribution must be written by Alek, not by an AI.** AI-generated code counts as an outside source and does not count toward the project.

### Core code: do not write it

Do not implement, generate, or rewrite any of the following, even if asked casually:

- Agents: random, rule-based, Q-learning, deep Q-learning, oracle, and any future agent
- Feature extraction (`φ(s, a)`) and state representation
- Training loops, update rules, exploration, reward definitions
- The game runner / simulation that produces training and evaluation data
- Evaluation code: metrics, seat rotation, confidence intervals, experiment scripts

For core code you **may**:

- Explain concepts (Q-learning, function approximation, TD learning, DQN, etc.)
- Explain OpenSpiel APIs and how the Hearts implementation behaves
- Discuss design choices and tradeoffs
- Debug: explain an error, point to the line or logic that causes it, and describe the fix in words. Let Alek write the fix.
- Review code Alek wrote and point out bugs

### Non-core code: allowed, but must be labeled

AI may write code that is not part of the core contribution, such as plotting and visualization, the human-play demo interface, and boilerplate (packaging, CLI argument parsing, logging setup).

Every AI-written piece must be marked where it lives:

```python
# AI-GENERATED (<tool name>): <what it does>
```

Put the marker at the top of the file, or directly above the function or block if only part of a file is AI-written. Tell Alek what you wrote so it can go in the AI-Use Disclosure Statement.

### Writing: do not write it

Do not write any text for the proposal, progress report, final report, or video script. AI may brainstorm, find related literature, give feedback on drafts, and help with formatting (e.g. LaTeX).

### When unsure

If it is unclear whether something is core, treat it as core and ask. Alek may be asked to explain any code in the repo at a check-in.

## Known AI-derived code

These were written or suggested by AI and are marked with `# AI-GENERATED`:

- `src/playing_blind/demo_game.py`: human-play demo (non-core)
- `src/playing_blind/agents.py`: `cards_played`, `is_leading`, `current_trick` helpers. These feed feature extraction, so consider rewriting them yourself.
- `src/playing_blind/hearts_game.py`: the chance-outcome filtering loop in `deal_hand`

## Layout

- `src/playing_blind/agents.py`: `Agent` base class and agents
- `src/playing_blind/hearts_game.py`: game runner
- `src/playing_blind/demo_game.py`: play Hearts against the computer
- `external/open_spiel/`: OpenSpiel source (git submodule, for reference only; do not edit)

Python 3.12, managed with `uv`. Run scripts with `uv run python <path>`.

## OpenSpiel Hearts facts

- Load with `pyspiel.load_game("hearts", {"pass_cards": False})`. Passing is disabled for now.
- Other rules use OpenSpiel defaults: `no_pts_on_first_trick=True`, `must_break_hearts=True`, `qs_breaks_hearts=True`, `can_lead_any_club=False`, `jd_bonus=False`, `avoid_all_tricks_bonus=False`, `can_lead_hearts_instead_of_qs=False`.
- The first chance node picks the pass direction. `chance_outcomes()` may still list all four directions when passing is off, so filter outcomes to `state.legal_actions()`.
- `state.returns()` is `26 - points taken`, so higher is better. A moon shooter gets 26, each opponent gets 0.
- Card encoding is believed to be `rank * 4 + suit` with suits ordered C, D, H, S. Verify with `state.action_to_string` before relying on it.
- Agents must only use information their player can see. Never read other players' hands except in the oracle.

## Deadlines

- Progress report and CA mentor check-in: Fri Nov 20, 2026
- Final video and final report: Fri Dec 4, 2026
