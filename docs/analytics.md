# Phase 13: Analytics Schema

## Objective

Define analytics tables for future metrics import. Schema-only implementation — no data generation.

## Metrics Schema

### Supported Metric Types

| Metric Type | Description | Unit |
|-------------|-------------|------|
| `views` | Page views | count |
| `clicks` | Link clicks | count |
| `shares` | Social shares | count |
| `comments` | Comment count | count |
| `ctr` | Click-through rate | percentage |
| `conversions` | Goal completions | count |
| `book_sales` | Book purchases | count |
| `email_signups` | Newsletter subscriptions | count |
| `github_stars` | Repository stars | count |
| `downloads` | File/resource downloads | count |
| `time_on_page` | Average time on page | seconds |
| `bounce_rate` | Bounce rate | percentage |
| `campaign_effectiveness` | Campaign performance score | 0-100 |

### Manual Import Interface

```python
def import_analytics(conn, article_id: int, platform: str, metrics: dict):
    """Import analytics data from external sources."""
    for metric_type, value in metrics.items():
        conn.execute("""
            INSERT INTO analytics (article_id, platform, metric_type, metric_value, source)
            VALUES (?, ?, ?, ?, 'import')
        """, (article_id, platform, metric_type, value))

# Usage:
import_analytics(conn, article_id=42, platform='linkedin', metrics={
    'views': 1250,
    'clicks': 89,
    'shares': 23,
    'comments': 7
})
```

## Analytics Queries

### Best Performing Articles

```sql
SELECT a.title, a.slug,
    SUM(CASE WHEN an.metric_type = 'views' THEN an.metric_value ELSE 0 END) as total_views,
    SUM(CASE WHEN an.metric_type = 'clicks' THEN an.metric_value ELSE 0 END) as total_clicks,
    SUM(CASE WHEN an.metric_type = 'shares' THEN an.metric_value ELSE 0 END) as total_shares
FROM articles a
JOIN analytics an ON a.id = an.article_id
GROUP BY a.id
ORDER BY total_views DESC;
```

### Platform Comparison

```sql
SELECT an.platform,
    AVG(CASE WHEN an.metric_type = 'ctr' THEN an.metric_value END) as avg_ctr,
    SUM(CASE WHEN an.metric_type = 'conversions' THEN an.metric_value ELSE 0 END) as total_conversions
FROM analytics an
GROUP BY an.platform;
```

## Output

- Analytics tables created and ready for import
- Import functions available
- No data generated — waiting for real metrics

## Validation

1. All analytics tables created
2. Import functions accept valid metric types
3. Foreign key constraints enforce valid article/campaign IDs
4. Timestamp tracking functional
