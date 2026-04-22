"""
Category classification job.

Input:
- data/silver/articles_clean.json

Output:
- data/silver/articles_classified.json

Controlled categories:
- football
- tennis
- basketball
- other

Classification strategy:
- keyword matching on title + content
- deterministic mapping to avoid ambiguous values
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

SILVER_INPUT = Path("data/silver/articles_clean.json")
SILVER_OUTPUT = Path("data/silver/articles_classified.json")

CATEGORY_KEYWORDS = {
    "football": ["football", "soccer", "fifa", "uefa", "liga", "premier league", "champions league"],
    "tennis": ["tennis", "atp", "wta", "roland garros", "grand slam", "us open", "wimbledon"],
    "basketball": ["basketball", "nba", "euroleague", "fiba", "playoffs", "dunk"],
}


def classify_article(title: str, content: str) -> str:
    """Classify article using ordered keyword matching with strict output values."""
    text = f"{title} {content}".lower()

    for category in ("football", "tennis", "basketball"):
        keywords = CATEGORY_KEYWORDS[category]
        if any(keyword in text for keyword in keywords):
            return category

    return "other"


def load_rows() -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if not SILVER_INPUT.exists():
        return rows

    with SILVER_INPUT.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return rows


def save_rows(rows: List[Dict[str, str]]) -> None:
    SILVER_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with SILVER_OUTPUT.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    rows = load_rows()

    for row in rows:
        row["category"] = classify_article(row.get("title", ""), row.get("content", ""))

    save_rows(rows)
    print(f"[classification] classified_rows={len(rows)}")


if __name__ == "__main__":
    main()
