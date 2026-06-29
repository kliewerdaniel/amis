# Phase 12: Marketing Memory

## Objective

Persist every recommendation with full reasoning trace so future agents can build on prior analysis without regenerating identical reasoning.

## Memory Record Structure

```python
@dataclass
class ReasoningRecord:
    reasoning_type: str       # 'campaign_generation', 'platform_rec', 'ranking', etc.
    entity_type: str          # 'article', 'campaign', 'recommendation'
    entity_id: int            # ID of the related entity
    prompt: str               # Exact prompt sent to LLM
    response: str             # Full LLM response
    model_used: str           # Model identifier
    confidence: float         # 0-1 confidence in this reasoning
    context: dict             # Additional context used
    outcome: str              # 'pending', 'accepted', 'rejected', 'acted_on'
```

## Storage

```python
def store_reasoning(conn, record: ReasoningRecord):
    conn.execute("""
        INSERT INTO reasoning_history
        (reasoning_type, entity_type, entity_id, prompt, response,
         model_used, confidence, context_json, outcome)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (record.reasoning_type, record.entity_type, record.entity_id,
          record.prompt, record.response, record.model_used,
          record.confidence, json.dumps(record.context), record.outcome))
```

## Memory Retrieval

```python
def get_prior_reasoning(conn, entity_type: str, entity_id: int, reasoning_type: str = None):
    """Retrieve prior reasoning for an entity to avoid regeneration."""
    query = "SELECT * FROM reasoning_history WHERE entity_type = ? AND entity_id = ?"
    params = [entity_type, entity_id]
    if reasoning_type:
        query += " AND reasoning_type = ?"
        params.append(reasoning_type)
    query += " ORDER BY timestamp DESC"
    return conn.execute(query, params).fetchall()
```

## Deduplication

Before calling LLM, check if identical reasoning already exists:

```python
def needs_llm_call(conn, entity_type: str, entity_id: int, reasoning_type: str) -> bool:
    """Check if we already have reasoning for this entity."""
    existing = conn.execute("""
        SELECT id FROM reasoning_history
        WHERE entity_type = ? AND entity_id = ? AND reasoning_type = ?
        AND outcome != 'rejected'
        ORDER BY timestamp DESC LIMIT 1
    """, (entity_type, entity_id, reasoning_type)).fetchone()
    return existing is None
```

## Output

- `reasoning_history` table populated with all LLM calls
- Deduplication prevents redundant LLM usage

## Validation

1. Every LLM call is recorded in `reasoning_history`
2. No duplicate reasoning for same entity/type combination
3. All prompts and responses stored (not truncated)
4. Confidence values populated
5. Outcome tracking functional
