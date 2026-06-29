# Phase 10: Campaign Planner

## Objective

Generate reusable marketing campaigns with structured steps, schedules, and success metrics.

## Campaign Object Model

```python
@dataclass
class Campaign:
    name: str
    goal: str                              # "drive_book_sales", "build_authority", etc.
    audience: str                          # Target audience segment
    book_chapters: list[str]               # Related book chapters
    supporting_articles: list[int]         # Article IDs
    repositories: list[str]                # GitHub repo references
    landing_page: str                      # URL
    call_to_action: str                    # Primary CTA
    platforms: list[str]                   # Target platforms
    publishing_schedule: list[ScheduleEntry]
    estimated_duration_days: int
    estimated_reach: int
    estimated_conversion_rate: float
    dependencies: list[str]
    success_metrics: list[Metric]
    status: str                            # draft, active, completed, archived
```

## Campaign Types

| Type | Description | Goal |
|------|-------------|------|
| `book_launch` | Promote book release | Drive pre-orders/sales |
| `authority_builder` | Establish thought leadership | Grow reputation |
| `community_growth` | Build developer community | GitHub stars, followers |
| `consulting_pipeline` | Generate consulting leads | Client acquisition |
| `content_series` | Multi-part article series | Sustained engagement |
| `product_showcase` | Demo a tool or repo | Adoption, usage |
| `newsletter_growth` | Grow email subscriber list | List building |

## Campaign Generation Prompt

```python
CAMPAIGN_GENERATION_PROMPT = """
Based on the following articles and their marketing scores,
generate a campaign plan to {goal}.

Top Articles:
{top_articles_json}

Target Audience: {audience}
Available Platforms: {platforms}

Return JSON:
{{
  "name": "...",
  "goal": "...",
  "audience": "...",
  "supporting_articles": [article_ids...],
  "platforms": ["..."],
  "publishing_schedule": [
    {{"day": 1, "platform": "...", "article_id": ..., "action": "..."}}
  ],
  "estimated_duration_days": 30,
  "estimated_reach": 10000,
  "estimated_conversion_rate": 0.02,
  "success_metrics": [
    {{"metric": "email_signups", "target": 500}},
    {{"metric": "github_stars", "target": 100}}
  ],
  "steps": [
    {{"order": 1, "type": "publish", "platform": "...", "content_plan": "..."}}
  ]
}}
"""
```

## Storage

```python
def store_campaign(conn, campaign: dict) -> int:
    cursor = conn.execute("""
        INSERT INTO campaigns (name, goal, audience, book_chapters_json,
            supporting_articles_json, repositories_json, landing_page,
            call_to_action, platforms_json, publishing_schedule_json,
            estimated_duration_days, estimated_reach, estimated_conversion_rate,
            dependencies_json, success_metrics_json, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'draft')
    """, (campaign['name'], campaign['goal'], campaign['audience'],
          json.dumps(campaign['book_chapters']),
          json.dumps(campaign['supporting_articles']),
          json.dumps(campaign['repositories']),
          campaign.get('landing_page', ''),
          campaign.get('call_to_action', ''),
          json.dumps(campaign['platforms']),
          json.dumps(campaign['publishing_schedule']),
          campaign['estimated_duration_days'],
          campaign['estimated_reach'],
          campaign['estimated_conversion_rate'],
          json.dumps(campaign.get('dependencies', [])),
          json.dumps(campaign['success_metrics'])))
    campaign_id = cursor.lastrowid

    for step in campaign.get('steps', []):
        conn.execute("""
            INSERT INTO campaign_steps
            (campaign_id, step_order, step_type, platform, article_id, content_plan)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (campaign_id, step['order'], step['type'], step['platform'],
              step.get('article_id'), step.get('content_plan', '')))

    return campaign_id
```

## Auto-Generated Campaigns

The system automatically generates campaigns for:

1. **Book Launch**: Top 10 book-relevant articles → multi-platform campaign
2. **Monthly Authority**: Top 5 authority articles → LinkedIn + newsletter
3. **Developer Community**: Top 5 developer-appeal articles → Dev.to + HN + GitHub
4. **Hidden Gems**: Lowest-platform-recommendation articles with high scores → targeted promotion

## Output

- `campaigns` table with campaign definitions
- `campaign_steps` table with execution steps
- Campaign JSON files in `campaigns/` directory

## Validation

1. Every campaign has at least 3 supporting articles
2. Every campaign has a publishing schedule
3. All article IDs reference valid articles
4. Steps are ordered sequentially
5. Estimated metrics are positive numbers
