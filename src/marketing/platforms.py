import logging
import sqlite3

from src.llm.client import LLMClient
from src.llm.prompts import PLATFORM_RECOMMENDATION_PROMPT

logger = logging.getLogger("amis.marketing.platforms")

PLATFORMS = [
    "LinkedIn", "X", "Dev.to", "Hashnode", "Medium",
    "Hacker News", "GitHub", "Personal Blog", "Email Newsletter",
    "YouTube", "Conference CFP", "Podcast Pitch",
]


def _safe_str(v):
    if isinstance(v, (dict, list)):
        return str(v)
    if v is None:
        return ""
    return str(v)

def _safe_int(v):
    if isinstance(v, (int, float)):
        return int(v)
    return 0


def store_platform_recommendation(conn: sqlite3.Connection, article_id: int, platform: str, data: dict):
    conn.execute("""
        INSERT OR REPLACE INTO platform_recommendations
        (article_id, platform, suitability_score, reason, optimal_format,
         posting_frequency, ideal_cta, audience_match, competition_estimate, expected_roi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        article_id, platform,
        _safe_int(data.get("suitability_score")),
        _safe_str(data.get("reason")),
        _safe_str(data.get("optimal_format")),
        _safe_str(data.get("posting_frequency")),
        _safe_str(data.get("ideal_cta")),
        _safe_str(data.get("audience_match")),
        _safe_str(data.get("competition_estimate")),
        _safe_str(data.get("expected_roi")),
    ))


def recommend_platforms(conn: sqlite3.Connection, llm: LLMClient, article_id: int):
    article = conn.execute(
        """SELECT id, title, content,
                  COALESCE((SELECT score_value FROM scores WHERE article_id = ? AND score_type='semantic' AND metric_name='technical_difficulty'), 50) as tech_diff
         FROM articles WHERE id = ?""",
        (article_id, article_id),
    ).fetchone()
    if not article:
        return

    existing = conn.execute(
        "SELECT 1 FROM platform_recommendations WHERE article_id = ? LIMIT 1",
        (article_id,),
    ).fetchone()
    if existing:
        logger.debug("Article %d already has platform recommendations, skipping", article_id)
        return

    ap = conn.execute(
        "SELECT reasoning FROM audience_profiles WHERE article_id = ? AND audience_type = 'developer' LIMIT 1",
        (article_id,),
    ).fetchone()

    primary_audience = "developers"
    summary = article["content"][:2000]

    for platform in PLATFORMS:
        prompt = PLATFORM_RECOMMENDATION_PROMPT.format(
            platform=platform,
            title=article["title"],
            summary=summary,
            primary_audience=primary_audience,
            technical_difficulty=article["tech_diff"],
        )
        try:
            result = llm.complete_json(prompt)
            store_platform_recommendation(conn, article_id, platform, result)
        except Exception as e:
            logger.error("Failed platform rec for article %d, platform %s: %s", article_id, platform, e)

    conn.commit()
    logger.info("Platform recommendations for article %d complete", article_id)


def recommend_all_platforms(conn: sqlite3.Connection, llm: LLMClient):
    articles = conn.execute("""
        SELECT id FROM articles
        WHERE id NOT IN (SELECT DISTINCT article_id FROM platform_recommendations)
    """).fetchall()
    logger.info("Generating platform recommendations for %d articles", len(articles))
    for art in articles:
        recommend_platforms(conn, llm, art["id"])


def get_platform_articles(conn: sqlite3.Connection, platform: str, limit: int = 10) -> list[dict]:
    rows = conn.execute("""
        SELECT a.id, a.title, a.slug, pr.suitability_score, pr.reason
        FROM articles a
        JOIN platform_recommendations pr ON a.id = pr.article_id
        WHERE pr.platform = ?
        ORDER BY pr.suitability_score DESC
        LIMIT ?
    """, (platform, limit)).fetchall()
    return [dict(r) for r in rows]
