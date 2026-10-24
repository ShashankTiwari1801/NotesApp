from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel

# User Schemas
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    api_key: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyLogin(BaseModel):
    api_key: str

# Note Schemas
class NoteBase(BaseModel):
    title: str
    content: Optional[str] = ""
    category: Optional[str] = "General"
    tags: Optional[str] = ""
    pinned: Optional[bool] = False

class NoteCreate(NoteBase):
    pass

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    pinned: Optional[bool] = None

class NoteResponse(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
