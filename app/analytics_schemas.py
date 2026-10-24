from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class SummaryStats(BaseModel):
    total_views: int
    unique_visitors: int
    views_today: int
    views_this_week: int
    views_this_month: int
    avg_response_time_ms: float

    class Config:
        from_attributes = True

class DateCountEntry(BaseModel):
    date: str
    count: int

class NameCountEntry(BaseModel):
    name: str
    count: int

class PathCountEntry(BaseModel):
    path: str
    count: int

class ReferrerEntry(BaseModel):
    referrer: str
    count: int

class RecentVisitResponse(BaseModel):
    id: int
    timestamp: datetime
    path: str
    method: str
    status_code: int
    ip_address: str
    browser: Optional[str] = None
    os: Optional[str] = None
    device_type: Optional[str] = None
    country: Optional[str] = None
    referrer: Optional[str] = None
    response_time_ms: Optional[float] = None

    class Config:
        from_attributes = True

class PasswordRequest(BaseModel):
    password: str
