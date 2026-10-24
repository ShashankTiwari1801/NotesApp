from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base

class PageView(Base):
    __tablename__ = "page_views"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    path = Column(String(500), index=True)
    method = Column(String(10))
    status_code = Column(Integer)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    referrer = Column(String(500), nullable=True)
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    device_type = Column(String(20), nullable=True)
    response_time_ms = Column(Float, nullable=True)
    session_id = Column(String(64), nullable=True, index=True)
