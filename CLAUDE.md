# Kindle Dashboard — Server Repo Context

## What this is
Self-hosted backend for the Kindle Dashboard project. Fetches weather, F1, SailGP, stocks and news articles from various sources, caches them as JSON/text files, and serves them to a Kindle 4 device via a single HTTPS API endpoint.

## Companion repo
The device app is at `https://github.com/Turux/kindle-dashboard-device` — a Python app running directly on a jailbroken Kindle 4, reading from this API.

## Stack
- **API:** Flask + Gunicorn (Python 3.11)
- **Fetcher:** Python scheduler, runs every 30 minutes
- **Reverse proxy:** Caddy (automatic HTTPS via Let's Encrypt)
- **Storage:** JSON/txt files on shared Docker volume at `/data/cache/`
- **Deployment:** Docker Compose on a Linux VPS
- **Domain:** `kindle.turux.co.uk`

## Architecture
Two containers sharing a volume:

```
fetcher → writes /data/cache/
api     → reads  /data/cache/
caddy   → proxies HTTPS to api:8000
```

The fetcher runs on a schedule — the API never fetches data itself. Communication between containers is via the shared volume only. This separation is intentional and should be maintained.

## API endpoints
- `GET /api/health` → `{"status": "ok"}`
- `GET /api/full-sync?lat=52.6&lon=-1.1` → full payload (home, sources, articles)

The `lat`/`lon` params are optional. When provided, the API saves them to `/data/cache/device_config.json` for the fetcher to use on next run for weather.

## Data sources
| Source | Method | Notes |
|--------|--------|-------|
| Weather | Open-Meteo API | Free, no key. Reads coords from device_config.json if available, falls back to config.py |
| F1 | OpenF1 API | Free. Returns 401 during live sessions — falls back to last known session cached in f1_last.json |
| SailGP | ICS calendar from Contentful CDN | DTSTART = Race Day 1 (Saturday), DTSTART+1 = Race Day 2 (Sunday) |
| Stocks | yfinance | Free, 15-min delayed. LSE tickers in pence not pounds |
| News | RSS + trafilatura | feedparser for headlines, trafilatura for full article extraction |

## RSS sources (config.py)
```python
RSS_SOURCES = {
    "guardian":             "https://www.theguardian.com/uk/rss",
    "semafor":              "https://www.semafor.com/rss.xml",
    "bellingcat":           "https://www.bellingcat.com/feed/",
    "the_nerve":            "https://rss.beehiiv.com/feeds/30tXEwEwRx.xml",
    "the_dial":             "https://thedialrss.com/combined-rss/",
    "the_conversation":     "https://theconversation.com/uk/articles.atom",
    "propublica":           "https://www.propublica.org/rss",
    "404_media":            "https://www.404media.co/rss",
    "guardian_long_read":   "https://www.theguardian.com/news/series/the-long-read/rss",
}
```

Guardian Long Read shares url_hash with any overlap in the main Guardian feed — article text is never stored twice. Podcast/audio entries are filtered out via enclosure type check. FT was previously attempted via podcast RSS (acast) — access token URLs in show notes are blocked by Cloudflare bot detection server-side. Not currently implemented.

## Cache structure
```
/data/cache/
├── home.json           # home screen payload (weather, f1, sailgp, stocks, headlines)
├── meta.json           # last fetch timestamp (not currently used by API)
├── device_config.json  # lat/lon written by API when device sends coordinates
├── f1_last.json        # last successful F1 fetch, used as fallback during live sessions
├── sources/            # per-source headline JSON files
│   └── *.json
└── articles/           # pre-fetched article text files
    └── *.txt
```

Article cache policy:
- Server keeps max 250 articles, deletes oldest beyond that
- Kindle keeps max 120 articles for 7 days
- Kindle never overwrites existing articles on sync (add only)

## Text cleaning (_clean_text in rss.py)
Applied to all article text and summaries:
- Strip markdown links `[text](url)` → `text`
- Strip bare URLs
- Replace unicode punctuation with ASCII equivalents
- Strip HTML entities (`&nbsp;` etc)
- Preserve newlines (encode line by line, not whole text)
- Strip paywall/subscription prompts

## Configuration (fetcher/config.py)
```python
WEATHER_LAT = 52.61457      # fallback if device doesn't send coords
WEATHER_LON = -1.1239
LOCAL_TIMEZONE = "Europe/London"  # used for F1 session time conversion (zoneinfo)
STOCK_TICKERS = [...]       # Yahoo Finance format
RSS_SOURCES = {...}         # 9 sources — see above
HOME_HEADLINE_SOURCES = {   # which sources + how many for home screen
    "guardian": 2,
    "semafor": 1,
    "the_nerve": 1,
}
SOURCE_DISPLAY_NAMES = {...} # display names sent to Kindle
```

## Deployment
```bash
# on VPS
cd /usr/local/kindle-dashboard-server
git pull
docker compose build
docker compose up -d

# force manual fetch
docker compose exec fetcher python -c "import fetch; fetch.run_fetch()"

# view logs
docker compose logs fetcher -f
docker compose logs api -f
```

## Open issues
1. **FT articles** — FT's bot detection blocks server-side fetching even with access tokens. Replaced with The Conversation for now.
2. **SailGP session times** — ICS only gives event dates, no race times. Race days inferred as Sat/Sun from DTSTART.
3. **America's Cup widget** — AC37 2027 in Barcelona. Needs ICS source + layout change on device side.
4. **Ocean Race widget** — same as above.
5. **Market hours indicator** — show when LSE/NYSE are closed on stocks widget.
6. **FT fetch rate limiting** — if FT is re-attempted in future, fetch weekdays only.

## Recently fixed
- Photo/image caption paragraphs stripped from article text (`_strip_captions()` in rss.py)
- Duplicate intro paragraph stripped when it matches the RSS summary (`_strip_duplicate_intro()` in rss.py)
- Guardian summary body-bleed: RSS standfirst has body text concatenated onto it; server now finds first 5 body words in summary and trims from there (`_strip_body_bleed()` in rss.py)
- Title and publication date stripped if trafilatura pulls them into article body (`_strip_title_from_body()` in rss.py)
- Podcast/audio entries filtered out by enclosure type before processing (catches Guardian Long Read audio episodes)
- F1 session times converted from UTC to local timezone via `LOCAL_TIMEZONE` in config.py (zoneinfo, handles BST/GMT automatically)
- SailGP stale event: DTEND is exclusive in iCalendar — changed `<` to `<=` so event is filtered on the day after it ends
- F1 live session fallback (caches last known session in f1_last.json)
- SailGP Race Day 1/2 logic (DTSTART = Saturday = Race Day 1)
- Weather coordinates configurable from device (via ?lat=&lon= params)
- Article cleanup limit increased to 250 (was 150)
- Text cleaning preserves newlines (was corrupting paragraph structure)
- HTML entities stripped from article text