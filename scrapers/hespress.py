"""
Hespress sports scraper (example skeleton).

Purpose:
- Fetch sports listing pages and article pages from Hespress
- Extract a normalized article payload
- Save each record as JSON lines in Bronze layer

Important:
- Website HTML changes frequently. Keep selectors centralized and easy to update.
- Respect robots.txt and legal constraints before production use.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

SOURCE_NAME = "hespress"
BASE_URL = "https://fr.hespress.com/sport"
BRONZE_PATH = Path("data/bronze/hespress_raw.json")


def fetch_listing_html(url: str) -> str:
    """Download listing page HTML with minimal error handling and timeout."""
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.text


def parse_listing_for_links(html: str) -> List[str]:
    """
    Extract article links from listing page.

    Replace CSS selectors based on the current page structure.
    Keep only unique absolute URLs.
    """
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a_tag in soup.select("a"):
        href = a_tag.get("href")
        if not href:
            continue
        if href.startswith("http") and "hespress.com" in href:
            links.append(href)
    return list(dict.fromkeys(links))


def extract_article(url: str) -> Dict[str, str]:
    """
    Extract title/content/published_at from one article URL.

    This is intentionally conservative and selector-driven.
    If extraction fails, fields can be empty and quality checks later will filter.
    """
    article_html = requests.get(url, timeout=20)
    article_html.raise_for_status()

    soup = BeautifulSoup(article_html.text, "lxml")
    title = soup.title.text.strip() if soup.title else ""

    # Basic content extraction fallback.
    paragraphs = [p.get_text(" ", strip=True) for p in soup.select("p")]
    content = "\n".join(p for p in paragraphs if p)

    return {
        "source": SOURCE_NAME,
        "url": url,
        "title": title,
        "content": content,
        "published_at": "",
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def save_bronze(records: List[Dict[str, str]]) -> None:
    """Append records as JSONL to Bronze storage path."""
    BRONZE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BRONZE_PATH.open("a", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run() -> int:
    """Main scraper flow: list page -> links -> article extraction -> bronze write."""
    html = fetch_listing_html(BASE_URL)
    links = parse_listing_for_links(html)

    records = []
    for url in links[:20]:
        try:
            records.append(extract_article(url))
        except Exception:
            continue

    save_bronze(records)
    return len(records)


if __name__ == "__main__":
    count = run()
    print(f"[{SOURCE_NAME}] collected={count}")
