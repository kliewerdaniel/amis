# System Architecture

## Vision

AMIS is a reasoning engine, not a content generator. It ingests a corpus of Markdown blog posts and builds a continuously improving marketing knowledge graph capable of planning, ranking, recommending, and generating marketing campaigns for a technical book and related engineering work.

## Design Principles

| Principle | Rationale |
|-----------|-----------|
| **Local-first** | No cloud dependencies for core operation |
| **Markdown is source of truth** | All intelligence derives from authored content |
| **SQLite for structured persistence** | Single-file, zero-config, portable database |
| **ChromaDB for semantic retrieval** | Vector similarity search for semantic queries |
| **Graph relationships stored separately** | Adjacency list in SQLite, not embedded in documents |
| **Deterministic ingestion** | Same input always produces same output |
| **LLM only where reasoning is required** | Parse deterministically, reason with LLM selectively |
| **Every inference stored** | All LLM outputs persisted with reasoning trace |
| **Idempotent ingestion** | Re-running ingestion overwrites stale data safely |

## Directory Layout

```
amis/
├── blog/                          # Source markdown corpus (moved here)
├── content/
│   └── posts/                     # Symlinked or copied blog posts
├── database/
│   └── sqlite.db                  # All structured data
├── chroma/                        # ChromaDB vector store
├── graph/                         # Exported graph snapshots
├── campaigns/                     # Generated campaign JSON files
├── analytics/                     # Imported analytics data
├── generated/                     # LLM-generated content artifacts
├── configs/                       # System configuration
├── logs/                          # Processing logs
├── docs/                          # This documentation
└── src/
    ├── __init__.py
    ├── cli.py                     # CLI entry point
    ├── config.py                  # Configuration management
    ├── ingestion/                 # Phase 1
    │   ├── __init__.py
    │   ├── parser.py              # Markdown parsing
    │   └── normalizer.py          # Document normalization
    ├── analysis/                  # Phases 2-4
    │   ├── __init__.py
    │   ├── semantic.py            # Phase 2: Semantic scoring
    │   ├── topics.py              # Phase 3: Topic extraction
    │   └── entities.py            # Phase 4: Entity recognition
    ├── graph/                     # Phases 5-6
    │   ├── __init__.py
    │   ├── builder.py             # Phase 5: Graph construction
    │   └── duplicates.py          # Phase 6: Duplicate detection
    ├── marketing/                 # Phases 7-11
    │   ├── __init__.py
    │   ├── ranking.py             # Phase 7: Marketing ranking
    │   ├── audiences.py           # Phase 8: Audience mapping
    │   ├── platforms.py           # Phase 9: Platform recommendations
    │   ├── campaigns.py           # Phase 10: Campaign planner
    │   └── repurposing.py         # Phase 11: Content repurposing
    ├── memory/                    # Phase 12
    │   ├── __init__.py
    │   └── reasoning.py           # Marketing memory persistence
    ├── analytics/                 # Phase 13
    │   ├── __init__.py
    │   └── schema.py              # Analytics tables + import
    ├── recommendations/           # Phases 14-15
    │   ├── __init__.py
    │   ├── engine.py              # Phase 14: Recommendation engine
    │   └── agent_tools.py         # Phase 15: Agent interface
    ├── loop/                      # Phase 16
    │   ├── __init__.py
    │   └── autonomous.py          # Nightly processing loop
    ├── llm/                       # LLM abstraction layer
    │   ├── __init__.py
    │   ├── client.py              # Ollama/OpenAI-compatible client
    │   ├── prompts.py             # All prompt templates
    │   └── structured.py          # Structured output parsing
    └── db/                        # Database layer
        ├── __init__.py
        ├── connection.py          # SQLite connection management
        ├── migrations.py          # Schema versioning
        └── queries.py             # Common query helpers
├── tests/                         # Test suite
├── pyproject.toml                 # Project metadata + dependencies
└── README.md
```

## Data Flow Summary

```
Markdown Files
      │
      ▼
┌─────────────┐
│  Ingestion   │  Phase 1: Parse, normalize, store
└──────┬──────┘
       │
       ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Semantic    │    │   Topics    │    │  Entities   │  Phases 2-4
│  Analysis    │    │  Extraction │    │  Recognition│  (parallel)
└──────┬──────┘    └──────┬──────┘    └──────┬──────┘
       │                  │                   │
       └──────────────────┼───────────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Knowledge   │  Phase 5: Build graph
                   │    Graph     │
                   └──────┬──────┘
                          │
           ┌──────────────┼──────────────┐
           │              │              │
           ▼              ▼              ▼
    ┌────────────┐ ┌────────────┐ ┌────────────┐
    │ Duplicate  │ │ Marketing  │ │ Audience   │  Phases 6-8
    │ Detection  │ │  Ranking   │ │  Mapping   │
    └─────┬──────┘ └─────┬──────┘ └─────┬──────┘
          │              │              │
          └──────────────┼──────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Platform Recs +    │  Phases 9-11
              │  Campaigns +        │
              │  Repurposing        │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Memory + Recommend │  Phases 12-14
              │  + Agent Interface  │
              └──────────┬──────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  Autonomous Loop    │  Phase 16
              └─────────────────────┘
```

## Configuration

All configuration stored in `configs/amis.yaml`:

```yaml
paths:
  content_dir: content/posts
  db_path: database/sqlite.db
  chroma_dir: chroma
  graph_dir: graph
  campaigns_dir: campaigns
  analytics_dir: analytics
  generated_dir: generated
  logs_dir: logs

llm:
  provider: ollama          # or openai
  model: llama3.1:8b
  base_url: http://localhost:11434
  temperature: 0.3
  max_tokens: 4096

embedding:
  provider: sentence-transformers
  model: all-MiniLM-L6-v2

ingestion:
  batch_size: 10
  overwrite_existing: true
  extract_images: true
  extract_code_blocks: true

analysis:
  parallel_scoring: true
  confidence_threshold: 0.7
  max_retries: 2
```
