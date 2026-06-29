import json
import logging
import sqlite3

from src.llm.client import LLMClient
from src.llm.prompts import SEMANTIC_ANALYSIS_PROMPT

logger = logging.getLogger("amis.analysis.semantic")


def already_scored(conn: sqlite3.Connection, article_id: int, score_type: str = "semantic") -> bool:
    row = conn.execute(
        "SELECT 1 FROM scores WHERE article_id = ? AND score_type = ? LIMIT 1",
        (article_id, score_type),
    ).fetchone()
    return row is not None


def store_scores(conn: sqlite3.Connection, article_id: int, result: dict, model_used: str):
    scores = result.get("scores", {})
    for metric_name, metric_data in scores.items():
        conn.execute("""
            INSERT OR REPLACE INTO scores
            (article_id, score_type, metric_name, score_value, confidence, reasoning, model_used)
            VALUES (?, 'semantic', ?, ?, ?, ?, ?)
        """, (
            article_id,
            metric_name,
            metric_data.get("score", 0),
            metric_data.get("confidence", 0.0),
            metric_data.get("reasoning", ""),
            model_used,
        ))
    conn.commit()


def analyze_article(conn: sqlite3.Connection, llm: LLMClient, article_id: int):
    article = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    if not article:
        logger.warning("Article %d not found, skipping", article_id)
        return

    if already_scored(conn, article_id):
        logger.debug("Article %d already scored, skipping", article_id)
        return

    tags = json.loads(article["tags_json"] or "[]")
    prompt = SEMANTIC_ANALYSIS_PROMPT.format(
        title=article["title"],
        author=article["author"] or "Unknown",
        publication_date=article["publication_date"] or "Unknown",
        tags=", ".join(tags),
        content=article["content"][:8000],
    )

    try:
        result = llm.complete_json(prompt)
        store_scores(conn, article_id, result, llm.model)
        logger.info("Scored article %d: %s", article_id, article["title"])
    except Exception as e:
        logger.error("Failed to score article %d: %s", article_id, e)


def analyze_all_articles(conn: sqlite3.Connection, llm: LLMClient):
    articles = conn.execute("""
        SELECT id, title FROM articles
        WHERE id NOT IN (
            SELECT DISTINCT article_id FROM scores WHERE score_type = 'semantic'
        )
    """).fetchall()

    logger.info("Analyzing %d articles", len(articles))
    for article in articles:
        analyze_article(conn, llm, article["id"])
