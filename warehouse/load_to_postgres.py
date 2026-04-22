"""
Warehouse load script.

Input files:
- Silver classified articles: data/silver/articles_classified.json
- Gold aggregates: data/gold/articles_stats.json

This loader is idempotent enough for demo use:
- article table uses URL uniqueness with ON CONFLICT DO NOTHING
- stats table uses (event_date, source, category) upsert
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List

import psycopg2
from dateutil import parser as date_parser

SILVER_CLASSIFIED = Path("data/silver/articles_classified.json")
GOLD_STATS = Path("data/gold/articles_stats.json")


def get_connection():
    """Create PostgreSQL connection from env vars or defaults."""
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "sports_warehouse"),
        user=os.getenv("PGUSER", "sports_user"),
        password=os.getenv("PGPASSWORD", "sports_pass"),
    )


def load_jsonl(path: Path) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not path.exists():
        return rows

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return rows


def to_timestamp(value: str) -> datetime:
    """Parse timestamp safely with fallback to current time."""
    try:
        return date_parser.parse(value)
    except Exception:
        return datetime.utcnow()


def insert_articles(conn, rows: Iterable[Dict[str, str]]) -> int:
    query = """
        INSERT INTO articles_clean
        (source, url, title, content, published_at, scraped_at, language, category)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (url) DO NOTHING;
    """

    inserted = 0
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                query,
                (
                    row.get("source", "unknown"),
                    row.get("url", ""),
                    row.get("title", ""),
                    row.get("content", ""),
                    to_timestamp(row.get("published_at", "")),
                    to_timestamp(row.get("scraped_at", "")),
                    row.get("language", "unknown"),
                    row.get("category", "other"),
                ),
            )
            inserted += cur.rowcount

    return inserted


def upsert_stats(conn, rows: Iterable[Dict[str, str]]) -> int:
    query = """
        INSERT INTO articles_stats (event_date, source, category, article_count)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (event_date, source, category)
        DO UPDATE SET article_count = EXCLUDED.article_count;
    """

    changed = 0
    with conn.cursor() as cur:
        for row in rows:
            cur.execute(
                query,
                (
                    row.get("event_date"),
                    row.get("source", "unknown"),
                    row.get("category", "other"),
                    int(row.get("article_count", 0)),
                ),
            )
            changed += cur.rowcount

    return changed


def main() -> None:
    article_rows = load_jsonl(SILVER_CLASSIFIED)
    stats_rows = load_jsonl(GOLD_STATS)

    conn = get_connection()
    try:
        article_count = insert_articles(conn, article_rows)
        stats_count = upsert_stats(conn, stats_rows)
        conn.commit()
        print(f"[warehouse] inserted_articles={article_count} upserted_stats={stats_count}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
