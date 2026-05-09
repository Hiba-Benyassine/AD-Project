"""
Silver cleaning job.

Input:
- data/bronze/*.json (JSON Lines)

Output:
- data/silver/articles_clean.json (JSON Lines)

Main responsibilities:
- remove HTML leftovers
- normalize whitespace
- lowercase and remove punctuation
- enforce quality rules
"""

from __future__ import annotations

import json
import html
import re
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, Generator, List

from bs4 import BeautifulSoup

try:
    from dateutil import parser as date_parser
except Exception:  # pragma: no cover - fallback for environments without dateutil
    date_parser = None

try:
    from langdetect import DetectorFactory, LangDetectException, detect

    DetectorFactory.seed = 0
except Exception:  # pragma: no cover - fallback for environments without langdetect
    DetectorFactory = None
    LangDetectException = Exception
    detect = None

BRONZE_DIR = Path("data/bronze")
SILVER_DIR = Path("data/silver")
SILVER_FILE = SILVER_DIR / "articles_clean.json"
MIN_CONTENT_LENGTH = 100


def strip_html(text: str) -> str:
    """Remove simple HTML tags if source content still contains markup."""
    text = html.unescape(text or "")
    return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)


def normalize_text(text: str) -> str:
    """Normalize text for Silver layer: lowercase, remove punctuation and extra spaces."""
    text = strip_html(text)
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
    text = re.sub(r"[^\w\sàâäçéèêëîïôöùûüÿœ'-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def coalesce(*values: str) -> str:
    """Return the first non-empty normalized string value."""
    for value in values:
        if value and str(value).strip():
            return str(value).strip()
    return ""


def is_valid_date(value: str) -> bool:
    """Return True if date can be parsed, otherwise False."""
    if not value:
        return False
    try:
        if date_parser is not None:
            date_parser.parse(value)
        else:
            datetime.fromisoformat(value.replace("Z", "+00:00"))
        return True
    except Exception:
        return False


def detect_language(text: str) -> str:
    """Detect language with fallback to 'unknown' for short/bad text."""
    if len(text or "") < 20:
        return "unknown"
    if detect is None:
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
    url = (row.get("url") or "").strip()

    has_valid_date = is_valid_date(published_at) or is_valid_date(scraped_at)
    return bool(title) and bool(url) and len(content) >= MIN_CONTENT_LENGTH and has_valid_date


def iter_bronze_rows() -> Generator[Dict[str, str], None, None]:
    """Yield rows from every Bronze JSONL file."""
    for file_path in BRONZE_DIR.glob("*.json"):
        with file_path.open("r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                continue

            # Support either JSONL or a single JSON array/object.
            if content.startswith("["):
                try:
                    parsed = json.loads(content)
                    if isinstance(parsed, list):
                        for row in parsed:
                            if isinstance(row, dict):
                                yield row
                    elif isinstance(parsed, dict):
                        yield parsed
                    continue
                except json.JSONDecodeError:
                    pass

            for line in content.splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue


def _build_published_at(row: Dict[str, str]) -> str:
    """Choose the most useful date field from raw rows."""
    candidate = coalesce(
        row.get("published_at"),
        row.get("date"),
        row.get("scraped_at"),
    )
    return candidate or datetime.utcnow().isoformat()


def _deduplicate_key(row: Dict[str, str]) -> str:
    """Build a stable dedupe key."""
    return coalesce(row.get("url"), row.get("title"), row.get("content"))


def clean_rows(rows: Generator[Dict[str, str], None, None]) -> List[Dict[str, str]]:
    """Apply text normalization and quality checks."""
    cleaned: List[Dict[str, str]] = []
    seen: set[str] = set()

    for row in rows:
        raw_title = coalesce(row.get("title"), row.get("headline"))
        raw_content = coalesce(row.get("content"), row.get("body"), row.get("description"))
        raw_url = coalesce(row.get("url"), row.get("link"))

        if not raw_title or not raw_content or not raw_url:
            continue

        row["title"] = normalize_text(raw_title)
        row["content"] = normalize_text(raw_content)
        row["url"] = raw_url
        row["published_at"] = _build_published_at(row)
        row["scraped_at"] = coalesce(row.get("scraped_at"), datetime.utcnow().isoformat())
        row["source"] = coalesce(row.get("source"), "unknown")
        row["category"] = coalesce(row.get("category"), "other").lower()
        row["language"] = detect_language(row["content"])

        dedupe_key = _deduplicate_key(row)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

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
