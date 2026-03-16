"""
Configuration: Uruguayan news sources with RSS feeds and metadata.
"""

SOURCES = {
    "elpais": {
        "name": "El País",
        "short": "EP",
        "url": "https://www.elpais.com.uy",
        "rss": "https://www.elpais.com.uy/rss",
        "color": "#003F7F",
        "text_color": "#FFFFFF",
    },
    "observador": {
        "name": "El Observador",
        "short": "EO",
        "url": "https://www.elobservador.com.uy",
        "rss": "https://www.elobservador.com.uy/rss",
        "color": "#D32F2F",
        "text_color": "#FFFFFF",
    },
    "ladiaria": {
        "name": "La Diaria",
        "short": "LD",
        "url": "https://ladiaria.com.uy",
        "rss": "https://ladiaria.com.uy/atom/",
        "color": "#1B5E20",
        "text_color": "#FFFFFF",
    },
    "montevideoportal": {
        "name": "Montevideo Portal",
        "short": "MP",
        "url": "https://www.montevideo.com.uy",
        "rss": "https://www.montevideo.com.uy/rss.xml",
        "color": "#0D47A1",
        "text_color": "#FFFFFF",
    },
    "larepublica": {
        "name": "La República",
        "short": "LR",
        "url": "https://larepublica.com.uy",
        "rss": "https://larepublica.com.uy/rss.xml",
        "color": "#B71C1C",
        "text_color": "#FFFFFF",
    },
    "subrayado": {
        "name": "Subrayado",
        "short": "SB",
        "url": "https://www.subrayado.com.uy",
        "rss": "https://www.subrayado.com.uy/rss",
        "color": "#E65100",
        "text_color": "#FFFFFF",
    },
    "carasycaretas": {
        "name": "Caras y Caretas",
        "short": "CC",
        "url": "https://www.carasycaretas.com.uy",
        "rss": "https://www.carasycaretas.com.uy/feed",
        "color": "#4A148C",
        "text_color": "#FFFFFF",
    },
    "180": {
        "name": "180.com.uy",
        "short": "180",
        "url": "https://www.180.com.uy",
        "rss": "https://www.180.com.uy/rss",
        "color": "#F57F17",
        "text_color": "#000000",
    },
    "busqueda": {
        "name": "Búsqueda",
        "short": "BQ",
        "url": "https://www.busqueda.com.uy",
        "rss": "https://www.busqueda.com.uy/rss",
        "color": "#37474F",
        "text_color": "#FFFFFF",
    },
    "teledoce": {
        "name": "Teledoce",
        "short": "T12",
        "url": "https://www.teledoce.com",
        "rss": "https://www.teledoce.com/rss",
        "color": "#006064",
        "text_color": "#FFFFFF",
    },
    "lr21": {
        "name": "LR21",
        "short": "LR21",
        "url": "https://www.lr21.com.uy",
        "rss": "https://www.lr21.com.uy/rss",
        "color": "#827717",
        "text_color": "#FFFFFF",
    },
    "elpueblo": {
        "name": "El Pueblo",
        "short": "EP2",
        "url": "https://www.elpueblo.com.uy",
        "rss": "https://www.elpueblo.com.uy/feed",
        "color": "#4E342E",
        "text_color": "#FFFFFF",
    },
}

# How many hours back to look for articles
LOOKBACK_HOURS = 24

# Max story groups to analyze with Claude (controls API cost)
MAX_STORIES_PER_RUN = 20

# Clustering similarity threshold (0-1). Higher = stricter grouping.
CLUSTER_THRESHOLD = 0.72
