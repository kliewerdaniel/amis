import logging
import sqlite3

logger = logging.getLogger("amis.marketing.ranking")

RANKING_WEIGHTS = {
    "marketing_score": 0.20,
    "authority_score": 0.15,
    "trust_score": 0.10,
    "book_conversion_score": 0.15,
    "seo_score": 0.10,
    "evergreen_score": 0.05,
    "shareability": 0.10,
    "conference_potential": 0.05,
    "podcast_potential": 0.05,
    "newsletter_potential": 0.05,
}

DIMENSION_COMPONENTS = {
    "marketing_score": ["marketing_value", "virality_potential", "seo_potential"],
    "authority_score": ["authority_score", "practicality", "originality"],
    "trust_score": ["educational_value", "evergreen_score"],
    "book_conversion_score": ["book_relevance", "educational_value", "authority_score"],
    "seo_score": ["seo_potential", "evergreen_score"],
    "evergreen_score": ["evergreen_score"],
    "shareability": ["virality_potential", "marketing_value"],
    "conference_potential": ["authority_score", "practicality", "originality"],
    "podcast_potential": ["executive_appeal"],
    "newsletter_potential": ["educational_value", "practicality"],
}


def compute_dimension_scores(conn: sqlite3.Connection) -> dict[int, dict[str, float]]:
    articles = conn.execute("SELECT DISTINCT article_id FROM scores WHERE score_type = 'semantic'").fetchall()
    article_scores = {}

    for art in articles:
        aid = art["article_id"]
        scores = conn.execute(
            "SELECT metric_name, score_value FROM scores WHERE article_id = ? AND score_type = 'semantic'",
            (aid,),
        ).fetchall()
        score_map = {s["metric_name"]: s["score_value"] for s in scores}
        article_scores[aid] = score_map

    dimension_scores = {}
    for aid, score_map in article_scores.items():
        dims = {}
        for dim_name, components in DIMENSION_COMPONENTS.items():
            values = [score_map.get(c, 0) for c in components]
            dims[dim_name] = sum(values) / len(values) if values else 0
        dims["composite"] = sum(
            dims.get(k, 0) * w for k, w in RANKING_WEIGHTS.items()
        )
        dimension_scores[aid] = dims

    return dimension_scores


def store_marketing_scores(conn: sqlite3.Connection):
    dim_scores = compute_dimension_scores(conn)
    stored = 0
    for aid, dims in dim_scores.items():
        for dim_name, score in dims.items():
            conn.execute("""
                INSERT OR REPLACE INTO scores
                (article_id, score_type, metric_name, score_value, confidence, model_used)
                VALUES (?, 'marketing', ?, ?, 0.8, 'computed')
            """, (aid, dim_name, round(score, 2)))
            stored += 1
    conn.commit()
    logger.info("Stored %d marketing scores for %d articles", stored, len(dim_scores))
    return stored


def get_article_ranking(conn: sqlite3.Connection, dimension: str = "composite", limit: int = 20) -> list[dict]:
    rows = conn.execute("""
        SELECT a.id, a.title, a.slug, s.score_value as score
        FROM articles a
        JOIN scores s ON a.id = s.article_id
        WHERE s.score_type = 'marketing' AND s.metric_name = ?
        ORDER BY s.score_value DESC
        LIMIT ?
    """, (dimension, limit)).fetchall()
    return [dict(r) for r in rows]
