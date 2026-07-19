# Gradient Quest — Game Guide

## How to Run

```bash
cd /path/to/GradientQuestGame
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run GradientQuest/app.py
```

A browser tab opens at `http://localhost:8501`.

---

## How to Play

### Progression Path (recommended order)

| Step | Where | What you do |
|------|-------|-------------|
| 1 | **Learn** | Start with Chapter 1 and complete the first challenge |
| 2 | **Playground** | Try a simple expression and inspect the computation graph |
| 3 | **Playground → Forward Pass** | Watch values compute step by step |
| 4 | **Playground → Backprop** | Watch gradients flow backward with color coding |
| 5 | **Learn** | Unlock later chapters by earning XP |
| 6 | **Train MLP** | Once comfortable, train a real network on XOR or a linear dataset |
| 7 | **Boss Fights** | Battle the Vanishing Gradient Dragon and Exploding Gradient Titan |
| 8 | **Home** | Check your level, badges, streak, hearts, and chapter progress |

---

## Navigation

- **Sidebar** (left panel) — lists the main app pages. Click any to switch.
- **Home page** — your dashboard with XP, streak, hearts, badges, and chapter progress.

### Pages

| Page | Purpose |
|------|---------|
| Home | Track XP, level, badges, streaks, hearts, and your journey |
| Learn | Work through chapters and answer one challenge at a time |
| Playground | Explore computation graphs, forward pass, and backprop animations |
| Train MLP | Train a neural network with the built-in autograd engine |
| Boss Fights | Battle bosses that teach gradient stability concepts |

---

## XP & Unlocks

| XP | Level | What unlocks |
|----|-------|--------------|
| 0 | 1 | Chapter 1: Derivative Village |
| 50 | 2 | — |
| 100 | 3 | Chapter 2: Graph Forest |
| 200 | 4 | Chapter 3: Chain Rule Caverns |
| 350 | 5 | Chapter 4: Backprop Temple |
| 500 | 6 | Chapter 5: Neural Academy |
| 700 | 7 | Chapter 6: MLP Fortress |
| 1000 | 8 | Max level |

---

## Earning XP

| Source | XP per action | Total available |
|--------|--------------|-----------------|
| Challenges (Ch 1-3) | 25-35 XP each | ~270 XP |
| Challenges (Ch 4-6) | 30-50 XP each | ~280 XP |
| Training MLP | +50 XP on convergence | 50 XP per run |
| Boss Fights | +100 XP per boss | 200 XP |

---

## Badges

| Badge | How to earn |
|-------|-------------|
| 🏅 Neural Trainer | Train MLP to convergence (loss < 1.0) |
| 🏅 Dragon Slayer | Defeat the Vanishing Gradient Dragon (choose ReLU) |
| 🏅 Titan Tamer | Defeat the Exploding Gradient Titan (choose gradient clipping) |

---

## Chapter Guide

### Chapter 1: Derivative Village (0 XP to unlock)
**Concepts:** Derivative, Slope, Sensitivity  
**Challenges:** f(x)=x² derivative, f(x)=3x derivative, f(x)=x³ derivative  
**Tip:** The derivative of x^n is n·x^(n-1)

### Chapter 2: Graph Forest (100 XP)
**Concepts:** Computational Graphs, Operations, Nodes  
**Challenges:** Computing values through graphs, counting operation nodes  
**Tip:** Use the Graph Explorer to type expressions and see the DAG

### Chapter 3: Chain Rule Caverns (200 XP)
**Concepts:** Local gradients, Chain Rule  
**Challenges:** dc/da for a*b, gradient accumulation when a node is used twice  
**Tip:** When a variable appears multiple times, its gradient accumulates (adds up)

### Chapter 4: Backprop Temple (350 XP)
**Concepts:** Backward pass, Gradient accumulation  
**Challenges:** Output gradient is always 1, addition passes gradient through, a+a gives grad=2  
**Tip:** Use the Backprop Simulator to watch gradients propagate step by step

### Chapter 5: Neural Academy (500 XP)
**Concepts:** Neuron, Activation functions  
**Challenges:** tanh(0)=0, ReLU(-3)=0, Tanh outputs negatives  
**Tip:** Tanh → [-1,1], Sigmoid → [0,1], ReLU → [0,∞)

### Chapter 6: MLP Fortress (700 XP)
**Concepts:** Networks, Training, Optimization  
**Challenges:** Parameter counting, training direction, learning rate effects  
**Tip:** [nin, hidden, out] → params = nin×hidden + hidden biases + hidden×out + out biases

---

## Boss Fight Tips

### Vanishing Gradient Dragon (Chapter 5)
- **Problem:** Gradients shrink to zero in deep networks
- **Wrong answers:** Sigmoid (saturates), Tanh (saturates)
- **Correct:** ReLU — gradient = 1 for positive inputs, never shrinks

### Exploding Gradient Titan (Chapter 6)
- **Problem:** Gradients grow uncontrollably with depth
- **Wrong answers:** Add more layers (makes it worse), Increase LR (makes it worse)
- **Correct:** Gradient clipping — caps the maximum gradient magnitude

---

## Playground Tips

### Graph tab
- Type any expression using `Value(number, label='name')`
- Example: `a = Value(2, label='a'); b = Value(3, label='b'); c = a * b`
- The graph will redraw automatically and show node details such as value, gradient, and operation

### Forward Pass tab
- Click **Play** to watch the computation unfold step by step
- **Green** = computed, **Orange** = active, **Blue** = pending
- The step description shows exactly how each value was calculated

### Backprop tab
- Watch gradients flow from the output back to the inputs
- **Blue** = unvisited, **Orange** = active, **Green** = computed, **Red** = high gradient
- The explanation inside each node shows the local chain-rule contribution

### Train MLP
- Start with XOR dataset + tanh activation + lr=0.05 + 100 epochs
- Watch the loss chart drop in real-time
- If it doesn't converge, try: more epochs, a different learning rate, or a larger hidden size
- For the Simple Linear dataset, use ReLU (tanh can saturate on large targets)

---

## Running Tests

```bash
cd /path/to/GradientQuestGame
source .venv/bin/activate
python -m pytest tests/ -v
```

50 tests covering: autograd engine, neural network, XP system, challenges, and boss fights.

---

## Resetting Progress

Delete or reset the progress file:

```bash
# Reset to fresh start
echo '{"xp": 0, "level": 1, "completed_challenges": [], "badges": [], "streak": 0, "hearts": 3, "daily_xp": 0, "daily_xp_goal": 50}' > GradientQuest/data/progress.json
```