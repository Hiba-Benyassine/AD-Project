#!/usr/bin/env python3
"""
===============================================
SCRAPER SPÉCIALISÉ - L'ÉQUIPE.FR
===============================================
Auteur: Équipe ETL Sport
Date: 24/04/2026
Objectif: Scraper pour L'Équipe.fr

Hérite de BaseScraper - À adapter selon la structure HTML
URLs directes: /Football/, /Tennis/, /Basket/, etc.
"""

import sys
import os
from typing import List

# Ajouter le chemin courant pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_scraper import BaseScraper

class LequipeScraper(BaseScraper):
    """
    ===============================================
    SCRAPER SPÉCIALISÉ L'ÉQUIPE.FR
    ===============================================
    Template à adapter selon la structure réelle du site
    """
    
    def __init__(self):
        """Initialisation spécifique à L'Équipe"""
        super().__init__(
            site_name="LEquipe",
            base_url="https://www.lequipe.fr"
        )
        
        # 🎯 URLs directes par sport (à vérifier/adapter)
        self.sport_urls = {
            "football": "https://www.lequipe.fr/Football",
            "tennis": "https://www.lequipe.fr/Tennis", 
            "basketball": "https://www.lequipe.fr/Basket"
        }
    
    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        ===============================================
        RÉCUPÉRATION URLs L'ÉQUIPE
        ===============================================
        À ADAPTER: inspecter le HTML de lequipe.fr
        """
        print(f"🔍 Recherche articles sur {self.base_url}")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # 🔄 À ADAPTER: trouver les bons sélecteurs CSS
            article_selectors = [
                'a[href*="/article/"]',
                '.article-title a',
                '.headline a',
                'h2 a',
                'h3 a'
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
        EXTRACTION TITRE L'ÉQUIPE
        ===============================================
        À ADAPTER selon les classes CSS de L'Équipe
        """
        # 🔄 À ADAPTER: trouver les bons sélecteurs
        selectors = [
            'h1.article-title',
            'h1.headline',
            '.title h1',
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
    TEST SCRAPER L'ÉQUIPE
    ===============================================
    À adapter une fois la structure HTML analysée
    """
    print("🚀 LANCEMENT SCRAPER L'ÉQUIPE (TEMPLATE)")
    print("🔄 À ADAPTER: inspecter HTML de www.lequipe.fr")
    print("=" * 60)
    
    scraper = LequipeScraper()
    
    # Test scraping
    articles = scraper.scrape_articles(max_articles=3)
    
    if articles:
        filename = scraper.save_to_json(articles)
        print(f"\n🎉 SCRAPER L'ÉQUIPE FONCTIONNEL!")
        print(f"📁 Fichier: {filename}")
        
    else:
        print("\n❌ SCRAPER L'ÉQUIPE - À ADAPTER")
        print("🔧 Actions nécessaires:")
        print("   1. Inspecter HTML de www.lequipe.fr")
        print("   2. Adapter les sélecteurs CSS")
        print("   3. Tester les URLs directes /Football, /Tennis")

if __name__ == "__main__":
    main()
