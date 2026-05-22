# fetcher/sources/f1.py

import requests
from datetime import datetime, timezone

def fetch_f1():
    try:
        r = requests.get(
            "https://api.openf1.org/v1/sessions?year=2026",
            timeout=10
        )

        if r.status_code == 401:
            return {
                "label": "Session live!",
                "name":  "F1 on now",
                "date":  "Check TV",
            }

        r.raise_for_status()
        sessions = r.json()

        if not sessions:
            return {"label": "No sessions", "name": "---", "date": "---"}

        today  = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        future = [
            s for s in sessions
            if s.get("date_start", "")[:10] >= today
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

    except Exception as e:
        print(f"  f1 failed: {e}")
        return {"label": "Unavailable", "name": "---", "date": "---"}