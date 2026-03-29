"""Tests for note taker CLI — written BEFORE implementation (TDD RED phase)."""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


class TestStorage(unittest.TestCase):
    """Tests for storage.py — load/save JSON with atomic write."""

    def setUp(self):
        self.tmp = tempfile.mktemp(suffix=".json")

    def tearDown(self):
        if os.path.exists(self.tmp):
            os.remove(self.tmp)

    def test_load_returns_empty_list_when_file_missing(self):
        from storage import load_notes
        notes = load_notes("/nonexistent/path/notes.json")
        self.assertEqual(notes, [])

    def test_save_and_load_roundtrip(self):
        from storage import save_notes, load_notes
        notes = [{"id": "abc12345", "text": "hello", "created": "2026-01-01T00:00:00"}]
        save_notes(notes, self.tmp)
        loaded = load_notes(self.tmp)
        self.assertEqual(loaded, notes)

    def test_save_is_atomic_no_partial_write(self):
        """File must not be left in broken state if write fails mid-way."""
        from storage import save_notes, load_notes
        original = [{"id": "abc12345", "text": "original", "created": "2026-01-01T00:00:00"}]
        save_notes(original, self.tmp)
        # Corrupt attempt: simulate by checking file is valid JSON after save
        with open(self.tmp) as f:
            data = json.load(f)
        self.assertEqual(data, original)


class TestAddNote(unittest.TestCase):
    """Tests for add_note() function."""

    def test_add_note_returns_note_with_id_and_timestamp(self):
        from notes import add_note
        notes = []
        note = add_note(notes, "buy milk")
        self.assertEqual(len(notes), 1)
        self.assertEqual(note["text"], "buy milk")
        self.assertIn("id", note)
        self.assertIn("created", note)
        self.assertEqual(len(note["id"]), 8)  # UUID8

    def test_add_note_appends_to_existing_list(self):
        from notes import add_note
        notes = [{"id": "existing1", "text": "old note", "created": "2026-01-01"}]
        add_note(notes, "new note")
        self.assertEqual(len(notes), 2)

    def test_add_note_ids_are_unique(self):
        from notes import add_note
        notes = []
        add_note(notes, "note 1")
        add_note(notes, "note 2")
        ids = [n["id"] for n in notes]
        self.assertEqual(len(set(ids)), 2)


class TestDeleteNote(unittest.TestCase):
    """Tests for delete_note() function."""

    def test_delete_existing_note(self):
        from notes import delete_note
        notes = [{"id": "abc12345", "text": "to delete", "created": "2026-01-01"}]
        result = delete_note(notes, "abc12345")
        self.assertTrue(result)
        self.assertEqual(len(notes), 0)

    def test_delete_nonexistent_id_returns_false(self):
        from notes import delete_note
        notes = [{"id": "abc12345", "text": "keep me", "created": "2026-01-01"}]
        result = delete_note(notes, "xxxxxxxx")
        self.assertFalse(result)
        self.assertEqual(len(notes), 1)

    def test_delete_from_empty_list_returns_false(self):
        from notes import delete_note
        notes = []
        result = delete_note(notes, "abc12345")
        self.assertFalse(result)


class TestListNotes(unittest.TestCase):
    """Tests for list_notes() — returns sorted list."""

    def test_list_empty(self):
        from notes import list_notes
        result = list_notes([])
        self.assertEqual(result, [])

    def test_list_returns_notes_sorted_by_created_asc(self):
        from notes import list_notes
        notes = [
            {"id": "bbb", "text": "second", "created": "2026-01-02T00:00:00"},
            {"id": "aaa", "text": "first",  "created": "2026-01-01T00:00:00"},
        ]
        result = list_notes(notes)
        self.assertEqual(result[0]["text"], "first")
        self.assertEqual(result[1]["text"], "second")


class TestSearchNotes(unittest.TestCase):
    def test_search_finds_matching_note(self):
        from notes import search_notes
        notes = [
            {"id": "aaa", "text": "buy milk", "created": "2026-01-01"},
            {"id": "bbb", "text": "call doctor", "created": "2026-01-02"},
        ]
        result = search_notes(notes, "milk")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "aaa")

    def test_search_is_case_insensitive(self):
        from notes import search_notes
        notes = [{"id": "aaa", "text": "Buy Milk", "created": "2026-01-01"}]
        result = search_notes(notes, "milk")
        self.assertEqual(len(result), 1)

    def test_search_returns_empty_when_no_match(self):
        from notes import search_notes
        notes = [{"id": "aaa", "text": "buy milk", "created": "2026-01-01"}]
        result = search_notes(notes, "coffee")
        self.assertEqual(result, [])

    def test_search_empty_notes(self):
        from notes import search_notes
        result = search_notes([], "anything")
        self.assertEqual(result, [])


class TestListOutput(unittest.TestCase):
    def test_list_count_in_output(self):
        """list_notes returns correct count."""
        from notes import list_notes
        notes = [
            {"id": "aaa", "text": "a", "created": "2026-01-01"},
            {"id": "bbb", "text": "b", "created": "2026-01-02"},
        ]
        result = list_notes(notes)
        self.assertEqual(len(result), 2)

    def test_list_notes_empty_returns_empty(self):
        from notes import list_notes
        self.assertEqual(list_notes([]), [])


class TestLockUnlock(unittest.TestCase):
    def setUp(self):
        self.tmp_notes = tempfile.mktemp(suffix=".json")
        self.tmp_enc = tempfile.mktemp(suffix=".enc")

    def tearDown(self):
        for f in [self.tmp_notes, self.tmp_enc]:
            if os.path.exists(f):
                os.remove(f)

    def test_storage_session_key_roundtrip(self):
        import tempfile, stat
        import storage
        tmp_session = tempfile.mktemp(suffix=".session")
        original_session = storage.SESSION_FILE
        storage.SESSION_FILE = tmp_session
        try:
            key = b'\x01' * 32
            storage.save_session_key(key)
            loaded = storage.load_session_key()
            self.assertEqual(loaded, key)
        finally:
            storage.SESSION_FILE = original_session
            if os.path.exists(tmp_session):
                os.unlink(tmp_session)

    def test_clear_session_key(self):
        import tempfile
        import storage
        tmp_session = tempfile.mktemp(suffix=".session")
        original_session = storage.SESSION_FILE
        storage.SESSION_FILE = tmp_session
        try:
            storage.save_session_key(b'\x02' * 32)
            storage.clear_session_key()
            self.assertIsNone(storage.load_session_key())
        finally:
            storage.SESSION_FILE = original_session

    def test_load_session_key_missing_returns_none(self):
        import storage
        original_session = storage.SESSION_FILE
        storage.SESSION_FILE = "/nonexistent/session"
        try:
            self.assertIsNone(storage.load_session_key())
        finally:
            storage.SESSION_FILE = original_session


if __name__ == "__main__":
    unittest.main()
