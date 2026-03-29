"""Note Taker CLI — add, list, delete notes saved in ~/.notes.json"""

import argparse
import io
import os
import sys
import uuid
from datetime import datetime

# Force UTF-8 output on Windows so non-ASCII text prints correctly
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import storage


def add_note(notes: list, text: str) -> dict:
    """Add a new note. Mutates notes list. Returns the new note."""
    note = {
        "id": uuid.uuid4().hex[:8],
        "text": text,
        "created": datetime.now().isoformat(timespec="seconds"),
    }
    notes.append(note)
    return note


def delete_note(notes: list, note_id: str) -> bool:
    """Delete note by ID. Mutates notes list. Returns True if found."""
    for i, note in enumerate(notes):
        if note["id"] == note_id:
            notes.pop(i)
            return True
    return False


def list_notes(notes: list) -> list:
    """Return notes sorted by created date ascending."""
    return sorted(notes, key=lambda n: n["created"])


def search_notes(notes: list, query: str) -> list:
    """Return notes where query appears in text (case-insensitive). Sorted by created asc."""
    q = query.lower()
    matches = [n for n in notes if q in n["text"].lower()]
    return sorted(matches, key=lambda n: n["created"])


# ─── CLI ────────────────────────────────────────────────────────────────────


def cmd_add(args, notes, path):
    note = add_note(notes, args.text)
    storage.save_notes(notes, path)
    print(f"Added [{note['id']}]: {note['text']}")


def cmd_list(args, notes, path):
    sorted_notes = list_notes(notes)
    if getattr(args, "json", False):
        import json as _json
        print(_json.dumps(sorted_notes, ensure_ascii=False, indent=2))
        return
    if not sorted_notes:
        print("No notes yet. Use: note add \"your text\"")
        return
    print(f"--- {len(sorted_notes)} note(s) ---")
    for note in sorted_notes:
        print(f"[{note['id']}] {note['created']}  {note['text']}")


def cmd_delete(args, notes, path):
    if delete_note(notes, args.id):
        storage.save_notes(notes, path)
        print(f"Deleted note [{args.id}]")
    else:
        print(f"Note [{args.id}] not found.", file=sys.stderr)
        sys.exit(1)


def cmd_search(args, notes, path):
    results = search_notes(notes, args.query)
    if not results:
        print(f'No notes matching "{args.query}"')
        return
    for note in results:
        print(f"[{note['id']}] {note['created']}  {note['text']}")


def cmd_lock(args, notes, path):
    """Encrypt notes file and remove plain JSON."""
    import getpass
    from crypto import encrypt_data
    # Load current notes
    current_notes = storage.load_notes(path)
    if not os.path.exists(path) and not current_notes:
        print("No notes to lock.")
        return
    password = getpass.getpass("Set lock password: ")
    confirm = getpass.getpass("Confirm password: ")
    if password != confirm:
        print("Passwords do not match.", file=sys.stderr)
        sys.exit(1)
    import json as _json
    data = _json.dumps(current_notes, ensure_ascii=False).encode("utf-8")
    blob = encrypt_data(data, password)
    enc_path = storage.ENCRYPTED_FILE
    with open(enc_path, "wb") as f:
        f.write(blob)
    # Remove plain file
    if os.path.exists(path):
        os.unlink(path)
    # Cache session key
    from crypto import derive_key
    import struct
    salt = blob[:16]
    key = derive_key(password, salt)
    storage.save_session_key(key)
    print("Notes locked. Session active (no need to unlock for this session).")
    print("WARNING: If you forget your password, notes cannot be recovered.")


def cmd_unlock(args, notes, path):
    """Decrypt notes file back to plain JSON."""
    import getpass
    from crypto import decrypt_data
    enc_path = storage.ENCRYPTED_FILE
    if not os.path.exists(enc_path):
        print("Notes are not locked.")
        return
    password = getpass.getpass("Enter password: ")
    with open(enc_path, "rb") as f:
        blob = f.read()
    try:
        data = decrypt_data(blob, password)
    except ValueError:
        print("Wrong password.", file=sys.stderr)
        sys.exit(1)
    import json as _json
    current_notes = _json.loads(data.decode("utf-8"))
    storage.save_notes(current_notes, path)
    os.unlink(enc_path)
    storage.clear_session_key()
    print(f"Notes unlocked. {len(current_notes)} note(s) restored.")


def main(argv=None, path=None):
    if path is None:
        path = storage.DEFAULT_PATH

    parser = argparse.ArgumentParser(
        prog="note",
        description="Simple note taker — notes saved in ~/.notes.json",
    )
    sub = parser.add_subparsers(dest="command", metavar="command")
    sub.required = True

    p_add = sub.add_parser("add", help="Add a new note")
    p_add.add_argument("text", help="Note text")

    p_list = sub.add_parser("list", help="List all notes")
    p_list.add_argument("--json", action="store_true", dest="json", help="Output as JSON")

    p_del = sub.add_parser("delete", help="Delete a note by ID")
    p_del.add_argument("id", help="Note ID (8 chars)")

    p_search = sub.add_parser("search", help="Search notes by keyword")
    p_search.add_argument("query", help="Search keyword (case-insensitive)")

    sub.add_parser("lock", help="Encrypt notes with a password")
    sub.add_parser("unlock", help="Decrypt notes (enter password)")

    args = parser.parse_args(argv)
    notes = storage.load_notes(path)

    dispatch = {
        "add": cmd_add,
        "list": cmd_list,
        "delete": cmd_delete,
        "search": cmd_search,
        "lock": cmd_lock,
        "unlock": cmd_unlock,
    }
    dispatch[args.command](args, notes, path)


if __name__ == "__main__":
    main()
