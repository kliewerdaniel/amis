import logging
import sqlite3
from datetime import datetime, timedelta

logger = logging.getLogger("amis.recommendations.engine")


class RecommendationEngine:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def best_article_today(self) -> dict | None:
        row = self.conn.execute("""
            SELECT a.id, a.title, a.slug, s.score_value as composite_score
            FROM articles a
            JOIN scores s ON a.id = s.article_id
            WHERE s.score_type = 'marketing' AND s.metric_name = 'composite'
            ORDER BY s.score_value DESC
            LIMIT 1
        """).fetchone()
        return dict(row) if row else None

    def best_for_linkedin(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT a.id, a.title, a.slug, pr.suitability_score, pr.reason
            FROM articles a
            JOIN platform_recommendations pr ON a.id = pr.article_id
            WHERE pr.platform = 'LinkedIn'
            ORDER BY pr.suitability_score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def best_for_executives(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                   COALESCE(ap.relevance_score, 0) as executive_score
            FROM articles a
            LEFT JOIN audience_profiles ap ON a.id = ap.article_id AND ap.audience_type = 'cto'
            JOIN scores s ON a.id = s.article_id
            WHERE s.score_type = 'semantic'
            GROUP BY a.id
            ORDER BY executive_score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def best_book_seller(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                   COALESCE((SELECT score_value FROM scores
                    WHERE article_id = a.id AND score_type = 'semantic' AND metric_name = 'book_relevance'), 0) as book_score
            FROM articles a
            ORDER BY book_score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def most_evergreen(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                   COALESCE((SELECT score_value FROM scores
                    WHERE article_id = a.id AND score_type = 'semantic' AND metric_name = 'evergreen_score'), 0) as evergreen_score
            FROM articles a
            ORDER BY evergreen_score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def highest_authority(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                   COALESCE((SELECT score_value FROM scores
                    WHERE article_id = a.id AND score_type = 'semantic' AND metric_name = 'authority_score'), 0) as authority_score
            FROM articles a
            ORDER BY authority_score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def most_underutilized(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                   AVG(s.score_value) as avg_score,
                   COUNT(pr.id) as platform_count
            FROM articles a
            JOIN scores s ON a.id = s.article_id
            LEFT JOIN platform_recommendations pr ON a.id = pr.article_id
            WHERE s.score_type = 'semantic' AND s.metric_name NOT IN ('summary', 'core_thesis', 'problem_solved')
            GROUP BY a.id
            HAVING avg_score > 60 AND platform_count < 3
            ORDER BY avg_score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def best_hidden_gems(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                   AVG(s.score_value) as avg_score
            FROM articles a
            JOIN scores s ON a.id = s.article_id
            WHERE s.score_type = 'semantic' AND s.metric_name NOT IN ('summary', 'core_thesis', 'problem_solved')
            AND a.id NOT IN (
                SELECT DISTINCT article_id FROM analytics WHERE metric_type = 'views'
            )
            GROUP BY a.id
            HAVING avg_score > 65
            ORDER BY avg_score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def best_followup(self, limit: int = 10) -> dict:
        series = self.conn.execute("""
            SELECT title, slug FROM articles
            WHERE title LIKE '%Part %'
            ORDER BY publication_date
        """).fetchall()
        return {"series_articles": [dict(r) for r in series]}

    def needs_update(self, limit: int = 10) -> list[dict]:
        rows = self.conn.execute("""
            SELECT id, title, slug, publication_date
            FROM articles
            WHERE publication_date < date('now', '-6 months')
            ORDER BY publication_date ASC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]

    def highest_roi_campaign(self, limit: int = 5) -> list[dict]:
        rows = self.conn.execute("""
            SELECT id, name, goal, estimated_reach, estimated_conversion_rate,
                   (estimated_reach * estimated_conversion_rate) as estimated_roi
            FROM campaigns
            WHERE status = 'active'
            ORDER BY estimated_roi DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
