"""Challenge bank for Gradient Quest."""

CHALLENGES = [
    # ── Chapter 1: Derivative Village ──
    {
        "id": "deriv_basic_1",
        "chapter": 1,
        "question": "f(x) = x². What is the derivative at x = 4?",
        "graph_setup": "x = Value(4, label='x'); f = x ** 2",
        "options": ["2", "4", "8", "16"],
        "correct": "8",
        "xp_reward": 25,
    },
    {
        "id": "deriv_basic_2",
        "chapter": 1,
        "question": "f(x) = 3x. What is the derivative at x = 5?",
        "graph_setup": "x = Value(5, label='x'); f = 3 * x",
        "options": ["3", "5", "15", "1"],
        "correct": "3",
        "xp_reward": 25,
    },
    {
        "id": "deriv_basic_3",
        "chapter": 1,
        "question": "f(x) = x³. What is the derivative at x = 2?",
        "graph_setup": "x = Value(2, label='x'); f = x ** 3",
        "options": ["4", "6", "8", "12"],
        "correct": "12",
        "xp_reward": 25,
    },
    # ── Chapter 2: Graph Forest ──
    {
        "id": "graph_read_1",
        "chapter": 2,
        "question": "a=2, b=3, c=a*b. What is the value of c?",
        "graph_setup": "a = Value(2, label='a'); b = Value(3, label='b'); c = a * b",
        "options": ["5", "6", "8", "1"],
        "correct": "6",
        "xp_reward": 25,
    },
    {
        "id": "graph_read_2",
        "chapter": 2,
        "question": "a=2, b=3, c=a*b, d=c+1. What is d?",
        "graph_setup": "a = Value(2, label='a'); b = Value(3, label='b'); c = a * b; d = c + 1",
        "options": ["6", "7", "8", "9"],
        "correct": "7",
        "xp_reward": 25,
    },
    {
        "id": "graph_build_1",
        "chapter": 2,
        "question": "a=4, b=2, c=a+b, d=c*a. How many operation nodes are in this graph?",
        "graph_setup": "a = Value(4, label='a'); b = Value(2, label='b'); c = a + b; d = c * a",
        "options": ["1", "2", "3", "4"],
        "correct": "2",
        "xp_reward": 30,
    },
    # ── Chapter 3: Chain Rule Caverns ──
    {
        "id": "chain_rule_1",
        "chapter": 3,
        "question": "a=2, b=3, c=a*b. What is dc/da?",
        "graph_setup": "a = Value(2, label='a'); b = Value(3, label='b'); c = a * b",
        "options": ["2", "3", "6", "9"],
        "correct": "3",
        "xp_reward": 30,
    },
    {
        "id": "chain_rule_2",
        "chapter": 3,
        "question": "a=2, b=3, c=a*b, d=c+a. What is dd/da?",
        "graph_setup": "a = Value(2, label='a'); b = Value(3, label='b'); c = a * b; d = c + a",
        "options": ["1", "3", "4", "6"],
        "correct": "4",
        "xp_reward": 35,
    },
    {
        "id": "chain_rule_3",
        "chapter": 3,
        "question": "x=3, y=x*x (i.e., x²). What is dy/dx?",
        "graph_setup": "x = Value(3, label='x'); y = x * x",
        "options": ["3", "6", "9", "1"],
        "correct": "6",
        "xp_reward": 35,
    },
    # ── Chapter 4: Backprop Temple ──
    {
        "id": "backprop_1",
        "chapter": 4,
        "question": "After backprop, what is the gradient of the output node itself?",
        "graph_setup": "a = Value(2, label='a'); b = a * 3",
        "options": ["0", "1", "2", "3"],
        "correct": "1",
        "xp_reward": 30,
    },
    {
        "id": "backprop_2",
        "chapter": 4,
        "question": "a=2, b=3, c=a+b. After backprop from c, what is a.grad?",
        "graph_setup": "a = Value(2, label='a'); b = Value(3, label='b'); c = a + b",
        "options": ["0", "1", "2", "3"],
        "correct": "1",
        "xp_reward": 30,
    },
    {
        "id": "backprop_accum_1",
        "chapter": 4,
        "question": "a=3, b=a+a. After backprop from b, what is a.grad?",
        "graph_setup": "a = Value(3, label='a'); b = a + a",
        "options": ["1", "2", "3", "6"],
        "correct": "2",
        "xp_reward": 40,
    },
    # ── Chapter 5: Neural Academy ──
    {
        "id": "neuron_1",
        "chapter": 5,
        "question": "A neuron computes w*x + b, then applies tanh. If w=1, x=0, b=0, what is tanh(0)?",
        "graph_setup": None,
        "options": ["0", "0.5", "1", "-1"],
        "correct": "0",
        "xp_reward": 25,
    },
    {
        "id": "activation_1",
        "chapter": 5,
        "question": "What is ReLU(-3)?",
        "graph_setup": None,
        "options": ["-3", "0", "3", "1"],
        "correct": "0",
        "xp_reward": 25,
    },
    {
        "id": "activation_compare",
        "chapter": 5,
        "question": "Which activation can output negative values?",
        "graph_setup": None,
        "options": ["ReLU", "Sigmoid", "Tanh", "None of them"],
        "correct": "Tanh",
        "xp_reward": 30,
    },
    # ── Chapter 6: MLP Fortress ──
    {
        "id": "mlp_forward_1",
        "chapter": 6,
        "question": "An MLP with architecture [2, 3, 1] has how many total parameters (weights + biases)?",
        "graph_setup": None,
        "options": ["9", "10", "12", "13"],
        "correct": "13",
        "xp_reward": 35,
    },
    {
        "id": "mlp_train_1",
        "chapter": 6,
        "question": "During training, we adjust parameters in the direction that ___ the loss.",
        "graph_setup": None,
        "options": ["Increases", "Decreases", "Randomizes", "Freezes"],
        "correct": "Decreases",
        "xp_reward": 30,
    },
    {
        "id": "mlp_boss",
        "chapter": 6,
        "question": "Gradient descent updates: w = w - lr * grad. If lr is too large, what happens?",
        "graph_setup": None,
        "options": ["Converges faster", "Loss oscillates/diverges", "Nothing changes", "Gradients vanish"],
        "correct": "Loss oscillates/diverges",
        "xp_reward": 50,
    },
]


def get_challenges_for_chapter(chapter_id):
    """Return challenges belonging to a specific chapter."""
    return [c for c in CHALLENGES if c["chapter"] == chapter_id]


def get_challenge_by_id(challenge_id):
    """Return a single challenge by its id."""
    for c in CHALLENGES:
        if c["id"] == challenge_id:
            return c
    return None


def check_answer(challenge_id, answer):
    """Check if the given answer is correct. Returns (is_correct, xp_reward)."""
    challenge = get_challenge_by_id(challenge_id)
    if challenge is None:
        return False, 0
    is_correct = str(answer).strip() == str(challenge["correct"]).strip()
    return is_correct, challenge["xp_reward"] if is_correct else 0