"""
Site builder: renders Jinja2 templates into static HTML files.
"""

import json
import shutil
import logging
import datetime
from pathlib import Path
from typing import List

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

BASE_URL = "https://contrapunto.uy"


def _setup_jinja(templates_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=True,
    )
    # Custom filter: truncate text
    env.filters["truncate_chars"] = lambda s, n: (s[:n] + "…") if len(s) > n else s
    return env


def _generate_sitemap(stories: List[dict], site_dir: Path) -> None:
    urls = [f"{BASE_URL}/", f"{BASE_URL}/index.html"]
    for story in stories:
        urls.append(f"{BASE_URL}/story/{story['id']}.html")

    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        lines.append(f"  <url><loc>{url}</loc></url>")
    lines.append("</urlset>")

    (site_dir / "sitemap.xml").write_text("\n".join(lines), encoding="utf-8")
    logger.info("sitemap.xml generated")


def build_site(stories: List[dict], base_dir: Path) -> None:
    """Generate the full static site from story data."""
    templates_dir = base_dir / "templates"
    static_dir = base_dir / "static"
    site_dir = base_dir / "docs"

    # Ensure output dirs exist
    for d in [site_dir / "story", site_dir / "data", site_dir / "assets" / "css", site_dir / "assets" / "js"]:
        d.mkdir(parents=True, exist_ok=True)

    # Copy static assets to docs/
    if static_dir.exists():
        for src in static_dir.rglob("*"):
            if src.is_file():
                dest = site_dir / src.relative_to(static_dir)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dest)
        logger.info("Static assets copied")

    env = _setup_jinja(templates_dir)

    now = datetime.datetime.now()
    months_es = [
        "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
        "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
    ]
    date_str = f"{now.day} de {months_es[now.month]} de {now.year}"
    time_str = now.strftime("%H:%M")

    base_ctx = {
        "stories": stories,
        "last_update_date": date_str,
        "last_update_time": time_str,
        "total_stories": len(stories),
        "total_sources": len({h["source_id"] for s in stories for h in s["headlines"]}),
        "base_url": BASE_URL,
        "year": now.year,
    }

    # Render index.html
    index_tpl = env.get_template("index.html.j2")
    index_html = index_tpl.render(**base_ctx)
    (site_dir / "index.html").write_text(index_html, encoding="utf-8")
    logger.info("index.html generated")

    # Render individual story pages
    story_tpl = env.get_template("story.html.j2")
    for story in stories:
        story_ctx = {**base_ctx, "story": story, "stories": None}
        story_html = story_tpl.render(**story_ctx)
        (site_dir / "story" / f"{story['id']}.html").write_text(story_html, encoding="utf-8")
    logger.info(f"{len(stories)} story pages generated")

    # Save raw data
    data = {"generated_at": now.isoformat(), "stories": stories}
    (site_dir / "data" / "stories.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Sitemap
    _generate_sitemap(stories, site_dir)

    logger.info(f"Site build complete → {site_dir}")
