import logging
import sqlite3
from src.recommendations.engine import RecommendationEngine
from src.llm.client import LLMClient
from src.marketing.campaigns import generate_campaign as _gen_campaign
from src.marketing.campaigns import get_active_campaigns, update_campaign_status
from src.marketing.platforms import get_platform_articles
from src.marketing.audiences import get_audience_articles
from src.marketing.repurposing import get_repurposing_options
from src.graph.duplicates import find_exact_duplicates

logger = logging.getLogger("amis.agent_tools")


class AMISTools:
    def __init__(self, engine: RecommendationEngine, conn: sqlite3.Connection, llm: LLMClient = None):
        self.engine = engine
        self.conn = conn
        self.llm = llm

    def find_best_articles(self, platform: str = None, audience: str = None,
                           topic: str = None, limit: int = 10) -> list[dict]:
        if platform:
            return get_platform_articles(self.conn, platform, limit)
        if audience:
            return get_audience_articles(self.conn, audience)
        return self.engine.best_for_linkedin(limit)

    def generate_campaign(self, goal: str, audience: str = None,
                          budget: str = None, duration_days: int = 30) -> dict:
        if not self.llm:
            return {"error": "LLM client required for campaign generation"}
        campaign_id = _gen_campaign(self.conn, self.llm, goal, audience)
        if campaign_id <= 0:
            return {"error": "Campaign generation failed"}
        row = self.conn.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,)).fetchone()
        return dict(row) if row else {"error": "Campaign not found"}

    def recommend_platform(self, article_id: int, top_n: int = 3) -> list[dict]:
        rows = self.conn.execute("""
            SELECT platform, suitability_score, reason, optimal_format, ideal_cta
            FROM platform_recommendations
            WHERE article_id = ?
            ORDER BY suitability_score DESC
            LIMIT ?
        """, (article_id, top_n)).fetchall()
        return [dict(r) for r in rows]

    def rank_articles(self, dimension: str = "composite", limit: int = 20) -> list[dict]:
        return self.engine.best_for_linkedin(limit) if dimension == "composite" else []

    def find_hidden_gems(self, min_score: float = 70.0) -> list[dict]:
        return self.engine.best_hidden_gems(10)

    def find_duplicate_content(self, threshold: float = 0.85) -> list[dict]:
        return find_exact_duplicates(self.conn)

    def find_missing_topics(self) -> list[dict]:
        return self.engine.best_followup().get("series_articles", [])

    def recommend_book_marketing(self) -> dict:
        articles = self.engine.best_book_seller(10)
        return {
            "recommendation": "Top articles for book marketing",
            "articles": articles,
        }

    def recommend_consulting_content(self) -> list[dict]:
        rows = self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                   COALESCE((SELECT score_value FROM scores
                    WHERE article_id = a.id AND score_type = 'semantic' AND metric_name = 'consulting_relevance'), 0) as consulting_score
            FROM articles a
            ORDER BY consulting_score DESC
            LIMIT 10
        """).fetchall()
        return [dict(r) for r in rows]

    def generate_monthly_plan(self, month: str = None) -> dict:
        top = self.engine.best_for_linkedin(5)
        hidden = self.engine.best_hidden_gems(3)
        campaigns = get_active_campaigns(self.conn)
        return {
            "month": month or "current",
            "top_articles": top,
            "hidden_gems": hidden,
            "active_campaigns": [c["name"] for c in campaigns] if campaigns else [],
            "weekly_plan": [
                {"week": 1, "focus": "Top content promotion", "articles": top[:3]},
                {"week": 2, "focus": "Hidden gems", "articles": hidden},
                {"week": 3, "focus": "Campaign execution", "articles": top[3:]},
                {"week": 4, "focus": "Review and planning"},
            ],
        }
