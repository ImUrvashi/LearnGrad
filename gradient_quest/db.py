"""SQLite database for per-user game sessions in Gradient Quest."""

import sqlite3
import json
import os
from datetime import datetime, timezone

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "gradient_quest.db")

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


def _get_conn():
    """Get a SQLite connection, creating DB and tables if needed."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    _init_tables(conn)
    return conn


def _init_tables(conn):
    """Create tables if they don't exist."""
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            picture TEXT DEFAULT '',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS game_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT NOT NULL,
            session_name TEXT NOT NULL DEFAULT 'Game 1',
            progress_data TEXT NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS oauth_pkce (
            state TEXT PRIMARY KEY,
            code_verifier TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()


def store_pkce_verifier(state, code_verifier):
    """Persist a PKCE code_verifier keyed by OAuth state, surviving the redirect to Google."""
    conn = _get_conn()
    conn.execute(
        "INSERT INTO oauth_pkce (state, code_verifier) VALUES (?, ?) "
        "ON CONFLICT(state) DO UPDATE SET code_verifier=excluded.code_verifier",
        (state, code_verifier)
    )
    conn.commit()
    conn.close()


def pop_pkce_verifier(state):
    """Retrieve and delete the code_verifier for an OAuth state. Returns None if missing."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT code_verifier FROM oauth_pkce WHERE state = ?", (state,)
    ).fetchone()
    conn.execute("DELETE FROM oauth_pkce WHERE state = ?", (state,))
    conn.commit()
    conn.close()
    return row["code_verifier"] if row else None


def get_or_create_user(email, name, picture=""):
    """Upsert a user record. Returns the user dict."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        "INSERT INTO users (email, name, picture, created_at, last_login) "
        "VALUES (?, ?, ?, ?, ?) "
        "ON CONFLICT(email) DO UPDATE SET "
        "name=excluded.name, picture=excluded.picture, last_login=?",
        (email, name, picture, now, now, now)
    )
    conn.commit()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    return dict(row)


def get_active_session(email):
    """Get the active game session's progress. Creates one if none exists."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT * FROM game_sessions "
        "WHERE user_email = ? AND is_active = 1 "
        "ORDER BY updated_at DESC LIMIT 1",
        (email,)
    ).fetchone()
    if row is None:
        conn.close()
        return create_new_session(email, "Game 1")
    conn.close()
    return json.loads(row["progress_data"])


def get_active_session_id(email):
    """Get the active session's database ID."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT id FROM game_sessions "
        "WHERE user_email = ? AND is_active = 1 "
        "ORDER BY updated_at DESC LIMIT 1",
        (email,)
    ).fetchone()
    conn.close()
    return row["id"] if row else None


def save_session(email, progress):
    """Save progress to the user's active game session."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    progress_json = json.dumps(progress, indent=2)
    result = conn.execute(
        "UPDATE game_sessions SET progress_data = ?, updated_at = ? "
        "WHERE user_email = ? AND is_active = 1",
        (progress_json, now, email)
    )
    if result.rowcount == 0:
        # No active session — create one
        conn.execute(
            "INSERT INTO game_sessions "
            "(user_email, session_name, progress_data, is_active, updated_at) "
            "VALUES (?, 'Game 1', ?, 1, ?)",
            (email, progress_json, now)
        )
    conn.commit()
    conn.close()


def create_new_session(email, session_name):
    """Create a new game with default progress. Deactivates others. Returns progress."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    # Deactivate all existing sessions for this user
    conn.execute(
        "UPDATE game_sessions SET is_active = 0 WHERE user_email = ?",
        (email,)
    )
    progress_json = json.dumps(DEFAULT_PROGRESS, indent=2)
    conn.execute(
        "INSERT INTO game_sessions "
        "(user_email, session_name, progress_data, is_active, created_at, updated_at) "
        "VALUES (?, ?, ?, 1, ?, ?)",
        (email, session_name, progress_json, now, now)
    )
    conn.commit()
    conn.close()
    return dict(DEFAULT_PROGRESS)


def list_sessions(email):
    """List all game sessions for a user with summary info."""
    conn = _get_conn()
    rows = conn.execute(
        "SELECT id, session_name, progress_data, is_active, created_at, updated_at "
        "FROM game_sessions WHERE user_email = ? ORDER BY updated_at DESC",
        (email,)
    ).fetchall()
    conn.close()
    sessions = []
    for row in rows:
        progress = json.loads(row["progress_data"])
        sessions.append({
            "id": row["id"],
            "session_name": row["session_name"],
            "is_active": bool(row["is_active"]),
            "xp": progress.get("xp", 0),
            "level": progress.get("level", 1),
            "badges": len(progress.get("badges", [])),
            "challenges_done": len(progress.get("completed_challenges", [])),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        })
    return sessions


def set_active_session(email, session_id):
    """Switch which session is active for a user."""
    conn = _get_conn()
    conn.execute(
        "UPDATE game_sessions SET is_active = 0 WHERE user_email = ?",
        (email,)
    )
    conn.execute(
        "UPDATE game_sessions SET is_active = 1 "
        "WHERE id = ? AND user_email = ?",
        (session_id, email)
    )
    conn.commit()
    conn.close()


def delete_session(email, session_id):
    """Delete a game session. Activates most recent if the deleted one was active."""
    conn = _get_conn()
    row = conn.execute(
        "SELECT is_active FROM game_sessions WHERE id = ? AND user_email = ?",
        (session_id, email)
    ).fetchone()
    was_active = row and row["is_active"]
    conn.execute(
        "DELETE FROM game_sessions WHERE id = ? AND user_email = ?",
        (session_id, email)
    )
    if was_active:
        remaining = conn.execute(
            "SELECT id FROM game_sessions "
            "WHERE user_email = ? ORDER BY updated_at DESC LIMIT 1",
            (email,)
        ).fetchone()
        if remaining:
            conn.execute(
                "UPDATE game_sessions SET is_active = 1 WHERE id = ?",
                (remaining["id"],)
            )
    conn.commit()
    conn.close()


def restart_session(email, session_id):
    """Reset a session's progress to defaults."""
    conn = _get_conn()
    now = datetime.now(timezone.utc).isoformat()
    progress_json = json.dumps(DEFAULT_PROGRESS, indent=2)
    conn.execute(
        "UPDATE game_sessions SET progress_data = ?, updated_at = ? "
        "WHERE id = ? AND user_email = ?",
        (progress_json, now, session_id, email)
    )
    conn.commit()
    conn.close()
    return dict(DEFAULT_PROGRESS)
