# Testing Strategy

## Test Levels

### 1. Unit Tests

Test individual functions in isolation.

```
tests/
├── test_ingestion/
│   ├── test_parser.py
│   ├── test_normalizer.py
│   └── test_date_parsing.py
├── test_analysis/
│   ├── test_semantic.py
│   ├── test_topics.py
│   └── test_entities.py
├── test_graph/
│   ├── test_builder.py
│   └── test_duplicates.py
├── test_marketing/
│   ├── test_ranking.py
│   ├── test_audiences.py
│   ├── test_platforms.py
│   ├── test_campaigns.py
│   └── test_repurposing.py
├── test_recommendations/
│   ├── test_engine.py
│   └── test_agent_tools.py
└── test_db/
    ├── test_connection.py
    └── test_migrations.py
```

### 2. Integration Tests

Test phase pipelines end-to-end with test data.

```
tests/integration/
├── test_ingestion_pipeline.py
├── test_analysis_pipeline.py
├── test_graph_pipeline.py
├── test_marketing_pipeline.py
└── test_full_pipeline.py
```

### 3. Validation Tests

Verify data integrity across all tables.

```
tests/validation/
├── test_article_integrity.py
├── test_score_ranges.py
├── test_relationship_integrity.py
├── test_campaign_integrity.py
└── test_referential_integrity.py
```

## Test Data

Use a small subset of the blog for testing:

```
tests/fixtures/
├── articles/
│   ├── 2025-11-02-rise-of-vibe-coding.md
│   ├── 2026-06-14-sovereign-memory-bank-a-deep-dive-into-autonomous-cognitive-memory-for-agent-systems.md
│   └── 2024-12-01-basic-rag.md
└── expected/
    ├── parsed_articles.json
    ├── expected_scores.json
    └── expected_relationships.json
```

## Key Test Cases

### Ingestion

| Test | Expected |
|------|----------|
| Parse valid markdown file | Correct fields extracted |
| Parse file with no frontmatter | Filename used as title |
| Parse file with missing date | Date extracted from filename |
| Parse `temp.md` | Excluded from ingestion |
| Ingest same file twice | Idempotent, no duplicates |
| Ingest 135 blog posts | All ingested without errors |

### Analysis

| Test | Expected |
|------|----------|
| Semantic analysis produces 27 scores | All scores 0-100 |
| Topic extraction produces ≥3 topics | All normalized |
| Entity extraction produces ≥2 entities | All types valid |
| Analysis with mock LLM | Deterministic output |
| Re-analysis of same article | Scores replaced, not duplicated |

### Graph

| Test | Expected |
|------|----------|
| Reference detection via links | Correct edges created |
| Topic-based related_to edges | Weight scales with shared topics |
| No self-referencing edges | Verified |
| Export graph snapshot | Valid JSON output |

### Marketing

| Test | Expected |
|------|----------|
| Composite score calculation | Weighted average correct |
| Platform recommendations × 12 | All platforms covered |
| Audience mapping × 12 | All audiences covered |
| Campaign generation | Valid structure with steps |

### Recommendations

| Test | Expected |
|------|----------|
| best_article_today returns 1 result | Has title and score |
| best_for_linkedin returns ≤10 | Sorted by score desc |
| find_hidden_gems filters correctly | Score > 70, low platform count |

### Agent Tools

| Test | Expected |
|------|----------|
| All 10 tools callable | No exceptions |
| Tools return JSON-serializable output | Valid dict/list |
| Tools handle empty database | Graceful empty results |

## Running Tests

```bash
# Unit tests
pytest tests/ -v

# Integration tests
pytest tests/integration/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific phase
pytest tests/test_ingestion/ -v
```

## Mock Strategy

LLM calls mocked in unit tests:

```python
@pytest.fixture
def mock_llm():
    client = MockLLMClient()
    client.set_response("semantic_analysis", MOCK_SEMANTIC_RESPONSE)
    client.set_response("topic_extraction", MOCK_TOPIC_RESPONSE)
    client.set_response("entity_recognition", MOCK_ENTITY_RESPONSE)
    return client
```

## CI/CD

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v --cov=src
```
