# Phase 11: Content Repurposing

## Objective

Identify how each article can be transformed into other content formats and generate transformation recommendations.

## Target Formats

| Format | Description | Transformation |
|--------|-------------|----------------|
| `linkedin_article` | Long-form LinkedIn post | Condense, professional tone |
| `technical_thread` | X/Twitter thread | Break into 10-15 tweets |
| `newsletter` | Email newsletter section | Curate, add commentary |
| `conference_talk` | Conference presentation | Outline slides, talking points |
| `workshop` | Hands-on workshop | Step-by-step exercises |
| `podcast_pitch` | Podcast guest pitch | Episode outline, talking points |
| `video_script` | YouTube video script | Visual narrative, B-roll suggestions |
| `github_readme` | GitHub README section | Technical docs, code examples |
| `whitepaper` | Formal whitepaper | In-depth analysis, citations |
| `book_chapter` | Book chapter draft | Expanded version with exercises |

## LLM Prompt Template

```python
REPURPOSING_PROMPT = """
Analyze this blog article and recommend content repurposing opportunities.

Article: {title}
Content Summary: {summary}
Marketing Scores: {scores_json}
Platform Recommendations: {platform_recs_json}

For each target format, provide:
- Suitability score (0-100)
- Transformation notes
- Estimated effort (low/medium/high)

Return JSON:
{{
  "repurposing": [
    {{
      "format": "linkedin_article",
      "suitability_score": 85,
      "transformation_notes": "Condense the technical deep-dive into 5 key insights...",
      "estimated_effort": "medium"
    }}
  ]
}}
"""
```

## Storage

```python
def store_repurposing(conn, article_id: int, recommendations: list):
    for rec in recommendations:
        conn.execute("""
            INSERT INTO content_repurposing
            (article_id, target_format, suitability_score, transformation_notes, estimated_effort)
            VALUES (?, ?, ?, ?, ?)
        """, (article_id, rec['format'], rec['suitability_score'],
              rec['transformation_notes'], rec['estimated_effort']))
```

## Output

- `content_repurposing` table: 10 rows per article (135 × 10 = 1,350 rows)

## Validation

1. Every article has repurposing recommendations for all 10 formats
2. At least 3 formats per article have score > 50
3. All transformation notes populated
4. Effort levels are valid (low/medium/high)
