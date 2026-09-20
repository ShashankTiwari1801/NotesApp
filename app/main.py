from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from starlette import status
from typing import List
import os
from dotenv import load_dotenv
from app import crud, database
from app.models import Note, NoteCreate, NoteUpdate
from sqlalchemy.orm import Session

load_dotenv()

# SECURITY CONFIGURATION
API_KEY_NAME = "X-API-Key"
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

@app.post("/notes", response_model=Note)
def add_note(note: NoteCreate):
    db = next(database.get_db())
    return crud.create_note(db, note)

@app.get("/notes", response_model=List[Note])
def get_notes():
    db = next(database.get_db())
    return crud.get_all_notes(db)

@app.get("/notes/{note_id}", response_model=Note)
def get_note(note_id: int):
    db = next(database.get_db())
    note = crud.get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@app.put("/notes/{note_id}", response_model=Note)
def update_note(note_id: int, note: NoteUpdate):
    db = next(database.get_db())
    updated_note = crud.update_note(db, note_id, note)
    if not updated_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return updated_note

@app.delete("/notes/{note_id}")
def delete_note(note_id: int):
    db = next(database.get_db())
    if not crud.delete_note(db, note_id):
        raise HTTPException(status_code=404, detail="Note not found")
    return {"message": "Note deleted"}

@app.get("/notes/count")
def count_notes():
    db = next(database.get_db())
    return {"total_notes": crud.count_notes(db)}

@app.get("/notes/by-tag/{tag}", response_model=List[Note])
def get_notes_by_tag(tag: str):
    db = next(database.get_db())
    return crud.get_notes_by_tag(db, tag)
