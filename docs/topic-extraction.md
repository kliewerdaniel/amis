# Phase 3: Topic Extraction

## Objective

Extract a normalized taxonomy of topics, subtopics, concepts, technologies, and categories from each article.

## Input

- All rows from `articles` table
- Full article content

## Extraction Categories

| Category | Description | Examples |
|----------|-------------|----------|
| `topic` | High-level subject areas | AI, Machine Learning, Web Development |
| `subtopic` | Narrower topic areas | LLM Integration, RAG, Fine-tuning |
| `concept` | Abstract ideas | Sovereignty, Autonomy, Local-first |
| `technology` | Specific technologies | Ollama, ChromaDB, SQLite, Next.js |
| `framework` | Frameworks/libraries | React, Django, LangChain, FastAPI |
| `language` | Programming languages | Python, TypeScript, Rust |
| `industry` | Industry verticals | Healthcare, Finance, Education |
| `ai_concept` | AI-specific concepts | Agents, Embeddings, Fine-tuning |
| `arch_pattern` | Architectural patterns | Microservices, Event-driven, CQRS |
| `enterprise` | Enterprise concerns | Security, Compliance, Scalability |
| `cloud_provider` | Cloud platforms | AWS, Azure, GCP |
| `security` | Security topics | API security, Authentication |
| `optimization` | Performance topics | Caching, Indexing, Profiling |

## LLM Prompt Template

```python
TOPIC_EXTRACTION_PROMPT = """
Extract all topics and concepts from this blog article.
Classify each into the appropriate category.

Article Title: {title}
Article Content:
{content}

Return JSON:
{{
  "topics": ["..."],
  "subtopics": ["..."],
  "concepts": ["..."],
  "technologies": ["..."],
  "frameworks": ["..."],
  "languages": ["..."],
  "industries": ["..."],
  "ai_concepts": ["..."],
  "architectural_patterns": ["..."],
  "enterprise_concerns": ["..."],
  "cloud_providers": ["..."],
  "security_topics": ["..."],
  "optimization_topics": ["..."]
}}
"""
```

## Storage

### Topic Normalization

```python
def normalize_topic(name: str, topic_type: str) -> str:
    """Lowercase, strip whitespace, deduplicate."""
    return name.strip().lower()
```

### Upsert Logic

```python
def store_topics(conn, article_id: int, extracted: dict):
    for category, items in extracted.items():
        for item in items:
            topic_id = upsert_topic(conn, item, category)
            conn.execute("""
                INSERT OR IGNORE INTO article_topics
                (article_id, topic_id, relevance_score, is_primary)
                VALUES (?, ?, 1.0, 0)
            """, (article_id, topic_id))
```

## Output

- `topics` table: unique normalized taxonomy
- `article_topics` table: many-to-many article-topic mapping

## Dependencies

- LLM client for extraction
- Deterministic normalization (no LLM needed for dedup)

## Validation

1. Every article has at least 3 topics
2. No duplicate topics within same `topic_type`
3. All `article_topics` reference valid `article_id` and `topic_id`
4. Topic names are normalized (lowercase, trimmed)
