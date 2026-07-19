"""Shared UI chrome helpers for Gradient Quest pages."""

import streamlit as st


def setup_chrome():
    """Add sidebar chrome: user info, rerun button, and logout.

    The default Streamlit toolbar (Deploy button + menu with theme settings, etc.)
    is left intact.
    """
    with st.sidebar:
        user = st.session_state.get("user")
        if user:
            # User profile section
            col1, col2 = st.columns([1, 3])
            with col1:
                if user.get("picture"):
                    st.image(user["picture"], width=45)
                else:
                    st.markdown("👤")
            with col2:
                st.markdown(f"**{user.get('name', 'Player')}**")
                st.caption(user.get("email", ""))

            st.divider()

        if st.button("🔄 Rerun", width="stretch", key="sidebar_rerun"):
            st.rerun()

        if user:
            if st.button("🚪 Logout", width="stretch", key="sidebar_logout"):
                import sys, os
                sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
                from auth import logout
                logout()