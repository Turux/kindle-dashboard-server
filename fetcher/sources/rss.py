# fetcher/sources/rss.py

import feedparser
import trafilatura
import hashlib
import os
from datetime import datetime, timezone
from config import RSS_SOURCES, HOME_HEADLINE_SOURCES, ARTICLES_DIR
from config import RSS_SOURCES, HOME_HEADLINE_SOURCES, ARTICLES_DIR, SOURCE_DISPLAY_NAMES

def _url_hash(url):
    return hashlib.md5(url.encode()).hexdigest()[:10]

def _parse_date(entry):
    """Extract a clean date string from a feed entry"""
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                dt = datetime(*t[:6], tzinfo=timezone.utc)
                return dt.strftime("%-d %b")
            except:
                pass
    return ""

def _fetch_article(url):
    """Fetch and clean article text using trafilatura"""
    try:
        downloaded = trafilatura.fetch_url(url)
        if not downloaded:
            return None
        text = trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            no_fallback=False,
        )
        return text
    except Exception as e:
        print(f"    article fetch failed for {url}: {e}")
        return None

def fetch_all_rss():
    """
    Fetch all RSS sources.
    Returns:
        headlines: list of top headlines for home screen
        sources:   dict of {source_id: [headline, ...]} for source view
    """
    all_sources = {}
    home_pool   = {}   # source_id -> list of items

    for source_id, url in RSS_SOURCES.items():
        if not url:
            print(f"  rss: skipping {source_id} (no URL)")
            continue

        print(f"  rss: fetching {source_id}...")
        try:
            feed  = feedparser.parse(url)
            items = []

            for entry in feed.entries[:10]:   # max 10 per source
                title   = entry.get("title", "").strip()
                link    = entry.get("link", "")
                summary = entry.get("summary", "").strip()
                date    = _parse_date(entry)

                if not title or not link:
                    continue

                # clean summary — strip HTML tags crudely
                if summary:
                    import re
                    summary = re.sub(r"<[^>]+>", "", summary)
                    summary = summary[:200].strip()

                url_hash = _url_hash(link)

                # fetch and cache article text
                article_path = f"{ARTICLES_DIR}/{url_hash}.txt"
                if not os.path.exists(article_path):
                    text = _fetch_article(link)
                    if text:
                        os.makedirs(ARTICLES_DIR, exist_ok=True)
                        with open(article_path, "w") as f:
                            f.write(text)

                items.append({
                    "title":    title,
                    "source":   SOURCE_DISPLAY_NAMES.get(source_id, source_id),  # ← this line
                    "date":     date,
                    "summary":  summary,
                    "url":      link,
                    "url_hash": url_hash,
                })

            all_sources[source_id] = items
            home_pool[source_id]   = items
            print(f"    {len(items)} items")

        except Exception as e:
            print(f"  rss: failed for {source_id}: {e}")
            all_sources[source_id] = []

    # build home headlines from configured sources
    headlines = []
    for source_id, count in HOME_HEADLINE_SOURCES.items():
        items = home_pool.get(source_id, [])
        headlines.extend(items[:count])

    return headlines, all_sources