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

Classification strategy (hierarchical):
1. URL-based classification (highest priority)
2. Keyword matching on title + content (medium priority)
3. Regex patterns (lowest priority)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

SILVER_INPUT = Path("data/silver/articles_clean.json")
SILVER_OUTPUT = Path("data/silver/articles_classified.json")

# URL patterns for direct classification (highest priority)
URL_PATTERNS = {
    "football": [
        r"/football/?",
        r"/soccer/?",
        r"/fifa/?",
        r"/uefa/?",
        r"/liga/?",
        r"/premier-league/?",
        r"/champions-league/?",
        r"/coupe-du-monde/?",
        r"/world-cup/?",
        r"/bundesliga/?",
        r"/serie-a/?",
        r"/laliga/?",
        r"/ligue-1/?",
    ],
    "tennis": [
        r"/tennis/?",
        r"/atp/?",
        r"/wta/?",
        r"/roland-garros/?",
        r"/grand-slam/?",
        r"/us-open/?",
        r"/wimbledon/?",
        r"/australian-open/?",
    ],
    "basketball": [
        r"/basketball/?",
        r"/nba/?",
        r"/euroleague/?",
        r"/fiba/?",
        r"/playoffs/?",
        r"/basket/?",
    ],
}

# Keyword matching (medium priority)
CATEGORY_KEYWORDS = {
    "football": ["football", "soccer", "fifa", "uefa", "liga", "premier league", "champions league", "coupe du monde", "world cup", "bundesliga", "serie a", "laliga", "ligue 1"],
    "tennis": ["tennis", "atp", "wta", "roland garros", "grand slam", "us open", "wimbledon", "australian open"],
    "basketball": ["basketball", "nba", "euroleague", "fiba", "playoffs", "dunk", "basket"],
}

# Regex patterns for complex matching (lowest priority)
REGEX_PATTERNS = {
    "football": [
        r"\b(football|soccer)\b",
        r"\b(fifa|uefa)\b",
        r"\b(premier league|champions league|liga|bundesliga|serie a|laliga|ligue 1)\b",
    ],
    "tennis": [
        r"\b(tennis|atp|wta)\b",
        r"\b(roland garros|grand slam|us open|wimbledon|australian open)\b",
    ],
    "basketball": [
        r"\b(basketball|nba|basket)\b",
        r"\b(euroleague|fiba)\b",
    ],
}


def classify_by_url(url: str) -> str | None:
    """Classify article based on URL patterns (highest priority)."""
    if not url:
        return None

    url_lower = url.lower()
    for category, patterns in URL_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, url_lower):
                return category

    return None


def classify_by_keywords(title: str, content: str) -> str | None:
    """Classify article using keyword matching on title + content (medium priority)."""
    text = f"{title} {content}".lower()

    for category in ("football", "tennis", "basketball"):
        keywords = CATEGORY_KEYWORDS[category]
        if any(keyword in text for keyword in keywords):
            return category

    return None


def classify_by_regex(title: str, content: str) -> str | None:
    """Classify article using regex patterns (lowest priority)."""
    text = f"{title} {content}".lower()

    for category in ("football", "tennis", "basketball"):
        patterns = REGEX_PATTERNS[category]
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return category

    return None


def classify_article(url: str, title: str, content: str) -> str:
    """
    Classify article using hierarchical strategy:
    1. URL-based classification (highest priority)
    2. Keyword matching (medium priority)
    3. Regex patterns (lowest priority)
    4. Default to 'other'
    """
    # Priority 1: URL classification
    category = classify_by_url(url)
    if category:
        return category

    # Priority 2: Keyword matching
    category = classify_by_keywords(title, content)
    if category:
        return category

    # Priority 3: Regex patterns
    category = classify_by_regex(title, content)
    if category:
        return category

    # Default
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
        url = row.get("url", "")
        title = row.get("title", "")
        content = row.get("content", "")
        row["category"] = classify_article(url, title, content)

    save_rows(rows)
    print(f"[classification] classified_rows={len(rows)}")


if __name__ == "__main__":
    main()
