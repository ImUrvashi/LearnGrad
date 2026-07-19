"""Boss fight definitions for Gradient Quest."""

BOSSES = [
    {
        "id": "vanishing_gradient_dragon",
        "name": "Vanishing Gradient Dragon",
        "chapter": 5,
        "description": (
            "The Vanishing Gradient Dragon lurks in deep networks. "
            "Choose the right activation function to keep your gradients alive!"
        ),
        "mechanic": "activation_choice",
        "choices": ["Sigmoid", "Tanh", "ReLU"],
        "best_choice": "ReLU",
        "explanation": (
            "Sigmoid and Tanh squash gradients toward zero in deep networks. "
            "ReLU preserves gradient magnitude (gradient = 1 for positive inputs), "
            "making it the best weapon against the Vanishing Gradient Dragon."
        ),
        "xp_reward": 100,
        "badge": "Dragon Slayer",
    },
    {
        "id": "exploding_gradient_titan",
        "name": "Exploding Gradient Titan",
        "chapter": 6,
        "description": (
            "The Exploding Gradient Titan grows stronger with every layer. "
            "Your gradients are spiraling out of control — find a way to tame them!"
        ),
        "mechanic": "depth_experiment",
        "choices": ["Add more layers", "Use gradient clipping", "Increase learning rate"],
        "best_choice": "Use gradient clipping",
        "explanation": (
            "Adding more layers or increasing the learning rate makes exploding gradients worse. "
            "Gradient clipping caps the gradient magnitude, keeping training stable."
        ),
        "xp_reward": 100,
        "badge": "Titan Tamer",
    },
]


def get_boss_by_id(boss_id):
    """Return a boss definition by id."""
    for b in BOSSES:
        if b["id"] == boss_id:
            return b
    return None


def get_bosses_for_chapter(chapter_id):
    """Return bosses belonging to a chapter."""
    return [b for b in BOSSES if b["chapter"] == chapter_id]


def evaluate_boss_choice(boss_id, choice):
    """Evaluate a player's choice in a boss fight. Returns (won, explanation, xp)."""
    boss = get_boss_by_id(boss_id)
    if boss is None:
        return False, "Boss not found.", 0
    won = choice == boss["best_choice"]
    return won, boss["explanation"], boss["xp_reward"] if won else 0