# fetcher/sources/f1.py

import requests
from datetime import datetime, timezone

def fetch_f1():
    # get remaining sessions this year
    now = datetime.now(timezone.utc).isoformat()
    url = (
        f"https://api.openf1.org/v1/sessions"
        f"?date_start>={now[:10]}"
        f"&session_type!=Race"  
    )
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    sessions = r.json()

    if not sessions:
        return {"label": "No upcoming sessions", "name": "---", "date": "---"}

    # sort by date, take the next one
    sessions.sort(key=lambda s: s["date_start"])
    next_session = sessions[0]

    name     = next_session.get("session_name", "---")
    location = next_session.get("location", "")
    dt_str   = next_session.get("date_start", "")

    # format date
    try:
        dt    = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        # convert to UK time (BST = UTC+1 in summer)
        label = dt.strftime("%-d %b %H:%M")
    except:
        label = dt_str[:10]

    return {
        "label": "Next Session",
        "name":  f"{location} {name}",
        "date":  label,
    }