"""
Feed discovery: visita la homepage de cada medio y busca
el link RSS/Atom en el HTML (tag <link rel="alternate">).
Correr con: python scripts/discover_feeds.py
"""
import sys
import warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import requests
from bs4 import BeautifulSoup

warnings.filterwarnings("ignore")

from config import SOURCES

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-UY,es;q=0.9",
}

print(f"\n{'='*70}")
print("Descubrimiento de feeds RSS via homepage")
print(f"{'='*70}\n")

for source_id, source in SOURCES.items():
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=12, verify=False, allow_redirects=True)
        soup = BeautifulSoup(resp.text, "html.parser")

        feeds = []
        for tag in soup.find_all("link", rel=lambda r: r and any(
            v in (r if isinstance(r, list) else [r]) for v in ["alternate"]
        )):
            t = tag.get("type", "")
            href = tag.get("href", "")
            if any(x in t for x in ["rss", "atom", "xml"]) and href:
                feeds.append((t, href))

        if feeds:
            print(f"✓ {source['name']}:")
            for t, href in feeds:
                # Make absolute if relative
                if href.startswith("/"):
                    href = source["url"].rstrip("/") + href
                print(f"    [{t}] {href}")
        else:
            print(f"✗ {source['name']}: no RSS links found in homepage")

    except Exception as e:
        print(f"✗ {source['name']}: ERROR {str(e)[:60]}")

print()
