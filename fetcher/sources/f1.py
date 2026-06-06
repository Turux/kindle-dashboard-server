# fetcher/sources/f1.py

import requests
import json
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from config import LOCAL_TIMEZONE

CACHE_FILE = "/data/cache/f1_last.json"

def _save_last(data):
    try:
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def _load_last():
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE) as f:
                return json.load(f)
    except:
        pass
    return None

def fetch_f1():
    try:
        r = requests.get(
            "https://api.openf1.org/v1/sessions?year=2026",
            timeout=10
        )

        if r.status_code == 401:
            # session is live — fall back to last known session
            last = _load_last()
            if last:
                return {
                    "label": "Live now",
                    "event": last.get("event", "F1"),
                    "name":  last.get("name", "Session live"),
                    "date":  last.get("date", ""),
                }
            else:
                return {
                    "label": "Live now",
                    "event": "On air",
                    "name":  "Session live",
                    "date":  "Check TV",
                }

        r.raise_for_status()
        sessions = r.json()

        if not sessions:
            return {"label": "No sessions", "event": "---",
                    "name": "---", "date": "---"}

        # compare full datetime not just date
        now    = datetime.now(timezone.utc).isoformat()
        future = [
            s for s in sessions
            if s.get("date_end", "") > now
            and not s.get("is_cancelled", False)
        ]

        if not future:
            return {"label": "Season complete", "event": "---",
                    "name": "---", "date": "---"}

        future.sort(key=lambda s: s["date_start"])
        s = future[0]

        location = s.get("location", "")
        name     = s.get("session_name", "---")

        try:
            dt    = datetime.fromisoformat(s["date_start"]).astimezone(ZoneInfo(LOCAL_TIMEZONE))
            label = dt.strftime("%-d %b %H:%M")
        except:
            label = s["date_start"][:10]

        result = {
            "label": "Next Session",
            "event": f"{location} GP",
            "name":  name,
            "date":  label,
        }

        # save for use during live sessions
        _save_last(result)
        return result

    except Exception as e:
        print(f"  f1 failed: {e}")
        # fall back to last known on any error
        last = _load_last()
        return last if last else {
            "label": "Unavailable", "event": "---",
            "name": "---", "date": "---"
        }