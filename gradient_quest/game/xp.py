"""XP and progression system for Gradient Quest."""

import json
import os
from datetime import date, timedelta

DEFAULT_PROGRESS = {
    "xp": 0,
    "level": 1,
    "completed_challenges": [],
    "badges": [],
    "streak": 0,
    "last_active": None,
    "hearts": 3,
    "daily_xp": 0,
    "daily_xp_goal": 50,
}

MAX_HEARTS = 3

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")

# XP thresholds per level
LEVEL_THRESHOLDS = [0, 50, 100, 200, 350, 500, 700, 1000]


def _ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def load_progress(path=None):
    """Load player progress from JSON file. Migrates old format."""
    path = path or PROGRESS_FILE
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
        # Migrate old progress files missing new fields
        for key, default in DEFAULT_PROGRESS.items():
            if key not in data:
                data[key] = default
        return data
    return dict(DEFAULT_PROGRESS)


def save_progress(progress, path=None):
    """Save player progress to JSON file."""
    path = path or PROGRESS_FILE
    _ensure_data_dir()
    with open(path, 'w') as f:
        json.dump(progress, f, indent=2)


def update_streak(progress):
    """Update streak based on today's activity. Call on each session start."""
    today = str(date.today())
    last = progress.get("last_active")

    if last == today:
        return progress  # already active today

    if last:
        yesterday = str(date.today() - timedelta(days=1))
        if last == yesterday:
            progress["streak"] += 1
        else:
            progress["streak"] = 1
    else:
        progress["streak"] = 1

    progress["last_active"] = today
    progress["daily_xp"] = 0
    progress["hearts"] = MAX_HEARTS  # refill hearts daily
    return progress


def add_xp(progress, amount):
    """Add XP and recalculate level. Returns updated progress dict."""
    progress["xp"] += amount
    progress["daily_xp"] = progress.get("daily_xp", 0) + amount
    progress["level"] = calculate_level(progress["xp"])
    return progress


def calculate_level(xp):
    """Determine level from total XP."""
    level = 1
    for i, threshold in enumerate(LEVEL_THRESHOLDS):
        if xp >= threshold:
            level = i + 1
    return level


def get_xp_for_next_level(xp):
    """Return (current_threshold, next_threshold) for progress bar."""
    level = calculate_level(xp)
    current = LEVEL_THRESHOLDS[level - 1] if level - 1 < len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1]
    nxt = LEVEL_THRESHOLDS[level] if level < len(LEVEL_THRESHOLDS) else LEVEL_THRESHOLDS[-1]
    return current, nxt


def award_badge(progress, badge_name):
    """Award a badge if not already earned."""
    if badge_name not in progress["badges"]:
        progress["badges"].append(badge_name)
    return progress


def mark_challenge_complete(progress, challenge_id):
    """Mark a challenge as completed."""
    if challenge_id not in progress["completed_challenges"]:
        progress["completed_challenges"].append(challenge_id)
    return progress


def lose_heart(progress):
    """Lose a heart on wrong answer. Returns updated progress."""
    progress["hearts"] = max(0, progress.get("hearts", MAX_HEARTS) - 1)
    return progress


def has_hearts(progress):
    """Check if player still has hearts remaining."""
    return progress.get("hearts", MAX_HEARTS) > 0