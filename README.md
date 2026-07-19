# ⚡ Gradient Quest

**An interactive, gamified app that teaches neural networks and backpropagation from first principles — built on a custom scalar autograd engine (no PyTorch, no TensorFlow).**

Learn by *playing* through story chapters, quizzes, live training, and boss fights.

---

## Features

- **Custom autograd engine** — a `Value` class with reverse-mode automatic differentiation, `tanh` / `relu` / `sigmoid` / `exp`, and a topological-sort backward pass.
- **Neural nets from scratch** — `Neuron`, `Layer`, and `MLP` with configurable activations, built on the engine.
- **Playground** — step through the forward pass and watch gradients flow backward node-by-node with color coding on a rendered computation graph.
- **Story mode** — 6 themed chapters: Derivative Village → Graph Forest → Chain Rule Caverns → Backprop Temple → Neural Academy → MLP Fortress.
- **18 challenges** — quiz-style gradient questions verified against the real engine.
- **Live MLP training** — train on toy datasets with real-time Plotly loss charts.
- **Boss fights** — the Vanishing Gradient Dragon and Exploding Gradient Titan test your intuition about activations and gradient stability.
- **Duolingo-style progression** — XP, levels, badges, daily streaks, hearts, and a daily XP goal, persisted to JSON.

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Engine, neural nets, game logic |
| Streamlit | Multi-page UI |
| Graphviz | Computation-graph rendering |
| Plotly | Training loss & gradient-flow charts |

> **Note:** Graphviz rendering requires the Graphviz **system binaries** in addition to the Python package. Install from [graphviz.org/download](https://graphviz.org/download/) (e.g. `winget install graphviz` on Windows, `brew install graphviz` on macOS, `apt install graphviz` on Linux).

## Quick Start

Run all commands from the **workspace root** (the folder containing `requirements.txt`):

```bash
# 1. (Recommended) create and activate a virtual environment
python -m venv .venv
# Windows:     .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the app
python -m streamlit run gradient_quest/app.py
```

Streamlit opens the app in your browser (default: http://localhost:8501 or Live Demo: https://learngrad.onrender.com)

## Project Structure

```
.
├── requirements.txt              # Python dependencies
├── README.md
├── GameGuide.md
├── GradientQuest/
│   ├── app.py                    # Home dashboard (XP, streak, journey) + entry point
│   ├── engine/
│   │   ├── value.py              # Value — scalar autograd engine
│   │   └── nn.py                 # Module, Neuron, Layer, MLP
│   ├── visualization/
│   │   ├── graph.py              # Graphviz DAG rendering + trace
│   │   ├── forward_pass.py       # Topological order + per-node formulas
│   │   └── backprop.py           # Reverse-topo steps + gradient color coding
│   ├── game/
│   │   ├── story.py              # 6 chapter definitions
│   │   ├── challenges.py         # 18 quiz challenges
│   │   ├── bosses.py             # 2 boss-fight definitions
│   │   ├── xp.py                 # XP / level / badge / streak / hearts system
│   │   └── ui.py                 # Shared page chrome / styling
│   ├── pages/
│   │   ├── 01_learn.py           # Story + challenges (guided flow)
│   │   ├── 02_playground.py      # Step-through forward pass & backprop
│   │   ├── 03_train_mlp.py       # Live MLP training
│   │   └── 04_boss_fights.py     # Boss battles
│   └── data/
│       └── progress.json         # Player progress (local state)
└── tests/
    ├── test_value.py             # 16 tests — autograd correctness
    ├── test_nn.py                # 10 tests — MLP forward/backward
    ├── test_xp.py                # 11 tests — progression system
    ├── test_challenges.py        #  7 tests — challenge validation
    └── test_bosses.py            #  6 tests — boss-fight logic
```

## How It Works

### The engine

Every `Value` wraps a scalar, records the operation that produced it, and knows how to
push gradients to its inputs. Calling `.backward()` builds a topological order of the
graph and applies the chain rule in reverse.

```python
from engine.value import Value

a = Value(2.0, label='a')
b = Value(3.0, label='b')
c = a * b          # c.data = 6.0
d = c + 1          # d.data = 7.0

d.backward()       # populate gradients
print(a.grad)      # 3.0  -> dd/da = b
print(b.grad)      # 2.0  -> dd/db = a
```

Supported ops: `+`, `-`, `*`, `/`, `**` (int/float powers), unary `-`, and the
activations `tanh()`, `relu()`, `sigmoid()`, `exp()`.

### Building and training a network

```python
from engine.nn import MLP

model = MLP(2, [4, 4, 1])          # 2 inputs, two hidden layers of 4, 1 output
xs = [[0, 0], [0, 1], [1, 0], [1, 1]]
ys = [-1.0, 1.0, 1.0, -1.0]        # XOR-style targets

for epoch in range(100):
    ypred = [model(x) for x in xs]
    loss = sum((yp - yt) ** 2 for yp, yt in zip(ypred, ys))

    model.zero_grad()
    loss.backward()
    for p in model.parameters():
        p.data -= 0.05 * p.grad    # gradient descent step
```

Hidden layers use the chosen activation (`tanh` by default; `relu` / `sigmoid`
also supported); the output layer is linear.

### Progression system

- **Levels** are derived from total XP using the thresholds `[0, 50, 100, 200, 350, 500, 700, 1000]`.
- **Chapters** unlock as you earn XP (0 / 100 / 200 / 350 / 500 / 700).
- **Hearts** (max 3) are spent on wrong answers and refill daily.
- **Streaks** and a **daily XP goal** reward consistent practice.
- All state is stored in [GradientQuest/data/progress.json](GradientQuest/data/progress.json).

## Running the Tests

```bash
python -m pytest tests/ -v
# 50 tests
```

The tests validate autograd correctness against analytic derivatives, MLP
forward/backward behavior, the XP/progression logic, and that every quiz answer
matches what the engine actually computes.

## Inspired By

- The original scalar autograd engine and `Module` pattern.
- Extended here with additional activations (`tanh`, `sigmoid`, `exp`), configurable neurons, node labels for visualization, and a full gamified learning experience.