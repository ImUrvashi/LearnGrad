"""Story mode chapter definitions for Gradient Quest."""

CHAPTERS = [
    {
        "id": 1,
        "name": "Derivative Village",
        "concepts": ["Derivative", "Slope", "Sensitivity"],
        "intro": (
            "Welcome to Derivative Village, traveler. Here, everything changes — "
            "and your job is to measure *how fast*. Master the slope, and the gates "
            "to the Graph Forest will open."
        ),
        "unlock_xp": 0,
        "challenges": ["deriv_basic_1", "deriv_basic_2", "deriv_basic_3"],
    },
    {
        "id": 2,
        "name": "Graph Forest",
        "concepts": ["Computational Graphs", "Operations", "Nodes"],
        "intro": (
            "The Graph Forest is alive with computation. Every tree is a DAG, every "
            "branch an operation. Learn to read the forest, and you'll see how data flows."
        ),
        "unlock_xp": 100,
        "challenges": ["graph_read_1", "graph_read_2", "graph_build_1"],
    },
    {
        "id": 3,
        "name": "Chain Rule Caverns",
        "concepts": ["Local gradients", "Chain Rule"],
        "intro": (
            "Deep in the caverns, gradients echo through chains of operations. "
            "The Chain Rule is your torch — without it, you're lost in the dark."
        ),
        "unlock_xp": 200,
        "challenges": ["chain_rule_1", "chain_rule_2", "chain_rule_3"],
    },
    {
        "id": 4,
        "name": "Backprop Temple",
        "concepts": ["Backward pass", "Gradient accumulation"],
        "intro": (
            "The Backprop Temple is where gradients are born. Watch them flow backwards "
            "through the graph, accumulating wisdom at every node."
        ),
        "unlock_xp": 350,
        "challenges": ["backprop_1", "backprop_2", "backprop_accum_1"],
    },
    {
        "id": 5,
        "name": "Neural Academy",
        "concepts": ["Neuron", "Activation functions"],
        "intro": (
            "Welcome to the Neural Academy. Here, simple units combine weights and inputs "
            "with activation functions to make decisions. Build your first neuron."
        ),
        "unlock_xp": 500,
        "challenges": ["neuron_1", "activation_1", "activation_compare"],
    },
    {
        "id": 6,
        "name": "MLP Fortress",
        "concepts": ["Networks", "Training", "Optimization"],
        "intro": (
            "The MLP Fortress stands tall — layers of neurons stacked into a network. "
            "Train it, optimize it, and conquer the final challenge."
        ),
        "unlock_xp": 700,
        "challenges": ["mlp_forward_1", "mlp_train_1", "mlp_boss"],
    },
]


def get_unlocked_chapters(xp):
    """Return list of chapters the player has unlocked based on XP."""
    return [ch for ch in CHAPTERS if xp >= ch["unlock_xp"]]


def get_chapter_by_id(chapter_id):
    """Return a chapter dict by its id. Used by challenges and boss fights."""
    for ch in CHAPTERS:
        if ch["id"] == chapter_id:
            return ch
    return None