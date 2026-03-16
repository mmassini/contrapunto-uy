"""
Diagnóstico rápido: verifica qué feeds RSS responden y cuántos artículos tienen.
Correr con: python scripts/diagnose.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import feedparser
import datetime
from config import SOURCES, LOOKBACK_HOURS

cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=LOOKBACK_HOURS)

print(f"\n{'='*60}")
print(f"Diagnóstico de feeds RSS — últimas {LOOKBACK_HOURS}h")
print(f"{'='*60}\n")

total_articles = 0
working_feeds = 0

for source_id, source in SOURCES.items():
    try:
        feed = feedparser.parse(source["rss"], request_headers={"User-Agent": "ContrapuntoUY/1.0"})
        entries = feed.entries
        total = len(entries)

        # Count recent ones
        recent = 0
        for e in entries:
            for attr in ("published_parsed", "updated_parsed"):
                val = getattr(e, attr, None)
                if val:
                    dt = datetime.datetime(*val[:6], tzinfo=datetime.timezone.utc)
                    if dt >= cutoff:
                        recent += 1
                    break

        status = "✓" if total > 0 else "✗"
        if total > 0:
            working_feeds += 1
            total_articles += recent
        print(f"  {status} {source['name']:<22} {total:>3} entradas total  {recent:>3} recientes")

        if feed.bozo and total == 0:
            print(f"    ⚠ Feed error: {feed.get('bozo_exception', 'unknown')}")

    except Exception as e:
        print(f"  ✗ {source['name']:<22} ERROR: {e}")

print(f"\n{'='*60}")
print(f"  Feeds activos: {working_feeds}/{len(SOURCES)}")
print(f"  Artículos recientes total: {total_articles}")
print(f"{'='*60}\n")
