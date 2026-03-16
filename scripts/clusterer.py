"""
Story clusterer: groups articles about the same topic from different sources
using multilingual sentence embeddings and cosine similarity.
"""

import logging
from typing import List, Dict

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from config import CLUSTER_THRESHOLD

logger = logging.getLogger(__name__)

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def _load_model() -> SentenceTransformer:
    logger.info(f"Loading embedding model ({MODEL_NAME}) ...")
    return SentenceTransformer(MODEL_NAME)


def cluster_articles(articles: List[Dict]) -> List[List[Dict]]:
    """
    Group articles about the same topic, keeping only groups that have
    at least 2 articles from different sources.

    Returns clusters sorted by number of sources (descending).
    """
    if len(articles) < 2:
        logger.warning("Not enough articles to cluster.")
        return []

    model = _load_model()

    titles = [a["title"] for a in articles]
    logger.info(f"Generating embeddings for {len(titles)} articles ...")
    embeddings = model.encode(titles, show_progress_bar=False, batch_size=64)

    sim_matrix = cosine_similarity(embeddings)
    n = len(articles)
    assigned = [False] * n
    clusters: List[List[int]] = []

    for i in range(n):
        if assigned[i]:
            continue

        cluster_indices = [i]
        assigned[i] = True

        for j in range(i + 1, n):
            if assigned[j]:
                continue

            # Use max similarity to any article already in the cluster
            max_sim = max(sim_matrix[k][j] for k in cluster_indices)
            if max_sim < CLUSTER_THRESHOLD:
                continue

            # Only add if it comes from a different source
            cluster_sources = {articles[k]["source_id"] for k in cluster_indices}
            if articles[j]["source_id"] not in cluster_sources:
                cluster_indices.append(j)
                assigned[j] = True

        clusters.append(cluster_indices)

    # Convert index lists to article lists; keep multi-source clusters only
    valid: List[List[Dict]] = []
    for idx_list in clusters:
        group = [articles[i] for i in idx_list]
        sources = {a["source_id"] for a in group}
        if len(sources) >= 2:
            valid.append(group)

    # Sort: most sources first (most covered story = most interesting)
    valid.sort(key=lambda g: len(g), reverse=True)

    logger.info(f"Clusters found: {len(valid)} (threshold={CLUSTER_THRESHOLD})")
    return valid
