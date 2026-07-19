"""Tests for the SQLite database layer."""

import os
import sqlite3
import pytest
import json

from gradient_quest import db

# Use an in-memory database for testing
@pytest.fixture(autouse=True)
def setup_test_db(monkeypatch, tmp_path):
    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr(db, "DB_PATH", db_path)
    monkeypatch.setattr(db, "DB_DIR", str(tmp_path))
    yield
    if os.path.exists(db_path):
        os.remove(db_path)

def test_get_or_create_user():
    user = db.get_or_create_user("test@example.com", "Test User", "http://example.com/pic.jpg")
    assert user["email"] == "test@example.com"
    assert user["name"] == "Test User"
    assert user["picture"] == "http://example.com/pic.jpg"
    
    # Test upsert
    user = db.get_or_create_user("test@example.com", "Updated User", "http://example.com/pic2.jpg")
    assert user["name"] == "Updated User"
    assert user["picture"] == "http://example.com/pic2.jpg"

def test_session_lifecycle():
    email = "test@example.com"
    db.get_or_create_user(email, "Test User")
    
    # Auto-create active session if none exists
    progress = db.get_active_session(email)
    assert progress["xp"] == 0
    assert progress["level"] == 1
    
    # Save session
    progress["xp"] = 100
    db.save_session(email, progress)
    
    # Load session
    loaded = db.get_active_session(email)
    assert loaded["xp"] == 100
    
    # Create new session (deactivates old one)
    new_progress = db.create_new_session(email, "My New Game")
    assert new_progress["xp"] == 0
    
    # Verify we are on the new session
    active = db.get_active_session(email)
    assert active["xp"] == 0
    
    # List sessions
    sessions = db.list_sessions(email)
    assert len(sessions) == 2
    assert sessions[0]["session_name"] == "My New Game"
    assert sessions[0]["is_active"] is True
    assert sessions[1]["session_name"] == "Game 1"
    assert sessions[1]["is_active"] is False
    assert sessions[1]["xp"] == 100
    
    # Set active session
    old_id = sessions[1]["id"]
    db.set_active_session(email, old_id)
    
    # Verify old session is active again
    active = db.get_active_session(email)
    assert active["xp"] == 100
    
    # Restart session
    restarted = db.restart_session(email, old_id)
    assert restarted["xp"] == 0
    
    # Verify it was reset
    active = db.get_active_session(email)
    assert active["xp"] == 0
    
    # Delete session
    db.delete_session(email, old_id)
    sessions = db.list_sessions(email)
    assert len(sessions) == 1
    assert sessions[0]["session_name"] == "My New Game"
    assert sessions[0]["is_active"] is True # It should have auto-activated the remaining one
