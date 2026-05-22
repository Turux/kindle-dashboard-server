# fetcher/fetch.py

import json
import os
import time
import schedule
from config import DATA_DIR, SOURCES_DIR, ARTICLES_DIR

from sources.weather import fetch_weather
from sources.f1      import fetch_f1
from sources.sailgp  import fetch_sailgp
from sources.stocks  import fetch_stocks
from sources.rss     import fetch_all_rss

def ensure_dirs():
    os.makedirs(DATA_DIR,     exist_ok=True)
    os.makedirs(SOURCES_DIR,  exist_ok=True)
    os.makedirs(ARTICLES_DIR, exist_ok=True)

def run_fetch():
    print("Fetching all data...")
    ensure_dirs()

    data = {}

    try:
        data["weather"] = fetch_weather()
        print("  weather ok")
    except Exception as e:
        print(f"  weather failed: {e}")
        data["weather"] = {}

    try:
        data["f1"] = fetch_f1()
        print("  f1 ok")
    except Exception as e:
        print(f"  f1 failed: {e}")
        data["f1"] = {}

    try:
        data["sailgp"] = fetch_sailgp()
        print("  sailgp ok")
    except Exception as e:
        print(f"  sailgp failed: {e}")
        data["sailgp"] = {}

    try:
        data["stocks"] = fetch_stocks()
        print("  stocks ok")
    except Exception as e:
        print(f"  stocks failed: {e}")
        data["stocks"] = []

    try:
        headlines, sources = fetch_all_rss()
        data["headlines"] = headlines
        # write per-source files
        for source_id, items in sources.items():
            path = f"{SOURCES_DIR}/{source_id}.json"
            with open(path, "w") as f:
                json.dump(items, f)
        print("  rss ok")
    except Exception as e:
        print(f"  rss failed: {e}")
        data["headlines"] = []

    # write home cache
    home_path = f"{DATA_DIR}/home.json"
    with open(home_path, "w") as f:
        json.dump(data, f)

    print(f"Fetch complete.")

if __name__ == "__main__":
    # run once immediately on start
    run_fetch()

    interval = int(os.environ.get("FETCH_INTERVAL", 1800))
    schedule.every(interval).seconds.do(run_fetch)

    while True:
        schedule.run_pending()
        time.sleep(60)