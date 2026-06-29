import sqlite3
import os
from pathlib import Path


def get_connection(db_path: str = "database/sqlite.db") -> sqlite3.Connection:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_database(db_path: str = "database/sqlite.db") -> sqlite3.Connection:
    conn = get_connection(db_path)
    apply_schema(conn)
    return conn


def apply_schema(conn: sqlite3.Connection):
    conn.executescript(SCHEMA_SQL)
    conn.commit()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);

INSERT OR IGNORE INTO schema_version (version, description)
VALUES (1, 'initial schema');

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    author TEXT,
    description TEXT,
    canonical_url TEXT,
    publication_date TEXT,
    frontmatter_json TEXT,
    content TEXT NOT NULL,
    html_content TEXT,
    word_count INTEGER,
    reading_time_minutes INTEGER,
    headings_json TEXT,
    images_json TEXT,
    links_json TEXT,
    code_blocks_json TEXT,
    references_json TEXT,
    categories_json TEXT,
    tags_json TEXT,
    ingestion_hash TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_articles_slug ON articles(slug);
CREATE INDEX IF NOT EXISTS idx_articles_publication_date ON articles(publication_date);
CREATE INDEX IF NOT EXISTS idx_articles_ingestion_hash ON articles(ingestion_hash);

CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    score_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    score_value REAL NOT NULL,
    confidence REAL,
    reasoning TEXT,
    scored_at TEXT NOT NULL DEFAULT (datetime('now')),
    model_used TEXT,
    UNIQUE(article_id, score_type, metric_name)
);

CREATE INDEX IF NOT EXISTS idx_scores_article ON scores(article_id);
CREATE INDEX IF NOT EXISTS idx_scores_type ON scores(score_type);
CREATE INDEX IF NOT EXISTS idx_scores_metric ON scores(metric_name);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    topic_type TEXT NOT NULL,
    description TEXT,
    parent_id INTEGER REFERENCES topics(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(name, topic_type)
);

CREATE INDEX IF NOT EXISTS idx_topics_type ON topics(topic_type);
CREATE INDEX IF NOT EXISTS idx_topics_parent ON topics(parent_id);

CREATE TABLE IF NOT EXISTS article_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    relevance_score REAL DEFAULT 1.0,
    is_primary BOOLEAN DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id, topic_id)
);

CREATE INDEX IF NOT EXISTS idx_article_topics_article ON article_topics(article_id);
CREATE INDEX IF NOT EXISTS idx_article_topics_topic ON article_topics(topic_id);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    description TEXT,
    url TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(name, entity_type)
);

CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(entity_type);

CREATE TABLE IF NOT EXISTS article_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    context TEXT,
    mention_count INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_article_entities_article ON article_entities(article_id);
CREATE INDEX IF NOT EXISTS idx_article_entities_entity ON article_entities(entity_id);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,
    source_type TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    target_type TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    weight REAL DEFAULT 0.5,
    confidence REAL,
    reasoning TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source_id, source_type, target_id, target_type, relationship_type)
);

CREATE INDEX IF NOT EXISTS idx_relationships_source ON relationships(source_id, source_type);
CREATE INDEX IF NOT EXISTS idx_relationships_target ON relationships(target_id, target_type);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships(relationship_type);

CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    goal TEXT NOT NULL,
    audience TEXT,
    book_chapters_json TEXT,
    supporting_articles_json TEXT,
    repositories_json TEXT,
    landing_page TEXT,
    call_to_action TEXT,
    platforms_json TEXT,
    publishing_schedule_json TEXT,
    estimated_duration_days INTEGER,
    estimated_reach INTEGER,
    estimated_conversion_rate REAL,
    dependencies_json TEXT,
    success_metrics_json TEXT,
    status TEXT DEFAULT 'draft',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS campaign_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL,
    platform TEXT,
    article_id INTEGER REFERENCES articles(id),
    content_plan TEXT,
    scheduled_date TEXT,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_campaign_steps_campaign ON campaign_steps(campaign_id);

CREATE TABLE IF NOT EXISTS platform_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    suitability_score REAL NOT NULL,
    reason TEXT,
    optimal_format TEXT,
    posting_frequency TEXT,
    ideal_cta TEXT,
    audience_match TEXT,
    competition_estimate TEXT,
    expected_roi TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_platform_recs_article ON platform_recommendations(article_id);
CREATE INDEX IF NOT EXISTS idx_platform_recs_platform ON platform_recommendations(platform);

CREATE TABLE IF NOT EXISTS audience_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    audience_type TEXT NOT NULL,
    relevance_score REAL NOT NULL,
    reasoning TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id, audience_type)
);

CREATE INDEX IF NOT EXISTS idx_audience_article ON audience_profiles(article_id);

CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_type TEXT NOT NULL,
    article_id INTEGER REFERENCES articles(id),
    campaign_id INTEGER REFERENCES campaigns(id),
    score REAL,
    reasoning TEXT,
    confidence REAL,
    related_content_json TEXT,
    outcome TEXT DEFAULT 'pending',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_recommendations_type ON recommendations(recommendation_type);
CREATE INDEX IF NOT EXISTS idx_recommendations_article ON recommendations(article_id);

CREATE TABLE IF NOT EXISTS reasoning_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reasoning_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    prompt TEXT,
    response TEXT,
    model_used TEXT,
    confidence REAL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    context_json TEXT,
    outcome TEXT
);

CREATE INDEX IF NOT EXISTS idx_reasoning_entity ON reasoning_history(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_reasoning_type ON reasoning_history(reasoning_type);

CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER REFERENCES articles(id),
    campaign_id INTEGER REFERENCES campaigns(id),
    platform TEXT,
    metric_type TEXT NOT NULL,
    metric_value REAL NOT NULL,
    recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
    source TEXT
);

CREATE INDEX IF NOT EXISTS idx_analytics_article ON analytics(article_id);
CREATE INDEX IF NOT EXISTS idx_analytics_metric ON analytics(metric_type);
CREATE INDEX IF NOT EXISTS idx_analytics_recorded ON analytics(recorded_at);

CREATE TABLE IF NOT EXISTS book_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    chapter_number INTEGER,
    chapter_title TEXT,
    relevance_score REAL,
    mapping_type TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_book_mappings_article ON book_mappings(article_id);

CREATE TABLE IF NOT EXISTS repository_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    repository_name TEXT NOT NULL,
    repository_url TEXT,
    relevance_score REAL,
    mapping_type TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_repo_mappings_article ON repository_mappings(article_id);

CREATE TABLE IF NOT EXISTS content_repurposing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    target_format TEXT NOT NULL,
    suitability_score REAL NOT NULL,
    transformation_notes TEXT,
    estimated_effort TEXT,
    priority INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_repurposing_article ON content_repurposing(article_id);
CREATE INDEX IF NOT EXISTS idx_repurposing_format ON content_repurposing(target_format);
"""
