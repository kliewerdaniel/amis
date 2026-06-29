# API Reference

## Database Layer

### `src/db/connection.py`

```python
def get_connection(db_path: str = "database/sqlite.db") -> sqlite3.Connection:
    """Get SQLite connection with WAL mode and foreign keys enabled."""

def init_database(db_path: str) -> sqlite3.Connection:
    """Initialize database with schema. Idempotent."""
```

### `src/db/migrations.py`

```python
def get_current_version(conn: sqlite3.Connection) -> int:
    """Get current schema version."""

def apply_migrations(conn: sqlite3.Connection, migrations_dir: str):
    """Apply all pending migrations."""
```

## Ingestion Layer

### `src/ingestion/parser.py`

```python
def parse_markdown(file_path: Path) -> dict:
    """
    Parse a single markdown file.

    Returns:
        {
            "filename": str,
            "slug": str,
            "title": str,
            "content": str,
            "frontmatter": dict,
            "headings": list[dict],
            "images": list[dict],
            "links": list[dict],
            "code_blocks": list[dict],
            "references": list[dict],
            "word_count": int,
            "reading_time_minutes": int,
            "publication_date": str,
            "ingestion_hash": str
        }
    """

def discover_files(content_dir: str) -> list[Path]:
    """Find all ingestible markdown files."""
```

### `src/ingestion/normalizer.py`

```python
def normalize_article(parsed: dict) -> dict:
    """Normalize parsed markdown into database-ready format."""

def upsert_article(conn: sqlite3.Connection, article: dict):
    """Insert or update article. Idempotent by filename."""
```

## Analysis Layer

### `src/analysis/semantic.py`

```python
def analyze_article(conn: sqlite3.Connection, llm_client, article_id: int):
    """Run full semantic analysis on an article."""

def already_scored(conn: sqlite3.Connection, article_id: int, score_type: str) -> bool:
    """Check if article already has scores of this type."""

def store_scores(conn: sqlite3.Connection, article_id: int, result: dict):
    """Store semantic analysis scores."""
```

### `src/analysis/topics.py`

```python
def extract_topics(conn: sqlite3.Connection, llm_client, article_id: int):
    """Extract and store topics for an article."""

def upsert_topic(conn: sqlite3.Connection, name: str, topic_type: str) -> int:
    """Insert or get existing topic. Returns topic ID."""
```

### `src/analysis/entities.py`

```python
def extract_entities(conn: sqlite3.Connection, llm_client, article_id: int):
    """Extract and store entities for an article."""

def upsert_entity(conn: sqlite3.Connection, name: str, entity_type: str, description: str = None) -> int:
    """Insert or get existing entity. Returns entity ID."""
```

## Graph Layer

### `src/graph/builder.py`

```python
def build_graph(conn: sqlite3.Connection):
    """Build complete knowledge graph."""

def detect_relationships(conn: sqlite3.Connection, article_id: int):
    """Detect all relationships for a specific article."""

def insert_relationship(conn, source_id: int, source_type: str,
                       target_id: int, target_type: str,
                       rel_type: str, weight: float, confidence: float = None,
                       reasoning: str = None):
    """Insert a relationship edge."""

def export_graph_snapshot(conn: sqlite3.Connection, output_dir: str):
    """Export graph as JSON snapshot."""
```

### `src/graph/duplicates.py`

```python
def find_exact_duplicates(conn: sqlite3.Connection) -> list[tuple]:
    """Find articles with identical content hashes."""

def find_near_duplicates(chroma_client, threshold: float = 0.92) -> list[tuple]:
    """Find articles with high semantic similarity."""

def find_outdated_content(conn: sqlite3.Connection, llm_client) -> list[dict]:
    """Identify potentially outdated articles."""
```

## Marketing Layer

### `src/marketing/ranking.py`

```python
def compute_marketing_scores(conn: sqlite3.Connection):
    """Compute all marketing ranking dimensions."""

def get_article_ranking(conn: sqlite3.Connection, dimension: str = "composite", limit: int = 20) -> list[dict]:
    """Get ranked list of articles."""

def compute_composite_score(scores: dict) -> float:
    """Calculate weighted composite score."""
```

### `src/marketing/audiences.py`

```python
def map_audiences(conn: sqlite3.Connection, llm_client, article_id: int):
    """Map article to audience segments."""

def get_audience_articles(conn: sqlite3.Connection, audience_type: str) -> list[dict]:
    """Get all articles relevant to an audience."""
```

### `src/marketing/platforms.py`

```python
def recommend_platforms(conn: sqlite3.Connection, llm_client, article_id: int):
    """Generate platform recommendations for an article."""

def get_platform_articles(conn: sqlite3.Connection, platform: str, limit: int = 10) -> list[dict]:
    """Get top articles for a specific platform."""
```

### `src/marketing/campaigns.py`

```python
def generate_campaign(conn: sqlite3.Connection, llm_client, goal: str, **kwargs) -> int:
    """Generate a campaign plan. Returns campaign ID."""

def get_active_campaigns(conn: sqlite3.Connection) -> list[dict]:
    """Get all active campaigns."""

def update_campaign_status(conn: sqlite3.Connection, campaign_id: int, status: str):
    """Update campaign status."""
```

### `src/marketing/repurposing.py`

```python
def generate_repurposing(conn: sqlite3.Connection, llm_client, article_id: int):
    """Generate content repurposing recommendations."""

def get_repurposing_options(conn: sqlite3.Connection, article_id: int) -> list[dict]:
    """Get repurposing options for an article."""
```

## Memory Layer

### `src/memory/reasoning.py`

```python
def store_reasoning(conn: sqlite3.Connection, record: dict):
    """Store a reasoning record."""

def get_prior_reasoning(conn: sqlite3.Connection, entity_type: str, entity_id: int,
                       reasoning_type: str = None) -> list[dict]:
    """Retrieve prior reasoning for an entity."""

def needs_llm_call(conn: sqlite3.Connection, entity_type: str, entity_id: int,
                  reasoning_type: str) -> bool:
    """Check if LLM call is needed (no prior reasoning exists)."""
```

## LLM Layer

### `src/llm/client.py`

```python
class LLMClient:
    def __init__(self, provider: str = "ollama", model: str = "llama3.1:8b",
                 base_url: str = "http://localhost:11434"):
        """Initialize LLM client."""

    def complete(self, prompt: str, temperature: float = 0.3) -> str:
        """Get text completion."""

    def complete_json(self, prompt: str, temperature: float = 0.3) -> dict:
        """Get JSON completion with parsing."""
```

### `src/llm/prompts.py`

All prompt templates stored as constants:

```python
SEMANTIC_ANALYSIS_PROMPT = "..."
TOPIC_EXTRACTION_PROMPT = "..."
ENTITY_RECOGNITION_PROMPT = "..."
RELATIONSHIP_DETECTION_PROMPT = "..."
AUDIENCE_MAPPING_PROMPT = "..."
PLATFORM_RECOMMENDATION_PROMPT = "..."
CAMPAIGN_GENERATION_PROMPT = "..."
REPURPOSING_PROMPT = "..."
OUTDATED_DETECTION_PROMPT = "..."
IDEA_OVERLAP_PROMPT = "..."
WEEKLY_REPORT_PROMPT = "..."
```

## Recommendation Engine

### `src/recommendations/engine.py`

```python
class RecommendationEngine:
    def __init__(self, conn: sqlite3.Connection, chroma_client):
        """Initialize engine."""

    def best_article_today(self) -> dict
    def best_for_linkedin(self) -> list[dict]
    def best_for_executives(self) -> list[dict]
    def best_book_seller(self) -> list[dict]
    def most_evergreen(self) -> list[dict]
    def highest_authority(self) -> list[dict]
    def most_underutilized(self) -> list[dict]
    def best_hidden_gems(self) -> list[dict]
    def best_followup(self) -> list[dict]
    def needs_update(self) -> list[dict]
    def highest_roi_campaign(self) -> list[dict]
```

### `src/recommendations/agent_tools.py`

```python
class AMISTools:
    def __init__(self, engine: RecommendationEngine):
        """Initialize with engine instance."""

    def find_best_articles(self, platform=None, audience=None, topic=None, limit=10) -> list[dict]
    def generate_campaign(self, goal, audience=None, budget=None, duration_days=30) -> dict
    def recommend_platform(self, article_id, top_n=3) -> list[dict]
    def rank_articles(self, dimension="composite", limit=20) -> list[dict]
    def find_hidden_gems(self, min_score=70.0) -> list[dict]
    def find_duplicate_content(self, threshold=0.85) -> list[dict]
    def find_missing_topics(self) -> list[dict]
    def recommend_book_marketing(self) -> dict
    def recommend_consulting_content(self) -> list[dict]
    def generate_monthly_plan(self, month=None) -> dict
```

## Autonomous Loop

### `src/loop/autonomous.py`

```python
def run_nightly_pipeline():
    """Execute the complete nightly processing pipeline."""

def ingest_new_content(conn, content_dir: str) -> int:
    """Ingest new/changed files. Returns count."""

def detect_changes(conn) -> list[dict]:
    """Find articles changed since last run."""

def update_scores(conn, llm_client, changed: list[dict]):
    """Re-score changed articles."""

def suggest_campaigns(conn, llm_client):
    """Generate new campaign suggestions."""

def generate_weekly_report(conn, llm_client) -> str:
    """Generate weekly summary report."""

def recommend_actions(conn, llm_client) -> list[dict]:
    """Prioritize pending recommendations."""
```
