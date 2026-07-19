"""Gradient Quest — Learn neural networks by playing through backpropagation."""

import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from auth import require_auth, get_current_user
from game.xp import load_progress, save_progress, update_streak, get_xp_for_next_level, MAX_HEARTS
from game.story import CHAPTERS, get_unlocked_chapters
from game.ui import setup_chrome

st.set_page_config(
    page_title="Gradient Quest",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

setup_chrome()

# ── Require authentication ──
require_auth()
user = get_current_user()
user_email = user["email"]

# ── Load and update progress ──
progress = load_progress(user_email=user_email)
progress = update_streak(progress)
save_progress(progress, user_email=user_email)

xp = progress["xp"]
streak = progress.get("streak", 0)
hearts = progress.get("hearts", MAX_HEARTS)
daily_xp = progress.get("daily_xp", 0)
daily_goal = progress.get("daily_xp_goal", 50)
badges = progress["badges"]
completed_challenges = progress["completed_challenges"]
level = progress["level"]

# ── Theme-aware CSS (readable in BOTH light and dark Streamlit themes) ──
st.markdown("""
<style>
    .main-title {
        text-align: center; font-size: 3rem; margin-bottom: 0; font-weight: 800;
        background: linear-gradient(135deg, #58cc02, #1cb0f6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .tagline { text-align: center; opacity: 0.65; font-size: 1.1rem; margin-top: 4px; }
    .stat-bar { display: flex; justify-content: center; gap: 10px; margin: 18px 0; flex-wrap: wrap; }
    .stat-pill {
        padding: 8px 18px; border-radius: 24px; font-weight: 700; font-size: 0.95rem;
        border: 1px solid rgba(128,128,128,0.35); background: rgba(128,128,128,0.10);
    }
    .big-stat {
        text-align: center; padding: 16px 12px; border-radius: 16px;
        border: 1px solid rgba(128,128,128,0.35); background: rgba(128,128,128,0.06);
    }
    .big-stat .number { font-size: 1.9rem; font-weight: 800; margin: 4px 0; }
    .big-stat .label { font-size: 0.72rem; opacity: 0.6; text-transform: uppercase; letter-spacing: 1px; }
    .path-node {
        padding: 13px 18px; margin: 3px 0; border-radius: 14px;
        font-size: 1rem; font-weight: 600; border: 2px solid transparent;
    }
    .path-node.complete { background: rgba(88,204,2,0.15); border-color: #58cc02; color: #58cc02; }
    .path-node.current { background: rgba(28,176,246,0.15); border-color: #1cb0f6; color: #1cb0f6; animation: pulse 2s infinite; }
    .path-node.locked { background: rgba(128,128,128,0.08); border-color: rgba(128,128,128,0.3); opacity: 0.55; }
    .path-connector { text-align: center; opacity: 0.3; font-size: 1rem; margin: 0; line-height: 1; }
    .badge-card { text-align: center; padding: 12px; border-radius: 14px; border: 1px solid #58cc02; background: rgba(88,204,2,0.10); }
    .hint-box {
        text-align: center; margin: 18px auto; padding: 14px 22px; border-radius: 14px;
        border: 1px solid #1cb0f6; color: #1cb0f6; font-weight: 600; max-width: 480px;
        background: rgba(28,176,246,0.10);
    }
    @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.72; } }
</style>
""", unsafe_allow_html=True)

# ── Header ──
st.markdown('<h1 class="main-title">⚡ Gradient Quest</h1>', unsafe_allow_html=True)
st.markdown('<p class="tagline">Learn neural networks by playing — not reading.</p>', unsafe_allow_html=True)

# ── Stat bar ──
hearts_display = "❤️" * hearts + "🖤" * (MAX_HEARTS - hearts)
st.markdown(f"""
<div class="stat-bar">
    <span class="stat-pill">🔥 {streak} day{"s" if streak != 1 else ""}</span>
    <span class="stat-pill">{hearts_display}</span>
    <span class="stat-pill">⚡ Lv.{level} · {xp} XP</span>
    <span class="stat-pill">📅 {daily_xp}/{daily_goal} today</span>
</div>
""", unsafe_allow_html=True)

# ── XP progress toward next level ──
current_thresh, next_thresh = get_xp_for_next_level(xp)
pct = (xp - current_thresh) / (next_thresh - current_thresh) if next_thresh > current_thresh else 1.0
st.progress(min(pct, 1.0), text=f"⚡ {xp} / {next_thresh} XP to next level")

# ── Big stat cards ──
c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f'<div class="big-stat"><div class="number" style="color:#ff9500">🔥 {streak}</div><div class="label">Day Streak</div></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div class="big-stat"><div class="number" style="color:#ff4b4b">{hearts_display}</div><div class="label">Hearts</div></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div class="big-stat"><div class="number" style="color:#58cc02">{xp}</div><div class="label">Total XP</div></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div class="big-stat"><div class="number" style="color:#a855f7">{len(badges)}</div><div class="label">Badges</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Badges ──
if badges:
    st.subheader("🏅 Badges")
    bcols = st.columns(min(len(badges), 4))
    for i, badge in enumerate(badges):
        with bcols[i % 4]:
            st.markdown(f'<div class="badge-card"><div style="font-size:1.6rem">🏅</div><div style="font-size:0.8rem;font-weight:600;color:#58cc02">{badge}</div></div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ── Progress path (chapter journey) ──
st.subheader("📖 Your Journey")
unlocked = get_unlocked_chapters(xp)
unlocked_ids = {ch["id"] for ch in unlocked}

for i, ch in enumerate(CHAPTERS):
    is_unlocked = ch["id"] in unlocked_ids
    done_count = sum(1 for c in ch["challenges"] if c in completed_challenges)
    total = len(ch["challenges"])
    is_complete = done_count == total

    if is_complete:
        st.markdown(f'<div class="path-node complete">✅ {ch["name"]} <span style="float:right;font-size:0.85rem;opacity:0.7">{done_count}/{total}</span></div>', unsafe_allow_html=True)
    elif is_unlocked:
        st.markdown(f'<div class="path-node current">▶️ {ch["name"]} <span style="float:right;font-size:0.85rem;opacity:0.7">{done_count}/{total}</span></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="path-node locked">🔒 {ch["name"]} <span style="float:right;font-size:0.85rem;opacity:0.7">{ch["unlock_xp"]} XP</span></div>', unsafe_allow_html=True)

    if i < len(CHAPTERS) - 1:
        st.markdown('<p class="path-connector">│</p>', unsafe_allow_html=True)

# ── Next action hint ──
next_chapter = None
for ch in CHAPTERS:
    if ch["id"] in unlocked_ids:
        done = sum(1 for c in ch["challenges"] if c in completed_challenges)
        if done < len(ch["challenges"]):
            next_chapter = ch
            break

if next_chapter:
    st.markdown(f'<div class="hint-box">👉 Next up: <strong>{next_chapter["name"]}</strong> — open <strong>Learn</strong> in the sidebar</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="hint-box">🏆 All challenges done! Try <strong>Boss Fights</strong> or <strong>Train MLP</strong></div>', unsafe_allow_html=True)