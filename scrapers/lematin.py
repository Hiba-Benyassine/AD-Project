"""
Le Matin sports scraper (example skeleton).

This scraper follows the same contract as other sources so downstream jobs
can process all files with a unified schema.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

SOURCE_NAME = "lematin"
BASE_URL = "https://lematin.ma/sports"
BRONZE_PATH = Path("data/bronze/lematin_raw.json")


def fetch_listing_html(url: str) -> str:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    return response.text


def parse_listing_for_links(html: str) -> List[str]:
    # Keep parser minimal and robust; tune selectors as needed.
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a_tag in soup.select("a"):
        href = a_tag.get("href")
        if not href:
            continue
        if href.startswith("http") and "lematin.ma" in href:
            links.append(href)
    return list(dict.fromkeys(links))


def extract_article(url: str) -> Dict[str, str]:
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml")

    title = soup.title.text.strip() if soup.title else ""
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
    BRONZE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with BRONZE_PATH.open("a", encoding="utf-8") as f:
        for row in records:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run() -> int:
    html = fetch_listing_html(BASE_URL)
    links = parse_listing_for_links(html)

    rows: List[Dict[str, str]] = []
    for url in links[:20]:
        try:
            rows.append(extract_article(url))
        except Exception:
            continue

    save_bronze(rows)
    return len(rows)


if __name__ == "__main__":
    count = run()
    print(f"[{SOURCE_NAME}] collected={count}")
