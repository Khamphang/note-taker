"""Atomic JSON storage for note taker CLI."""

import json
import os
import stat
import tempfile
from pathlib import Path

DEFAULT_PATH = str(Path.home() / ".notes.json")


def load_notes(path: str = DEFAULT_PATH) -> list:
    """Load notes from JSON file. Returns [] if file missing or unreadable."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_notes(notes: list, path: str = DEFAULT_PATH) -> None:
    """Save notes to JSON file using atomic write (temp → rename)."""
    path = str(path)
    dir_ = os.path.dirname(path) or "."
    fd, tmp_path = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except Exception:
        os.unlink(tmp_path)
        raise


SESSION_FILE = str(Path.home() / ".notes.session")
ENCRYPTED_FILE = str(Path.home() / ".notes.enc")


def save_session_key(key: bytes) -> None:
    """Cache the derived key in a session file (chmod 600)."""
    with open(SESSION_FILE, "w") as f:
        f.write(key.hex())
    try:
        os.chmod(SESSION_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass


def load_session_key() -> bytes | None:
    """Load cached session key. Returns None if not found."""
    try:
        with open(SESSION_FILE) as f:
            return bytes.fromhex(f.read().strip())
    except Exception:
        return None


def clear_session_key() -> None:
    """Delete session cache file."""
    try:
        os.unlink(SESSION_FILE)
    except Exception:
        pass
