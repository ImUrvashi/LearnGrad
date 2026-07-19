"""Tests for the boss fight system."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gradient_quest.game.bosses import (
    BOSSES, get_boss_by_id, get_bosses_for_chapter, evaluate_boss_choice,
)


def test_boss_structure():
    required = {"id", "name", "chapter", "description", "mechanic", "choices",
                "best_choice", "explanation", "xp_reward", "badge"}
    for b in BOSSES:
        assert required.issubset(b.keys()), f"Boss {b.get('id')} missing fields"
        assert b["best_choice"] in b["choices"]
        assert b["xp_reward"] > 0


def test_get_boss_by_id():
    boss = get_boss_by_id("vanishing_gradient_dragon")
    assert boss is not None
    assert boss["name"] == "Vanishing Gradient Dragon"
    assert get_boss_by_id("nonexistent") is None


def test_get_bosses_for_chapter():
    ch5 = get_bosses_for_chapter(5)
    assert len(ch5) == 1
    assert ch5[0]["id"] == "vanishing_gradient_dragon"


def test_evaluate_correct_choice():
    won, explanation, xp = evaluate_boss_choice("vanishing_gradient_dragon", "ReLU")
    assert won is True
    assert xp == 100
    assert len(explanation) > 0


def test_evaluate_wrong_choice():
    won, explanation, xp = evaluate_boss_choice("vanishing_gradient_dragon", "Sigmoid")
    assert won is False
    assert xp == 0


def test_evaluate_nonexistent_boss():
    won, explanation, xp = evaluate_boss_choice("fake_boss", "anything")
    assert won is False
    assert xp == 0


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])