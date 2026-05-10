#!/usr/bin/env python3
"""
===============================================
SCRAPER SPÉCIALISÉ - L'ÉQUIPE.FR
===============================================
Auteur: Équipe ETL Sport
Date: 10/05/2026
Objectif: Scraper robuste pour L'Équipe.fr
"""

import sys
import os
from typing import List, Dict, Optional
from datetime import datetime
import time
import re
from bs4 import BeautifulSoup

# Ajouter le chemin courant pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_scraper import BaseScraper

class LequipeScraper(BaseScraper):
    """
    ===============================================
    SCRAPER SPÉCIALISÉ L'ÉQUIPE.FR
    ===============================================
    Combine RSS et Scraping direct pour une robustesse maximale
    """
    
    def __init__(self):
        """Initialisation spécifique à L'Équipe"""
        super().__init__(
            site_name="LEquipe",
            base_url="https://www.lequipe.fr"
        )
        
        # URLs des rubriques principales
        self.sections = {
            "football": "https://www.lequipe.fr/Football/",
            "tennis": "https://www.lequipe.fr/Tennis/", 
            "basketball": "https://www.lequipe.fr/Basket/",
            "actualites": "https://www.lequipe.fr/Chrono"
        }

    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        Récupère les URLs des articles.
        Tente le scraping des pages de rubriques car le RSS est instable.
        """
        print(f"SCRAPING: L'quipe via rubriques directes")
        urls = []
        
        for section, section_url in self.sections.items():
            print(f"  ANALYSE section: {section}")
            try:
                response = self.session.get(section_url, timeout=15)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Chercher tous les liens
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    # On ne garde que les articles (ceux qui contiennent /Actualites/ ou /Article/)
                    if any(x in href for x in ['/Actualites/', '/Article/']):
                        if not href.startswith('http'):
                            href = self.base_url + href
                        
                        if href not in urls:
                            urls.append(href)
                            if len(urls) >= max_articles:
                                break
                
                if len(urls) >= max_articles:
                    break
                    
            except Exception as e:
                print(f"    ERREUR sur la section {section}: {e}")
                continue
        
        print(f"{len(urls)} URLs rcupres pour L'quipe")
        return urls[:max_articles]

    def _extract_title(self, soup):
        """Extraction optimisée du titre pour L'Équipe"""
        selectors = [
            'h1.headline',
            'h1.Article__title',
            'h1[class*="title"]',
            'h1',
            'meta[property="og:title"]'
        ]
        
        for selector in selectors:
            if selector.startswith('meta'):
                tag = soup.find('meta', property='og:title')
                if tag: return tag.get('content')
            else:
                elem = soup.select_one(selector)
                if elem: return elem.get_text().strip()
        
        return "No title"

    def _extract_content(self, soup):
        """Extraction optimisée du contenu pour L'Équipe"""
        # Nettoyage des éléments inutiles
        for trash in soup.select('.Ad, .Newsletter, .SocialShare, .Related'):
            trash.decompose()
            
        selectors = [
            'div.Article__content p',
            'section.article-body p',
            'div[class*="article-content"] p',
            'div[class*="body"] p',
            'article p',
            'p'
        ]
        
        paragraphs = []
        for selector in selectors:
            elems = soup.select(selector)
            if elems:
                for elem in elems:
                    text = elem.get_text().strip()
                    # On filtre les paragraphes trop courts ou publicitaires
                    if len(text) > 40 and not text.startswith(('Inscrivez-vous', 'Lire aussi')):
                        paragraphs.append(text)
                if paragraphs:
                    break
        
        return "\n\n".join(paragraphs) if paragraphs else "No content"

    def extract_article_data(self, url: str) -> Optional[Dict]:
        """Extraction complète avec gestion du lazy loading ou des structures complexes"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            title = self._extract_title(soup)
            content = self._extract_content(soup)
            
            if not title or title == "No title" or len(content) < 100:
                return None

            # Classification
            category = self.classify_by_url(url)
            
            return {
                "title": title,
                "content": content,
                "url": url,
                "source": "LEquipe",
                "category": category,
                "published_at": datetime.utcnow().isoformat(),
                "scraped_at": datetime.utcnow().isoformat(),
                "author": "Rédaction L'Équipe"
            }
            
        except Exception as e:
            print(f"     Erreur extraction {url}: {e}")
            return None

def run() -> int:
    """
    ===============================================
    FONCTION RUN POUR BATCH PIPELINE
    ===============================================
    """
    scraper = LequipeScraper()
    articles = scraper.scrape_articles(max_articles=50)
    
    if articles:
        scraper.save_to_json(articles)
        return len(articles)
    
    return 0

def main():
    print("LAUNCHING: TEST SCRAPER L'EQUIPE OPTIMISE")
    scraper = LequipeScraper()
    articles = scraper.scrape_articles(max_articles=3)
    
    if articles:
        filename = scraper.save_to_json(articles)
        print(f"\nSUCCESS: {len(articles)} articles collects")
    else:
        print("\nFAILURE: Aucun article collect. Vrifiez la connexion ou les slecteurs.")

if __name__ == "__main__":
    main()
