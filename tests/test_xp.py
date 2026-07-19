"""Tests for the XP and progression system."""

import sys
import os
import json
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gradient_quest.game.xp import (
    load_progress, save_progress, add_xp, calculate_level,
    get_xp_for_next_level, award_badge, mark_challenge_complete,
    DEFAULT_PROGRESS,
)
from gradient_quest.game.story import CHAPTERS, get_unlocked_chapters, get_chapter_by_id


# ── XP tests ──

def test_default_progress():
    p = dict(DEFAULT_PROGRESS)
    assert p["xp"] == 0
    assert p["level"] == 1
    assert p["completed_challenges"] == []
    assert p["badges"] == []


def test_add_xp():
    p = dict(DEFAULT_PROGRESS)
    p = add_xp(p, 50)
    assert p["xp"] == 50
    assert p["level"] == 2


def test_calculate_level():
    assert calculate_level(0) == 1
    assert calculate_level(49) == 1
    assert calculate_level(50) == 2
    assert calculate_level(100) == 3
    assert calculate_level(999) == 7
    assert calculate_level(1000) == 8


def test_get_xp_for_next_level():
    current, nxt = get_xp_for_next_level(75)
    assert current == 50
    assert nxt == 100


def test_award_badge():
    p = dict(DEFAULT_PROGRESS)
    p["badges"] = []
    p = award_badge(p, "Dragon Slayer")
    assert "Dragon Slayer" in p["badges"]
    # No duplicates
    p = award_badge(p, "Dragon Slayer")
    assert p["badges"].count("Dragon Slayer") == 1


def test_mark_challenge_complete():
    p = dict(DEFAULT_PROGRESS)
    p["completed_challenges"] = []
    p = mark_challenge_complete(p, "deriv_basic_1")
    assert "deriv_basic_1" in p["completed_challenges"]
    # No duplicates
    p = mark_challenge_complete(p, "deriv_basic_1")
    assert p["completed_challenges"].count("deriv_basic_1") == 1


def test_save_and_load_progress():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        tmp_path = f.name

    try:
        p = dict(DEFAULT_PROGRESS)
        p = add_xp(p, 200)
        p = award_badge(p, "Test Badge")
        save_progress(p, path=tmp_path)

        loaded = load_progress(path=tmp_path)
        assert loaded["xp"] == 200
        assert loaded["level"] == 4
        assert "Test Badge" in loaded["badges"]
    finally:
        os.unlink(tmp_path)


def test_load_missing_file():
    p = load_progress(path="/nonexistent/path/progress.json")
    assert p == DEFAULT_PROGRESS


# ── Story tests ──

def test_chapters_structure():
    assert len(CHAPTERS) == 6
    assert CHAPTERS[0]["unlock_xp"] == 0
    for ch in CHAPTERS:
        assert "id" in ch
        assert "name" in ch
        assert "challenges" in ch
        assert len(ch["challenges"]) > 0


def test_get_unlocked_chapters():
    assert len(get_unlocked_chapters(0)) == 1  # Chapter 1 always unlocked
    assert len(get_unlocked_chapters(100)) == 2
    assert len(get_unlocked_chapters(1000)) == 6


def test_get_chapter_by_id():
    ch = get_chapter_by_id(1)
    assert ch["name"] == "Derivative Village"
    assert get_chapter_by_id(99) is None


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])