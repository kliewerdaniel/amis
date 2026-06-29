# Phase 14: Recommendation Engine

## Objective

Provide a queryable recommendation engine answering marketing strategy questions with ranked results.

## Supported Queries

| Query | Description | Returns |
|-------|-------------|---------|
| `best_article_today` | Best article to promote right now | Top article + reasoning |
| `best_for_linkedin` | Best article for LinkedIn | Ranked list |
| `best_for_executives` | Best article for executive audience | Ranked list |
| `best_book_seller` | Best article to drive book sales | Ranked list |
| `most_evergreen` | Most timeless content | Ranked list |
| `highest_authority` | Highest authority score | Ranked list |
| `most_underutilized` | High score but low promotion | Ranked list |
| `best_hidden_gem` | High quality, low visibility | Ranked list |
| `best_followup` | Best article to write next | Gap analysis |
| `needs_update` | Article requiring refresh | Ranked list |
| `highest_roi_campaign` | Best ROI campaign | Ranked list |

## Implementation

```python
class RecommendationEngine:
    def __init__(self, conn, chroma_client):
        self.conn = conn
        self.chroma = chroma_client

    def best_article_today(self) -> dict:
        """Composite score weighted by recency."""
        return self.conn.execute("""
            SELECT a.id, a.title, a.slug, a.publication_date,
                s.score_value as composite_score
            FROM articles a
            JOIN (
                SELECT article_id,
                    SUM(score_value * CASE metric_name
                        WHEN 'marketing_value' THEN 0.3
                        WHEN 'virality_potential' THEN 0.25
                        WHEN 'seo_potential' THEN 0.2
                        WHEN 'evergreen_score' THEN 0.15
                        WHEN 'authority_score' THEN 0.1
                    END) as weighted_score
                FROM scores WHERE score_type = 'semantic'
                GROUP BY article_id
            ) s ON a.id = s.article_id
            ORDER BY s.weighted_score DESC
            LIMIT 1
        """).fetchone()

    def best_for_linkedin(self) -> list:
        """Articles with highest LinkedIn suitability."""
        return self.conn.execute("""
            SELECT a.id, a.title, pr.suitability_score, pr.reason
            FROM articles a
            JOIN platform_recommendations pr ON a.id = pr.article_id
            WHERE pr.platform = 'LinkedIn'
            ORDER BY pr.suitability_score DESC
            LIMIT 10
        """).fetchall()

    def best_hidden_gems(self) -> list:
        """High-scoring articles with low platform recommendations."""
        return self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                AVG(s.score_value) as avg_score,
                COUNT(pr.id) as platform_count
            FROM articles a
            JOIN scores s ON a.id = s.article_id
            LEFT JOIN platform_recommendations pr ON a.id = pr.article_id
            WHERE s.score_type = 'semantic'
            GROUP BY a.id
            HAVING avg_score > 70 AND platform_count < 5
            ORDER BY avg_score DESC
            LIMIT 10
        """).fetchall()

    def most_underutilized(self) -> list:
        """High quality articles not yet promoted."""
        return self.conn.execute("""
            SELECT a.id, a.title, a.slug,
                AVG(s.score_value) as avg_score
            FROM articles a
            JOIN scores s ON a.id = s.article_id
            WHERE s.score_type = 'semantic'
            AND a.id NOT IN (
                SELECT DISTINCT article_id FROM analytics
                WHERE metric_type IN ('views', 'clicks', 'shares')
            )
            GROUP BY a.id
            HAVING avg_score > 60
            ORDER BY avg_score DESC
            LIMIT 10
        """).fetchall()
```

## Output

- `recommendations` table populated with query results
- Each recommendation includes reasoning and confidence

## Validation

1. All 11 query types produce results
2. Recommendations include reasoning text
3. Confidence scores populated
4. Results are deterministic
