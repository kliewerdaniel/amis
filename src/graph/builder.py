import json
import logging
import sqlite3
from datetime import datetime

logger = logging.getLogger("amis.graph")

RELATIONSHIP_TYPES = [
    "references", "expands", "contradicts", "depends_on",
    "introduces", "explains", "updates", "duplicates",
    "supports", "markets", "implements", "mentions",
    "recommended_after", "recommended_before", "related_to",
    "derived_from", "visualizes",
]


def insert_relationship(
    conn: sqlite3.Connection,
    source_id: int, source_type: str,
    target_id: int, target_type: str,
    rel_type: str, weight: float = 0.5,
    confidence: float = None, reasoning: str = None,
):
    conn.execute("""
        INSERT OR IGNORE INTO relationships
        (source_id, source_type, target_id, target_type, relationship_type, weight, confidence, reasoning)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (source_id, source_type, target_id, target_type, rel_type, weight, confidence, reasoning))


def detect_reference_edges(conn: sqlite3.Connection):
    articles = conn.execute("SELECT id, links_json FROM articles").fetchall()
    count = 0
    for article in articles:
        links = json.loads(article["links_json"] or "[]")
        for link in links:
            href = link.get("href", "")
            target = conn.execute(
                "SELECT id FROM articles WHERE slug LIKE ? OR canonical_url = ?",
                (f"%{href}%", href),
            ).fetchone()
            if target:
                insert_relationship(
                    conn, article["id"], "article",
                    target["id"], "article",
                    "references", 0.8, 0.9,
                )
                count += 1
    conn.commit()
    logger.info("Created %d reference edges", count)
    return count


def detect_topic_edges(conn: sqlite3.Connection, min_shared: int = 3):
    shared = conn.execute("""
        SELECT a.article_id as a_id, b.article_id as b_id, COUNT(*) as shared_count
        FROM article_topics a
        JOIN article_topics b ON a.topic_id = b.topic_id AND a.article_id < b.article_id
        GROUP BY a.article_id, b.article_id
        HAVING shared_count >= ?
    """, (min_shared,)).fetchall()

    count = 0
    for row in shared:
        weight = min(1.0, row["shared_count"] / 10.0)
        insert_relationship(
            conn, row["a_id"], "article",
            row["b_id"], "article",
            "related_to", weight, 0.8,
        )
        count += 1
    conn.commit()
    logger.info("Created %d topic-based edges", count)
    return count


def detect_entity_edges(conn: sqlite3.Connection):
    shared = conn.execute("""
        SELECT a.article_id as a_id, b.article_id as b_id, COUNT(*) as shared_entities
        FROM article_entities a
        JOIN article_entities b ON a.entity_id = b.entity_id AND a.article_id < b.article_id
        GROUP BY a.article_id, b.article_id
    """).fetchall()

    count = 0
    for row in shared:
        insert_relationship(
            conn, row["a_id"], "article",
            row["b_id"], "article",
            "mentions", min(1.0, row["shared_entities"] / 5.0), 0.7,
        )
        count += 1
    conn.commit()
    logger.info("Created %d entity-based edges", count)
    return count


def build_graph(conn: sqlite3.Connection):
    logger.info("Building knowledge graph...")
    refs = detect_reference_edges(conn)
    topics = detect_topic_edges(conn)
    entities = detect_entity_edges(conn)
    total = refs + topics + entities
    logger.info("Graph built: %d total edges", total)
    return total


def export_graph_snapshot(conn: sqlite3.Connection, output_dir: str):
    nodes = []
    edges = []

    articles = conn.execute("SELECT id, title, slug FROM articles").fetchall()
    for a in articles:
        nodes.append({"id": f"article:{a['id']}", "type": "article", "label": a["title"], "slug": a["slug"]})

    topics = conn.execute("SELECT id, name, topic_type FROM topics").fetchall()
    for t in topics:
        nodes.append({"id": f"topic:{t['id']}", "type": t["topic_type"], "label": t["name"]})

    entities = conn.execute("SELECT id, name, entity_type FROM entities").fetchall()
    for e in entities:
        nodes.append({"id": f"entity:{e['id']}", "type": e["entity_type"], "label": e["name"]})

    rels = conn.execute("""
        SELECT source_id, source_type, target_id, target_type, relationship_type, weight
        FROM relationships
    """).fetchall()
    for r in rels:
        edges.append({
            "source": f"{r['source_type']}:{r['source_id']}",
            "target": f"{r['target_type']}:{r['target_id']}",
            "type": r["relationship_type"],
            "weight": r["weight"],
        })

    snapshot = {
        "generated_at": datetime.now().isoformat(),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
    }

    import os
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(path, "w") as f:
        json.dump(snapshot, f, indent=2)

    logger.info("Graph snapshot exported: %s", path)
    return path
