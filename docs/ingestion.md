# Phase 1: Markdown Ingestion

## Objective

Read every Markdown file from the content directory, parse structure, extract metadata, and store normalized documents in SQLite with idempotent re-ingestion.

## Input

- Directory of `.md` files (blog folder with 135 posts)
- Frontmatter format: YAML between `---` delimiters

## Pipeline Steps

### 1. File Discovery

```python
# Pseudocode
def discover_files(content_dir: str) -> list[Path]:
    """Find all .md files recursively, sorted by date."""
    files = sorted(Path(content_dir).glob("**/*.md"))
    return [f for f in files if f.name != "temp.md"]
```

### 2. Content Reading

```python
def read_file(path: Path) -> tuple[str, dict]:
    """Read markdown file, split frontmatter from content."""
    raw = path.read_text(encoding="utf-8")
    content = frontmatter.parse(raw)
    return content.content, content.metadata
```

### 3. Frontmatter Extraction

Extract from YAML frontmatter:
- `title` (required)
- `author`
- `description`
- `tags` (array)
- `canonical_url`
- `image`, `og:image`, `twitter:image`
- `og:title`, `og:description`, `og:url`, `og:type`
- `twitter:card`, `twitter:title`, `twitter:description`
- `date` (publication date)

### 4. Structural Extraction

Parse Markdown AST to extract:

| Field | Type | Method |
|-------|------|--------|
| `headings` | `[{level, text, id}]` | Parse `#` headings |
| `images` | `[{src, alt, title}]` | Parse `![]()` syntax |
| `links` | `[{href, text, title}]` | Parse `[]()` syntax |
| `code_blocks` | `[{language, content, line_start}]` | Parse fenced code blocks |
| `references` | `[{type, target, context}]` | Parse reference-style links and citations |

### 5. Computed Fields

```python
def compute_metadata(content: str) -> dict:
    word_count = len(content.split())
    reading_time = max(1, word_count // 225)  # ~225 WPM
    slug = generate_slug(filename)  # from filename
    return {
        "word_count": word_count,
        "reading_time_minutes": reading_time,
        "slug": slug,
        "ingestion_hash": sha256(content)
    }
```

### 6. Normalization

Store as JSON arrays in their respective columns:
- `headings_json`
- `images_json`
- `links_json`
- `code_blocks_json`
- `references_json`
- `categories_json`
- `tags_json`

### 7. Database Storage

```python
def upsert_article(conn, article: dict):
    """Insert or update article. Idempotent by filename."""
    conn.execute("""
        INSERT INTO articles (filename, slug, title, ...)
        VALUES (:filename, :slug, :title, ...)
        ON CONFLICT(filename) DO UPDATE SET
            slug = excluded.slug,
            title = excluded.title,
            ...
            updated_at = datetime('now')
    """, article)
```

## Output

- One row per article in `articles` table
- All structural data as JSON columns
- `ingestion_hash` for idempotent re-runs

## Dependencies

- `python-frontmatter` — YAML frontmatter parsing
- `markdown-it-py` — Markdown to HTML + AST
- `hashlib` — SHA-256 content hashing

## Edge Cases

| Case | Handling |
|------|----------|
| Missing frontmatter | Use filename as title, extract date from filename |
| Missing date | Parse from filename pattern `YYYY-MM-DD-*` |
| Binary/corrupt files | Log warning, skip file |
| Duplicate filenames | `ON CONFLICT` upsert |
| Unicode content | UTF-8 encoding throughout |
| Empty files | Skip with warning |
| `temp.md` in blog | Exclude from ingestion |

## Filename Date Parsing

```python
import re
from datetime import datetime

def parse_date_from_filename(filename: str) -> str | None:
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})-", filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None
```

## Validation

After ingestion, verify:
1. Total article count matches expected (135 blog posts)
2. All articles have non-empty `content`
3. All articles have valid `slug`
4. No duplicate slugs
5. All `ingestion_hash` values are unique
