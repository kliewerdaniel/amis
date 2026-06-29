import json
import logging
import sqlite3

from src.llm.client import LLMClient
from src.llm.prompts import ENTITY_RECOGNITION_PROMPT

logger = logging.getLogger("amis.analysis.entities")


def upsert_entity(conn: sqlite3.Connection, name: str, entity_type: str, description: str = None) -> int:
    existing = conn.execute(
        "SELECT id FROM entities WHERE name = ? AND entity_type = ?",
        (name.strip(), entity_type),
    ).fetchone()
    if existing:
        if description:
            conn.execute(
                "UPDATE entities SET description = COALESCE(NULLIF(?, ''), description) WHERE id = ?",
                (description, existing["id"]),
            )
        return existing["id"]

    cursor = conn.execute(
        "INSERT INTO entities (name, entity_type, description) VALUES (?, ?, ?)",
        (name.strip(), entity_type, description or ""),
    )
    return cursor.lastrowid


def store_article_entities(conn: sqlite3.Connection, article_id: int, entities: list):
    for entity in entities:
        entity_id = upsert_entity(
            conn, entity["name"], entity["type"], entity.get("description")
        )
        conn.execute("""
            INSERT OR IGNORE INTO article_entities
            (article_id, entity_id, context, mention_count)
            VALUES (?, ?, ?, 1)
        """, (article_id, entity_id, entity.get("description", "")))


def extract_entities(conn: sqlite3.Connection, llm: LLMClient, article_id: int):
    article = conn.execute(
        "SELECT id, title, content FROM articles WHERE id = ?",
        (article_id,),
    ).fetchone()
    if not article:
        return

    existing = conn.execute(
        "SELECT 1 FROM article_entities WHERE article_id = ? LIMIT 1",
        (article_id,),
    ).fetchone()
    if existing:
        logger.debug("Article %d already has entities, skipping", article_id)
        return

    prompt = ENTITY_RECOGNITION_PROMPT.format(
        title=article["title"],
        content=article["content"][:6000],
    )

    try:
        result = llm.complete_json(prompt)
        entities = result.get("entities", [])
        if entities:
            store_article_entities(conn, article_id, entities)
            conn.commit()
            logger.info("Extracted %d entities for article %d: %s", len(entities), article_id, article["title"])
    except Exception as e:
        logger.error("Failed to extract entities for article %d: %s", article_id, e)
