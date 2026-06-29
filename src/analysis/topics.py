import json
import logging
import sqlite3

from src.llm.client import LLMClient
from src.llm.prompts import TOPIC_EXTRACTION_PROMPT

logger = logging.getLogger("amis.analysis.topics")


def upsert_topic(conn: sqlite3.Connection, name: str, topic_type: str) -> int:
    name = name.strip().lower()
    existing = conn.execute(
        "SELECT id FROM topics WHERE name = ? AND topic_type = ?",
        (name, topic_type),
    ).fetchone()
    if existing:
        return existing["id"]

    cursor = conn.execute(
        "INSERT INTO topics (name, topic_type) VALUES (?, ?)",
        (name, topic_type),
    )
    return cursor.lastrowid


def store_article_topics(conn: sqlite3.Connection, article_id: int, extracted: dict):
    for category, items in extracted.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not item or not isinstance(item, str):
                continue
            topic_id = upsert_topic(conn, item, category)
            conn.execute("""
                INSERT OR IGNORE INTO article_topics
                (article_id, topic_id, relevance_score, is_primary)
                VALUES (?, ?, 1.0, 0)
            """, (article_id, topic_id))


def extract_topics(conn: sqlite3.Connection, llm: LLMClient, article_id: int):
    article = conn.execute(
        "SELECT id, title, content FROM articles WHERE id = ?",
        (article_id,),
    ).fetchone()
    if not article:
        return

    existing = conn.execute(
        "SELECT 1 FROM article_topics WHERE article_id = ? LIMIT 1",
        (article_id,),
    ).fetchone()
    if existing:
        logger.debug("Article %d already has topics, skipping", article_id)
        return

    prompt = TOPIC_EXTRACTION_PROMPT.format(
        title=article["title"],
        content=article["content"][:6000],
    )

    try:
        result = llm.complete_json(prompt)
        store_article_topics(conn, article_id, result)
        conn.commit()
        logger.info("Extracted topics for article %d: %s", article_id, article["title"])
    except Exception as e:
        logger.error("Failed to extract topics for article %d: %s", article_id, e)
