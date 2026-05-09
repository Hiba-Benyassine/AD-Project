#!/usr/bin/env python3
"""
===============================================
SCRAPER SPÉCIALISÉ - L'ÉQUIPE.FR
===============================================
Auteur: Équipe ETL Sport
Date: 24/04/2026
Objectif: Scraper pour L'Équipe.fr (version RSS robuste)

Utilise le flux RSS pour être plus stable
"""

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime
import time

# Ajouter le chemin courant pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_scraper import BaseScraper

class LequipeScraper(BaseScraper):
    """
    ===============================================
    SCRAPER SPÉCIALISÉ L'ÉQUIPE.FR (RSS)
    ===============================================
    Utilise le flux RSS pour une meilleure stabilité
    """
    
    def __init__(self):
        """Initialisation spécifique à L'Équipe"""
        super().__init__(
            site_name="LEquipe",
            base_url="https://www.lequipe.fr"
        )
        
        # 🎯 URLs RSS par section
        self.rss_urls = {
            "football": "https://www.lequipe.fr/rss/football.xml",
            "tennis": "https://www.lequipe.fr/rss/tennis.xml", 
            "basketball": "https://www.lequipe.fr/rss/basket.xml",
            "general": "https://www.lequipe.fr/rss/actualites.xml"
        }
    
    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        Récupère les URLs des articles depuis le flux RSS de L'Équipe
        """
        print(f"🔍 Scraping L'Équipe via RSS")
        
        urls = []
        
        try:
            import xml.etree.ElementTree as ET
            
            # Essayer le flux general RSS
            for section, rss_url in self.rss_urls.items():
                print(f"  📡 Section: {section}")
                try:
                    response = self.session.get(rss_url, timeout=10)
                    response.raise_for_status()
                    
                    # Parser le XML
                    root = ET.fromstring(response.content)
                    
                    # Extraire les liens (RSS utilise <link> ou <enclosure>)
                    namespaces = {
                        '': 'http://www.w3.org/2005/Atom',
                        'content': 'http://purl.org/rss/1.0/modules/content/'
                    }
                    
                    # Chercher les liens dans les items
                    items = root.findall('.//item')
                    if not items:
                        items = root.findall('.//entry')
                    
                    for item in items[:max_articles]:
                        # Chercher le lien
                        link_elem = item.find('link')
                        if link_elem is None:
                            link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                        
                        if link_elem is not None:
                            href = link_elem.text or link_elem.get('href')
                            if href and href not in urls:
                                urls.append(href)
                    
                    if len(urls) >= max_articles:
                        break
                        
                except Exception as e:
                    print(f"    ⚠️  Erreur RSS {section}: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ Erreur parsing RSS: {e}")
        
        # Fallback: utiliser des URLs connues de L'Équipe
        if not urls:
            print("  📌 Utilisation URLs de fallback")
            urls = [
                "https://www.lequipe.fr/Football/",
                "https://www.lequipe.fr/Tennis/",
                "https://www.lequipe.fr/Basket/",
            ][:max_articles]
        
        print(f"✅ {len(urls)} URLs récupérées")
        return urls
    
    def _extract_title(self, soup):
        """Extraction du titre - L'Équipe"""
        selectors = [
            'h1.headline',
            'h1[class*="title"]',
            'h1',
            'h2.headline'
        ]
        
        for selector in selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                return title_elem.get_text().strip()
        
        return "No title"
    
    def _extract_content(self, soup):
        """Extraction du contenu - L'Équipe"""
        selectors = [
            'article > p',
            '[class*="article-content"] p',
            '[class*="body"] p',
            'p'
        ]
        
        paragraphs = []
        for selector in selectors:
            elems = soup.select(selector)
            if elems:
                for elem in elems[:5]:  # Max 5 paragraphes
                    text = elem.get_text().strip()
                    if len(text) > 50:
                        paragraphs.append(text)
                break
        
        return " ".join(paragraphs) or "No content"
    
    def extract_article_data(self, url: str) -> Optional[Dict]:
        """Extraction complète des données d'article"""
        print(f"    📥 Extraction: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = self._extract_title(soup)
            if not title or title == "No title":
                print(f"    ⚠️  Pas de titre trouvé")
                return None
            
            content = self._extract_content(soup)
            
            # Classification par URL
            category = "other"
            url_lower = url.lower()
            if any(x in url_lower for x in ['/football', '/foot']):
                category = "football"
            elif any(x in url_lower for x in ['/tennis', '/roland']):
                category = "tennis"
            elif any(x in url_lower for x in ['/basket', '/nba']):
                category = "basketball"
            
            article = {
                "title": title,
                "content": content,
                "url": url,
                "source": "LEquipe",
                "category": category,
                "published_at": datetime.utcnow().isoformat(),
                "scraped_at": datetime.utcnow().isoformat(),
            }
            
            print(f"    ✅ Article extrait: {category}")
            return article
            
        except Exception as e:
            print(f"    ❌ Erreur extraction: {e}")
            return None

def run() -> int:
    """
    ===============================================
    FONCTION RUN POUR BATCH PIPELINE
    ===============================================
    Fonction appelée par batch_pipeline.py
    
    Retourne:
    - int: nombre d'articles collectés
    """
    scraper = LequipeScraper()
    articles = scraper.scrape_articles(max_articles=50)
    
    if articles:
        scraper.save_to_json(articles)
        return len(articles)
    
    return 0


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
