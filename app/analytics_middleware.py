import time
import hashlib
import re
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import SessionLocal
from app.analytics_models import PageView

def parse_user_agent(ua_string: str):
    if not ua_string:
        return "Unknown", "Unknown", "Desktop"

    ua = ua_string.lower()

    # Device Type
    device_type = "Desktop"
    if any(b in ua for b in ["bot", "crawler", "spider", "slurp", "fetch"]):
        device_type = "Bot"
    elif "ipad" in ua or "tablet" in ua:
        device_type = "Tablet"
    elif "mobi" in ua or "android" in ua or "iphone" in ua:
        device_type = "Mobile"

    # OS
    os_name = "Other"
    if "windows" in ua:
        os_name = "Windows"
    elif "macintosh" in ua or "mac os" in ua:
        os_name = "macOS"
    elif "iphone" in ua or "ipad" in ua or "ipod" in ua:
        os_name = "iOS"
    elif "android" in ua:
        os_name = "Android"
    elif "linux" in ua:
        os_name = "Linux"

    # Browser
    browser = "Other"
    if "edg" in ua:
        browser = "Edge"
    elif "opr" in ua or "opera" in ua:
        browser = "Opera"
    elif "chrome" in ua and "chromium" not in ua:
        browser = "Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"
    elif "bot" in ua or "crawler" in ua:
        browser = "Bot"

    return browser, os_name, device_type

class AnalyticsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Skip tracking for analytics dashboard, analytics APIs, and favicon/static
        if path.startswith("/analytics") or path.startswith("/api/analytics") or path in ["/favicon.ico"]:
            return await call_next(request)

        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        # Extract real IP (Cloudflare tunnel support)
        ip_address = (
            request.headers.get("cf-connecting-ip") or
            request.headers.get("x-forwarded-for", "").split(",")[0].strip() or
            (request.client.host if request.client else "127.0.0.1")
        )

        user_agent = request.headers.get("user-agent", "")
        referrer = request.headers.get("referer", None)
        method = request.method
        status_code = response.status_code

        browser, os_name, device_type = parse_user_agent(user_agent)

        # Approximate unique session ID from IP + UA
        session_id = hashlib.sha256((ip_address + user_agent).encode()).hexdigest()

        # Save to database in background / synchronous session
        try:
            db = SessionLocal()
            page_view = PageView(
                path=path,
                method=method,
                status_code=status_code,
                ip_address=ip_address,
                user_agent=user_agent[:500],
                referrer=referrer[:500] if referrer else None,
                browser=browser,
                os=os_name,
                device_type=device_type,
                response_time_ms=duration_ms,
                session_id=session_id
            )
            db.add(page_view)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Analytics logging error: {e}")

        return response
