import json
import sqlite3


def get_article(conn: sqlite3.Connection, article_id: int) -> dict | None:
    row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    return dict(row) if row else None


def get_article_by_slug(conn: sqlite3.Connection, slug: str) -> dict | None:
    row = conn.execute("SELECT * FROM articles WHERE slug = ?", (slug,)).fetchone()
    return dict(row) if row else None


def get_article_by_filename(conn: sqlite3.Connection, filename: str) -> dict | None:
    row = conn.execute("SELECT * FROM articles WHERE filename = ?", (filename,)).fetchone()
    return dict(row) if row else None


def get_all_articles(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT * FROM articles ORDER BY publication_date DESC").fetchall()
    return [dict(r) for r in rows]


def get_scores_for_article(conn: sqlite3.Connection, article_id: int, score_type: str = None) -> list[dict]:
    query = "SELECT * FROM scores WHERE article_id = ?"
    params = [article_id]
    if score_type:
        query += " AND score_type = ?"
        params.append(score_type)
    return [dict(r) for r in conn.execute(query, params).fetchall()]


def get_relationships_for_article(conn: sqlite3.Connection, article_id: int) -> list[dict]:
    rows = conn.execute("""
        SELECT * FROM relationships
        WHERE (source_id = ? AND source_type = 'article')
           OR (target_id = ? AND target_type = 'article')
    """, (article_id, article_id)).fetchall()
    return [dict(r) for r in rows]


def get_topics_for_article(conn: sqlite3.Connection, article_id: int) -> list[dict]:
    rows = conn.execute("""
        SELECT t.*, at.relevance_score, at.is_primary
        FROM topics t
        JOIN article_topics at ON t.id = at.topic_id
        WHERE at.article_id = ?
    """, (article_id,)).fetchall()
    return [dict(r) for r in rows]


def get_entities_for_article(conn: sqlite3.Connection, article_id: int) -> list[dict]:
    rows = conn.execute("""
        SELECT e.*, ae.context, ae.mention_count
        FROM entities e
        JOIN article_entities ae ON e.id = ae.entity_id
        WHERE ae.article_id = ?
    """, (article_id,)).fetchall()
    return [dict(r) for r in rows]


def article_exists(conn: sqlite3.Connection, filename: str) -> bool:
    return conn.execute(
        "SELECT 1 FROM articles WHERE filename = ?", (filename,)
    ).fetchone() is not None
