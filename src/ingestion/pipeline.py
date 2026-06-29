import sqlite3
import logging
from pathlib import Path

from src.ingestion.parser import discover_files, parse_markdown

logger = logging.getLogger("amis.ingestion")


def upsert_article(conn: sqlite3.Connection, article: dict) -> int:
    existing = conn.execute(
        "SELECT id FROM articles WHERE filename = ?", (article["filename"],)
    ).fetchone()

    if existing:
        conn.execute("""
            UPDATE articles SET
                slug = :slug,
                title = :title,
                author = :author,
                description = :description,
                canonical_url = :canonical_url,
                publication_date = :publication_date,
                frontmatter_json = :frontmatter_json,
                content = :content,
                html_content = :html_content,
                word_count = :word_count,
                reading_time_minutes = :reading_time_minutes,
                headings_json = :headings_json,
                images_json = :images_json,
                links_json = :links_json,
                code_blocks_json = :code_blocks_json,
                references_json = :references_json,
                categories_json = :categories_json,
                tags_json = :tags_json,
                ingestion_hash = :ingestion_hash,
                updated_at = datetime('now')
            WHERE id = ?
        """, {**article, "id": existing["id"]})
        return existing["id"]
    else:
        cursor = conn.execute("""
            INSERT INTO articles (
                filename, slug, title, author, description, canonical_url,
                publication_date, frontmatter_json, content, html_content,
                word_count, reading_time_minutes, headings_json, images_json,
                links_json, code_blocks_json, references_json, categories_json,
                tags_json, ingestion_hash
            ) VALUES (
                :filename, :slug, :title, :author, :description, :canonical_url,
                :publication_date, :frontmatter_json, :content, :html_content,
                :word_count, :reading_time_minutes, :headings_json, :images_json,
                :links_json, :code_blocks_json, :references_json, :categories_json,
                :tags_json, :ingestion_hash
            )
        """, article)
        return cursor.lastrowid


def run_ingestion(conn: sqlite3.Connection, content_dir: str | Path) -> int:
    content_dir = Path(content_dir)
    if not content_dir.exists():
        logger.error("Content directory does not exist: %s", content_dir)
        return 0

    files = discover_files(content_dir)
    logger.info("Found %d markdown files in %s", len(files), content_dir)

    count = 0
    for file_path in files:
        try:
            article = parse_markdown(file_path)
            article_id = upsert_article(conn, article)
            count += 1
            logger.debug("Ingested: %s (id=%d)", file_path.name, article_id)
        except Exception as e:
            logger.error("Failed to ingest %s: %s", file_path.name, e)

    conn.commit()
    logger.info("Ingestion complete: %d articles processed", count)
    return count
