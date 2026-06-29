# SQLite Database Schema

## Overview

All structured data persists in a single SQLite database at `database/sqlite.db`. The schema is versioned via a `schema_version` table to support incremental migrations.

## Schema Version

```sql
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now')),
    description TEXT
);
```

## Core Tables

### Articles

```sql
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
    headings_json TEXT,          -- JSON array of heading objects
    images_json TEXT,            -- JSON array of image references
    links_json TEXT,             -- JSON array of link objects
    code_blocks_json TEXT,       -- JSON array of code block objects
    references_json TEXT,        -- JSON array of reference objects
    categories_json TEXT,        -- JSON array of category strings
    tags_json TEXT,              -- JSON array of tag strings
    ingestion_hash TEXT,         -- SHA-256 of content for idempotency
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_articles_publication_date ON articles(publication_date);
CREATE INDEX idx_articles_ingestion_hash ON articles(ingestion_hash);
```

### Scores

```sql
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    score_type TEXT NOT NULL,      -- e.g. 'marketing', 'authority', 'seo'
    metric_name TEXT NOT NULL,     -- e.g. 'summary', 'core_thesis', 'evergreen_score'
    score_value REAL NOT NULL,     -- 0-100
    confidence REAL,               -- 0-1
    reasoning TEXT,                -- LLM reasoning for this score
    scored_at TEXT NOT NULL DEFAULT (datetime('now')),
    model_used TEXT,
    UNIQUE(article_id, score_type, metric_name)
);

CREATE INDEX idx_scores_article ON scores(article_id);
CREATE INDEX idx_scores_type ON scores(score_type);
CREATE INDEX idx_scores_metric ON scores(metric_name);
```

### Topics

```sql
CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    topic_type TEXT NOT NULL,      -- 'topic', 'subtopic', 'concept', 'technology', etc.
    description TEXT,
    parent_id INTEGER REFERENCES topics(id),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(name, topic_type)
);

CREATE INDEX idx_topics_type ON topics(topic_type);
CREATE INDEX idx_topics_parent ON topics(parent_id);
```

### ArticleTopics

```sql
CREATE TABLE IF NOT EXISTS article_topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    relevance_score REAL DEFAULT 1.0,  -- 0-1
    is_primary BOOLEAN DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id, topic_id)
);

CREATE INDEX idx_article_topics_article ON article_topics(article_id);
CREATE INDEX idx_article_topics_topic ON article_topics(topic_id);
```

### Entities

```sql
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,     -- 'person', 'company', 'book', 'repository', etc.
    description TEXT,
    url TEXT,
    metadata_json TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(name, entity_type)
);

CREATE INDEX idx_entities_type ON entities(entity_type);
```

### ArticleEntities

```sql
CREATE TABLE IF NOT EXISTS article_entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    entity_id INTEGER NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
    context TEXT,                  -- surrounding text where entity appears
    mention_count INTEGER DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id, entity_id)
);

CREATE INDEX idx_article_entities_article ON article_entities(article_id);
CREATE INDEX idx_article_entities_entity ON article_entities(entity_id);
```

### Relationships

```sql
CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER NOT NULL,          -- article or entity id
    source_type TEXT NOT NULL,           -- 'article' or 'entity'
    target_id INTEGER NOT NULL,          -- article or entity id
    target_type TEXT NOT NULL,           -- 'article' or 'entity'
    relationship_type TEXT NOT NULL,     -- 17 types (see below)
    weight REAL DEFAULT 0.5,            -- 0-1
    confidence REAL,
    reasoning TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(source_id, source_type, target_id, target_type, relationship_type)
);

CREATE INDEX idx_relationships_source ON relationships(source_id, source_type);
CREATE INDEX idx_relationships_target ON relationships(target_id, target_type);
CREATE INDEX idx_relationships_type ON relationships(relationship_type);
```

**Relationship Types:**
1. `references` — Article A references Article B
2. `expands` — Article A expands on ideas in Article B
3. `contradicts` — Article A contradicts claims in Article B
4. `depends_on` — Article A depends on knowledge from Article B
5. `introduces` — Article A introduces concepts used in Article B
6. `explains` — Article A explains topics in Article B
7. `updates` — Article A updates/supersedes Article B
8. `duplicates` — Article A duplicates content in Article B
9. `supports` — Article A supports arguments in Article B
10. `markets` — Article A markets/promotes Article B
11. `implements` — Article A implements ideas from Article B
12. `mentions` — Article A mentions Article B
13. `recommended_after` — Read A before B
14. `recommended_before` — Read B before A
15. `related_to` — General relatedness
16. `derived_from` — Article A derived from Article B
17. `visualizes` — Article A visualizes concepts from Article B

### Campaigns

```sql
CREATE TABLE IF NOT EXISTS campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    goal TEXT NOT NULL,
    audience TEXT,
    book_chapters_json TEXT,       -- JSON array of chapter references
    supporting_articles_json TEXT,  -- JSON array of article IDs
    repositories_json TEXT,        -- JSON array of repo references
    landing_page TEXT,
    call_to_action TEXT,
    platforms_json TEXT,           -- JSON array of platform names
    publishing_schedule_json TEXT, -- JSON array of schedule entries
    estimated_duration_days INTEGER,
    estimated_reach INTEGER,
    estimated_conversion_rate REAL,
    dependencies_json TEXT,        -- JSON array of dependency strings
    success_metrics_json TEXT,     -- JSON array of metric definitions
    status TEXT DEFAULT 'draft',   -- draft, active, completed, archived
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

### CampaignSteps

```sql
CREATE TABLE IF NOT EXISTS campaign_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    step_order INTEGER NOT NULL,
    step_type TEXT NOT NULL,        -- 'publish', 'promote', 'follow_up', etc.
    platform TEXT,
    article_id INTEGER REFERENCES articles(id),
    content_plan TEXT,
    scheduled_date TEXT,
    status TEXT DEFAULT 'pending',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_campaign_steps_campaign ON campaign_steps(campaign_id);
```

### PlatformRecommendations

```sql
CREATE TABLE IF NOT EXISTS platform_recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    platform TEXT NOT NULL,
    suitability_score REAL NOT NULL,  -- 0-100
    reason TEXT,
    optimal_format TEXT,
    posting_frequency TEXT,
    ideal_cta TEXT,
    audience_match TEXT,
    competition_estimate TEXT,
    expected_roi TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_platform_recs_article ON platform_recommendations(article_id);
CREATE INDEX idx_platform_recs_platform ON platform_recommendations(platform);
```

### AudienceProfiles

```sql
CREATE TABLE IF NOT EXISTS audience_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    audience_type TEXT NOT NULL,    -- 'beginner', 'developer', 'cto', etc.
    relevance_score REAL NOT NULL,  -- 0-100
    reasoning TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(article_id, audience_type)
);

CREATE INDEX idx_audience_article ON audience_profiles(article_id);
```

### Recommendations

```sql
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recommendation_type TEXT NOT NULL,  -- 'best_for_linkedin', 'hidden_gem', etc.
    article_id INTEGER REFERENCES articles(id),
    campaign_id INTEGER REFERENCES campaigns(id),
    score REAL,
    reasoning TEXT,
    confidence REAL,
    related_content_json TEXT,
    outcome TEXT,                       -- 'pending', 'accepted', 'rejected', 'acted_on'
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_recommendations_type ON recommendations(recommendation_type);
CREATE INDEX idx_recommendations_article ON recommendations(article_id);
```

### ReasoningHistory

```sql
CREATE TABLE IF NOT EXISTS reasoning_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reasoning_type TEXT NOT NULL,
    entity_type TEXT NOT NULL,         -- 'article', 'campaign', 'recommendation'
    entity_id INTEGER NOT NULL,
    prompt TEXT,
    response TEXT,
    model_used TEXT,
    confidence REAL,
    timestamp TEXT NOT NULL DEFAULT (datetime('now')),
    context_json TEXT,
    outcome TEXT
);

CREATE INDEX idx_reasoning_entity ON reasoning_history(entity_type, entity_id);
CREATE INDEX idx_reasoning_type ON reasoning_history(reasoning_type);
```

### Analytics

```sql
CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER REFERENCES articles(id),
    campaign_id INTEGER REFERENCES campaigns(id),
    platform TEXT,
    metric_type TEXT NOT NULL,        -- 'views', 'clicks', 'shares', etc.
    metric_value REAL NOT NULL,
    recorded_at TEXT NOT NULL DEFAULT (datetime('now')),
    source TEXT                       -- 'manual', 'api', 'import'
);

CREATE INDEX idx_analytics_article ON analytics(article_id);
CREATE INDEX idx_analytics_metric ON analytics(metric_type);
CREATE INDEX idx_analytics_recorded ON analytics(recorded_at);
```

### BookMappings

```sql
CREATE TABLE IF NOT EXISTS book_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    chapter_number INTEGER,
    chapter_title TEXT,
    relevance_score REAL,            -- 0-1
    mapping_type TEXT,               -- 'prerequisite', 'companion', 'expansion'
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_book_mappings_article ON book_mappings(article_id);
```

### RepositoryMappings

```sql
CREATE TABLE IF NOT EXISTS repository_mappings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    repository_name TEXT NOT NULL,
    repository_url TEXT,
    relevance_score REAL,            -- 0-1
    mapping_type TEXT,               -- 'tutorial', 'showcase', 'dependency'
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_repo_mappings_article ON repository_mappings(article_id);
```

### ContentRepurposing

```sql
CREATE TABLE IF NOT EXISTS content_repurposing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL REFERENCES articles(id) ON DELETE CASCADE,
    target_format TEXT NOT NULL,     -- 'linkedin', 'thread', 'newsletter', etc.
    suitability_score REAL NOT NULL, -- 0-100
    transformation_notes TEXT,
    estimated_effort TEXT,           -- 'low', 'medium', 'high'
    priority INTEGER DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX idx_repurposing_article ON content_repurposing(article_id);
CREATE INDEX idx_repurposing_format ON content_repurposing(target_format);
```

## Migration Strategy

Schema version tracked in `schema_version` table. On startup:

1. Read current version from `schema_version`
2. Apply any pending migrations in order
3. Update version number

Migrations stored as numbered SQL files in `src/db/migrations/`:

```
src/db/migrations/
├── 001_initial.sql
├── 002_add_analytics.sql
└── ...
```
