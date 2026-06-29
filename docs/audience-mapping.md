# Phase 8: Audience Mapping

## Objective

Classify every article by target audience segments with relevance scores.

## Audience Types

| Audience Type | Description |
|---------------|-------------|
| `beginner` | New to the topic, needs foundational explanation |
| `intermediate` | Has some experience, wants deeper understanding |
| `advanced` | Expert level, wants cutting-edge or novel insights |
| `developer` | Hands-on coder, wants implementation details |
| `architect` | System design, patterns, tradeoffs |
| `cto` | Technical leadership, strategy, ROI |
| `engineering_manager` | Team leadership, process, hiring |
| `founder` | Startup context, MVP, growth, bootstrap |
| `consultant` | Client work, best practices, methodology |
| `researcher` | Academic rigor, novel contributions |
| `student` | Learning, coursework, career prep |
| `enterprise_buyer` | Procurement, compliance, vendor evaluation |

## LLM Prompt Template

```python
AUDIENCE_MAPPING_PROMPT = """
Classify this blog article by target audience.
For each audience type, provide a relevance score (0-100).

Article Title: {title}
Article Content Summary: {content_summary}

Return JSON:
{{
  "audiences": {{
    "beginner": {{"score": 45, "reasoning": "..."}},
    "intermediate": {{"score": 80, "reasoning": "..."}},
    "advanced": {{"score": 60, "reasoning": "..."}},
    "developer": {{"score": 90, "reasoning": "..."}},
    "architect": {{"score": 70, "reasoning": "..."}},
    "cto": {{"score": 30, "reasoning": "..."}},
    "engineering_manager": {{"score": 25, "reasoning": "..."}},
    "founder": {{"score": 50, "reasoning": "..."}},
    "consultant": {{"score": 40, "reasoning": "..."}},
    "researcher": {{"score": 35, "reasoning": "..."}},
    "student": {{"score": 55, "reasoning": "..."}},
    "enterprise_buyer": {{"score": 20, "reasoning": "..."}}
  }}
}}
"""
```

## Storage

```python
def store_audience_profiles(conn, article_id: int, audiences: dict):
    for audience_type, data in audiences.items():
        conn.execute("""
            INSERT OR REPLACE INTO audience_profiles
            (article_id, audience_type, relevance_score, reasoning)
            VALUES (?, ?, ?, ?)
        """, (article_id, audience_type, data['score'], data['reasoning']))
```

## Output

- `audience_profiles` table populated for all articles

## Validation

1. Every article has at least 3 audience profiles
2. At least one audience per article has score > 50
3. All scores in range 0-100
4. All reasoning fields populated
