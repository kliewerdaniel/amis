import logging
import sqlite3

from src.llm.client import LLMClient
from src.llm.prompts import REPURPOSING_PROMPT

logger = logging.getLogger("amis.marketing.repurposing")


TARGET_FORMATS = [
    "linkedin_article", "technical_thread", "newsletter", "conference_talk",
    "workshop", "podcast_pitch", "video_script", "github_readme",
    "whitepaper", "book_chapter",
]


def store_repurposing(conn: sqlite3.Connection, article_id: int, recommendations: list):
    for rec in recommendations:
        conn.execute("""
            INSERT INTO content_repurposing
            (article_id, target_format, suitability_score, transformation_notes, estimated_effort)
            VALUES (?, ?, ?, ?, ?)
        """, (
            article_id,
            rec.get("format", ""),
            rec.get("suitability_score", 0),
            rec.get("transformation_notes", ""),
            rec.get("estimated_effort", "medium"),
        ))


def generate_repurposing(conn: sqlite3.Connection, llm: LLMClient, article_id: int):
    article = conn.execute(
        "SELECT id, title, content FROM articles WHERE id = ?",
        (article_id,),
    ).fetchone()
    if not article:
        return

    existing = conn.execute(
        "SELECT 1 FROM content_repurposing WHERE article_id = ? LIMIT 1",
        (article_id,),
    ).fetchone()
    if existing:
        logger.debug("Article %d already has repurposing, skipping", article_id)
        return

    prompt = REPURPOSING_PROMPT.format(
        title=article["title"],
        summary=article["content"][:3000],
    )

    try:
        result = llm.complete_json(prompt)
        repurposing = result.get("repurposing", [])
        if repurposing:
            store_repurposing(conn, article_id, repurposing)
            conn.commit()
            logger.info("Repurposing generated for article %d: %s", article_id, article["title"])
    except Exception as e:
        logger.error("Failed to generate repurposing for article %d: %s", article_id, e)


def generate_all_repurposing(conn: sqlite3.Connection, llm: LLMClient):
    articles = conn.execute("""
        SELECT id FROM articles
        WHERE id NOT IN (SELECT DISTINCT article_id FROM content_repurposing)
    """).fetchall()
    logger.info("Generating repurposing for %d articles", len(articles))
    for art in articles:
        generate_repurposing(conn, llm, art["id"])


def get_repurposing_options(conn: sqlite3.Connection, article_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM content_repurposing WHERE article_id = ? ORDER BY suitability_score DESC",
        (article_id,),
    ).fetchall()
    return [dict(r) for r in rows]
