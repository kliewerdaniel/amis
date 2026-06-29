# Phase 7: Marketing Ranking

## Objective

Compute composite marketing scores across 12 dimensions and produce an overall ranking for every article.

## Scoring Dimensions

| Dimension | Weight | Components |
|-----------|--------|------------|
| `marketing_score` | 0.20 | marketing_value, virality_potential, seo_potential |
| `authority_score` | 0.15 | authority_score, practicality, originality |
| `trust_score` | 0.10 | confidence, educational_value, evergreen_score |
| `book_conversion_score` | 0.15 | book_relevance, educational_value, authority_score |
| `seo_score` | 0.10 | seo_potential, evergreen_score, word_count |
| `evergreen_score` | 0.05 | evergreen_score, trend_inverse |
| `shareability` | 0.10 | virality_potential, marketing_value |
| `conference_potential` | 0.05 | authority_score, practicality, originality |
| `podcast_potential` | 0.05 | executive_appeal, topic_breadth |
| `newsletter_potential` | 0.05 | educational_value, practicality |
| `developer_community_potential` | - | developer_appeal, github_relevance |
| `enterprise_decision_maker_potential` | - | enterprise_appeal, executive_appeal |

## Composite Score Formula

```python
def compute_composite_score(scores: dict) -> float:
    """Weighted average of all marketing dimensions."""
    weights = {
        'marketing_score': 0.20,
        'authority_score': 0.15,
        'trust_score': 0.10,
        'book_conversion_score': 0.15,
        'seo_score': 0.10,
        'evergreen_score': 0.05,
        'shareability': 0.10,
        'conference_potential': 0.05,
        'podcast_potential': 0.05,
        'newsletter_potential': 0.05,
    }
    total = sum(scores.get(k, 0) * v for k, v in weights.items())
    return round(total, 2)
```

## Ranking Query

```sql
SELECT
    a.id, a.title, a.slug,
    AVG(CASE WHEN s.metric_name = 'marketing_value' THEN s.score_value END) as marketing_score,
    AVG(CASE WHEN s.metric_name = 'authority_score' THEN s.score_value END) as authority_score,
    AVG(CASE WHEN s.metric_name = 'book_relevance' THEN s.score_value END) as book_conversion_score,
    AVG(CASE WHEN s.metric_name = 'seo_potential' THEN s.score_value END) as seo_score,
    AVG(CASE WHEN s.metric_name = 'evergreen_score' THEN s.score_value END) as evergreen_score,
    AVG(CASE WHEN s.metric_name = 'virality_potential' THEN s.score_value END) as shareability,
    AVG(CASE WHEN s.metric_name = 'practicality' THEN s.score_value END) as conference_potential,
    AVG(CASE WHEN s.metric_name = 'educational_value' THEN s.score_value END) as newsletter_potential
FROM articles a
JOIN scores s ON a.id = s.article_id
WHERE s.score_type = 'semantic'
GROUP BY a.id
ORDER BY composite_score DESC;
```

## Output

- Updated `scores` table with computed marketing dimensions
- `recommendations` table with top articles per dimension

## Validation

1. Every article has a composite score
2. Scores are in valid ranges
3. Ranking order is deterministic
4. Top 10 articles manually reviewed for sanity
