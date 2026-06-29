# Phase 5: Knowledge Graph Construction

## Objective

Build a knowledge graph connecting articles, entities, topics, and concepts through typed, weighted relationships.

## Input

- `articles` table
- `topics` and `article_topics` tables
- `entities` and `article_entities` tables
- LLM analysis from Phases 2-4

## Graph Node Types

| Node Type | Source | Key Fields |
|-----------|--------|------------|
| `article` | `articles` table | id, title, slug, date |
| `technology` | `topics` (type=technology) | id, name |
| `audience` | `audience_profiles` | id, type, score |
| `campaign` | `campaigns` table | id, name, goal |
| `platform` | Platform names | name |
| `topic` | `topics` table | id, name, type |
| `entity` | `entities` table | id, name, type |
| `product` | `entities` (type=product) | id, name |
| `book_chapter` | `book_mappings` | id, chapter, title |
| `repository` | `repository_mappings` | id, name, url |

## Graph Edge Types (17)

| Edge Type | Source → Target | Weight Meaning |
|-----------|-----------------|----------------|
| `references` | article → article | Citation frequency |
| `expands` | article → article | Depth of expansion |
| `contradicts` | article → article | Strength of contradiction |
| `depends_on` | article → article | Prerequisite strength |
| `introduces` | article → article | Concept introduction |
| `explains` | article → article | Explanation depth |
| `updates` | article → article | Recency/authority |
| `duplicates` | article → article | Content overlap |
| `supports` | article → article | Argument alignment |
| `markets` | article → article | Promotional strength |
| `implements` | article → entity | Implementation depth |
| `mentions` | article → entity | Mention frequency |
| `recommended_after` | article → article | Reading order value |
| `recommended_before` | article → article | Reading order value |
| `related_to` | any → any | General relatedness |
| `derived_from` | article → article | Derivation strength |
| `visualizes` | article → article | Visualization value |

## Relationship Detection

### Deterministic Relationships

```python
def detect_reference_edges(conn):
    """Detect references by analyzing links between articles."""
    articles = conn.execute("SELECT id, links_json FROM articles").fetchall()
    for article in articles:
        links = json.loads(article.links_json or "[]")
        for link in links:
            target_id = lookup_article_by_url(conn, link['href'])
            if target_id:
                insert_relationship(conn, article.id, 'article', target_id, 'article', 'references', 0.8)
```

### LLM-Detected Relationships

```python
RELATIONSHIP_DETECTION_PROMPT = """
Analyze the relationship between these two articles.
Identify all applicable relationship types and their strength.

Article A: {title_a}
Content A: {content_a_summary}

Article B: {title_b}
Content B: {content_b_summary}

Return JSON:
{{
  "relationships": [
    {{
      "type": "expands",
      "weight": 0.8,
      "confidence": 0.9,
      "reasoning": "Article A builds on the foundation laid in Article B..."
    }}
  ]
}}
"""
```

### Topic-Based Relationships

```python
def detect_topic_edges(conn):
    """Articles sharing many topics are related."""
    shared_topics = conn.execute("""
        SELECT a.article_id, b.article_id, COUNT(*) as shared
        FROM article_topics a
        JOIN article_topics b ON a.topic_id = b.topic_id AND a.article_id < b.article_id
        GROUP BY a.article_id, b.article_id
        HAVING shared >= 3
    """).fetchall()
    for a_id, b_id, count in shared_topics:
        weight = min(1.0, count / 10.0)
        insert_relationship(conn, a_id, 'article', b_id, 'article', 'related_to', weight)
```

## Graph Export

Export graph as JSON snapshots for visualization:

```python
def export_graph_snapshot(conn, output_dir: str):
    nodes = []
    edges = []
    # Collect all nodes and edges
    # Write to graph/snapshot_{timestamp}.json
```

## Output

- `relationships` table populated with all edges
- Graph snapshots in `graph/` directory

## Validation

1. Every article has at least 2 outgoing edges
2. No self-referencing edges
3. All edge weights in range 0-1
4. All edges reference valid entities
5. Bidirectional relationships created where appropriate (e.g., `related_to`)
