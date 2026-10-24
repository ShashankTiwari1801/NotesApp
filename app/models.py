from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    api_key = Column(String(64), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    notes = relationship("Note", back_populates="owner", cascade="all, delete-orphan")

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), index=True, nullable=False)
    content = Column(Text, nullable=True)
    category = Column(String(100), default="General", index=True)
    tags = Column(String(255), default="") # comma-separated tags
    pinned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="notes")
