# fetcher/sources/sailgp.py

import requests
from datetime import datetime, date
from icalendar import Calendar

ICS_URL = (
    "https://assets.ctfassets.net/2lppn7hwgzta/"
    "6HralgBt91NOXhRv1Um1LV/"
    "2d5b06c8a91a2c8afcbb5c414cc89c7f/"
    "SailGP_2026_Season_Events_c_92adfa12f333863ee04ba0594cea41338558f718ab1564552e7cd35caa085aad_group.calendar.google.com.ics"
)

def _clean_name(summary):
    """Extract a short display name from SailGP event summary"""
    # format 1: "Sponsor Name Sail Grand Prix | Location"
    if "|" in summary:
        location = summary.split("|")[1].strip()
        return f"{location} SGP"

    # format 2: "Sponsor Location Sail Grand Prix"
    if "Sail Grand Prix" in summary:
        before = summary.split("Sail Grand Prix")[0].strip()
        words  = before.split()
        if len(words) >= 2:
            return f"{' '.join(words[-2:])} SGP"
        elif words:
            return f"{words[-1]} SGP"

    # fallback
    return summary[:20]

def fetch_sailgp():
    r = requests.get(ICS_URL, timeout=10)
    r.raise_for_status()

    cal    = Calendar.from_ical(r.content)
    today  = date.today()
    events = []

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        dtstart = component.get("DTSTART").dt
        if isinstance(dtstart, datetime):
            event_date = dtstart.date()
        else:
            event_date = dtstart

        if event_date < today:
            continue

        summary = str(component.get("SUMMARY", ""))
        events.append({
            "date":    event_date,
            "summary": summary,
        })

    if not events:
        return {"label": "Season complete", "name": "---", "date": "---"}

    events.sort(key=lambda e: e["date"])
    next_event = events[0]

    name  = _clean_name(next_event["summary"])
    label = next_event["date"].strftime("%-d %b")

    return {
        "label": "Next Event",
        "name":  name,
        "date":  label,
    }