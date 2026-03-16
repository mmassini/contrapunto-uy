"""
RSS scraper: fetches and normalizes articles from all configured sources.
Uses requests for reliable fetching (SSL control, proper headers),
then feedparser for parsing.
"""

import re
import time
import logging
import datetime
import warnings
from typing import List, Dict, Optional

import feedparser
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from config import SOURCES, LOOKBACK_HOURS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ContrapuntoUY/1.0; +https://contrapunto.uy)"
    ),
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
}
TIMEOUT = 15  # seconds


def _strip_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _strip_gn_suffix(title: str) -> str:
    """Remove Google News ' - SOURCE NAME' suffix from titles."""
    return re.sub(r"\s+-\s+[^-]+$", "", title).strip()


def _parse_date(entry) -> Optional[datetime.datetime]:
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime.datetime(*val[:6], tzinfo=datetime.timezone.utc)
            except (TypeError, ValueError):
                continue
    return None


def _fetch_raw(url: str, ssl_verify: bool = True) -> Optional[bytes]:
    """Fetch raw bytes from a URL using requests."""
    try:
        if not ssl_verify:
            warnings.filterwarnings("ignore", category=InsecureRequestWarning)
        resp = requests.get(
            url, headers=HEADERS, timeout=TIMEOUT,
            verify=ssl_verify, allow_redirects=True
        )
        if resp.status_code == 200:
            return resp.content
        logger.debug(f"HTTP {resp.status_code} for {url}")
        return None
    except requests.exceptions.SSLError:
        if ssl_verify:
            logger.warning(f"SSL error for {url}, retrying without verification")
            return _fetch_raw(url, ssl_verify=False)
        return None
    except requests.exceptions.RequestException as e:
        logger.debug(f"Request failed for {url}: {e}")
        return None


def _try_urls(source: dict) -> Optional[feedparser.FeedParserDict]:
    """Try primary URL then fallbacks until one returns feed entries."""
    ssl_verify = source.get("ssl_verify", True)
    urls = [source["rss"]] + source.get("rss_fallbacks", [])

    for url in urls:
        raw = _fetch_raw(url, ssl_verify=ssl_verify)
        if raw is None:
            continue
        feed = feedparser.parse(raw)
        if feed.entries:
            logger.info(f"  ✓ {source['name']}: {len(feed.entries)} entries from {url}")
            return feed
        if feed.bozo:
            logger.debug(f"  Bozo at {url}: {feed.get('bozo_exception', '?')}")

    return None


def fetch_feed(source_id: str, source: dict) -> List[Dict]:
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=LOOKBACK_HOURS)
    articles = []

    feed = _try_urls(source)
    if feed is None:
        logger.warning(f"  ✗ {source['name']}: no working feed found")
        return []

    for entry in feed.entries:
        title = _strip_gn_suffix(_strip_html(entry.get("title", "")).strip())
        url = entry.get("link", "")
        if not title or not url:
            continue

        description = ""
        for attr in ("summary", "description"):
            val = getattr(entry, attr, None)
            if isinstance(val, list) and val:
                val = val[0].get("value", "")
            if val:
                description = _strip_html(str(val))[:500]
                break

        pub_date = _parse_date(entry)
        if pub_date and pub_date < cutoff:
            continue

        articles.append({
            "source_id": source_id,
            "source_name": source["name"],
            "source_short": source["short"],
            "source_color": source["color"],
            "source_text_color": source["text_color"],
            "source_url": source["url"],
            "title": title,
            "url": url,
            "description": description,
            "pub_date": pub_date.isoformat() if pub_date else None,
        })

    return articles


def fetch_all() -> List[Dict]:
    all_articles: List[Dict] = []
    for source_id, source in SOURCES.items():
        logger.info(f"Fetching {source['name']} ...")
        articles = fetch_feed(source_id, source)
        logger.info(f"  → {len(articles)} recent article(s)")
        all_articles.extend(articles)
        time.sleep(0.5)
    logger.info(f"Total: {len(all_articles)} articles from {len(SOURCES)} sources")
    return all_articles
