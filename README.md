# Contrapunto UY

> La misma noticia, distintas voces.

Agregador de noticias uruguayo que compara los titulares de los principales medios sobre la misma noticia y genera un análisis objetivo con IA.

## Cómo funciona

1. **Scraping**: Cada día a las 7am (Uruguay), GitHub Actions descarga los feeds RSS de 12 medios uruguayos.
2. **Clustering**: Las noticias similares se agrupan con embeddings multilingües (sentence-transformers).
3. **Análisis**: Claude genera un resumen objetivo y evalúa el nivel de tendenciosidad de cada titular.
4. **Publicación**: Se genera un sitio HTML estático y se publica en GitHub Pages.

## Medios incluidos

El País · El Observador · La Diaria · Montevideo Portal · La República · Subrayado · Caras y Caretas · 180.com.uy · Búsqueda · Teledoce · LR21 · El Pueblo

## Setup

### 1. Fork y clonar el repo

```bash
git clone https://github.com/TU_USUARIO/contrapunto-uy.git
cd contrapunto-uy
```

### 2. Agregar el secret de Anthropic

En GitHub → Settings → Secrets and variables → Actions → New repository secret:

- Name: `ANTHROPIC_API_KEY`
- Value: tu API key de Anthropic

### 3. Habilitar GitHub Pages

Settings → Pages → Source: `Deploy from a branch` → Branch: `main` → Folder: `/site`

### 4. Ejecutar manualmente (primer run)

Actions → `Daily Update` → `Run workflow`

## Desarrollo local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export ANTHROPIC_API_KEY=sk-ant-...
python scripts/main.py
```

El sitio generado queda en `site/`. Para verlo localmente:

```bash
cd site && python -m http.server 8000
```

## Estructura

```
scripts/       Código Python (scraper, clusterer, analyzer, builder)
templates/     Templates Jinja2
static/        Assets CSS/JS (copiados a site/ en cada build)
site/          Sitio HTML generado (trackeado en git → GitHub Pages)
prototype/     Prototipo visual estático
```

## Seguridad

- Sitio 100% estático: sin backend, sin DB, sin superficie de ataque.
- Secrets solo en GitHub Secrets, nunca en el código.
- DDoS protection por defecto vía GitHub Pages.
- Para producción: agregar Cloudflare como proxy para WAF y ocultar origen.
