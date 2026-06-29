import logging
import sqlite3
from src.llm.client import LLMClient

logger = logging.getLogger("amis.graph.duplicates")


def find_exact_duplicates(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("""
        SELECT a.id as aid, b.id as bid, a.title as atitle, b.title as btitle
        FROM articles a
        JOIN articles b ON a.ingestion_hash = b.ingestion_hash AND a.id < b.id
    """).fetchall()
    results = [dict(r) for r in rows]
    if results:
        logger.info("Found %d exact duplicates", len(results))
    return results


def find_near_duplicates_by_title(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("""
        SELECT a.id as aid, b.id as bid, a.title as atitle, b.title as btitle
        FROM articles a
        JOIN articles b ON a.id < b.id
        WHERE a.title = b.title
    """).fetchall()
    return [dict(r) for r in rows]


def find_outdated(conn: sqlite3.Connection, llm: LLMClient) -> list[dict]:
    articles = conn.execute("""
        SELECT id, title, publication_date, content
        FROM articles ORDER BY publication_date ASC LIMIT 20
    """).fetchall()

    outdated = []
    for article in articles:
        if not article["publication_date"]:
            continue
        prompt = f"""Analyze if this article is potentially outdated:

Article: {article['title']}
Published: {article['publication_date']}
Content start: {article['content'][:2000]}...

Return JSON: {{"is_outdated": true/false, "confidence": 0.0, "reasoning": "..."}}"""
        try:
            result = llm.complete_json(prompt)
            if result.get("is_outdated") and result.get("confidence", 0) > 0.7:
                outdated.append({
                    "id": article["id"],
                    "title": article["title"],
                    "reasoning": result.get("reasoning", ""),
                })
        except Exception as e:
            logger.debug("Failed to check outdated for %s: %s", article["title"], e)

    logger.info("Found %d potentially outdated articles", len(outdated))
    return outdated


def find_missing_followups(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("""
        SELECT title FROM articles
        WHERE title LIKE '%Part %'
        ORDER BY publication_date
    """).fetchall()
    return [dict(r) for r in rows]
