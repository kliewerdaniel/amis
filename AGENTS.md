# AMIS - Agentic Marketing Intelligence System

## Current State (June 30, 2026)

### Pipeline Complete - All 134 Articles Processed

| Phase | Coverage | Notes |
|-------|----------|-------|
| Ingestion | 134 articles | All blog posts ingested |
| Semantic Analysis | 102/134 (76%) | 32 skipped (score < threshold) |
| Topic Extraction | 131/134 (98%) | ~3 articles failed |
| Entity Recognition | 87/134 (65%) | Model struggles with entity extraction |
| Audience Mapping | 134/134 (100%) | Perfect |
| Platform Recommendations | 134/134 (100%) | 1560 recs across 12 platforms |
| Content Repurposing | 131/134 (98%) | ~3 failed |
| Knowledge Graph | 1763 edges | 9 reference + 1403 topic + 351 entity |
| Marketing Rankings | 1122 scores, 102 articles | Only scored articles ranked |
| Campaigns | 4 generated | promote_top_content, repurpose, audiences, cross-promote |
| Graph Export | 680KB JSON snapshot | `graph/snapshot_20260630_012851.json` |

### Key Fixes Made

1. **LLM Prompts** (`src/llm/prompts.py`): All prompts start with `_JSON_FIRST = "Respond with ONLY valid JSON."` to prevent `llama3.1:8b` from returning conversational text instead of JSON.

2. **LLM Client** (`src/llm/client.py`): Added `import re`, improved `_extract_json()` to clean trailing commas before parsing.

3. **Platforms Store** (`src/marketing/platforms.py`): Added `_safe_str()` and `_safe_int()` helpers to prevent `"type 'dict' is not supported"` SQLite errors when the model returns nested objects instead of primitives.

### Model
- **Active**: `llama3.1:8b` (Ollama, localhost:11434)
- **Inactive**: `qwen2.5-coder:32b` (too heavy for this machine), `llama3.2:1b` (too weak)
- **Embeddings**: `nomic-embed-text:latest`
- Config: temperature 0.1, max_tokens 4096
- Endpoint: `/api/generate` (not chat endpoint - better JSON compliance)

### Database
- `database/sqlite.db` (~15MB)
- Key tables: articles (134), scores (3060), topics (3725), article_topics (5083), entities (390), article_entities (498), audience_profiles (1607), platform_recommendations (1560), content_repurposing (1254), relationships (1759), campaigns (4), campaign_steps (6)

### Next Steps
1. Export campaign data for marketing use
2. Review the 32 articles that didn't get semantic scores (score < threshold)
3. Consider bumping entity extraction success rate
4. Generate marketing reports from the graph/export data
