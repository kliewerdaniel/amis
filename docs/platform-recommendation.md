# Phase 9: Platform Recommendation

## Objective

Score every article against 12 marketing platforms and recommend optimal promotion strategies.

## Supported Platforms

| Platform | Characteristics |
|----------|-----------------|
| `LinkedIn` | Professional, B2B, long-form posts |
| `X` | Short-form, threads, real-time |
| `Dev.to` | Developer-focused, technical content |
| `Hashnode` | Developer blogs, community |
| `Medium` | General audience, paywalled |
| `Hacker News` | Technical, startup, link aggregation |
| `GitHub` | Code, READMEs, documentation |
| `personal_blog` | Full control, SEO, long-form |
| `email_newsletter` | Direct audience, curated content |
| `youtube` | Video content, tutorials |
| `conference_cfp` | Talks, workshops, panels |
| `podcast_pitch` | Audio interviews, discussions |

## Per-Article Output

For each article × platform, generate:

```python
{
    "suitability_score": 0-100,
    "reason": "Why this article fits this platform",
    "optimal_format": "Thread | Article | Video | Talk | Newsletter",
    "posting_frequency": "one-time | weekly | series",
    "ideal_cta": "Read more | Star repo | Buy book | Sign up",
    "audience_match": "Which audience segments are on this platform",
    "competition_estimate": "low | medium | high",
    "expected_roi": "low | medium | high"
}
```

## LLM Prompt Template

```python
PLATFORM_RECOMMENDATION_PROMPT = """
Evaluate this blog article for promotion on {platform}.

Article: {title}
Summary: {summary}
Primary Audience: {primary_audience}
Platform Characteristics: {platform_description}

Return JSON:
{{
  "suitability_score": 0-100,
  "reason": "...",
  "optimal_format": "...",
  "posting_frequency": "...",
  "ideal_cta": "...",
  "audience_match": "...",
  "competition_estimate": "...",
  "expected_roi": "..."
}}
"""
```

## Storage

```python
def store_platform_recommendations(conn, article_id: int, platform: str, data: dict):
    conn.execute("""
        INSERT OR REPLACE INTO platform_recommendations
        (article_id, platform, suitability_score, reason, optimal_format,
         posting_frequency, ideal_cta, audience_match, competition_estimate, expected_roi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (article_id, platform, data['suitability_score'], data['reason'],
          data['optimal_format'], data['posting_frequency'], data['ideal_cta'],
          data['audience_match'], data['competition_estimate'], data['expected_roi']))
```

## Output

- `platform_recommendations` table: 12 rows per article (135 articles × 12 platforms = 1,620 rows)

## Validation

1. Every article has recommendations for all 12 platforms
2. At least one platform per article has score > 60
3. All scores in range 0-100
4. All reason fields populated
