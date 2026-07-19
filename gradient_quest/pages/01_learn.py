"""Learn — Story + Challenges combined into one guided flow."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from engine.value import Value
from visualization.graph import draw_graph
from game.challenges import get_challenges_for_chapter, check_answer
from game.xp import (
    load_progress, save_progress, add_xp, mark_challenge_complete,
    lose_heart, has_hearts, MAX_HEARTS,
)
from game.story import CHAPTERS, get_unlocked_chapters

st.set_page_config(page_title="Learn | Gradient Quest", page_icon="📖", layout="wide")
from game.ui import setup_chrome
setup_chrome()

# ── Theme-aware CSS ──
st.markdown("""
<style>
    /* Chapter header card */
    .chapter-banner {
        padding: 22px 26px; border-radius: 18px; margin-bottom: 14px;
        border: 1px solid rgba(28,176,246,0.35);
        background: linear-gradient(135deg, rgba(28,176,246,0.12), rgba(88,204,2,0.06));
    }
    .chapter-banner h2 { margin: 0 0 6px 0; color: #1cb0f6; font-size: 1.6rem; }
    .chapter-banner .intro { opacity: 0.85; font-style: italic; margin: 8px 0; }
    .chapter-banner .concepts { opacity: 0.65; font-size: 0.88rem; }

    /* Header stat row */
    .learn-head { display: flex; align-items: center; justify-content: space-between; margin: 6px 0 2px; }
    .learn-head .qnum { font-weight: 700; font-size: 1.05rem; opacity: 0.85; }
    .learn-head .hearts { font-size: 1.3rem; }

    /* Progress dots */
    .progress-dots { text-align: center; margin: 6px 0 16px; font-size: 1.1rem; letter-spacing: 6px; }

    /* Mini-lesson */
    .mini-lesson {
        border-left: 4px solid #58cc02; padding: 14px 18px; border-radius: 0 10px 10px 0;
        margin: 14px 0; background: rgba(88,204,2,0.08); font-size: 0.97rem;
    }

    /* Question card */
    .question-card {
        border: 1px solid rgba(128,128,128,0.25); border-radius: 18px;
        padding: 24px 28px; margin: 8px 0 18px;
        background: rgba(128,128,128,0.04);
    }
    .question-card .q-text { font-size: 1.35rem; font-weight: 700; margin: 0; line-height: 1.5; }

    /* Radio options styled as selectable cards */
    div[role="radiogroup"] { gap: 10px; }
    div[role="radiogroup"] > label {
        background: rgba(128,128,128,0.05);
        border: 2px solid rgba(128,128,128,0.25);
        border-radius: 14px; padding: 14px 20px; margin: 0;
        transition: all 0.15s ease; cursor: pointer; width: 100%;
        font-size: 1.05rem; font-weight: 600;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #1cb0f6; background: rgba(28,176,246,0.10);
        transform: translateX(3px);
    }

    /* Feedback banners */
    .feedback-correct {
        border: 2px solid #58cc02; border-radius: 14px; padding: 16px 20px;
        text-align: center; font-size: 1.2rem; color: #58cc02; font-weight: 700;
        background: rgba(88,204,2,0.10);
    }
    .feedback-wrong {
        border: 2px solid #ff4b4b; border-radius: 14px; padding: 16px 20px;
        text-align: center; font-size: 1.2rem; color: #ff4b4b; font-weight: 700;
        background: rgba(255,75,75,0.10);
    }
    .done-card {
        text-align: center; padding: 44px; border-radius: 18px;
        border: 2px solid #58cc02; background: rgba(88,204,2,0.10);
    }
</style>
""", unsafe_allow_html=True)

progress = load_progress()
unlocked = get_unlocked_chapters(progress["xp"])
unlocked_ids = sorted(ch["id"] for ch in unlocked)

if not unlocked_ids:
    st.warning("No chapters unlocked yet!")
    st.stop()

# ── Chapter selector: default to first incomplete chapter (once) ──
completed = progress["completed_challenges"]

if "learn_chapter" not in st.session_state or st.session_state["learn_chapter"] not in unlocked_ids:
    default_cid = unlocked_ids[0]
    for cid in unlocked_ids:
        ch = next(c for c in CHAPTERS if c["id"] == cid)
        if any(q not in completed for q in ch["challenges"]):
            default_cid = cid
            break
    st.session_state["learn_chapter"] = default_cid

chapter_id = st.selectbox(
    "📖 Chapter",
    unlocked_ids,
    key="learn_chapter",
    format_func=lambda x: f"Chapter {x}: {next(ch['name'] for ch in CHAPTERS if ch['id'] == x)}"
)

chapter = next(ch for ch in CHAPTERS if ch["id"] == chapter_id)

# ── Chapter story banner ──
st.markdown(f"""
<div class="chapter-banner">
    <h2>Chapter {chapter['id']}: {chapter['name']}</h2>
    <div class="intro">{chapter['intro']}</div>
    <div class="concepts">📚 Concepts: {', '.join(chapter['concepts'])}</div>
</div>
""", unsafe_allow_html=True)

challenges = get_challenges_for_chapter(chapter_id)

# ── Find current (first incomplete) challenge ──
current_challenge = None
current_idx = 0
for i, ch in enumerate(challenges):
    if ch["id"] not in completed:
        current_challenge = ch
        current_idx = i
        break

done_count = sum(1 for c in challenges if c["id"] in completed)
total = len(challenges)

# ── Header row: question number + hearts ──
hearts = progress.get("hearts", MAX_HEARTS)
hearts_display = "❤️" * hearts + "🖤" * (MAX_HEARTS - hearts)
qlabel = f"Question {current_idx + 1} of {total}" if current_challenge else f"Chapter complete · {total}/{total}"
st.markdown(
    f'<div class="learn-head"><span class="qnum">{qlabel}</span>'
    f'<span class="hearts">{hearts_display}</span></div>',
    unsafe_allow_html=True,
)

# ── Chapter progress bar + dots ──
st.progress(done_count / total if total else 0)
dots = ""
for i, ch in enumerate(challenges):
    if ch["id"] in completed:
        dots += "🟢"
    elif i == current_idx and current_challenge:
        dots += "🔵"
    else:
        dots += "⚪"
st.markdown(f'<div class="progress-dots">{dots}</div>', unsafe_allow_html=True)

# ── No hearts ──
if not has_hearts(progress):
    st.markdown('<div class="feedback-wrong">💔 Out of hearts! Come back tomorrow for a fresh start.</div>', unsafe_allow_html=True)
    st.caption("Hearts refill daily when you return.")
    st.stop()

# ── Chapter complete ──
if current_challenge is None:
    st.markdown(f"""
    <div class="done-card">
        <div style="font-size:3rem">🎉</div>
        <h2 style="color:#58cc02;margin:8px 0">Chapter {chapter['id']} Complete!</h2>
        <p style="opacity:0.7">You've mastered <b>{chapter['name']}</b>.</p>
    </div>
    """, unsafe_allow_html=True)

    next_unlocked = [c for c in unlocked_ids if c > chapter_id]
    locked_next = next((c for c in CHAPTERS if c["id"] == chapter_id + 1), None)

    cta, ctb = st.columns(2)
    with cta:
        if next_unlocked:
            nxt = next(c for c in CHAPTERS if c["id"] == next_unlocked[0])
            if st.button(f"▶️ Next: {nxt['name']}", use_container_width=True, type="primary"):
                st.session_state["learn_chapter"] = next_unlocked[0]
                st.rerun()
        elif locked_next:
            st.button(f"🔒 {locked_next['name']} · needs {locked_next['unlock_xp']} XP",
                      use_container_width=True, disabled=True)
        else:
            st.success("🏆 You've completed every chapter!")
    with ctb:
        if st.button("🔁 Retake this chapter", use_container_width=True):
            for q in chapter["challenges"]:
                if q in progress["completed_challenges"]:
                    progress["completed_challenges"].remove(q)
            save_progress(progress)
            st.rerun()

    st.stop()

# ── Mini-lesson ──
MINI_LESSONS = {
    1: "💡 The derivative measures how fast a function changes. For f(x) = xⁿ, the derivative is n·x^(n-1).",
    2: "💡 A computation graph shows how values flow through operations. Each node holds a value.",
    3: "💡 Chain rule: multiply local gradients along each path from output to input.",
    4: "💡 Backprop starts at the output (gradient = 1) and flows backward through the graph.",
    5: "💡 A neuron computes: activation(w·x + b). Different activations have different ranges.",
    6: "💡 An MLP stacks layers. Parameters = weights + biases across all layers.",
}
lesson = MINI_LESSONS.get(chapter_id, "")
if lesson:
    st.markdown(f'<div class="mini-lesson">{lesson}</div>', unsafe_allow_html=True)

# ── Question card ──
st.markdown(
    f'<div class="question-card"><p class="q-text">{current_challenge["question"]}</p></div>',
    unsafe_allow_html=True,
)

# Show graph if applicable
if current_challenge["graph_setup"]:
    namespace = {"Value": Value, "__builtins__": {}}
    try:
        exec(current_challenge["graph_setup"], namespace)  # noqa: S102
        values = {k: v for k, v in namespace.items() if isinstance(v, Value) and k != "Value"}
        if values:
            root = list(values.values())[-1]
            st.graphviz_chart(draw_graph(root).source)
    except Exception as e:
        st.caption(f"⚠️ Could not render graph: {e}")

# ── Answer options (styled as cards) ──
answer = st.radio("Choose your answer:", current_challenge["options"],
                  key=f"q_{current_challenge['id']}", label_visibility="collapsed")

st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("✅ Check Answer", use_container_width=True, type="primary"):
        correct, xp_earned = check_answer(current_challenge["id"], answer)
        if correct:
            st.markdown(f'<div class="feedback-correct">✅ Correct! +{xp_earned} XP</div>', unsafe_allow_html=True)
            st.balloons()
            progress = add_xp(progress, xp_earned)
            progress = mark_challenge_complete(progress, current_challenge["id"])
            save_progress(progress)
            st.session_state["just_answered"] = True
            st.rerun()
        else:
            progress = lose_heart(progress)
            save_progress(progress)
            remaining = progress["hearts"]
            st.markdown(f'<div class="feedback-wrong">❌ Not quite! Lost a heart. ({remaining} left)</div>', unsafe_allow_html=True)
            if remaining == 0:
                st.rerun()

# ── Show "continue" celebration if just answered ──
if st.session_state.get("just_answered"):
    st.session_state["just_answered"] = False
    st.toast("Great job! Next question loaded 🎯", icon="✅")