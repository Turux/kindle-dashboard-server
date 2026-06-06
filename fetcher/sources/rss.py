# fetcher/sources/rss.py

import feedparser
import trafilatura
import hashlib
import html
import os
import unicodedata
import re
from datetime import datetime, timezone
from config import RSS_SOURCES, HOME_HEADLINE_SOURCES, ARTICLES_DIR
from config import RSS_SOURCES, HOME_HEADLINE_SOURCES, ARTICLES_DIR, SOURCE_DISPLAY_NAMES

_CAPTION_RE = re.compile(
    r'(Photo|Photograph|Image|Picture|Credit|Pic)(\s+by\s+|\s*:\s*)',
    re.IGNORECASE
)

def _strip_captions(text):
    """Remove short paragraphs that look like photo/image captions."""
    paras = text.split('\n')
    cleaned = [p for p in paras
               if not (p.strip() and len(p.strip()) < 200 and _CAPTION_RE.search(p))]
    return '\n'.join(cleaned)

_DATE_LINE_RE = re.compile(
    r'^\s*(\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4}|\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s*$',
    re.IGNORECASE
)

def _strip_title_from_body(text, title):
    """Remove title and publication date if trafilatura pulled them into the body."""
    if not title or not text:
        return text
    t_norm = re.sub(r'\s+', ' ', title.strip().lower())
    check_len = min(len(t_norm), 60)
    if check_len < 10:
        return text
    paras = text.split('\n')
    i = 0
    while i < len(paras) and not paras[i].strip():
        i += 1
    if i >= len(paras):
        return text
    p_norm = re.sub(r'\s+', ' ', paras[i].strip().lower())
    if p_norm.startswith(t_norm[:check_len]) or t_norm.startswith(p_norm[:check_len]):
        paras.pop(i)
        # also strip the next line if it looks like a standalone date
        while i < len(paras) and not paras[i].strip():
            i += 1
        if i < len(paras) and len(paras[i].strip()) < 40 and _DATE_LINE_RE.match(paras[i]):
            paras.pop(i)
    return '\n'.join(paras)

def _strip_duplicate_intro(text, summary):
    """Remove first body paragraph if it duplicates the summary."""
    if not summary or not text:
        return text
    s_norm = re.sub(r'\s+', ' ', summary.strip().lower())
    check_len = min(len(s_norm), 60)
    if check_len < 15:
        return text
    paras = text.split('\n')
    for i, p in enumerate(paras):
        if p.strip():
            p_norm = re.sub(r'\s+', ' ', p.strip().lower())
            if p_norm.startswith(s_norm[:check_len]):
                paras.pop(i)
            break
    return '\n'.join(paras)

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

def _clean_text(text):
    if not text:
        return text

    text = html.unescape(text)

    # strip markdown links [text](url) → text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # strip common paywall prompts
    text = re.sub(r'\[Upgrade to.*?\]', '', text)
    text = re.sub(r'\[Subscribe.*?\]', '', text)
    text = re.sub(r'Upgrade to membership.*', '', text, flags=re.IGNORECASE)
    
    # strip bare URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # existing replacements
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "--",
        "\u2026": "...",
        "\u00a0": " ",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return text

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
        if text:
            text = _clean_text(text)
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

                # skip podcast/audio entries (e.g. Guardian Long Read audio feed)
                enclosures = getattr(entry, "enclosures", [])
                if any(e.get("type", "").startswith("audio/") for e in enclosures):
                    continue

                # clean summary — strip HTML tags
                if summary:
                    summary = re.sub(r"<[^>]+>", "", summary).strip()

                url_hash = _url_hash(link)

                # fetch and cache article text
                article_path = f"{ARTICLES_DIR}/{url_hash}.txt"
                if not os.path.exists(article_path):
                    text = _fetch_article(link)
                    if text:
                        text = _strip_captions(text)
                        text = _strip_duplicate_intro(text, summary)
                        text = _strip_title_from_body(text, title)
                        os.makedirs(ARTICLES_DIR, exist_ok=True)
                        with open(article_path, "w") as f:
                            f.write(text)

                # strip body-bleed from summary: some feeds (e.g. Guardian)
                # concatenate article body text directly onto the standfirst.
                # find the first 5 words of the body in the summary and trim there.
                if summary and os.path.exists(article_path):
                    try:
                        with open(article_path) as f:
                            body_start = f.read(300)
                        body_words = body_start.split()
                        if len(body_words) >= 5:
                            needle = " ".join(body_words[:5])
                            s_norm = re.sub(r"\s+", " ", summary.lower())
                            n_norm = re.sub(r"\s+", " ", needle.lower())
                            idx = s_norm.find(n_norm)
                            if idx > 20:
                                summary = summary[:idx].rstrip()
                    except Exception:
                        pass

                # cap only if unusually long; genuine long summaries are kept
                if len(summary) > 300:
                    summary = summary[:200].strip()

                items.append({
                    "title":    _clean_text(title),
                    "source":   SOURCE_DISPLAY_NAMES.get(source_id, source_id),  # ← this line
                    "date":     date,
                    "summary":  _clean_text(summary),
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