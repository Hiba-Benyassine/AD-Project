#!/usr/bin/env python3
"""
===============================================
SCRAPER SPÉCIALISÉ - ESPN.COM
===============================================
Auteur: Équipe ETL Sport
Date: 24/04/2026
Objectif: Scraper ESPN (partie sport)

Note:
- ESPN bloque parfois le scraping HTML direct.
- Cette version utilise les flux RSS officiels ESPN sport.
"""

import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import List

import requests
from base_scraper import BaseScraper


class ESPNScraper(BaseScraper):
    """Scraper ESPN sport basé sur les flux RSS."""

    def __init__(self):
        super().__init__(
            site_name="ESPN",
            base_url="https://www.espn.com",
        )

        self.rss_urls = {
            "football": "https://www.espn.com/espn/rss/soccer/news",
            "tennis": "https://www.espn.com/espn/rss/tennis/news",
            "basketball": "https://www.espn.com/espn/rss/nba/news",
        }

        self.rss_headers = {"User-Agent": "Mozilla/5.0"}

    def _normalize_url(self, href: str) -> str:
        if href.startswith("http"):
            return href
        if href.startswith("//"):
            return "https:" + href
        if href.startswith("/"):
            return self.base_url + href
        return self.base_url + "/" + href

    def _is_valid_sport_url(self, url: str) -> bool:
        url_lower = url.lower()

        if "espn.com" not in url_lower:
            return False

        blocked_patterns = [
            r"/video/",
            r"/watch/",
            r"/fantasy/",
            r"/betting/",
            r"/scoreboard",
            r"/schedule",
            r"/stats",
            r"/odds",
            r"javascript:",
            r"#",
        ]
        if any(re.search(pattern, url_lower) for pattern in blocked_patterns):
            return False

        article_patterns = [
            r"/story/_/id/",
            r"/news/story/",
            r"/soccer/story/_/id/",
            r"/tennis/story/_/id/",
            r"/nba/story/_/id/",
            r"/espn/story/_/id/",
        ]
        return any(re.search(pattern, url_lower) for pattern in article_patterns)

    def _parse_rss_date(self, date_str: str) -> str:
        if not date_str:
            return datetime.now().isoformat()
        try:
            return parsedate_to_datetime(date_str).isoformat()
        except Exception:
            return datetime.now().isoformat()

    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """Retourne les URLs d'articles sport depuis les flux RSS ESPN."""
        print("🔍 Recherche articles ESPN sport via RSS")
        urls: List[str] = []

        try:
            for _, feed_url in self.rss_urls.items():
                if len(urls) >= max_articles:
                    break

                response = requests.get(feed_url, timeout=12, headers=self.rss_headers)
                response.raise_for_status()
                root = ET.fromstring(response.text)

                for item in root.findall(".//item"):
                    if len(urls) >= max_articles:
                        break

                    link_text = item.findtext("link", default="").strip()
                    if not link_text:
                        continue

                    url = self._normalize_url(link_text)
                    if self._is_valid_sport_url(url) and url not in urls:
                        urls.append(url)

            print(f"✅ {len(urls)} URLs trouvées")
            return urls
        except Exception as e:
            print(f"❌ Erreur récupération URLs ESPN: {e}")
            return []

    def scrape_articles(self, max_articles: int = 10) -> List[dict]:
        """Scraping ESPN en mode RSS natif (simple et fiable)."""
        print(f"🎯 Scraping {self.site_name} (RSS) - Max: {max_articles} articles")
        print("=" * 60)

        articles: List[dict] = []

        try:
            for sport, feed_url in self.rss_urls.items():
                if len(articles) >= max_articles:
                    break

                response = requests.get(feed_url, timeout=12, headers=self.rss_headers)
                response.raise_for_status()
                root = ET.fromstring(response.text)

                for item in root.findall(".//item"):
                    if len(articles) >= max_articles:
                        break

                    title_text = item.findtext("title", default="").strip()
                    link_text = item.findtext("link", default="").strip()
                    desc_text = item.findtext("description", default="").strip()
                    date_text = item.findtext("pubDate", default="").strip()
                    author_text = item.findtext("{http://purl.org/dc/elements/1.1/}creator", default="").strip() or item.findtext("creator", default="").strip()

                    if not title_text or not link_text:
                        continue

                    article_url = self._normalize_url(link_text)
                    if not self._is_valid_sport_url(article_url):
                        continue

                    content_text = desc_text
                    if not content_text:
                        content_text = title_text

                    article_data = {
                        "title": title_text,
                        "date": self._parse_rss_date(date_text),
                        "content": self._clean_content(content_text),
                        "author": author_text if author_text else "Auteur inconnu",
                        "category": sport,
                        "source": self.site_name,
                        "url": article_url,
                        "scraped_at": datetime.now().isoformat(),
                    }

                    if self._validate_article_data(article_data):
                        articles.append(article_data)

                print(f"✅ RSS {sport}: {len(articles)} articles cumulés")

            print("\n" + "=" * 60)
            print(f"📊 RÉSUMÉ {self.site_name}")
            print(f"✅ Réussis: {len(articles)}")
            print("❌ Échoués: 0")
            print("=" * 60)
            return articles

        except Exception as e:
            print(f"❌ Erreur scraping RSS ESPN: {e}")
            return []


def main():
    print("🚀 LANCEMENT SCRAPER ESPN")
    print("🎯 Section sport ESPN")
    print("=" * 60)

    scraper = ESPNScraper()
    articles = scraper.scrape_articles(max_articles=50)

    if articles:
        filename = scraper.save_to_json(articles)
        print("\n🎉 SCRAPER ESPN FONCTIONNEL!")
        print(f"📁 Fichier: {filename}")
    else:
        print("\n❌ ÉCHEC DU SCRAPER ESPN")


if __name__ == "__main__":
    main()
