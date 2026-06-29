# Phase 16: Autonomous Loop

## Objective

Nightly pipeline that ingests new content, recomputes the graph, detects changes, updates scores, and suggests campaigns — never overwriting historical reasoning.

## Pipeline Steps

### 1. Ingest New Markdown

```python
def ingest_new_content(conn, content_dir: str):
    """Ingest only new or changed files."""
    files = discover_files(content_dir)
    for f in files:
        current_hash = sha256(f.read_text())
        existing = conn.execute(
            "SELECT ingestion_hash FROM articles WHERE filename = ?",
            (f.name,)
        ).fetchone()
        if existing and existing[0] == current_hash:
            continue  # Skip unchanged
        # Ingest the file
        ingest_file(conn, f)
```

### 2. Recompute Graph

```python
def recompute_graph(conn, chroma_client):
    """Rebuild relationships for new/changed articles."""
    new_articles = conn.execute("""
        SELECT id FROM articles
        WHERE updated_at > datetime('now', '-1 day')
    """).fetchall()
    for article in new_articles:
        detect_relationships(conn, article.id)
        update_embeddings(chroma_client, article.id)
```

### 3. Detect Changes

```python
def detect_changes(conn):
    """Identify content changes requiring re-analysis."""
    changed = conn.execute("""
        SELECT id, title FROM articles
        WHERE updated_at > datetime('now', '-1 day')
    """).fetchall()
    return changed
```

### 4. Update Scores

```python
def update_scores(conn, llm_client, changed_articles):
    """Re-score changed articles."""
    for article in changed_articles:
        # Clear old scores
        conn.execute("DELETE FROM scores WHERE article_id = ?", (article.id,))
        # Re-run semantic analysis
        analyze_article(conn, llm_client, article.id)
```

### 5. Suggest Campaigns

```python
def suggest_campaigns(conn, llm_client):
    """Generate new campaign suggestions based on current state."""
    # Check if any high-scoring articles lack campaigns
    unassigned = conn.execute("""
        SELECT a.id, a.title FROM articles a
        JOIN scores s ON a.id = s.article_id
        WHERE s.metric_name = 'marketing_value' AND s.score_value > 80
        AND a.id NOT IN (
            SELECT DISTINCT json_each.value::integer
            FROM campaigns, json_each(supporting_articles_json)
        )
    """).fetchall()
    if unassigned:
        generate_campaign_for_articles(conn, llm_client, unassigned)
```

### 6. Generate Weekly Report

```python
def generate_weekly_report(conn, llm_client) -> str:
    """Generate a markdown summary of the week's activity."""
    stats = {
        "new_articles": count_new_articles(conn, days=7),
        "top_performers": get_top_performers(conn, days=7),
        "campaigns_active": count_active_campaigns(conn),
        "recommendations_pending": count_pending_recommendations(conn),
    }
    report = llm_client.generate(PROMPTS['weekly_report'].format(**stats))
    # Save to generated/weekly_report_{date}.md
    return report
```

### 7. Recommend Highest ROI Actions

```python
def recommend_actions(conn, llm_client) -> list[dict]:
    """Prioritize actions by expected ROI."""
    return conn.execute("""
        SELECT r.id, r.recommendation_type, r.score, r.reasoning,
            a.title, a.slug
        FROM recommendations r
        JOIN articles a ON r.article_id = a.id
        WHERE r.outcome = 'pending'
        ORDER BY r.score DESC
        LIMIT 5
    """).fetchall()
```

## Cron Schedule

```bash
# Nightly at 2 AM
0 2 * * * cd /path/to/amis && python -m amis.loop.autonomous
```

## Logging

```python
import logging

logger = logging.getLogger('amis.autonomous')

def run_nightly_pipeline():
    logger.info("Starting nightly pipeline")
    try:
        new = ingest_new_content(conn, content_dir)
        logger.info(f"Ingested {new} new articles")
        changes = detect_changes(conn)
        logger.info(f"Detected {len(changes)} changes")
        # ... etc
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
```

## Idempotency Guarantees

- Ingestion skips unchanged files (hash comparison)
- Scores are deleted and re-computed for changed articles
- Graph edges are rebuilt for affected articles
- Campaigns are regenerated only when new high-scoring articles appear
- Historical reasoning is never overwritten (append-only)

## Output

- Updated database with new content and scores
- New campaigns in `campaigns/` directory
- Weekly report in `generated/` directory
- Log entries in `logs/` directory

## Validation

1. Pipeline runs without errors on clean database
2. Re-running pipeline produces identical results (deterministic)
3. Historical reasoning preserved across runs
4. New articles processed within 24 hours
5. Weekly report generated with all sections
