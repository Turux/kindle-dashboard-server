# fetcher/sources/f1.py

import requests
from datetime import datetime, timezone

def fetch_f1():
    r = requests.get(
        "https://api.openf1.org/v1/sessions?year=2026",
        timeout=10
    )
    r.raise_for_status()
    sessions = r.json()

    if not sessions:
        return {"label": "No upcoming sessions", "name": "---", "date": "---"}

    # filter to future sessions, ignore cancelled ones
    now    = datetime.now(timezone.utc).isoformat()
    future = [
        s for s in sessions
        if s.get("date_start", "") >= now
        and not s.get("is_cancelled", False)
    ]

    if not future:
        return {"label": "Season complete", "name": "---", "date": "---"}

    future.sort(key=lambda s: s["date_start"])
    s = future[0]

    location = s.get("location", "")
    name     = s.get("session_name", "---")

    try:
        dt    = datetime.fromisoformat(s["date_start"])
        label = dt.strftime("%-d %b %H:%M")
    except:
        label = s["date_start"][:10]

    return {
        "label": "Next Session",
        "name":  f"{location} {name}",
        "date":  label,
    }