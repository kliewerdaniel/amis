# Phase 15: Agent Interface

## Objective

Expose structured tools for autonomous agents to consume AMIS intelligence. No UI assumptions — pure API.

## Tool Definitions

### find_best_articles()

```python
def find_best_articles(
    platform: str = None,
    audience: str = None,
    topic: str = None,
    limit: int = 10
) -> list[dict]:
    """
    Find best articles matching criteria.

    Args:
        platform: Target platform (LinkedIn, Dev.to, etc.)
        audience: Target audience (developer, cto, etc.)
        topic: Topic filter
        limit: Max results

    Returns:
        List of {id, title, slug, score, reasoning}
    """
```

### generate_campaign()

```python
def generate_campaign(
    goal: str,
    audience: str = None,
    budget: str = None,
    duration_days: int = 30
) -> dict:
    """
    Generate a campaign plan.

    Args:
        goal: Campaign goal (book_sales, authority, community, etc.)
        audience: Target audience
        budget: Budget tier (low, medium, high)
        duration_days: Campaign duration

    Returns:
        Campaign object with steps and schedule
    """
```

### recommend_platform()

```python
def recommend_platform(
    article_id: int,
    top_n: int = 3
) -> list[dict]:
    """
    Get platform recommendations for an article.

    Args:
        article_id: Article ID
        top_n: Number of top platforms to return

    Returns:
        List of {platform, score, reason, format, cta}
    """
```

### rank_articles()

```python
def rank_articles(
    dimension: str = "composite",
    limit: int = 20
) -> list[dict]:
    """
    Rank articles by specified dimension.

    Args:
        dimension: Scoring dimension (composite, marketing, authority, seo, etc.)
        limit: Number of results

    Returns:
        Ranked list of {id, title, slug, score}
    """
```

### find_hidden_gems()

```python
def find_hidden_gems(min_score: float = 70.0) -> list[dict]:
    """Find high-quality articles with low promotion."""
```

### find_duplicate_content()

```python
def find_duplicate_content(threshold: float = 0.85) -> list[dict]:
    """Find duplicate and near-duplicate articles."""
```

### find_missing_topics()

```python
def find_missing_topics() -> list[dict]:
    """Identify topic gaps in the content corpus."""
```

### recommend_book_marketing()

```python
def recommend_book_marketing() -> dict:
    """Get marketing recommendations specifically for book promotion."""
```

### recommend_consulting_content()

```python
def recommend_consulting_content() -> list[dict]:
    """Find articles best suited for consulting lead generation."""
```

### generate_monthly_plan()

```python
def generate_monthly_plan(month: str = None) -> dict:
    """
    Generate a comprehensive monthly marketing plan.

    Returns:
        {
            "month": "2026-07",
            "weekly_plans": [...],
            "campaigns": [...],
            "content_calendar": [...],
            "kpis": [...]
        }
    """
```

## Agent Integration Pattern

```python
# Example: Autonomous agent using AMIS tools
from amis.recommendation_engine import RecommendationEngine
from amis.agent_tools import AMISTools

engine = RecommendationEngine(conn, chroma_client)
tools = AMISTools(engine)

# Agent discovers best content
best = tools.find_best_articles(platform="LinkedIn", limit=5)

# Agent generates campaign
campaign = tools.generate_campaign(goal="book_sales", audience="developers")

# Agent creates monthly plan
plan = tools.generate_monthly_plan()
```

## MCP Server (Optional)

Expose tools via Model Context Protocol for cross-agent interoperability:

```python
# mcp_server.py
from mcp.server import Server
from amis.agent_tools import AMISTools

server = Server("amis")

@server.tool()
async def find_best_articles(platform: str = None, limit: int = 10):
    return tools.find_best_articles(platform=platform, limit=limit)

@server.tool()
async def generate_campaign(goal: str, audience: str = None):
    return tools.generate_campaign(goal=goal, audience=audience)
```

## Output

- `src/recommendations/agent_tools.py` with all tool implementations
- Optional MCP server in `src/mcp_server.py`

## Validation

1. All 10 tools callable with valid arguments
2. All tools return structured JSON-compatible output
3. Tools handle empty results gracefully
4. Tools log reasoning to `reasoning_history`
5. MCP server passes protocol validation
