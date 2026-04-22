"""
Silver cleaning job.

Input:
- data/bronze/*.json (JSON Lines)

Output:
- data/silver/articles_clean.json (JSON Lines)

Main responsibilities:
- remove HTML leftovers
- normalize whitespace
- basic language detection
- enforce quality rules
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List

from dateutil import parser as date_parser
from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0

BRONZE_DIR = Path("data/bronze")
SILVER_DIR = Path("data/silver")
SILVER_FILE = SILVER_DIR / "articles_clean.json"


def strip_html(text: str) -> str:
    """Remove simple HTML tags if source content still contains markup."""
    return re.sub(r"<[^>]+>", " ", text or "")


def normalize_text(text: str) -> str:
    """Collapse repeated spaces/newlines and trim final text."""
    text = strip_html(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def is_valid_date(value: str) -> bool:
    """Return True if date can be parsed, otherwise False."""
    if not value:
        return False
    try:
        date_parser.parse(value)
        return True
    except Exception:
        return False


def detect_language(text: str) -> str:
    """Detect language with fallback to 'unknown' for short/bad text."""
    if len(text or "") < 20:
        return "unknown"
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


def quality_pass(row: Dict[str, str]) -> bool:
    """
    Minimal quality rules required by project:
    - non-empty title
    - content length >= 100
    - valid date (published_at) OR fallback scraped_at valid
    """
    title = (row.get("title") or "").strip()
    content = (row.get("content") or "").strip()
    published_at = (row.get("published_at") or "").strip()
    scraped_at = (row.get("scraped_at") or "").strip()

    has_valid_date = is_valid_date(published_at) or is_valid_date(scraped_at)
    return bool(title) and len(content) >= 100 and has_valid_date


def iter_bronze_rows() -> Generator[Dict[str, str], None, None]:
    """Yield rows from every Bronze JSONL file."""
    for file_path in BRONZE_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def clean_rows(rows: Generator[Dict[str, str], None, None]) -> List[Dict[str, str]]:
    """Apply text normalization and quality checks."""
    cleaned: List[Dict[str, str]] = []

    for row in rows:
        row["title"] = normalize_text(row.get("title", ""))
        row["content"] = normalize_text(row.get("content", ""))
        row["language"] = detect_language(row["content"])

        if not row.get("published_at"):
            # Use scrape timestamp as fallback date source when missing.
            row["published_at"] = row.get("scraped_at", datetime.utcnow().isoformat())

        if quality_pass(row):
            cleaned.append(row)

    return cleaned


def save_silver(rows: List[Dict[str, str]]) -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)
    with SILVER_FILE.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    rows = iter_bronze_rows()
    cleaned = clean_rows(rows)
    save_silver(cleaned)
    print(f"[cleaning] silver_rows={len(cleaned)}")


if __name__ == "__main__":
    main()
