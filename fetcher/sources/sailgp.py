# fetcher/sources/sailgp.py

import requests
from datetime import datetime, date, timezone
from icalendar import Calendar

ICS_URL = (
    "https://assets.ctfassets.net/2lppn7hwgzta/"
    "6HralgBt91NOXhRv1Um1LV/"
    "2d5b06c8a91a2c8afcbb5c414cc89c7f/"
    "SailGP_2026_Season_Events_c_92adfa12f333863ee04ba0594cea41338558f718ab1564552e7cd35caa085aad_group.calendar.google.com.ics"
)

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
        # DTSTART may be a date or datetime
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

    # clean up the summary — strip sponsor prefix if present
    # e.g. "Emirates Great Britain Sail Grand Prix | Portsmouth"
    # →    "Great Britain | Portsmouth"
    name = next_event["summary"]
    if "|" in name:
        parts = name.split("|")
        # strip "Sail Grand Prix" noise, keep location
        event_name = parts[0].strip()
        location   = parts[1].strip()
        # remove sponsor name (everything before "Sail Grand Prix")
        if "Sail Grand Prix" in event_name:
            event_name = event_name.split("Sail Grand Prix")[0].strip()
            # remove trailing sponsor word if present
            words = event_name.split()
            # heuristic: if last word looks like a country/city keep it
            name = f"{location} SGP"
        else:
            name = f"{location} SGP"
    
    label = next_event["date"].strftime("%-d %b")

    return {
        "label": "Next Event",
        "name":  name,
        "date":  label,
    }