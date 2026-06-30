import sqlite3
import json
import os
from collections import defaultdict

DB_PATH = "database/sqlite.db"
OUTPUT_DIR = "dashboard/data"

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

def dump(table):
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    data = [dict(r) for r in rows]
    with open(f"{OUTPUT_DIR}/{table}.json", "w") as f:
        json.dump(data, f, default=str)
    print(f"{table}: {len(data)} rows")
    return data

# Core content
articles = dump("articles")

# Topics & entities
topics_data = dump("topics")
article_topics = dump("article_topics")
entities_data = dump("entities")
article_entities = dump("article_entities")

# Marketing data
audiences = dump("audience_profiles")
platforms = dump("platform_recommendations")
repurposing = dump("content_repurposing")
scores = dump("scores")

# Graph & campaigns
relationships = dump("relationships")
campaigns_data = dump("campaigns")
campaign_steps = dump("campaign_steps")

# Build derived views

# Per-article summaries
article_summaries = []
for a in articles:
    aid = a["id"]
    article_scores = [s for s in scores if s["article_id"] == aid]
    article_platforms = [p for p in platforms if p["article_id"] == aid]
    article_audiences = [u for u in audiences if u["article_id"] == aid]
    article_topics_list = [t for t in article_topics if t["article_id"] == aid]
    article_entities_list = [e for e in article_entities if e["article_id"] == aid]
    article_repurposing = [r for r in repurposing if r["article_id"] == aid]

    summary = {
        "id": aid,
        "title": a["title"],
        "slug": a["slug"],
        "description": a["description"],
        "publication_date": a["publication_date"],
        "word_count": a["word_count"],
        "reading_time_minutes": a["reading_time_minutes"],
        "scores": {s["metric_name"]: s["score_value"] for s in article_scores},
        "platforms": [
            {
                "platform": p["platform"],
                "suitability_score": p["suitability_score"],
                "optimal_format": p["optimal_format"],
                "posting_frequency": p["posting_frequency"],
                "reason": p["reason"],
            }
            for p in sorted(article_platforms, key=lambda x: x["suitability_score"] or 0, reverse=True)
        ],
        "audiences": [
            {
                "audience_type": u["audience_type"],
                "relevance_score": u["relevance_score"],
                "reasoning": u["reasoning"],
            }
            for u in sorted(article_audiences, key=lambda x: x["relevance_score"] or 0, reverse=True)
        ],
        "topics": [
            {"name": t["name"], "relevance_score": at["relevance_score"], "is_primary": at["is_primary"]}
            for t in topics_data
            for at in article_topics_list
            if t["id"] == at["topic_id"]
        ],
        "entities": [
            {"name": e["name"], "entity_type": e["entity_type"]}
            for e in entities_data
            for ae in article_entities_list
            if e["id"] == ae["entity_id"]
        ],
        "repurposing": [
            {
                "target_format": r["target_format"],
                "suitability_score": r["suitability_score"],
                "transformation_notes": r["transformation_notes"],
                "estimated_effort": r["estimated_effort"],
            }
            for r in sorted(article_repurposing, key=lambda x: x["suitability_score"] or 0, reverse=True)
        ],
    }
    article_summaries.append(summary)

with open(f"{OUTPUT_DIR}/article_summaries.json", "w") as f:
    json.dump(article_summaries, f, default=str)
print(f"article_summaries: {len(article_summaries)} articles")

# Per-platform views
platform_articles = defaultdict(list)
for p in platforms:
    platform_articles[p["platform"]].append(p)
platform_summaries = {}
for plat, recs in platform_articles.items():
    top_articles = []
    for r in sorted(recs, key=lambda x: x["suitability_score"] or 0, reverse=True)[:50]:
        a = next((a for a in articles if a["id"] == r["article_id"]), None)
        if a:
            top_articles.append({
                "article_id": r["article_id"],
                "title": a["title"],
                "slug": a["slug"],
                "suitability_score": r["suitability_score"],
                "optimal_format": r["optimal_format"],
                "posting_frequency": r["posting_frequency"],
                "reason": r["reason"],
            })
    platform_summaries[plat] = {
        "platform": plat,
        "total_articles": len(recs),
        "avg_suitability": sum(r["suitability_score"] or 0 for r in recs) / len(recs),
        "top_articles": top_articles,
    }

with open(f"{OUTPUT_DIR}/platform_summaries.json", "w") as f:
    json.dump(platform_summaries, f, default=str)
print(f"platform_summaries: {len(platform_summaries)} platforms")

# Per-audience views
audience_articles = defaultdict(list)
for u in audiences:
    audience_articles[u["audience_type"]].append(u)
audience_summaries = {}
for aud, recs in audience_articles.items():
    top = []
    for r in sorted(recs, key=lambda x: x["relevance_score"] or 0, reverse=True)[:50]:
        a = next((a for a in articles if a["id"] == r["article_id"]), None)
        if a:
            top.append({
                "article_id": r["article_id"],
                "title": a["title"],
                "slug": a["slug"],
                "relevance_score": r["relevance_score"],
                "reasoning": r["reasoning"],
            })
    audience_summaries[aud] = {
        "audience_type": aud,
        "total_articles": len(recs),
        "avg_relevance": sum(r["relevance_score"] or 0 for r in recs) / len(recs),
        "top_articles": top,
    }

with open(f"{OUTPUT_DIR}/audience_summaries.json", "w") as f:
    json.dump(audience_summaries, f, default=str)
print(f"audience_summaries: {len(audience_summaries)} audiences")

# Knowledge graph for visualization
graph_nodes = set()
graph_links = []
for r in relationships:
    graph_links.append({
        "source": f"{r['source_type']}-{r['source_id']}",
        "target": f"{r['target_type']}-{r['target_id']}",
        "type": r["relationship_type"],
        "weight": r["weight"],
    })
    graph_nodes.add(f"{r['source_type']}-{r['source_id']}")
    graph_nodes.add(f"{r['target_type']}-{r['target_id']}")

# Enrich nodes with labels
node_labels = {}
for r in relationships:
    for prefix, tbl, id_col, label_col in [
        ("article", articles, "id", "title"),
        ("topic", topics_data, "id", "name"),
        ("entity", entities_data, "id", "name"),
    ]:
        key = f"{prefix}-{r['source_id']}"
        if key not in node_labels:
            match = next((item for item in tbl if item[id_col] == r["source_id"]), None)
            if match:
                node_labels[key] = {"id": key, "label": match[label_col][:50], "type": prefix}
        key = f"{prefix}-{r['target_id']}"
        if key not in node_labels:
            match = next((item for item in tbl if item[id_col] == r["target_id"]), None)
            if match:
                node_labels[key] = {"id": key, "label": match[label_col][:50], "type": prefix}

graph_data = {
    "nodes": list(node_labels.values()),
    "links": graph_links,
}
with open(f"{OUTPUT_DIR}/knowledge_graph.json", "w") as f:
    json.dump(graph_data, f, default=str)
print(f"knowledge_graph: {len(graph_data['nodes'])} nodes, {len(graph_data['links'])} edges")

# Top-level stats
topic_counts = defaultdict(int)
for at in article_topics:
    topic_counts[at["topic_id"]] += 1

entity_counts = defaultdict(int)
for ae in article_entities:
    entity_counts[ae["entity_id"]] += 1

top_topics = sorted(
    [{"name": t["name"], "count": topic_counts[t["id"]]} for t in topics_data if topic_counts[t["id"]] > 0],
    key=lambda x: x["count"], reverse=True
)[:50]

top_entities = sorted(
    [{"name": e["name"], "type": e["entity_type"], "count": entity_counts[e["id"]]} for e in entities_data if entity_counts[e["id"]] > 0],
    key=lambda x: x["count"], reverse=True
)[:50]

metrics_summary = defaultdict(lambda: {"values": [], "count": 0})
for s in scores:
    metrics_summary[s["metric_name"]]["values"].append(s["score_value"])
    metrics_summary[s["metric_name"]]["count"] += 1

metrics_stats = {}
for name, data in metrics_summary.items():
    vals = data["values"]
    metrics_stats[name] = {
        "count": data["count"],
        "avg": sum(vals) / len(vals),
        "max": max(vals),
        "min": min(vals),
    }

stats = {
    "total_articles": len(articles),
    "total_topics": len(topics_data),
    "total_entities": len(entities_data),
    "total_audiences": len(audiences),
    "total_platform_recs": len(platforms),
    "total_repurposing": len(repurposing),
    "total_scores": len(scores),
    "total_relationships": len(relationships),
    "total_campaigns": len(campaigns_data),
    "top_topics": top_topics,
    "top_entities": top_entities,
    "metrics_stats": metrics_stats,
}

with open(f"{OUTPUT_DIR}/stats.json", "w") as f:
    json.dump(stats, f, default=str)
print(f"stats: written")

conn.close()
print("Done!")
