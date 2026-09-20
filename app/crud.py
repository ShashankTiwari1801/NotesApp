import json
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Note, NoteCreate, NoteUpdate
from app.database import NoteModel, get_db

def create_note(db: Session, note: NoteCreate):
    db_note = NoteModel(
        title=note.title,
        content=note.content,
        tags=json.dumps(note.tags),
        tag_colors=json.dumps(note.tag_colors),
        created_at=datetime.utcnow()
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)

    # Return as dict and parse JSON fields
    note_dict = db_note.__dict__
    note_dict["tags"] = json.loads(note_dict["tags"])
    note_dict["tag_colors"] = json.loads(note_dict["tag_colors"])
    return note_dict

def get_all_notes(db: Session):
    notes = db.query(NoteModel).all()
    results = []
    for n in notes:
        d = n.__dict__
        d["tags"] = json.loads(d["tags"])
        d["tag_colors"] = json.loads(d["tag_colors"])
        results.append(d)
    return results

def get_note_by_id(db: Session, note_id: int):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        return None
    d = note.__dict__
    d["tags"] = json.loads(d["tags"])
    d["tag_colors"] = json.loads(d["tag_colors"])
    return d

def update_note(db: Session, note_id: int, note: NoteUpdate):
    db_note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not db_note:
        return None

    update_data = note.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key in ["tags", "tag_colors"]:
            value = json.dumps(value)
        setattr(db_note, key, value)

    db.commit()
    db.refresh(db_note)

    d = db_note.__dict__
    d["tags"] = json.loads(d["tags"])
    d["tag_colors"] = json.loads(d["tag_colors"])
    return d

def delete_note(db: Session, note_id: int):
    note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
    if not note:
        return False
    db.delete(note)
    db.commit()
    return True

def count_notes(db: Session):
    return db.query(NoteModel).count()

def get_notes_by_tag(db: Session, tag: str):
    search_term = f'%"{tag}"%'
    notes = db.query(NoteModel).filter(NoteModel.tags.like(search_term)).all()
    results = []
    for n in notes:
        d = n.__dict__
        d["tags"] = json.loads(d["tags"])
        d["tag_colors"] = json.loads(d["tag_colors"])
        results.append(d)
    return results
