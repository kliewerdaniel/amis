import sys
import json
import argparse
import logging
from pathlib import Path

from src.config import Config
from src.db.connection import init_database
from src.llm.client import LLMClient
from src.ingestion.pipeline import run_ingestion
from src.analysis.semantic import analyze_all_articles, analyze_article
from src.analysis.topics import extract_topics
from src.analysis.entities import extract_entities
from src.graph.builder import build_graph, export_graph_snapshot
from src.graph.duplicates import find_exact_duplicates
from src.marketing.ranking import store_marketing_scores, get_article_ranking
from src.marketing.audiences import map_audiences
from src.marketing.platforms import recommend_platforms, get_platform_articles
from src.marketing.campaigns import generate_campaign, get_active_campaigns
from src.marketing.repurposing import generate_repurposing
from src.recommendations.engine import RecommendationEngine
from src.recommendations.agent_tools import AMISTools
from src.loop.autonomous import run_nightly_pipeline


def main():
    parser = argparse.ArgumentParser(description="AMIS - Agentic Marketing Intelligence System")
    parser.add_argument("--config", default=None, help="Path to config YAML")
    parser.add_argument("--db", default=None, help="Path to SQLite database")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("ingest", help="Ingest markdown files")
    sub.add_parser("analyze", help="Run semantic analysis on all articles")
    sub.add_parser("analyze-one", help="Analyze a single article").add_argument("article_id", type=int)
    sub.add_parser("topics", help="Extract topics for all articles")
    sub.add_parser("entities", help="Extract entities for all articles")
    sub.add_parser("graph", help="Build knowledge graph")
    sub.add_parser("graph-export", help="Export graph snapshot")
    sub.add_parser("duplicates", help="Find duplicate articles")
    sub.add_parser("rank", help="Compute marketing rankings")
    sub.add_parser("rankings", help="Show article rankings").add_argument("--limit", type=int, default=20)
    sub.add_parser("audiences", help="Map audiences for all articles")
    sub.add_parser("platforms", help="Generate platform recommendations")
    sub.add_parser("campaign", help="Generate a campaign").add_argument("--goal", default="promote_top_content")
    sub.add_parser("repurpose", help="Generate content repurposing")
    sub.add_parser("pipeline", help="Run full pipeline")
    sub.add_parser("nightly", help="Run autonomous nightly pipeline")

    rec = sub.add_parser("recommend", help="Get recommendations")
    rec.add_argument("type", choices=[
        "today", "linkedin", "executives", "book", "evergreen",
        "authority", "underutilized", "gems", "followup", "update", "roi",
    ])

    tool = sub.add_parser("tool", help="Agent tool interface")
    tool.add_argument("tool_name", help="Tool name")
    tool.add_argument("--params", default="{}", help="JSON params")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    config = Config(args.config)
    if args.db:
        config.paths.db_path = args.db

    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    conn = init_database(config.db_path)
    llm = LLMClient(
        provider=config.llm.provider,
        model=config.llm.model,
        base_url=config.llm.base_url,
    )

    try:
        if args.command == "ingest":
            count = run_ingestion(conn, config.content_dir)
            print(f"Ingested {count} articles")

        elif args.command == "analyze":
            analyze_all_articles(conn, llm)
            print("Semantic analysis complete")

        elif args.command == "analyze-one":
            analyze_article(conn, llm, args.article_id)
            print(f"Analyzed article {args.article_id}")

        elif args.command == "topics":
            articles = conn.execute("SELECT id FROM articles").fetchall()
            for art in articles:
                extract_topics(conn, llm, art["id"])
            print("Topic extraction complete")

        elif args.command == "entities":
            articles = conn.execute("SELECT id FROM articles").fetchall()
            for art in articles:
                extract_entities(conn, llm, art["id"])
            print("Entity extraction complete")

        elif args.command == "graph":
            count = build_graph(conn)
            print(f"Graph built: {count} edges")

        elif args.command == "graph-export":
            path = export_graph_snapshot(conn, config.paths.graph_dir)
            print(f"Graph exported: {path}")

        elif args.command == "duplicates":
            dupes = find_exact_duplicates(conn)
            if dupes:
                for d in dupes:
                    print(f"  {d['atitle']} == {d['btitle']}")
            else:
                print("No exact duplicates found")

        elif args.command == "rank":
            count = store_marketing_scores(conn)
            print(f"Marketing scores stored: {count}")

        elif args.command == "rankings":
            rows = get_article_ranking(conn, limit=args.limit)
            for i, r in enumerate(rows, 1):
                print(f"  {i}. {r['title']} ({r['score']:.1f})")

        elif args.command == "audiences":
            articles = conn.execute("SELECT id FROM articles").fetchall()
            for art in articles:
                map_audiences(conn, llm, art["id"])
            print("Audience mapping complete")

        elif args.command == "platforms":
            articles = conn.execute("SELECT id FROM articles").fetchall()
            for art in articles:
                recommend_platforms(conn, llm, art["id"])
            print("Platform recommendations complete")

        elif args.command == "campaign":
            cid = generate_campaign(conn, llm, args.goal)
            print(f"Campaign created (id={cid})")

        elif args.command == "repurpose":
            articles = conn.execute("SELECT id FROM articles").fetchall()
            for art in articles:
                generate_repurposing(conn, llm, art["id"])
            print("Repurposing complete")

        elif args.command == "pipeline":
            run_ingestion(conn, config.content_dir)
            analyze_all_articles(conn, llm)
            articles = conn.execute("SELECT id FROM articles").fetchall()
            for art in articles:
                aid = art["id"]
                extract_topics(conn, llm, aid)
                extract_entities(conn, llm, aid)
                map_audiences(conn, llm, aid)
                recommend_platforms(conn, llm, aid)
                generate_repurposing(conn, llm, aid)
            build_graph(conn)
            store_marketing_scores(conn)
            generate_campaign(conn, llm, "promote_top_content")
            export_graph_snapshot(conn, config.paths.graph_dir)
            print("Full pipeline complete")

        elif args.command == "nightly":
            run_nightly_pipeline(args.config)

        elif args.command == "recommend":
            engine = RecommendationEngine(conn)
            result = {
                "today": engine.best_article_today,
                "linkedin": lambda: engine.best_for_linkedin(),
                "executives": lambda: engine.best_for_executives(),
                "book": lambda: engine.best_book_seller(),
                "evergreen": lambda: engine.most_evergreen(),
                "authority": lambda: engine.highest_authority(),
                "underutilized": lambda: engine.most_underutilized(),
                "gems": lambda: engine.best_hidden_gems(),
                "followup": lambda: engine.best_followup(),
                "update": lambda: engine.needs_update(),
                "roi": lambda: engine.highest_roi_campaign(),
            }.get(args.type, lambda: {})()
            print(json.dumps(result, indent=2))

        elif args.command == "tool":
            engine = RecommendationEngine(conn)
            tools = AMISTools(engine, conn, llm)
            params = json.loads(args.params)
            method = getattr(tools, args.tool_name, None)
            if method:
                result = method(**params)
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"Unknown tool: {args.tool_name}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
