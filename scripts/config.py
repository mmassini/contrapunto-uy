"""
Configuration: Uruguayan news sources with RSS feeds and metadata.

Strategy:
- Use native RSS when available and reliable.
- For sources without a working native feed, use Google News RSS
  (format: https://news.google.com/rss/search?q=site:DOMAIN&hl=es-419&gl=UY&ceid=UY:es-419).
  Google News reliably indexes all major Uruguayan media and returns the
  original article URLs and headlines.
"""

_GN = "https://news.google.com/rss/search?q=site:{domain}&hl=es-419&gl=UY&ceid=UY:es-419"

SOURCES = {
    "elpais": {
        "name": "El País",
        "short": "EP",
        "url": "https://www.elpais.com.uy",
        # Native RSS works (1–20 entries)
        "rss": "https://www.elpais.com.uy/rss/portada.xml",
        "rss_fallbacks": [
            _GN.format(domain="elpais.com.uy"),
        ],
        "color": "#003F7F",
        "text_color": "#FFFFFF",
    },
    "observador": {
        "name": "El Observador",
        "short": "EO",
        "url": "https://www.elobservador.com.uy",
        # Native RSS returns HTML; use Google News
        "rss": _GN.format(domain="elobservador.com.uy"),
        "rss_fallbacks": [],
        "color": "#D32F2F",
        "text_color": "#FFFFFF",
    },
    "ladiaria": {
        "name": "La Diaria",
        "short": "LD",
        "url": "https://ladiaria.com.uy",
        # Native RSS blocked (paywall); use Google News
        "rss": _GN.format(domain="ladiaria.com.uy"),
        "rss_fallbacks": [],
        "color": "#1B5E20",
        "text_color": "#FFFFFF",
    },
    "montevideoportal": {
        "name": "Montevideo Portal",
        "short": "MP",
        "url": "https://www.montevideo.com.uy",
        # Native RSS returns malformed HTML; use Google News
        "rss": _GN.format(domain="montevideo.com.uy"),
        "rss_fallbacks": [],
        "color": "#0D47A1",
        "text_color": "#FFFFFF",
    },
    "larepublica": {
        "name": "La República",
        "short": "LR",
        "url": "https://www.larepublica.com.uy",
        # Native RSS 404 + SSL errors; use Google News
        "rss": _GN.format(domain="larepublica.com.uy"),
        "rss_fallbacks": [],
        "color": "#B71C1C",
        "text_color": "#FFFFFF",
    },
    "subrayado": {
        "name": "Subrayado",
        "short": "SB",
        "url": "https://www.subrayado.com.uy",
        "rss": _GN.format(domain="subrayado.com.uy"),
        "rss_fallbacks": [],
        "color": "#E65100",
        "text_color": "#FFFFFF",
    },
    "carasycaretas": {
        "name": "Caras y Caretas",
        "short": "CC",
        "url": "https://www.carasycaretas.com.uy",
        "rss": _GN.format(domain="carasycaretas.com.uy"),
        "rss_fallbacks": [],
        "color": "#4A148C",
        "text_color": "#FFFFFF",
    },
    "180": {
        "name": "180.com.uy",
        "short": "180",
        "url": "https://www.180.com.uy",
        "rss": _GN.format(domain="180.com.uy"),
        "rss_fallbacks": [],
        "color": "#F57F17",
        "text_color": "#000000",
    },
    "teledoce": {
        "name": "Teledoce",
        "short": "T12",
        "url": "https://www.teledoce.com",
        # Native RSS works perfectly
        "rss": "https://www.teledoce.com/rss",
        "rss_fallbacks": [
            _GN.format(domain="teledoce.com"),
        ],
        "color": "#006064",
        "text_color": "#FFFFFF",
    },
    "lr21": {
        "name": "LR21",
        "short": "LR21",
        "url": "https://www.lr21.com.uy",
        # Native RSS returns 403; use Google News
        "rss": _GN.format(domain="lr21.com.uy"),
        "rss_fallbacks": [
            "https://www.lr21.com.uy/rss",
        ],
        "color": "#827717",
        "text_color": "#FFFFFF",
    },
    "busqueda": {
        "name": "Búsqueda",
        "short": "BQ",
        "url": "https://www.busqueda.com.uy",
        "rss": _GN.format(domain="busqueda.com.uy"),
        "rss_fallbacks": [],
        "color": "#37474F",
        "text_color": "#FFFFFF",
    },
    "elpueblo": {
        "name": "El Pueblo",
        "short": "EP2",
        "url": "https://www.elpueblo.com.uy",
        "rss": _GN.format(domain="elpueblo.com.uy"),
        "rss_fallbacks": [],
        "color": "#4E342E",
        "text_color": "#FFFFFF",
    },
}

# How many hours back to look for articles
LOOKBACK_HOURS = 48

# Max story groups to analyze with Claude (controls API cost)
MAX_STORIES_PER_RUN = 20

# Clustering similarity threshold (0-1). Higher = stricter grouping.
CLUSTER_THRESHOLD = 0.63
