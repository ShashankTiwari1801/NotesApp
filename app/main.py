from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from starlette import status
from typing import List
import json
import os
from dotenv import load_dotenv
import database
from app.models import Note, NoteCreate, NoteUpdate

load_dotenv()

# SECURITY CONFIGURATION
API_KEY_NAME = "X-API-Key"
# Comma-separated keys in .env file
ALLOWED_API_KEYS = os.getenv("ALLOWED_API_KEYS", "").split(",")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def get_api_key(api_key: str = Security(api_key_header)):
    if api_key in ALLOWED_API_KEYS:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

app = FastAPI(dependencies=[Depends(get_api_key)])

# Initialize DB on startup
@app.on_event("startup")
def startup_event():
    database.init_db()

def _format_note(note_dict):
    note_dict["tags"] = json.loads(note_dict["tags"])
    note_dict["tag_colors"] = json.loads(note_dict["tag_colors"])
    return note_dict

@app.post("/notes", response_model=Note)
def add_note(note: NoteCreate):
    note_id = database.create_note(note)
    new_note = database.get_note_by_id(note_id)
    return _format_note(new_note)

@app.get("/notes", response_model=List[Note])
def get_notes():
    notes = database.get_all_notes()
    return [_format_note(n) for n in notes]

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    note = database.get_note_by_id(note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return _format_note(note)

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate):
    if not database.update_note(note_id, note):
        raise HTTPException(status_code=404, detail="Note not found")
    updated_note = database.get_note_by_id(note_id)
    return _format_note(updated_note)

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    if not database.delete_note(note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}

@app.get("/notes/count")
def count_notes():
    return {"total_notes": database.count_notes()}

@app.get("/notes/by-tag/{tag}", response_model=List[Note])
def get_notes_by_tag(tag: str):
    notes = database.get_notes_by_tag(tag)
    return [_format_note(n) for n in notes]
