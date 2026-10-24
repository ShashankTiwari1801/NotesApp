import os
from pathlib import Path

# Load .env file if present
env_path = Path(".") / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"\''))

import hashlib
import secrets
from fastapi import FastAPI, Depends, HTTPException, Request, status, Security
from fastapi.security import APIKeyHeader
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import engine, Base, get_db
from app.models import User, Note
from app.analytics_models import PageView
from app.analytics_middleware import AnalyticsMiddleware
from app.analytics_routes import analytics_router
from app.schemas import (
    UserCreate, UserLogin, UserResponse, ApiKeyLogin,
    NoteCreate, NoteUpdate, NoteResponse
)

# Recreate database tables with new schema
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cloud Notes App", description="Multi-user Notes Application with API Key Sync", version="2.0.0")

# Register analytics middleware
app.add_middleware(AnalyticsMiddleware)

# Include analytics router
app.include_router(analytics_router)

templates = Jinja2Templates(directory="templates")

# Helper functions for password hashing
def hash_password(password: str) -> str:
    salt = "cloudnotes_secure_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

# API Key Header
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_current_user(api_key: str = Security(api_key_header), db: Session = Depends(get_db)) -> User:
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing API Key"
        )
    user = db.query(User).filter(User.api_key == api_key).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return user

# Frontend Route
@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

# --- Auth API Routes ---
@app.post("/api/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user_in.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    api_key = "sk_" + secrets.token_hex(24)
    hashed = hash_password(user_in.password)

    user = User(
        username=user_in.username,
        hashed_password=hashed,
        api_key=api_key
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/api/auth/login", response_model=UserResponse)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    hashed = hash_password(user_in.password)
    user = db.query(User).filter(User.username == user_in.username, User.hashed_password == hashed).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    return user

@app.post("/api/auth/generate-key", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def generate_instant_key(db: Session = Depends(get_db)):
    """Generate an instant API key without needing a username/password."""
    unique_id = secrets.token_hex(4)
    username = f"user_{unique_id}"
    api_key = "sk_" + secrets.token_hex(24)
    hashed = hash_password(secrets.token_hex(16))

    user = User(
        username=username,
        hashed_password=hashed,
        api_key=api_key
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.get("/api/auth/verify-key", response_model=UserResponse)
@app.post("/api/auth/verify-key", response_model=UserResponse)
def verify_key(current_user: User = Depends(get_current_user)):
    return current_user

# --- Note CRUD API Routes (User-scoped) ---
@app.post("/api/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_note = Note(
        user_id=current_user.id,
        title=note.title,
        content=note.content,
        category=note.category or "General",
        tags=note.tags or "",
        pinned=note.pinned
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note

@app.get("/api/notes", response_model=List[NoteResponse])
def get_notes(
    search: Optional[str] = None,
    category: Optional[str] = None,
    tag: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Note).filter(Note.user_id == current_user.id)
    if search:
        search_term = f"%{search}%"
        query = query.filter((Note.title.ilike(search_term)) | (Note.content.ilike(search_term)))
    if category and category != "All":
        query = query.filter(Note.category == category)
    if tag:
        query = query.filter(Note.tags.ilike(f"%{tag}%"))

    notes = query.order_by(Note.pinned.desc(), Note.updated_at.desc()).all()
    return notes

@app.get("/api/notes/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    return db_note

@app.put("/api/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")

    update_data = note_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_note, key, value)

    db.commit()
    db.refresh(db_note)
    return db_note

@app.delete("/api/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db.delete(db_note)
    db.commit()
    return None

@app.post("/api/notes/{note_id}/toggle-pin", response_model=NoteResponse)
def toggle_pin(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_note = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    db_note.pinned = not db_note.pinned
    db.commit()
    db.refresh(db_note)
    return db_note
