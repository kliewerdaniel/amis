import re
import hashlib
import json
from pathlib import Path
from datetime import datetime

import frontmatter
from markdown_it import MarkdownIt

md = MarkdownIt()

SKIP_FILES = {"temp.md"}


def discover_files(content_dir: str | Path) -> list[Path]:
    content_dir = Path(content_dir)
    files = sorted(content_dir.rglob("*.md"))
    return [f for f in files if f.name not in SKIP_FILES]


def parse_date_from_filename(filename: str) -> str | None:
    match = re.match(r"(\d{4})-(\d{2})-(\d{2})-", filename)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return None


def _generate_slug(filename: str) -> str:
    name = filename.replace(".md", "")
    return name.lower().strip()


def extract_headings(tokens: list) -> list[dict]:
    headings = []
    for token in tokens:
        if token.type == "heading_open":
            level = int(token.tag[1])
            heading_text = ""
            idx = tokens.index(token) + 1
            while idx < len(tokens) and tokens[idx].type != "heading_close":
                if tokens[idx].type == "inline":
                    heading_text = tokens[idx].content
                idx += 1
            heading_id = re.sub(r"[^a-z0-9]+", "-", heading_text.lower()).strip("-")
            headings.append({"level": level, "text": heading_text, "id": heading_id})
    return headings


def extract_images(tokens: list) -> list[dict]:
    images = []
    for token in tokens:
        if token.type == "inline":
            for child in token.children or []:
                if child.type == "image":
                    images.append({
                        "src": child.attrs.get("src", ""),
                        "alt": child.content,
                        "title": child.attrs.get("title", ""),
                    })
    return images


def extract_links(tokens: list) -> list[dict]:
    links = []
    for token in tokens:
        if token.type == "inline":
            for child in token.children or []:
                if child.type == "link_open":
                    href = child.attrs.get("href", "")
                    text = ""
                    idx = list(token.children).index(child)
                    for c in token.children[idx:]:
                        if c.type == "link_close":
                            break
                        if c.type == "text":
                            text = c.content
                    links.append({"href": href, "text": text, "title": child.attrs.get("title", "")})
    return links


def extract_code_blocks(tokens: list) -> list[dict]:
    blocks = []
    for i, token in enumerate(tokens):
        if token.type == "fence":
            blocks.append({
                "language": token.info.strip() if token.info else "",
                "content": token.content,
                "line_start": token.map[0] + 1 if token.map else 0,
            })
        elif token.type == "code_block":
            blocks.append({
                "language": "",
                "content": token.content,
                "line_start": token.map[0] + 1 if token.map else 0,
            })
    return blocks


def compute_word_count(content: str) -> int:
    return len(content.split())


def compute_reading_time(word_count: int) -> int:
    return max(1, word_count // 225)


def parse_markdown(file_path: Path) -> dict:
    raw = file_path.read_text(encoding="utf-8")
    metadata, content = frontmatter.parse(raw)

    parsed = md.parse(content)
    tokens = parsed

    headings = extract_headings(tokens)
    images = extract_images(tokens)
    links = extract_links(tokens)
    code_blocks = extract_code_blocks(tokens)
    word_count = compute_word_count(content)
    reading_time = compute_reading_time(word_count)

    filename = file_path.name
    slug = _generate_slug(filename)
    title = metadata.get("title", slug.replace("-", " ").title())
    pub_date = metadata.get("date")
    if not pub_date:
        pub_date = parse_date_from_filename(filename)

    if hasattr(pub_date, "strftime"):
        pub_date = pub_date.strftime("%Y-%m-%d")
    elif pub_date and isinstance(pub_date, str):
        try:
            pub_date = datetime.strptime(pub_date, "%m-%d-%Y").strftime("%Y-%m-%d")
        except ValueError:
            pass

    tags = metadata.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]

    ingestion_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def serialize_val(v):
        if isinstance(v, (datetime,)):
            return v.strftime("%Y-%m-%d")
        if hasattr(v, "strftime"):
            return v.strftime("%Y-%m-%d")
        return v

    serializable_meta = {}
    for k, v in metadata.items():
        if isinstance(v, list):
            serializable_meta[k] = [serialize_val(i) for i in v]
        else:
            serializable_meta[k] = serialize_val(v)

    return {
        "filename": filename,
        "slug": slug,
        "title": title,
        "author": metadata.get("author", ""),
        "description": metadata.get("description", ""),
        "canonical_url": metadata.get("canonical_url", ""),
        "publication_date": str(pub_date) if pub_date else None,
        "frontmatter_json": json.dumps(serializable_meta),
        "content": content,
        "html_content": md.render(content),
        "word_count": word_count,
        "reading_time_minutes": reading_time,
        "headings_json": json.dumps(headings),
        "images_json": json.dumps(images),
        "links_json": json.dumps(links),
        "code_blocks_json": json.dumps(code_blocks),
        "references_json": json.dumps([]),
        "categories_json": json.dumps(metadata.get("categories", [])),
        "tags_json": json.dumps(tags),
        "ingestion_hash": ingestion_hash,
    }
