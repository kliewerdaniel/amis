# Phase 2: Semantic Analysis

## Objective

For every article, generate a comprehensive marketing and content analysis using LLM reasoning, producing 27 scored metrics (0-100) with confidence values.

## Input

- All rows from `articles` table
- Full article content (markdown)

## Analysis Dimensions

### Content Quality Metrics (0-100)

| Metric | Description | LLM Prompt Focus |
|--------|-------------|------------------|
| `summary` | Brief summary of article | Summarize in 2-3 sentences |
| `core_thesis` | Central argument or claim | Identify main thesis statement |
| `problem_solved` | What problem does this address | Identify the problem/need |

### Audience Fit Metrics (0-100)

| Metric | Description | Evaluation Criteria |
|--------|-------------|---------------------|
| `technical_difficulty` | How technical is this content | Code examples, jargon, prerequisites |
| `business_difficulty` | How much business context needed | Business terms, strategy, ROI |
| `developer_appeal` | Appeal to developers | Hands-on, practical, code-heavy |
| `executive_appeal` | Appeal to C-suite/leadership | Strategic, high-level, outcomes |
| `research_appeal` | Appeal to researchers | Novel, analytical, citations |
| `startup_appeal` | Appeal to founders/startups | Lean, MVP, bootstrap, growth |
| `enterprise_appeal` | Appeal to enterprise buyers | Scale, compliance, governance |

### Relevance Metrics (0-100)

| Metric | Description | Evaluation Criteria |
|--------|-------------|---------------------|
| `book_relevance` | How relevant to the book project | Directly supports book topics |
| `github_relevance` | How relevant to GitHub repos | Showcases or documents repos |
| `consulting_relevance` | How relevant to consulting work | Demonstrates expertise |

### Value Metrics (0-100)

| Metric | Description | Evaluation Criteria |
|--------|-------------|---------------------|
| `marketing_value` | Overall marketing potential | Shareability, reach, conversion |
| `educational_value` | Teaching/learning potential | Clear explanations, examples |
| `originality` | How novel is the content | New ideas vs. rehashing |
| `practicality` | How actionable is the content | Step-by-step, immediately useful |

### Reach Metrics (0-100)

| Metric | Description | Evaluation Criteria |
|--------|-------------|---------------------|
| `authority_score` | Subject matter authority | Expertise demonstrated |
| `virality_potential` | Likelihood of viral sharing | Controversial, surprising, useful |
| `seo_potential` | Search engine visibility | Keywords, search intent match |

### Longevity Metrics (0-100)

| Metric | Description | Evaluation Criteria |
|--------|-------------|---------------------|
| `evergreen_score` | Timeless relevance | Will this matter in 2 years? |
| `trend_score` | Current trend alignment | Hot topic right now? |

### Persona Metrics (0-100)

| Metric | Description | Evaluation Criteria |
|--------|-------------|---------------------|
| `primary_audience` | Best-fit primary audience | Who is this written for? |
| `secondary_audience` | Secondary audience | Who else benefits? |

## LLM Prompt Template

```python
SEMANTIC_ANALYSIS_PROMPT = """
You are a marketing intelligence analyst. Analyze the following blog article
and provide scores for each dimension below.

Article Title: {title}
Article Content:
{content}

For each metric, provide:
1. A score from 0-100
2. A confidence value from 0-1
3. Brief reasoning (1-2 sentences)

Respond in JSON format:
{{
  "summary": "...",
  "core_thesis": "...",
  "problem_solved": "...",
  "scores": {{
    "technical_difficulty": {{"score": 0, "confidence": 0.0, "reasoning": "..."}},
    "business_difficulty": {{"score": 0, "confidence": 0.0, "reasoning": "..."}},
    ...
  }},
  "primary_audience": "...",
  "secondary_audience": "..."
}}
"""
```

## Output

For each article, insert rows into `scores` table:

```sql
INSERT INTO scores (article_id, score_type, metric_name, score_value, confidence, reasoning, model_used)
VALUES (?, 'semantic', 'technical_difficulty', 85, 0.9, '...', 'llama3.1:8b');
```

## Batch Processing

```python
def analyze_all_articles(conn, llm_client):
    articles = conn.execute("SELECT id, title, content FROM articles").fetchall()
    for article in articles:
        if already_scored(conn, article.id, 'semantic'):
            continue  # Skip if already analyzed
        result = llm_client.analyze(SEMANTIC_ANALYSIS_PROMPT.format(**article))
        store_scores(conn, article.id, result)
```

## Dependencies

- LLM client (Ollama or OpenAI-compatible)
- JSON response parsing
- Retry logic for failed LLM calls

## Validation

1. Every article has at least 25 score rows (27 metrics minus 2 text fields)
2. All scores are in range 0-100
3. All confidence values in range 0-1
4. No NULL reasoning fields
5. Model name recorded for reproducibility
