import json
import logging
import sqlite3

logger = logging.getLogger("amis.memory.reasoning")


def store_reasoning(conn: sqlite3.Connection, reasoning_type: str, entity_type: str,
                    entity_id: int, prompt: str, response: str, model_used: str,
                    confidence: float = None, context: dict = None, outcome: str = "pending"):
    conn.execute("""
        INSERT INTO reasoning_history
        (reasoning_type, entity_type, entity_id, prompt, response,
         model_used, confidence, context_json, outcome)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        reasoning_type, entity_type, entity_id, prompt, response,
        model_used, confidence, json.dumps(context or {}), outcome,
    ))
    conn.commit()


def get_prior_reasoning(conn: sqlite3.Connection, entity_type: str, entity_id: int,
                        reasoning_type: str = None) -> list[dict]:
    query = "SELECT * FROM reasoning_history WHERE entity_type = ? AND entity_id = ?"
    params = [entity_type, entity_id]
    if reasoning_type:
        query += " AND reasoning_type = ?"
        params.append(reasoning_type)
    query += " ORDER BY timestamp DESC"
    rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def needs_llm_call(conn: sqlite3.Connection, entity_type: str, entity_id: int,
                   reasoning_type: str) -> bool:
    existing = conn.execute("""
        SELECT id FROM reasoning_history
        WHERE entity_type = ? AND entity_id = ? AND reasoning_type = ?
        AND (outcome IS NULL OR outcome != 'rejected')
        ORDER BY timestamp DESC LIMIT 1
    """, (entity_type, entity_id, reasoning_type)).fetchone()
    return existing is None


def update_reasoning_outcome(conn: sqlite3.Connection, reasoning_id: int, outcome: str):
    conn.execute(
        "UPDATE reasoning_history SET outcome = ? WHERE id = ?",
        (outcome, reasoning_id),
    )
    conn.commit()
