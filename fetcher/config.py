# fetcher/config.py

# ── location ──────────────────────────────────────
WEATHER_LAT  = 51.5074   # London — update to your actual location
WEATHER_LON  = -0.1278
LOCAL_TIMEZONE = "Europe/London"

# ── stocks ────────────────────────────────────────
STOCK_TICKERS = [
    {"ticker": "AAPL",   "label": "AAPL"},
    {"ticker": "BA.L",   "label": "BA.L"},
    {"ticker": "SDUS.L", "label": "SDUS.L"},
]

# ── rss sources ───────────────────────────────────
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

# ── headlines for home screen ─────────────────────
# which sources contribute to the home screen mix, and how many each
HOME_HEADLINE_SOURCES = {
    "guardian":  2,
    "semafor":   1,
    "the_nerve": 1,
}

SOURCE_DISPLAY_NAMES = {
    "guardian":           "Guardian",
    "semafor":            "Semafor",
    "bellingcat":         "Bellingcat",
    "the_nerve":          "The Nerve",
    "the_dial":           "The Dial",
    "the_conversation":   "The Conversation",
    "propublica":         "ProPublica",
    "404_media":          "404 Media",
    "guardian_long_read": "G. Long Read",
}

# ── paths ─────────────────────────────────────────
DATA_DIR         = "/data/cache"
SOURCES_DIR      = f"{DATA_DIR}/sources"
ARTICLES_DIR     = f"{DATA_DIR}/articles"