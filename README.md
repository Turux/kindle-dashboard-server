# kindle-dashboard-server

Self-hosted backend for the Kindle Dashboard project. Fetches weather, motorsport and sailing schedules, stock prices and news articles from various sources, and serves them to the Kindle device via a single HTTPS API endpoint.

## Stack

- **API:** Flask + Gunicorn
- **Reverse proxy:** Caddy (automatic HTTPS via Let's Encrypt)
- **Fetcher:** Python scheduler with per-source modules
- **Storage:** JSON files on shared Docker volume
- **Deployment:** Docker Compose on any Linux VPS

## Prerequisites

- Docker + Docker Compose
- A domain with an A record pointing to your server
- Ports 80 and 443 open on your server firewall

## Installation

```bash
git clone https://github.com/Turux/kindle-dashboard-server.git
cd kindle-dashboard-server
```

Edit `Caddyfile` with your domain:
```
kindle.yourdomain.com {
    reverse_proxy api:8000
}
```

Edit `fetcher/config.py` with your settings (see Configuration below).

```bash
docker compose build
docker compose up -d
```

Verify:
```bash
curl https://kindle.yourdomain.com/api/health
# {"status": "ok"}
```

## Configuration

All configuration lives in `fetcher/config.py`:

```python
# Location for weather
WEATHER_LAT = 51.5074
WEATHER_LON = -0.1278

# Stock tickers (Yahoo Finance format)
STOCK_TICKERS = [
    {"ticker": "AAPL",   "label": "AAPL"},
    # add your tickers here
]

# RSS feed URLs per source
RSS_SOURCES = {
    "source_one": "https://example.com/feed",
    "source_two": "https://example.com/rss",
    # add your sources here
}

# Which sources contribute to the home screen, and how many headlines each
HOME_HEADLINE_SOURCES = {
    "source_one": 2,
    "source_two": 1,
}

# Display names shown on the Kindle
SOURCE_DISPLAY_NAMES = {
    "source_one": "Source One",
    "source_two": "Source Two",
}
```

## File Structure

```
kindle-dashboard-server/
├── docker-compose.yml
├── Caddyfile
├── api/
│   ├── Dockerfile
│   └── app.py            # Flask API
└── fetcher/
    ├── Dockerfile
    ├── fetch.py          # main scheduler, runs every 30 minutes
    ├── config.py         # all user configuration
    └── sources/
        ├── __init__.py
        ├── weather.py    # Open-Meteo API
        ├── f1.py         # OpenF1 API
        ├── sailgp.py     # ICS calendar file
        ├── stocks.py     # yfinance
        └── rss.py        # feedparser + trafilatura
```

## Architecture

```
Fetcher (every 30 min)
├── Open-Meteo → weather data
├── OpenF1 API → next F1 session
├── SailGP ICS → next sailing event
├── yfinance → stock prices
└── RSS feeds → headlines + article text (via trafilatura)
         │
         ▼
    /data/cache/
         │
         ▼
    Flask API
         │
    HTTPS (Caddy)
         │
         ▼
    Kindle device
```

### Shared volume

The fetcher writes JSON files to `/data/cache/`. The API reads from the same volume. No database required.

```
data/cache/
├── home.json          # home screen payload
├── meta.json          # last fetch timestamp
├── sources/           # per-source headline files
│   └── *.json
└── articles/          # pre-fetched article text
    └── *.txt
```

## API Endpoints

### `GET /api/health`
Returns `{"status": "ok"}`. Used by the Kindle to verify connectivity.

### `GET /api/full-sync`
Returns the complete payload the Kindle needs in a single request:

```json
{
    "home": {
        "weather": {"temp": "14°", "desc": "Cloudy", "rain": "Rain 70%"},
        "f1": {"label": "Next Session", "event": "Canada GP", "name": "Practice 2", "date": "23 May 14:00"},
        "sailgp": {"label": "Next Event", "name": "New York SGP", "date": "30 May"},
        "stocks": [
            {"ticker": "AAPL", "price": "213.4", "change": 1.2, "pct": "1.2"}
        ],
        "headlines": [
            {
                "source": "Guardian",
                "title": "Article headline",
                "date": "23 May",
                "summary": "Brief summary...",
                "url_hash": "abc123"
            }
        ]
    },
    "sources": {
        "source_one": [...],
        "source_two": [...]
    },
    "articles": {
        "abc123": "Full article text..."
    }
}
```

## Data Sources

| Data | Source | Notes |
|------|--------|-------|
| Weather | Open-Meteo | Free, no API key required |
| F1 | OpenF1 API | Free, locked during live sessions (handled gracefully) |
| SailGP | Official ICS calendar | Fetched from public CDN |
| Stocks | yfinance | Free, 15-minute delayed |
| News | RSS feeds | feedparser + trafilatura for article extraction |

## Cache Management

Articles are cached in `/data/cache/articles/`. Policy:
- Maximum 150 articles retained server-side
- Oldest files removed when limit exceeded
- Articles re-fetched automatically if missing on next run

Force a manual fetch:
```bash
docker compose exec fetcher python -c "import fetch; fetch.run_fetch()"
```

View fetcher logs:
```bash
docker compose logs fetcher -f
```

## Known Issues

- **OpenF1 during live sessions** — the API returns 401 during live F1 sessions. The fetcher handles this gracefully by returning a "Session live" indicator.
- **SailGP session detail** — the ICS file provides event-level dates only, not individual race session times (Race 1, Race 2, Final).

## Roadmap

- America's Cup schedule widget
- Ocean Race schedule widget
- Market hours indicator for stocks
- SailGP session-level detail