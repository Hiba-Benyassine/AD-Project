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
            base_url="https://www.lematin.ma"
        )
        
        # 🎯 URLs directes par sport (à vérifier/adapter)
        self.sport_urls = {
            "football": "https://www.lematin.ma/sport/football",
            "tennis": "https://www.lematin.ma/sport/tennis",
            "basketball": "https://www.lematin.ma/sport/basketball"
        }
    
    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        ===============================================
        RÉCUPÉRATION URLs LE MATIN
        ===============================================
        À ADAPTER: inspecter le HTML de lematin.ma/sport
        """
        print(f"🔍 Recherche articles sur {self.base_url}/sport")
        
        try:
            # Accéder directement à la section sport
            sport_url = f"{self.base_url}/sport"
            response = self.session.get(sport_url, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # 🔄 À ADAPTER: trouver les bons sélecteurs CSS
            article_selectors = [
                'a[href*="/article/"]',
                'a[href*="/sport/"]',
                '.article-title a',
                '.news-title a',
                'h3 a',
                'h2 a'
            ]
            
            for selector in article_selectors:
                links = soup.select(selector)
                if links:
                    print(f"✅ Sélecteur trouvé: {selector}")
                    for link in links[:max_articles]:
                        href = link.get('href')
                        if href and '/sport/' in href:
                            # Construire URL complet
                            if href.startswith('/'):
                                full_url = self.base_url + href
                            elif not href.startswith('http'):
                                full_url = self.base_url + '/' + href
                            else:
                                full_url = href
                            
                            if full_url not in articles:
                                articles.append(full_url)
                    break
            
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
        # 🔄 À ADAPTER: trouver les bons sélecteurs
        selectors = [
            'h1.article-title',
            'h1.post-title',
            '.entry-title h1',
            'h1'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()
        
        return super()._extract_title(soup)

def main():
    """
    ===============================================
    TEST SCRAPER LE MATIN
    ===============================================
    À adapter une fois la structure HTML analysée
    """
    print("🚀 LANCEMENT SCRAPER LE MATIN (TEMPLATE)")
    print("🔄 À ADAPTER: inspecter HTML de www.lematin.ma/sport")
    print("=" * 60)
    
    scraper = LeMatinScraper()
    
    # Test scraping
    articles = scraper.scrape_articles(max_articles=3)
    
    if articles:
        filename = scraper.save_to_json(articles)
        print(f"\n🎉 SCRAPER LE MATIN FONCTIONNEL!")
        print(f"📁 Fichier: {filename}")
        
    else:
        print("\n❌ SCRAPER LE MATIN - À ADAPTER")
        print("🔧 Actions nécessaires:")
        print("   1. Inspecter HTML de www.lematin.ma/sport")
        print("   2. Adapter les sélecteurs CSS")
        print("   3. Tester les URLs directes /sport/football")

if __name__ == "__main__":
    main()
