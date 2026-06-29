import logging
import sqlite3
from pathlib import Path

from src.config import Config
from src.db.connection import init_database
from src.llm.client import LLMClient
from src.ingestion.pipeline import run_ingestion
from src.analysis.semantic import analyze_all_articles
from src.analysis.topics import extract_topics
from src.analysis.entities import extract_entities
from src.graph.builder import build_graph, export_graph_snapshot
from src.marketing.ranking import store_marketing_scores
from src.marketing.audiences import map_audiences
from src.marketing.platforms import recommend_all_platforms
from src.marketing.campaigns import generate_campaign
from src.marketing.repurposing import generate_all_repurposing
from src.memory.reasoning import store_reasoning
from src.recommendations.engine import RecommendationEngine
from src.llm.prompts import WEEKLY_REPORT_PROMPT

logger = logging.getLogger("amis.loop.autonomous")


def run_nightly_pipeline(config_path: str = None):
    config = Config(config_path)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(Path(config.paths.logs_dir) / "autonomous.log"),
            logging.StreamHandler(),
        ],
    )

    logger.info("=== Autonomous Pipeline Start ===")

    conn = init_database(config.db_path)
    llm = LLMClient(
        provider=config.llm.provider,
        model=config.llm.model,
        base_url=config.llm.base_url,
        temperature=config.llm.temperature,
        max_tokens=config.llm.max_tokens,
    )

    try:
        ingested = run_ingestion(conn, config.content_dir)
        logger.info("Step 1 - Ingestion: %d articles processed", ingested)

        if ingested > 0:
            analyze_all_articles(conn, llm)
            logger.info("Step 2 - Semantic analysis complete")

        articles = conn.execute("SELECT id FROM articles").fetchall()
        for art in articles:
            aid = art["id"]
            extract_topics(conn, llm, aid)
            extract_entities(conn, llm, aid)
            map_audiences(conn, llm, aid)
        logger.info("Steps 3-4-8 - Topics, entities, audiences complete")

        build_graph(conn)
        export_graph_snapshot(conn, config.paths.graph_dir)
        logger.info("Step 5 - Knowledge graph built")

        store_marketing_scores(conn)
        logger.info("Step 7 - Marketing scores computed")

        recommend_all_platforms(conn, llm)
        logger.info("Step 9 - Platform recommendations complete")

        campaign_id = generate_campaign(conn, llm, "promote_top_content", "developers")
        if campaign_id > 0:
            logger.info("Step 10 - Campaign generated (id=%d)", campaign_id)

        generate_all_repurposing(conn, llm)
        logger.info("Step 11 - Content repurposing complete")

        report = generate_weekly_report(conn, llm, ingested)
        report_path = Path(config.paths.generated_dir) / f"weekly_report_{Path(config.db_path).stem}.md"
        with open(report_path, "w") as f:
            f.write(report)
        logger.info("Step 16 - Weekly report generated: %s", report_path)

    except Exception as e:
        logger.error("Pipeline failed: %s", e)
        raise
    finally:
        conn.close()

    logger.info("=== Autonomous Pipeline Complete ===")


def generate_weekly_report(conn: sqlite3.Connection, llm: LLMClient, new_count: int) -> str:
    engine = RecommendationEngine(conn)
    top = engine.best_for_linkedin(5)
    active = conn.execute("SELECT COUNT(*) as c FROM campaigns WHERE status = 'active'").fetchone()
    pending = conn.execute("SELECT COUNT(*) as c FROM recommendations WHERE outcome = 'pending'").fetchone()

    prompt = WEEKLY_REPORT_PROMPT.format(
        new_articles=str(new_count),
        top_performers="\n".join(f"- {a['title']} (score: {a['suitability_score']})" for a in top),
        campaigns_active=str(active["c"] if active else 0),
        recommendations_pending=str(pending["c"] if pending else 0),
    )

    try:
        return llm.complete(prompt)
    except Exception:
        return f"# Weekly Report\n\nNew articles: {new_count}\nTop articles: {len(top)}\nActive campaigns: {active['c'] if active else 0}"
