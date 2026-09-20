from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NoteBase(BaseModel):
    title: str
    content: str
    tags: List[str]
    tag_colors: List[str]

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    tag_colors: Optional[List[str]] = None

class Note(NoteBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
