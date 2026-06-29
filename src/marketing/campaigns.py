import json
import logging
import sqlite3
from datetime import datetime, timedelta

from src.llm.client import LLMClient
from src.llm.prompts import CAMPAIGN_GENERATION_PROMPT

logger = logging.getLogger("amis.marketing.campaigns")


def store_campaign(conn: sqlite3.Connection, campaign: dict) -> int:
    cursor = conn.execute("""
        INSERT INTO campaigns (
            name, goal, audience, book_chapters_json,
            supporting_articles_json, repositories_json, landing_page,
            call_to_action, platforms_json, publishing_schedule_json,
            estimated_duration_days, estimated_reach, estimated_conversion_rate,
            dependencies_json, success_metrics_json, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft')
    """, (
        campaign.get("name", ""),
        campaign.get("goal", ""),
        campaign.get("audience", ""),
        json.dumps(campaign.get("book_chapters", [])),
        json.dumps(campaign.get("supporting_articles", [])),
        json.dumps(campaign.get("repositories", [])),
        campaign.get("landing_page", ""),
        campaign.get("call_to_action", ""),
        json.dumps(campaign.get("platforms", [])),
        json.dumps(campaign.get("publishing_schedule", [])),
        campaign.get("estimated_duration_days", 30),
        campaign.get("estimated_reach", 0),
        campaign.get("estimated_conversion_rate", 0.0),
        json.dumps(campaign.get("dependencies", [])),
        json.dumps(campaign.get("success_metrics", [])),
    ))
    campaign_id = cursor.lastrowid

    steps = campaign.get("steps", [])
    for step in steps:
        conn.execute("""
            INSERT INTO campaign_steps
            (campaign_id, step_order, step_type, platform, article_id, content_plan, scheduled_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            campaign_id,
            step.get("order", 1),
            step.get("type", "publish"),
            step.get("platform", ""),
            step.get("article_id"),
            step.get("content_plan", ""),
            step.get("scheduled_date"),
        ))

    conn.commit()
    logger.info("Campaign created: %s (id=%d)", campaign.get("name"), campaign_id)
    return campaign_id


def generate_campaign(conn: sqlite3.Connection, llm: LLMClient, goal: str, audience: str = None) -> int:
    top_articles = conn.execute("""
        SELECT a.id, a.title, s.score_value
        FROM articles a
        JOIN scores s ON a.id = s.article_id
        WHERE s.score_type = 'marketing' AND s.metric_name = 'composite'
        ORDER BY s.score_value DESC
        LIMIT 10
    """).fetchall()

    platforms = conn.execute(
        "SELECT DISTINCT platform FROM platform_recommendations ORDER BY platform"
    ).fetchall()
    platform_list = [p["platform"] for p in platforms]

    prompt = CAMPAIGN_GENERATION_PROMPT.format(
        goal=goal,
        top_articles_json=json.dumps([dict(r) for r in top_articles], indent=2),
        audience=audience or "developers",
        platforms=json.dumps(platform_list),
    )

    try:
        result = llm.complete_json(prompt)
        return store_campaign(conn, result)
    except Exception as e:
        logger.error("Failed to generate campaign: %s", e)
        return -1


def get_active_campaigns(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM campaigns WHERE status = 'active' ORDER BY created_at DESC"
    ).fetchall()
    return [dict(r) for r in rows]


def update_campaign_status(conn: sqlite3.Connection, campaign_id: int, status: str):
    conn.execute(
        "UPDATE campaigns SET status = ?, updated_at = datetime('now') WHERE id = ?",
        (status, campaign_id),
    )
    conn.commit()


def get_campaign_steps(conn: sqlite3.Connection, campaign_id: int) -> list[dict]:
    rows = conn.execute(
        "SELECT * FROM campaign_steps WHERE campaign_id = ? ORDER BY step_order",
        (campaign_id,),
    ).fetchall()
    return [dict(r) for r in rows]
