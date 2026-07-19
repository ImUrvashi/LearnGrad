"""Tests for the challenge system."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from gradient_quest.game.challenges import (
    CHALLENGES, get_challenges_for_chapter, get_challenge_by_id, check_answer,
)
from gradient_quest.engine.value import Value


def test_challenge_structure():
    """Every challenge has required fields."""
    required = {"id", "chapter", "question", "options", "correct", "xp_reward"}
    for c in CHALLENGES:
        assert required.issubset(c.keys()), f"Challenge {c.get('id')} missing fields"
        assert len(c["options"]) >= 2
        assert c["correct"] in c["options"]
        assert c["xp_reward"] > 0


def test_all_chapters_have_challenges():
    for chapter_id in range(1, 7):
        challenges = get_challenges_for_chapter(chapter_id)
        assert len(challenges) >= 2, f"Chapter {chapter_id} has too few challenges"


def test_get_challenge_by_id():
    c = get_challenge_by_id("deriv_basic_1")
    assert c is not None
    assert c["chapter"] == 1
    assert get_challenge_by_id("nonexistent") is None


def test_check_answer_correct():
    is_correct, xp = check_answer("deriv_basic_1", "8")
    assert is_correct
    assert xp == 25


def test_check_answer_wrong():
    is_correct, xp = check_answer("deriv_basic_1", "4")
    assert not is_correct
    assert xp == 0


def test_check_answer_nonexistent():
    is_correct, xp = check_answer("fake_id", "1")
    assert not is_correct
    assert xp == 0


def test_gradient_challenges_correct():
    """Verify all challenges with graph_setup produce the correct answer via the engine."""
    for c in CHALLENGES:
        if c["graph_setup"] is None:
            continue
        namespace = {"Value": Value, "__builtins__": {}}
        exec(c["graph_setup"], namespace)  # noqa: S102
        values = {k: v for k, v in namespace.items() if isinstance(v, Value) and k != "Value"}
        root = list(values.values())[-1]

        if c["chapter"] in (1, 3, 4):
            # These ask about gradients — run backward and check
            root.backward()
            # The first Value variable's gradient should match for derivative questions
            first_val = list(values.values())[0]
            if "derivative" in c["question"].lower() or "dc/d" in c["question"].lower() or "dd/d" in c["question"].lower() or "dy/d" in c["question"].lower():
                expected = float(c["correct"])
                assert abs(first_val.grad - expected) < 1e-6, (
                    f"Challenge {c['id']}: expected grad={expected}, got {first_val.grad}"
                )
        elif c["chapter"] == 2:
            # These ask about forward values
            if "value" in c["question"].lower() or "what is" in c["question"].lower():
                if "operation nodes" not in c["question"].lower():
                    expected = float(c["correct"])
                    assert abs(root.data - expected) < 1e-6, (
                        f"Challenge {c['id']}: expected data={expected}, got {root.data}"
                    )


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])