"""
Diagnóstico rápido: verifica qué feeds RSS responden y cuántos artículos tienen.
Correr con: python scripts/diagnose.py
"""
import sys
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import feedparser
import requests
import datetime

warnings.filterwarnings("ignore")

from config import SOURCES, LOOKBACK_HOURS

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ContrapuntoUY/1.0)",
    "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*",
}
cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=LOOKBACK_HOURS)

print(f"\n{'='*70}")
print(f"Diagnóstico de feeds RSS — últimas {LOOKBACK_HOURS}h")
print(f"{'='*70}\n")

total_articles = 0
working_feeds = 0

for source_id, source in SOURCES.items():
    urls = [source["rss"]] + source.get("rss_fallbacks", [])
    ssl = source.get("ssl_verify", True)
    found = False

    for url in urls:
        try:
            resp = requests.get(url, headers=HEADERS, timeout=12, verify=ssl, allow_redirects=True)
            ct = resp.headers.get("content-type", "?")[:40]
            status = resp.status_code

            if status != 200:
                print(f"  ✗ {source['name']:<22} HTTP {status}  {url}")
                continue

            feed = feedparser.parse(resp.content)
            total_e = len(feed.entries)
            recent = sum(
                1 for e in feed.entries
                if (lambda d: d is None or d >= cutoff)(
                    next(
                        (datetime.datetime(*getattr(e, a)[:6], tzinfo=datetime.timezone.utc)
                         for a in ("published_parsed","updated_parsed")
                         if getattr(e, a, None)),
                        None
                    )
                )
            )

            if total_e > 0:
                print(f"  ✓ {source['name']:<22} {total_e:>3} entradas  {recent:>3} recientes  [{ct}]")
                total_articles += recent
                working_feeds += 1
                found = True
                break
            else:
                bozo = str(feed.get("bozo_exception", ""))[:60]
                print(f"  ~ {source['name']:<22} 0 entradas  [{ct}]  bozo:{bozo}  {url}")

        except Exception as e:
            print(f"  ✗ {source['name']:<22} ERROR: {str(e)[:70]}")
            break

    if not found and len(urls) > 1:
        print(f"    → ninguna URL funcionó para {source['name']}")

print(f"\n{'='*70}")
print(f"  Feeds activos: {working_feeds}/{len(SOURCES)}")
print(f"  Artículos recientes total: {total_articles}")
print(f"{'='*70}\n")
