# AMIS - Agentic Marketing Intelligence System

## Implementation Guide

This documentation provides a complete blueprint for building AMIS — an autonomous marketing intelligence platform that ingests Markdown blog posts and transforms them into a continuously improving marketing knowledge graph.

### Documentation Structure

| File | Description |
|------|-------------|
| [architecture.md](architecture.md) | System architecture, tech stack, directory layout, and design principles |
| [database.md](database.md) | Complete SQLite schema with all 15+ tables and relationships |
| [ingestion.md](ingestion.md) | Phase 1: Markdown parsing and normalization pipeline |
| [semantic-analysis.md](semantic-analysis.md) | Phase 2: LLM-powered article scoring across 27 dimensions |
| [topic-extraction.md](topic-extraction.md) | Phase 3: Taxonomy extraction (topics, technologies, concepts) |
| [entity-recognition.md](entity-recognition.md) | Phase 4: Named entity recognition and relationship mapping |
| [knowledge-graph.md](knowledge-graph.md) | Phase 5: Graph construction with 17 relationship types |
| [duplicate-detection.md](duplicate-detection.md) | Phase 6: Duplicate and near-duplicate content detection |
| [marketing-ranking.md](marketing-ranking.md) | Phase 7: Multi-dimensional marketing score computation |
| [audience-mapping.md](audience-mapping.md) | Phase 8: Audience persona classification |
| [platform-recommendation.md](platform-recommendation.md) | Phase 9: Platform suitability scoring and recommendations |
| [campaign-planner.md](campaign-planner.md) | Phase 10: Campaign plan generation and management |
| [content-repurposing.md](content-repurposing.md) | Phase 11: Cross-platform content transformation recommendations |
| [marketing-memory.md](marketing-memory.md) | Phase 12: Persistent reasoning and recommendation history |
| [analytics.md](analytics.md) | Phase 13: Analytics schema for future metrics import |
| [recommendation-engine.md](recommendation-engine.md) | Phase 14: Queryable recommendation engine |
| [agent-interface.md](agent-interface.md) | Phase 15: Structured tool/API interface for agents |
| [autonomous-loop.md](autonomous-loop.md) | Phase 16: Nightly autonomous processing pipeline |
| [api-reference.md](api-reference.md) | Complete Python API reference for all public functions |
| [data-flow.md](data-flow.md) | End-to-end data flow diagrams |
| [testing.md](testing.md) | Testing strategy and validation approach |

### Quick Start

1. Read `architecture.md` for the full system design
2. Start implementation with `ingestion.md` (Phase 1)
3. Follow phases sequentially — each builds on the prior
4. Reference `database.md` for schema at any point
5. Use `api-reference.md` for function signatures and contracts

### Tech Stack

- **Language**: Python 3.11+
- **Structured Storage**: SQLite via `sqlite3` (stdlib)
- **Semantic Search**: ChromaDB
- **Graph Relationships**: SQLite (adjacency list model)
- **LLM Reasoning**: Ollama (local) or OpenAI-compatible API
- **Markdown Parsing**: `markdown-it-py` + `python-frontmatter`
- **Embeddings**: Sentence Transformers (local) or OpenAI embeddings

### Implementation Order

```
Phase 1  → Ingestion         (no dependencies)
Phase 2  → Semantic Analysis  (requires Phase 1)
Phase 3  → Topic Extraction   (requires Phase 1)
Phase 4  → Entity Recognition (requires Phase 1)
Phase 5  → Knowledge Graph    (requires Phases 2-4)
Phase 6  → Duplicate Detection (requires Phases 1, 5)
Phase 7  → Marketing Ranking  (requires Phases 2, 3, 5)
Phase 8  → Audience Mapping   (requires Phases 2, 3)
Phase 9  → Platform Recs      (requires Phases 7, 8)
Phase 10 → Campaign Planner   (requires Phases 7, 8, 9)
Phase 11 → Content Repurposing (requires Phases 3, 5, 7)
Phase 12 → Marketing Memory   (requires all prior phases)
Phase 13 → Analytics Schema   (standalone, schema-only)
Phase 14 → Recommendation Eng (requires all prior phases)
Phase 15 → Agent Interface    (requires all prior phases)
Phase 16 → Autonomous Loop    (requires all prior phases)
```

### Blog Content

The `blog/` folder contains 135 Markdown posts spanning Oct 2024 – Jun 2026, covering:
- AI agents and autonomous systems
- Local LLM integration (Ollama, llama.cpp)
- Vibe coding and AI-assisted development
- Knowledge graphs and RAG
- Sovereign/spec-driven development
- Full-stack development (Next.js, Django, React)
- Digital resurrection and cognitive memory

These serve as the canonical input corpus for ingestion.
