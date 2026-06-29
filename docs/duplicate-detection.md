# Phase 6: Duplicate Detection

## Objective

Identify duplicate articles, near-duplicate ideas, outdated content, and content gaps requiring follow-up.

## Detection Methods

### 1. Exact Duplicate Detection

```python
def find_exact_duplicates(conn):
    """Find articles with identical content hashes."""
    dupes = conn.execute("""
        SELECT a.id, b.id, a.title, b.title
        FROM articles a
        JOIN articles b ON a.ingestion_hash = b.ingestion_hash AND a.id < b.id
    """).fetchall()
    return dupes
```

### 2. Near-Duplicate Detection

Use ChromaDB vector similarity:

```python
def find_near_duplicates(chroma_client, threshold=0.92):
    """Find articles with >92% semantic similarity."""
    all_embeddings = chroma_client.get_all()
    duplicates = []
    for i, emb_a in enumerate(all_embeddings):
        for j, emb_b in enumerate(all_embeddings):
            if i >= j:
                continue
            similarity = cosine_similarity(emb_a, emb_b)
            if similarity > threshold:
                duplicates.append((emb_a.id, emb_b.id, similarity))
    return duplicates
```

### 3. Idea Overlap Detection

```python
IDEA_OVERLAP_PROMPT = """
Compare these two articles and determine if they cover substantially
the same ideas, even with different wording or structure.

Article A: {title_a}
Summary A: {summary_a}

Article B: {title_b}
Summary B: {summary_b}

Return JSON:
{{
  "overlap_score": 0.0-1.0,
  "shared_ideas": ["..."],
  "unique_to_a": ["..."],
  "unique_to_b": ["..."],
  "recommendation": "keep_both | merge | supersede_a | supersede_b"
}}
"""
```

### 4. Outdated Content Detection

```python
OUTDATED_DETECTION_PROMPT = """
Analyze this article for potentially outdated information.
Consider: technology versions, API changes, deprecated tools,
current best practices vs. when the article was published.

Article: {title}
Published: {date}
Content: {content_summary}

Return JSON:
{{
  "is_outdated": true/false,
  "outdated_items": ["..."],
  "confidence": 0.0-1.0,
  "recommended_action": "update | archive | add_disclaimer"
}}
"""
```

### 5. Series Gap Detection

```python
def find_series_gaps(conn):
    """Detect articles that appear to be part of a series."""
    # Look for articles with similar titles or explicit series markers
    series = conn.execute("""
        SELECT id, title FROM articles
        WHERE title LIKE '%Part %' OR title LIKE '%Series%'
        ORDER BY publication_date
    """).fetchall()
    # Analyze for missing installments
```

## Output

Store findings in `relationships` table:
- `duplicates` edges between duplicate articles
- `updates` edges between outdated and replacement articles

## Validation

1. No duplicate pairs missed (run all detection methods)
2. All flagged duplicates reviewed by confidence threshold
3. Recommendations generated for each duplicate pair
