"""
Contrapunto UY — Main entry point.
Orchestrates: fetch → cluster → analyze → build.
"""

import os
import sys
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Ensure scripts/ is on the import path
sys.path.insert(0, str(Path(__file__).parent))

from scraper import fetch_all
from clusterer import cluster_articles
from analyzer import analyze_all_clusters
from builder import build_site


def main() -> None:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable is not set.")
        sys.exit(1)

    logger.info("═══ Contrapunto UY — Daily Update ═══")

    # 1. Fetch RSS feeds
    logger.info("▶ Step 1/4: Fetching RSS feeds ...")
    articles = fetch_all()
    if not articles:
        logger.error("No articles fetched. Check RSS feed URLs in config.py.")
        sys.exit(1)

    # 2. Cluster similar stories
    logger.info("▶ Step 2/4: Clustering similar stories ...")
    clusters = cluster_articles(articles)
    if not clusters:
        logger.warning("No multi-source clusters found. Lowering threshold or checking feeds may help.")
        # Build site with empty stories to at least update the timestamp
        stories = []
    else:
        # 3. Analyze with Claude
        logger.info("▶ Step 3/4: Analyzing with Claude ...")
        stories = analyze_all_clusters(clusters, api_key)

    # 4. Build HTML site
    logger.info("▶ Step 4/4: Building site ...")
    base_dir = Path(__file__).parent.parent
    build_site(stories, base_dir=base_dir)

    logger.info(f"═══ Done. {len(stories)} stories published. ═══")


if __name__ == "__main__":
    main()
