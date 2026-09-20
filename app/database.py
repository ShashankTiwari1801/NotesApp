import sqlite3
import json
from datetime import datetime
from app.models import NoteCreate, NoteUpdate

DB_NAME = "data/notes.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            tag_colors TEXT,
            created_at TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_note(note: NoteCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO notes (title, content, tags, tag_colors, created_at) VALUES (?, ?, ?, ?, ?)",
        (note.title, note.content, json.dumps(note.tags), json.dumps(note.tag_colors), datetime.now())
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return note_id

def get_all_notes():
    conn = get_db_connection()
    notes = conn.execute("SELECT * FROM notes").fetchall()
    conn.close()
    return [dict(n) for n in notes]

def get_note_by_id(note_id: int):
    conn = get_db_connection()
    note = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
    conn.close()
    return dict(note) if note else None

def update_note(note_id: int, note: NoteUpdate):
    conn = get_db_connection()
    # Simple dynamic update (for demo purposes)
    existing = get_note_by_id(note_id)
    if not existing:
        return False

    update_data = note.model_dump(exclude_unset=True)
    if not update_data:
        return True

    query = "UPDATE notes SET "
    params = []
    for key, value in update_data.items():
        if key in ["tags", "tag_colors"]:
            value = json.dumps(value)
        query += f"{key} = ?, "
        params.append(value)

    query = query.rstrip(", ") + " WHERE id = ?"
    params.append(note_id)

    conn.execute(query, tuple(params))
    conn.commit()
    conn.close()
    return True

def delete_note(note_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    conn.commit()
    conn.close()
    return True

def count_notes():
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
    conn.close()
    return count

def get_notes_by_tag(tag: str):
    conn = get_db_connection()
    # Searching within JSON array string stored as TEXT
    search_term = f'%"{tag}"%'
    notes = conn.execute("SELECT * FROM notes WHERE tags LIKE ?", (search_term,)).fetchall()
    conn.close()
    return [dict(n) for n in notes]
