#!/usr/bin/env python3
"""
===============================================
SCRAPER SPÉCIALISÉ - 360SPORT.MA
===============================================
Auteur: Équipe ETL Sport
Date: 23/04/2026
Objectif: Scraper optimisé pour 360Sport.ma

Hérite de BaseScraper et ajoute la logique spécifique:
- URLs directes par sport
- Sélecteurs CSS validés
- Structure .selections-list-item > a.text
"""

import re
from typing import List
from base_scraper import BaseScraper

class Sport360Scraper(BaseScraper):
    """
    ===============================================
    SCRAPER SPÉCIALISÉ 360SPORT.MA
    ===============================================
    Utilise la structure HTML validée de sport.le360.ma
    """
    
    def __init__(self):
        """Initialisation spécifique à 360Sport"""
        super().__init__(
            site_name="360Sport",
            base_url="https://sport.le360.ma"
        )
        
        # 🎯 URLs directes par sport - classification immédiate !
        self.sport_urls = {
            "football": "https://sport.le360.ma/football",
            "tennis": "https://sport.le360.ma/tennis/", 
            "basketball": "https://sport.le360.ma/basket-ball/",
            "athletisme": "https://sport.le360.ma/athletisme/",
            "auto-moto": "https://sport.le360.ma/auto-moto/",
            "coupe-du-monde": "https://sport.le360.ma/coupe-du-monde/",
            "lions-atlas": "https://sport.le360.ma/football/lions-atlas/"
        }
    
    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        ===============================================
        RÉCUPÉRATION URLs SPÉCIFIQUE 360SPORT
        ===============================================
        Utilise la structure .selections-list-item validée
        
        Paramètre:
        - max_articles: nombre max d'articles
        
        Retourne:
        - List[str]: URLs des articles
        """
        print(f"🔍 Recherche articles sur {self.base_url}")
        
        try:
            response = self.session.get(self.base_url, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Utiliser la structure validée: .selections-list-item > a.text
            article_items = soup.find_all('div', class_='selections-list-item')
            
            for item in article_items[:max_articles]:
                # Chercher le lien principal
                text_link = item.find('a', class_='text')
                if text_link and text_link.get('href'):
                    href = text_link.get('href')
                    
                    # Construire URL complet
                    if href.startswith('/'):
                        full_url = self.base_url + href
                    else:
                        full_url = href
                    
                    # Éviter les doublons
                    if full_url not in articles:
                        articles.append(full_url)
            
            print(f"✅ {len(articles)} URLs trouvées")
            return articles
            
        except Exception as e:
            print(f"❌ Erreur récupération URLs: {e}")
            return []
    
    def _extract_title(self, soup):
        """
        ===============================================
        EXTRACTION TITRE SPÉCIFIQUE 360SPORT
        ===============================================
        Utilise h1.le360-titre-title validé
        """
        # Stratégie 1: h1 avec classe spécifique 360Sport
        title_elem = soup.find('h1', class_='le360-titre-title')
        if title_elem:
            return title_elem.get_text().strip()
        
        # Fallback vers la méthode de base
        return super()._extract_title(soup)
    
    def scrape_by_sport(self, sport: str, max_articles: int = 5) -> List[str]:
        """
        ===============================================
        SCRAPING PAR SPORT SPÉCIFIQUE
        ===============================================
        Scrape une section sport particulière
        
        Paramètres:
        - sport: nom du sport (football, tennis, etc.)
        - max_articles: nombre max d'articles
        
        Retourne:
        - List[str]: URLs des articles de ce sport
        """
        if sport not in self.sport_urls:
            print(f"❌ Sport '{sport}' non configuré")
            return []
        
        sport_url = self.sport_urls[sport]
        print(f"🔍 Scraping section {sport}: {sport_url}")
        
        try:
            response = self.session.get(sport_url, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            articles = []
            
            # Utiliser la structure validée
            article_items = soup.find_all('div', class_='selections-list-item')
            
            for item in article_items[:max_articles]:
                text_link = item.find('a', class_='text')
                if text_link and text_link.get('href'):
                    href = text_link.get('href')
                    
                    if href.startswith('/'):
                        full_url = self.base_url + href
                    else:
                        full_url = href
                    
                    if full_url not in articles:
                        articles.append(full_url)
            
            print(f"✅ {len(articles)} articles trouvés pour {sport}")
            return articles
            
        except Exception as e:
            print(f"❌ Erreur section {sport}: {e}")
            return []

def main():
    """
    ===============================================
    TEST SCRAPER 360SPORT
    ===============================================
    Fonction de test pour valider le scraper spécialisé
    """
    print("🚀 LANCEMENT SCRAPER 360SPORT SPÉCIALISÉ")
    print("🎯 Hérite de BaseScraper + logique spécifique")
    print("=" * 60)
    
    scraper = Sport360Scraper()
    
    # Test scraping principal
    articles = scraper.scrape_articles(max_articles=5)
    
    if articles:
        filename = scraper.save_to_json(articles)
        
        print(f"\n📋 EXEMPLE D'ARTICLE:")
        article = articles[0]
        print(f"🏆 Sport: {article['category']}")
        print(f"📰 Titre: {article['title'][:60]}...")
        print(f"🔗 URL: {article['url']}")
        
        print(f"\n🎉 SCRAPER 360SPORT FONCTIONNEL!")
        print(f"📁 Fichier: {filename}")
        
    else:
        print("\n❌ ÉCHEC DU SCRAPER 360SPORT")

if __name__ == "__main__":
    main()
