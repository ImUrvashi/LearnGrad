"""Google OAuth 2.0 authentication for Gradient Quest."""

import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
import google.auth.transport.requests


SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]


def _get_google_flow():
    """Create a Google OAuth flow from Streamlit secrets."""
    client_config = {
        "web": {
            "client_id": st.secrets["google_auth"]["client_id"],
            "client_secret": st.secrets["google_auth"]["client_secret"],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [st.secrets["google_auth"]["redirect_uri"]],
        }
    }
    flow = Flow.from_client_config(
        client_config, scopes=SCOPES, autogenerate_code_verifier=True
    )
    flow.redirect_uri = st.secrets["google_auth"]["redirect_uri"]
    return flow


def get_current_user():
    """Return current user dict from session state, or None if not logged in."""
    return st.session_state.get("user", None)


def _handle_oauth_callback():
    """Check for OAuth callback code in query params and exchange for user info."""
    params = st.query_params
    code = params.get("code")
    state = params.get("state")
    if code and "user" not in st.session_state:
        try:
            from db import pop_pkce_verifier
            flow = _get_google_flow()
            code_verifier = pop_pkce_verifier(state) if state else None
            if code_verifier:
                flow.fetch_token(code=code, code_verifier=code_verifier)
            else:
                flow.fetch_token(code=code)
            credentials = flow.credentials
            # Verify the ID token
            request = google.auth.transport.requests.Request()
            id_info = id_token.verify_oauth2_token(
                credentials.id_token, request,
                st.secrets["google_auth"]["client_id"]
            )
            st.session_state["user"] = {
                "email": id_info.get("email", ""),
                "name": id_info.get("name", "Player"),
                "picture": id_info.get("picture", ""),
            }
            # Register user in the database
            from db import get_or_create_user
            user = st.session_state["user"]
            get_or_create_user(user["email"], user["name"], user["picture"])
            # Clear the code from URL
            st.query_params.clear()
            st.rerun()
        except Exception as e:
            st.error(f"Authentication failed: {e}")
            st.query_params.clear()


def logout():
    """Clear user session and rerun."""
    if "user" in st.session_state:
        del st.session_state["user"]
    # Clear any game-related session state
    keys_to_clear = [k for k in list(st.session_state.keys())
                     if k.startswith(("learn_", "just_"))]
    for k in keys_to_clear:
        del st.session_state[k]
    st.rerun()


def show_login_page():
    """Render a beautiful login page with Google Sign-In button."""
    st.markdown("""
    <style>
        .login-container {
            max-width: 480px; margin: 60px auto; text-align: center;
            padding: 48px 36px; border-radius: 24px;
            border: 1px solid rgba(128,128,128,0.2);
            background: rgba(128,128,128,0.04);
        }
        .login-title {
            font-size: 2.8rem; font-weight: 800; margin-bottom: 4px;
            background: linear-gradient(135deg, #58cc02, #1cb0f6);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .login-subtitle { opacity: 0.6; font-size: 1.1rem; margin-bottom: 32px; }
        .login-features {
            text-align: left; margin: 24px 0; padding: 18px 22px;
            border-radius: 14px; background: rgba(88,204,2,0.06);
            border: 1px solid rgba(88,204,2,0.15);
        }
        .login-features li { padding: 6px 0; font-size: 0.95rem; opacity: 0.85; }
        .google-btn {
            display: inline-block; padding: 14px 32px; border-radius: 50px;
            background: linear-gradient(135deg, #4285f4, #34a853);
            color: white !important; font-weight: 700; font-size: 1.1rem;
            text-decoration: none; margin-top: 20px;
            transition: transform 0.2s, box-shadow 0.2s;
            box-shadow: 0 4px 15px rgba(66,133,244,0.3);
        }
        .google-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(66,133,244,0.4);
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)

    from db import store_pkce_verifier
    flow = _get_google_flow()
    auth_url, state = flow.authorization_url(prompt='consent', access_type='offline')
    store_pkce_verifier(state, flow.code_verifier)

    st.markdown(f"""
    <div class="login-container">
        <div class="login-title">⚡ Gradient Quest</div>
        <p class="login-subtitle">Learn neural networks by playing — not reading.</p>
        <div class="login-features">
            <ul>
                <li>🎮 Your own game session — progress saved automatically</li>
                <li>🏆 Track XP, streaks, badges, and level up</li>
                <li>📖 6 chapters from derivatives to training MLPs</li>
                <li>🐉 Boss fights with gradient monsters</li>
            </ul>
        </div>
        <a href="{auth_url}" class="google-btn">🔐 Sign in with Google</a>
    </div>
    """, unsafe_allow_html=True)


def require_auth():
    """Guard function: if not logged in, show login page and stop."""
    _handle_oauth_callback()
    if get_current_user() is None:
        show_login_page()
        st.stop()
