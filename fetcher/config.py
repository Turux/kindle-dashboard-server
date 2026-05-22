# fetcher/config.py

# ── location ──────────────────────────────────────
WEATHER_LAT  = 51.5074   # London — update to your actual location
WEATHER_LON  = -0.1278

# ── stocks ────────────────────────────────────────
STOCK_TICKERS = [
    {"ticker": "AAPL",   "label": "AAPL"},
    {"ticker": "BA.L",   "label": "BA.L"},
    {"ticker": "SDUS.L", "label": "SDUS.L"},
]

# ── rss sources ───────────────────────────────────
RSS_SOURCES = {
    "guardian":  "https://www.theguardian.com/uk/rss",
    "semafor":   "https://www.semafor.com/feed",
    "bellingcat": "https://www.bellingcat.com/feed/",
    "the_nerve": "https://rss.beehiiv.com/feeds/30tXEwEwRx.xml",
    "the_dial":  "https://thedialrss.com/combined-rss/",
    "ft":        None,   # placeholder — TBD
}

# ── headlines for home screen ─────────────────────
# which sources contribute to the home screen mix, and how many each
HOME_HEADLINE_SOURCES = {
    "guardian":  2,
    "semafor":   1,
    "the_nerve": 1,
}

# ── paths ─────────────────────────────────────────
DATA_DIR         = "/data/cache"
SOURCES_DIR      = f"{DATA_DIR}/sources"
ARTICLES_DIR     = f"{DATA_DIR}/articles"