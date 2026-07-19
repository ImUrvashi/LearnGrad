"""Shared UI chrome helpers for Gradient Quest pages."""

import streamlit as st


def setup_chrome():
    """Add a clean Rerun button in the sidebar.

    The default Streamlit toolbar (Deploy button + menu with theme settings, etc.)
    is left intact.
    """
    with st.sidebar:
        if st.button("🔄 Rerun", use_container_width=True, key="sidebar_rerun"):
            st.rerun()