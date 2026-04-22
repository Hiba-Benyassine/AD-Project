"""
Gold analytics builder.

Input:
- data/silver/articles_classified.json

Output:
- data/gold/articles_stats.json

Metrics generated:
- count by day
- count by source
- count by category
- combined dimensions for warehouse loading
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

from dateutil import parser as date_parser

SILVER_CLASSIFIED = Path("data/silver/articles_classified.json")
GOLD_FILE = Path("data/gold/articles_stats.json")


def parse_day(date_str: str) -> str:
    """Convert any parseable date to YYYY-MM-DD; fallback to current UTC day."""
    try:
        dt = date_parser.parse(date_str)
        return dt.date().isoformat()
    except Exception:
        return datetime.utcnow().date().isoformat()


def load_rows() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not SILVER_CLASSIFIED.exists():
        return rows

    with SILVER_CLASSIFIED.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return rows


def build_stats(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    grouped: Dict[Tuple[str, str, str], int] = defaultdict(int)

    for row in rows:
        day = parse_day(row.get("published_at", ""))
        source = row.get("source", "unknown")
        category = row.get("category", "other")
        grouped[(day, source, category)] += 1

    results = []
    for (day, source, category), total in grouped.items():
        results.append(
            {
                "event_date": day,
                "source": source,
                "category": category,
                "article_count": total,
            }
        )

    return sorted(results, key=lambda x: (x["event_date"], x["source"], x["category"]))


def save_stats(stats: List[Dict[str, str]]) -> None:
    GOLD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with GOLD_FILE.open("w", encoding="utf-8") as f:
        for row in stats:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    rows = load_rows()
    stats = build_stats(rows)
    save_stats(stats)
    print(f"[gold] stats_rows={len(stats)}")


if __name__ == "__main__":
    main()
