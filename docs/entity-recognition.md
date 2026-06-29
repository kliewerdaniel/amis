# Phase 4: Entity Recognition

## Objective

Detect named entities (people, companies, products, technologies, etc.) and record their occurrences and relationships to articles.

## Input

- All rows from `articles` table
- Full article content

## Entity Types

| Type | Description | Examples |
|------|-------------|----------|
| `person` | Individual people | Daniel Kliewer, Andrej Karpathy |
| `company` | Organizations | OpenAI, Google, Microsoft |
| `book` | Published books | "Designing Data-Intensive Applications" |
| `repository` | GitHub repos | `kliewerdaniel/sovereignBank` |
| `product` | Software products | Cursor, VS Code, ChatGPT |
| `technology` | Technologies | Ollama, ChromaDB, SQLite |
| `protocol` | Protocols/standards | MCP, HTTP, WebSocket |
| `standard` | Standards bodies/specs | W3C, OpenAPI |
| `model` | AI models | GPT-4, LLaMA 3, Claude |
| `language` | Programming languages | Python, TypeScript, Rust |
| `library` | Libraries/packages | Pydantic, LangChain |
| `framework` | Frameworks | React, Django, Next.js |
| `api` | API endpoints/services | OpenAI API, Anthropic API |
| `cloud_service` | Cloud services | AWS Lambda, Azure OpenAI |
| `research_paper` | Academic papers | Attention Is All You Need |

## LLM Prompt Template

```python
ENTITY_RECOGNITION_PROMPT = """
Extract all named entities from this blog article.
For each entity, provide its name, type, and a brief description if available.

Article Title: {title}
Article Content:
{content}

Return JSON:
{{
  "entities": [
    {{"name": "...", "type": "person", "description": "..."}},
    {{"name": "...", "type": "technology", "description": "..."}}
  ]
}}
"""
```

## Storage

### Entity Upsert

```python
def upsert_entity(conn, name: str, entity_type: str, description: str = None):
    """Insert entity or update description if exists."""
    conn.execute("""
        INSERT INTO entities (name, entity_type, description)
        VALUES (?, ?, ?)
        ON CONFLICT(name, entity_type) DO UPDATE SET
            description = COALESCE(excluded.description, description)
    """, (name.strip(), entity_type, description))
```

### Article-Entity Mapping

```python
def store_article_entities(conn, article_id: int, entities: list):
    for entity in entities:
        entity_id = upsert_entity(conn, entity['name'], entity['type'], entity.get('description'))
        conn.execute("""
            INSERT OR REPLACE INTO article_entities
            (article_id, entity_id, context, mention_count)
            VALUES (?, ?, ?, ?)
        """, (article_id, entity_id, entity.get('context', ''), 1))
```

## Output

- `entities` table: unique entities with types and descriptions
- `article_entities` table: article-entity mappings with context

## Dependencies

- LLM entity extraction
- Deterministic normalization

## Validation

1. Every article has at least 2 entities
2. No duplicate `(name, entity_type)` pairs
3. All `article_entities` reference valid foreign keys
4. Entity names are trimmed and consistent
