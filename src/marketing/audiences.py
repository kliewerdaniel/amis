import logging
import sqlite3

from src.llm.client import LLMClient
from src.llm.prompts import AUDIENCE_MAPPING_PROMPT

logger = logging.getLogger("amis.marketing.audiences")


def store_audience_profiles(conn: sqlite3.Connection, article_id: int, audiences: dict):
    for audience_type, data in audiences.items():
        conn.execute("""
            INSERT OR REPLACE INTO audience_profiles
            (article_id, audience_type, relevance_score, reasoning)
            VALUES (?, ?, ?, ?)
        """, (article_id, audience_type, data.get("score", 0), data.get("reasoning", "")))


def map_audiences(conn: sqlite3.Connection, llm: LLMClient, article_id: int):
    article = conn.execute(
        "SELECT id, title, content FROM articles WHERE id = ?",
        (article_id,),
    ).fetchone()
    if not article:
        return

    existing = conn.execute(
        "SELECT 1 FROM audience_profiles WHERE article_id = ? LIMIT 1",
        (article_id,),
    ).fetchone()
    if existing:
        logger.debug("Article %d already has audiences, skipping", article_id)
        return

    prompt = AUDIENCE_MAPPING_PROMPT.format(
        title=article["title"],
        summary=article["content"][:3000],
    )

    try:
        result = llm.complete_json(prompt)
        audiences = result.get("audiences", {})
        if audiences:
            store_audience_profiles(conn, article_id, audiences)
            conn.commit()
            logger.info("Mapped audiences for article %d: %s", article_id, article["title"])
    except Exception as e:
        logger.error("Failed to map audiences for article %d: %s", article_id, e)


def get_audience_articles(conn: sqlite3.Connection, audience_type: str) -> list[dict]:
    rows = conn.execute("""
        SELECT a.id, a.title, a.slug, ap.relevance_score
        FROM articles a
        JOIN audience_profiles ap ON a.id = ap.article_id
        WHERE ap.audience_type = ?
        ORDER BY ap.relevance_score DESC
        LIMIT 20
    """, (audience_type,)).fetchall()
    return [dict(r) for r in rows]
