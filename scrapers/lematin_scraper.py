#!/usr/bin/env python3
"""
===============================================
SCRAPER SPÉCIALISÉ - LE MATIN.MA
===============================================
Auteur: Équipe ETL Sport
Date: 23/04/2026
Objectif: Scraper pour Le Matin.ma (section sport)

Hérite de BaseScraper - À adapter selon la structure HTML
URLs directes: /sport/football/, /sport/tennis/, etc.
"""

import re
from typing import List
from base_scraper import BaseScraper

class LeMatinScraper(BaseScraper):
    """
    ===============================================
    SCRAPER SPÉCIALISÉ LE MATIN.MA
    ===============================================
    Template à adapter selon la structure réelle du site
    """
    
    def __init__(self):
        """Initialisation spécifique à Le Matin"""
        super().__init__(
            site_name="LeMatin",
            base_url="https://lematin.ma"
        )
        self.session.headers.update({'Accept-Encoding': 'gzip, deflate'})
        
        # 🎯 Sections sport
        self.sport_urls = {
            "football": "https://lematin.ma/sports/football",
            "tennis": "https://lematin.ma/sports/tennis",
            "basketball": "https://lematin.ma/sports/basketball",
            "sport": "https://lematin.ma/sports",
        }

    def _normalize_url(self, href: str) -> str:
        if href.startswith('http'):
            return href
        if href.startswith('/'):
            return self.base_url + href
        return self.base_url + '/' + href

    def _is_valid_sport_article_url(self, url: str) -> bool:
        url_lower = url.lower()

        if not url_lower.startswith("https://lematin.ma/"):
            return False
        if "/sports/" not in url_lower:
            return False

        # Exemple valide: /sports/.../342005
        if not re.search(r"/sports/.+/\d+$", url_lower):
            return False

        blocked = [r"/auteur/", r"/tag/", r"\?page=", r"#", r"javascript:"]
        return not any(re.search(pattern, url_lower) for pattern in blocked)
    
    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        ===============================================
        RÉCUPÉRATION URLs LE MATIN
        ===============================================
        À ADAPTER: inspecter le HTML de lematin.ma/sport
        """
        print(f"🔍 Recherche articles sur {self.base_url}/sports")
        
        try:
            from bs4 import BeautifulSoup

            articles = []

            pages = [self.sport_urls["sport"]]
            estimated_pages = max(1, (max_articles // 20) + 3)
            for page_num in range(2, min(25, estimated_pages) + 1):
                pages.append(f"{self.sport_urls['sport']}?page={page_num}")

            pages.extend([
                self.sport_urls["football"],
                self.sport_urls["tennis"],
                self.sport_urls["basketball"],
            ])

            for page_url in pages:
                if len(articles) >= max_articles:
                    break

                response = self.session.get(page_url, timeout=12)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                for link in soup.select('a[href]'):
                    if len(articles) >= max_articles:
                        break
                    href = link.get('href')
                    if not href:
                        continue

                    full_url = self._normalize_url(href)
                    if self._is_valid_sport_article_url(full_url) and full_url not in articles:
                        articles.append(full_url)
            
            print(f"✅ {len(articles)} URLs trouvées")
            return articles
            
        except Exception as e:
            print(f"❌ Erreur récupération URLs: {e}")
            return []
    
    def _extract_title(self, soup):
        """
        ===============================================
        EXTRACTION TITRE LE MATIN
        ===============================================
        À ADAPTER selon les classes CSS de Le Matin
        """
        selectors = [
            'h1.article-title',
            'h1.post-title',
            'h1.page-title',
            '.entry-title h1',
            'meta[property="og:title"]',
            'h1'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                if title_elem.name == 'meta':
                    val = title_elem.get('content', '').strip()
                    if val:
                        return val
                return title_elem.get_text().strip()
        
        return super()._extract_title(soup)

    def _extract_date(self, soup):
        selectors = [
            'time[datetime]',
            'meta[property="article:published_time"]',
            '.article-date',
            '.post-date',
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if not elem:
                continue
            value = elem.get('datetime') or elem.get('content') or elem.get_text().strip()
            if value:
                return self._normalize_date(value)

        return super()._extract_date(soup)

    def _extract_author(self, soup):
        selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.article-author',
            '.author-name',
            '.byline',
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if not elem:
                continue
            value = elem.get('content') or elem.get_text().strip()
            if value:
                return re.sub(r'^(Par|By|Auteur)\s*', '', value, flags=re.IGNORECASE).strip()

        return super()._extract_author(soup)

    def _extract_content(self, soup):
        selectors = [
            'article',
            '.article-content',
            '.post-content',
            '.entry-content',
            '.article-body',
        ]

        for selector in selectors:
            elem = soup.select_one(selector)
            if elem:
                text = self._clean_content(elem.get_text(" ", strip=True))
                if len(text) >= 120:
                    return text

        return super()._extract_content(soup)

def main():
    """
    ===============================================
    TEST SCRAPER LE MATIN
    ===============================================
    À adapter une fois la structure HTML analysée
    """
    print("🚀 LANCEMENT SCRAPER LE MATIN")
    print("🎯 Section sport Le Matin")
    print("=" * 60)
    
    scraper = LeMatinScraper()
    
    articles = scraper.scrape_articles(max_articles=50)
    
    if articles:
        filename = scraper.save_to_json(articles)
        print(f"\n🎉 SCRAPER LE MATIN FONCTIONNEL!")
        print(f"📁 Fichier: {filename}")
        
    else:
        print("\n❌ ÉCHEC DU SCRAPER LE MATIN")

if __name__ == "__main__":
    main()
