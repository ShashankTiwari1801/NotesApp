import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status, Header, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.analytics_models import PageView
from app.analytics_schemas import (
    SummaryStats, DateCountEntry, NameCountEntry, PathCountEntry,
    ReferrerEntry, RecentVisitResponse, PasswordRequest
)

analytics_router = APIRouter()
templates = Jinja2Templates(directory="templates")

ANALYTICS_PASSWORD = os.environ.get("ANALYTICS_PASSWORD", "admin123")

def verify_analytics_auth(x_analytics_password: Optional[str] = Header(None), password: Optional[str] = Query(None)):
    provided = x_analytics_password or password
    if not provided or provided != ANALYTICS_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized: Invalid analytics password"
        )
    return True


@analytics_router.get("/analytics", response_class=HTMLResponse)
def analytics_page(request: Request):
    return templates.TemplateResponse(request, "analytics.html", {})

@analytics_router.post("/api/analytics/verify-password")
def verify_password(payload: PasswordRequest):
    if payload.password == ANALYTICS_PASSWORD:
        return {"success": True}
    raise HTTPException(status_code=403, detail="Incorrect password")

@analytics_router.get("/api/analytics/summary", response_model=SummaryStats, dependencies=[Depends(verify_analytics_auth)])
def get_analytics_summary(db: Session = Depends(get_db)):
    now = datetime.utcnow()
    today_start = datetime(now.year, now.month, now.day)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    total_views = db.query(func.count(PageView.id)).scalar() or 0
    unique_visitors = db.query(func.count(func.distinct(PageView.session_id))).scalar() or 0

    views_today = db.query(func.count(PageView.id)).filter(PageView.timestamp >= today_start).scalar() or 0
    views_this_week = db.query(func.count(PageView.id)).filter(PageView.timestamp >= week_start).scalar() or 0
    views_this_month = db.query(func.count(PageView.id)).filter(PageView.timestamp >= month_start).scalar() or 0

    avg_duration = db.query(func.avg(PageView.response_time_ms)).scalar() or 0.0

    return SummaryStats(
        total_views=total_views,
        unique_visitors=unique_visitors,
        views_today=views_today,
        views_this_week=views_this_week,
        views_this_month=views_this_month,
        avg_response_time_ms=round(avg_duration, 2)
    )

@analytics_router.get("/api/analytics/views-over-time", dependencies=[Depends(verify_analytics_auth)])
def get_views_over_time(days: int = 30, db: Session = Depends(get_db)):
    start_date = datetime.utcnow() - timedelta(days=days)

    results = (
        db.query(
            func.date(PageView.timestamp).label("date"),
            func.count(PageView.id).label("count")
        )
        .filter(PageView.timestamp >= start_date)
        .group_by(func.date(PageView.timestamp))
        .order_by(func.date(PageView.timestamp))
        .all()
    )

    data = [{"date": r.date, "count": r.count} for r in results]
    return data

@analytics_router.get("/api/analytics/top-pages", dependencies=[Depends(verify_analytics_auth)])
def get_top_pages(limit: int = 10, db: Session = Depends(get_db)):
    results = (
        db.query(
            PageView.path.label("path"),
            func.count(PageView.id).label("count")
        )
        .group_by(PageView.path)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    return [{"path": r.path, "count": r.count} for r in results]

@analytics_router.get("/api/analytics/referrers", dependencies=[Depends(verify_analytics_auth)])
def get_referrers(limit: int = 10, db: Session = Depends(get_db)):
    results = (
        db.query(
            PageView.referrer.label("referrer"),
            func.count(PageView.id).label("count")
        )
        .filter(PageView.referrer.isnot(None), PageView.referrer != "")
        .group_by(PageView.referrer)
        .order_by(desc("count"))
        .limit(limit)
        .all()
    )
    return [{"referrer": r.referrer, "count": r.count} for r in results]

@analytics_router.get("/api/analytics/browsers", dependencies=[Depends(verify_analytics_auth)])
def get_browsers(db: Session = Depends(get_db)):
    results = (
        db.query(
            PageView.browser.label("name"),
            func.count(PageView.id).label("count")
        )
        .group_by(PageView.browser)
        .order_by(desc("count"))
        .all()
    )
    return [{"name": r.name or "Unknown", "count": r.count} for r in results]

@analytics_router.get("/api/analytics/os", dependencies=[Depends(verify_analytics_auth)])
def get_os(db: Session = Depends(get_db)):
    results = (
        db.query(
            PageView.os.label("name"),
            func.count(PageView.id).label("count")
        )
        .group_by(PageView.os)
        .order_by(desc("count"))
        .all()
    )
    return [{"name": r.name or "Unknown", "count": r.count} for r in results]

@analytics_router.get("/api/analytics/devices", dependencies=[Depends(verify_analytics_auth)])
def get_devices(db: Session = Depends(get_db)):
    results = (
        db.query(
            PageView.device_type.label("name"),
            func.count(PageView.id).label("count")
        )
        .group_by(PageView.device_type)
        .order_by(desc("count"))
        .all()
    )
    return [{"name": r.name or "Desktop", "count": r.count} for r in results]

@analytics_router.get("/api/analytics/recent", response_model=List[RecentVisitResponse], dependencies=[Depends(verify_analytics_auth)])
def get_recent_visits(limit: int = 50, db: Session = Depends(get_db)):
    visits = (
        db.query(PageView)
        .order_by(desc(PageView.timestamp))
        .limit(limit)
        .all()
    )
    return visits
