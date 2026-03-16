"""
RSS scraper: fetches and normalizes articles from all configured sources.
"""

import re
import time
import logging
import datetime
from typing import List, Dict, Optional

import feedparser

from config import SOURCES, LOOKBACK_HOURS

logger = logging.getLogger(__name__)

# Increase feedparser timeout
feedparser.PREFERRED_XML_PARSERS = []


def _strip_html(text: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _parse_date(entry) -> Optional[datetime.datetime]:
    """Extract publication date from a feed entry."""
    for attr in ("published_parsed", "updated_parsed", "created_parsed"):
        val = getattr(entry, attr, None)
        if val:
            try:
                return datetime.datetime(*val[:6], tzinfo=datetime.timezone.utc)
            except (TypeError, ValueError):
                continue
    return None


def fetch_feed(source_id: str, source: dict) -> List[Dict]:
    """Fetch and normalize articles from a single RSS/Atom feed."""
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=LOOKBACK_HOURS)
    articles = []

    try:
        feed = feedparser.parse(source["rss"], request_headers={"User-Agent": "ContrapuntoUY/1.0"})

        if feed.bozo and not feed.entries:
            logger.warning(f"[{source['name']}] Feed error: {feed.get('bozo_exception', 'unknown')}")
            return []

        for entry in feed.entries:
            title = _strip_html(entry.get("title", "")).strip()
            url = entry.get("link", "")

            if not title or not url:
                continue

            # Get description/summary
            description = ""
            for attr in ("summary", "description", "content"):
                val = getattr(entry, attr, None)
                if isinstance(val, list) and val:
                    val = val[0].get("value", "")
                if val:
                    description = _strip_html(str(val))[:500]
                    break

            pub_date = _parse_date(entry)

            # Skip articles older than the lookback window (be lenient if no date)
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

    except Exception as e:
        logger.error(f"[{source['name']}] Unexpected error: {e}")

    return articles


def fetch_all() -> List[Dict]:
    """Fetch recent articles from all configured sources."""
    all_articles: List[Dict] = []

    for source_id, source in SOURCES.items():
        logger.info(f"Fetching {source['name']} ...")
        articles = fetch_feed(source_id, source)
        logger.info(f"  → {len(articles)} article(s)")
        all_articles.extend(articles)
        time.sleep(0.8)  # polite crawl delay

    logger.info(f"Total articles fetched: {len(all_articles)}")
    return all_articles
