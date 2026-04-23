#!/usr/bin/env python3
"""
===============================================
SCRAPER SPÉCIALISÉ - MSPORT.MA
===============================================
Auteur: Équipe ETL Sport
Date: 23/04/2026
Objectif: Scraper pour MSport.ma

Hérite de BaseScraper - À adapter selon la structure HTML
URLs directes: /football/, /tennis/, etc.
"""

from typing import List
from base_scraper import BaseScraper

class MSportScraper(BaseScraper):
    """
    ===============================================
    SCRAPER SPÉCIALISÉ MSPORT.MA
    ===============================================
    Template à adapter selon la structure réelle du site
    """
    
    def __init__(self):
        """Initialisation spécifique à MSport"""
        super().__init__(
            site_name="MSport",
            base_url="https://www.msport.ma"
        )
        
        # 🎯 URLs directes par sport (à vérifier/adapter)
        self.sport_urls = {
            "football": "https://www.msport.ma/football",
            "tennis": "https://www.msport.ma/tennis",
            "basketball": "https://www.msport.ma/basketball"
        }
    
    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        ===============================================
        RÉCUPÉRATION URLs MSPORT
        ===============================================
        À ADAPTER: inspecter le HTML de msport.ma
        
        Pour l'instant: fallback vers recherche générique
        """
        print(f"🔍 Recherche articles sur {self.base_url}")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # 🔄 À ADAPTER: trouver les bons sélecteurs CSS
            # Exemples de patterns communs:
            article_selectors = [
                'a[href*="/article/"]',
                'a[href*="/news/"]', 
                'article a',
                '.article-item a',
                '.news-item a'
            ]
            
            for selector in article_selectors:
                links = soup.select(selector)
                if links:
                    print(f"✅ Sélecteur trouvé: {selector}")
                    for link in links[:max_articles]:
                        href = link.get('href')
                        if href:
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
        EXTRACTION TITRE MSPORT
        ===============================================
        À ADAPTER selon les classes CSS de MSport
        """
        # 🔄 À ADAPTER: trouver les bons sélecteurs
        selectors = [
            'h1.article-title',
            'h1.title',
            '.post-title h1',
            'h1'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()
        
        # Fallback vers méthode de base
        return super()._extract_title(soup)
    
    def _extract_date(self, soup):
        """
        ===============================================
        EXTRACTION DATE MSPORT
        ===============================================
        À ADAPTER selon les classes CSS de MSport
        """
        # 🔄 À ADAPTER: trouver les bons sélecteurs
        selectors = [
            '.post-date',
            '.article-date', 
            '.publish-date',
            'time'
        ]
        
        for selector in selectors:
            date_elem = soup.select_one(selector)
            if date_elem:
                date_str = date_elem.get('datetime') or date_elem.get_text().strip()
                if date_str:
                    return self._normalize_date(date_str)
        
        # Fallback vers méthode de base
        return super()._extract_date(soup)
    
    def _extract_author(self, soup):
        """
        ===============================================
        EXTRACTION AUTEUR MSPORT
        ===============================================
        À ADAPTER selon les classes CSS de MSport
        """
        # 🔄 À ADAPTER: trouver les bons sélecteurs
        selectors = [
            '.author-name',
            '.post-author',
            '.article-author'
        ]
        
        for selector in selectors:
            author_elem = soup.select_one(selector)
            if author_elem:
                return author_elem.get_text().strip()
        
        # Fallback vers méthode de base
        return super()._extract_author(soup)

def main():
    """
    ===============================================
    TEST SCRAPER MSPORT
    ===============================================
    À adapter une fois la structure HTML analysée
    """
    print("🚀 LANCEMENT SCRAPER MSPORT (TEMPLATE)")
    print("🔄 À ADAPTER: inspecter HTML de www.msport.ma")
    print("=" * 60)
    
    scraper = MSportScraper()
    
    # Test scraping
    articles = scraper.scrape_articles(max_articles=3)
    
    if articles:
        filename = scraper.save_to_json(articles)
        print(f"\n🎉 SCRAPER MSPORT FONCTIONNEL!")
        print(f"📁 Fichier: {filename}")
        
    else:
        print("\n❌ SCRAPER MSPORT - À ADAPTER")
        print("🔧 Actions nécessaires:")
        print("   1. Inspecter HTML de www.msport.ma")
        print("   2. Adapter les sélecteurs CSS")
        print("   3. Tester les URLs directes /football, /tennis")

if __name__ == "__main__":
    main()
