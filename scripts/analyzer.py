"""
Claude analyzer: generates objective analysis for each story cluster.
"""

import json
import logging
from typing import List, Dict, Optional

import anthropic

from config import MAX_STORIES_PER_RUN

logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """\
Sos un periodista uruguayo experimentado e imparcial. Te muestro titulares de distintos medios uruguayos sobre la misma noticia.

MEDIOS Y TITULARES:
{headlines}

Tu tarea:
1. Escribí un RESUMEN OBJETIVO de lo que pasó (máximo 150 palabras, en español rioplatense, sin tomar partido).
2. Para cada titular, asigná un SCORE DE TENDENCIOSIDAD del 0 al 10:
   - 0–2: Neutral, informativo, sin carga emocional
   - 3–4: Leve encuadre o énfasis particular
   - 5–6: Moderadamente tendencioso o alarmista
   - 7–8: Lenguaje cargado, bastante parcial
   - 9–10: Muy sensacionalista o claramente sesgado
3. Una frase breve (máx. 12 palabras) justificando cada score.
4. 2 o 3 puntos donde TODOS los medios coinciden.
5. 2 o 3 diferencias de ENFOQUE principales entre los medios.
6. El TEMA PRINCIPAL en máximo 8 palabras (para usar como título).
7. La CATEGORÍA: Política, Economía, Sociedad, Deportes, Internacional, Cultura, Seguridad, Salud, Educación, u Otro.

Respondé ÚNICAMENTE con JSON válido, sin texto adicional ni markdown:
{{
  "tema": "...",
  "categoria": "...",
  "resumen": "...",
  "titulares": [
    {{"fuente": "Nombre del medio", "score": 0, "razon": "..."}}
  ],
  "coincidencias": ["...", "...", "..."],
  "diferencias": ["...", "...", "..."]
}}
"""


def _build_prompt(cluster: List[Dict]) -> str:
    lines = []
    for a in cluster:
        lines.append(f'- {a["source_name"]}: "{a["title"]}"')
        if a.get("description"):
            lines.append(f'  Descripción: {a["description"][:200]}')
    return ANALYSIS_PROMPT.format(headlines="\n".join(lines))


def _parse_response(text: str) -> Optional[Dict]:
    """Parse Claude's JSON response, stripping markdown fences if present."""
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 3:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw: {text[:300]}")
        return None


def _fallback_analysis(cluster: List[Dict]) -> Dict:
    return {
        "tema": cluster[0]["title"][:70],
        "categoria": "General",
        "resumen": (
            "El análisis automático no está disponible para esta noticia. "
            "Hacé click en cada titular para leer la nota original en el medio correspondiente."
        ),
        "titulares": [
            {"fuente": a["source_name"], "score": 5, "razon": "Análisis no disponible"}
            for a in cluster
        ],
        "coincidencias": ["Todos los medios cubren este tema"],
        "diferencias": ["Los enfoques varían entre los distintos medios"],
    }


def analyze_cluster(cluster: List[Dict], client: anthropic.Anthropic) -> Optional[Dict]:
    """Send a cluster to Claude and return structured analysis."""
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1200,
            messages=[{"role": "user", "content": _build_prompt(cluster)}],
        )
        raw = response.content[0].text
        result = _parse_response(raw)
        if result is None:
            return _fallback_analysis(cluster)
        return result
    except anthropic.RateLimitError:
        logger.warning("Rate limit hit; using fallback analysis.")
        return _fallback_analysis(cluster)
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return None


def analyze_all_clusters(clusters: List[List[Dict]], api_key: str) -> List[Dict]:
    """
    Analyze the top N clusters and return enriched story objects ready for rendering.
    """
    client = anthropic.Anthropic(api_key=api_key)
    stories: List[Dict] = []

    to_analyze = clusters[:MAX_STORIES_PER_RUN]
    logger.info(f"Analyzing {len(to_analyze)} clusters with Claude ...")

    for i, cluster in enumerate(to_analyze):
        preview = cluster[0]["title"][:60]
        logger.info(f"  [{i+1}/{len(to_analyze)}] {preview} ...")

        analysis = analyze_cluster(cluster, client)
        if not analysis:
            continue

        # Build score lookup by source name
        score_map: Dict[str, Dict] = {
            t["fuente"]: {"score": t["score"], "razon": t.get("razon", "")}
            for t in analysis.get("titulares", [])
        }

        headlines = []
        for article in cluster:
            sa = score_map.get(article["source_name"], {"score": 5, "razon": ""})
            score = max(0, min(10, sa["score"]))
            headlines.append({
                **article,
                "score": score,
                "score_reason": sa["razon"],
                "score_pct": score * 10,  # 0-100 for CSS positioning
            })

        # Sort: neutral first (ascending score)
        headlines.sort(key=lambda h: h["score"])

        stories.append({
            "id": f"story_{i+1:03d}",
            "topic": analysis.get("tema", cluster[0]["title"][:70]),
            "category": analysis.get("categoria", "General"),
            "sources_count": len(cluster),
            "headlines": headlines,
            "analysis": {
                "resumen": analysis.get("resumen", ""),
                "coincidencias": analysis.get("coincidencias", []),
                "diferencias": analysis.get("diferencias", []),
            },
        })

    logger.info(f"Stories ready: {len(stories)}")
    return stories
