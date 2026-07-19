"""🎮 My Games — Manage your game sessions."""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from auth import require_auth, get_current_user
from db import (
    list_sessions, create_new_session, set_active_session,
    delete_session, restart_session, get_active_session_id,
)
from game.xp import MAX_HEARTS

st.set_page_config(page_title="My Games | Gradient Quest", page_icon="🎮", layout="wide")
from game.ui import setup_chrome
setup_chrome()

require_auth()
user = get_current_user()
email = user["email"]

# ── Theme-aware CSS ──
st.markdown("""
<style>
    .profile-header {
        display: flex; align-items: center; gap: 18px; margin-bottom: 24px;
        padding: 22px 26px; border-radius: 18px;
        border: 1px solid rgba(28,176,246,0.25);
        background: linear-gradient(135deg, rgba(28,176,246,0.08), rgba(88,204,2,0.04));
    }
    .profile-header img {
        width: 64px; height: 64px; border-radius: 50%;
        border: 3px solid #1cb0f6;
    }
    .profile-header .info h2 { margin: 0; font-size: 1.4rem; }
    .profile-header .info p { margin: 2px 0; opacity: 0.6; font-size: 0.9rem; }

    .game-card {
        padding: 20px 24px; border-radius: 16px; margin: 8px 0;
        border: 2px solid rgba(128,128,128,0.2);
        background: rgba(128,128,128,0.04);
        transition: border-color 0.2s;
    }
    .game-card.active {
        border-color: #58cc02;
        background: rgba(88,204,2,0.06);
    }
    .game-card .title { font-weight: 700; font-size: 1.15rem; margin-bottom: 8px; }
    .game-card .stats {
        display: flex; gap: 14px; flex-wrap: wrap; font-size: 0.88rem; opacity: 0.75;
    }
    .game-card .stats span {
        padding: 4px 10px; border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.2);
        background: rgba(128,128,128,0.06);
    }
    .active-badge {
        display: inline-block; padding: 3px 10px; border-radius: 10px;
        background: #58cc02; color: white; font-size: 0.75rem;
        font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
        margin-left: 8px;
    }
    .new-game-box {
        text-align: center; padding: 36px; border-radius: 18px;
        border: 2px dashed rgba(28,176,246,0.3);
        background: rgba(28,176,246,0.04);
        margin: 12px 0;
    }
</style>
""", unsafe_allow_html=True)

# ── Profile header ──
picture_html = f'<img src="{user.get("picture", "")}" />' if user.get("picture") else '<div style="width:64px;height:64px;border-radius:50%;background:#1cb0f6;display:flex;align-items:center;justify-content:center;font-size:2rem">👤</div>'
st.markdown(f"""
<div class="profile-header">
    {picture_html}
    <div class="info">
        <h2>{user.get("name", "Player")}</h2>
        <p>{user.get("email", "")}</p>
    </div>
</div>
""", unsafe_allow_html=True)

st.title("🎮 My Games")

# ── Game sessions list ──
sessions = list_sessions(email)

if not sessions:
    st.info("You don't have any games yet. Create your first one below!")

for session in sessions:
    active_cls = "active" if session["is_active"] else ""
    active_badge = '<span class="active-badge">Active</span>' if session["is_active"] else ""

    st.markdown(f"""
    <div class="game-card {active_cls}">
        <div class="title">{session["session_name"]}{active_badge}</div>
        <div class="stats">
            <span>⚡ Lv.{session["level"]}</span>
            <span>✨ {session["xp"]} XP</span>
            <span>🏅 {session["badges"]} badges</span>
            <span>✅ {session["challenges_done"]} challenges</span>
            <span>📅 {session["updated_at"][:10] if session["updated_at"] else "—"}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Action buttons
    cols = st.columns([1, 1, 1, 1])
    with cols[0]:
        if session["is_active"]:
            st.button("▶️ Playing", disabled=True, key=f"play_{session['id']}",
                      width="stretch")
        else:
            if st.button("▶️ Switch", key=f"switch_{session['id']}",
                         width="stretch"):
                set_active_session(email, session["id"])
                st.rerun()

    with cols[1]:
        if st.button("🔄 Restart", key=f"restart_{session['id']}",
                     width="stretch"):
            st.session_state[f"confirm_restart_{session['id']}"] = True

    with cols[2]:
        if st.button("🗑️ Delete", key=f"delete_{session['id']}",
                     width="stretch"):
            st.session_state[f"confirm_delete_{session['id']}"] = True

    with cols[3]:
        pass  # Spacer

    # Confirmation dialogs
    if st.session_state.get(f"confirm_restart_{session['id']}"):
        st.warning(f"⚠️ This will reset **{session['session_name']}** to the beginning. All progress will be lost!")
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("✅ Yes, restart", key=f"confirm_yes_restart_{session['id']}",
                         type="primary"):
                restart_session(email, session["id"])
                st.session_state[f"confirm_restart_{session['id']}"] = False
                st.rerun()
        with c2:
            if st.button("❌ Cancel", key=f"confirm_no_restart_{session['id']}"):
                st.session_state[f"confirm_restart_{session['id']}"] = False
                st.rerun()

    if st.session_state.get(f"confirm_delete_{session['id']}"):
        st.warning(f"⚠️ This will permanently delete **{session['session_name']}**!")
        c1, c2, c3 = st.columns([1, 1, 2])
        with c1:
            if st.button("✅ Yes, delete", key=f"confirm_yes_delete_{session['id']}",
                         type="primary"):
                delete_session(email, session["id"])
                st.session_state[f"confirm_delete_{session['id']}"] = False
                st.rerun()
        with c2:
            if st.button("❌ Cancel", key=f"confirm_no_delete_{session['id']}"):
                st.session_state[f"confirm_delete_{session['id']}"] = False
                st.rerun()

    st.markdown("")  # spacing

# ── New game button ──
st.markdown("---")
st.markdown("""
<div class="new-game-box">
    <div style="font-size: 2rem; margin-bottom: 8px">➕</div>
    <div style="font-weight: 600; font-size: 1.1rem; opacity: 0.8">Start a new adventure</div>
</div>
""", unsafe_allow_html=True)

new_name = st.text_input("Game name", value=f"Game {len(sessions) + 1}",
                         key="new_game_name", placeholder="Enter a name for your new game")

if st.button("➕ Create New Game", type="primary", width="stretch"):
    name = new_name.strip() or f"Game {len(sessions) + 1}"
    create_new_session(email, name)
    st.toast(f"🎮 Created '{name}'!", icon="✅")
    st.rerun()
