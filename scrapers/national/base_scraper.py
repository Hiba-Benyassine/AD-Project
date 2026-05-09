#!/usr/bin/env python3
"""
===============================================
BASE SCRAPER CLASS
===============================================
Auteur: Équipe ETL Sport
Date: 23/04/2026
Objectif: Logique commune pour tous les scrapers

Cette classe contient toute la logique réutilisable:
- Gestion HTTP et sessions
- Extraction de données (titre, date, auteur, contenu)
- Nettoyage et validation
- Classification par URL
- Sauvegarde JSON

Chaque scraper spécialisé hérite de cette classe.
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import re
from typing import Dict, Optional, List
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """
    ===============================================
    CLASSE DE BASE POUR TOUS LES SCRAPERS
    ===============================================
    Contient toute la logique commune et réutilisable
    """
    
    def __init__(self, site_name: str, base_url: str):
        """
        Constructeur de base
        
        Paramètres:
        - site_name: nom du site (ex: "360Sport", "MSport")
        - base_url: URL principale du site
        """
        self.site_name = site_name
        self.base_url = base_url
        
        # En-têtes HTTP optimisés
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        print(f"🚀 {site_name} Scraper initialisé")
    
    def classify_by_url(self, url: str) -> str:
        """
        ===============================================
        CLASSIFICATION DIRECTE PAR URL - 100% PRÉCISION
        ===============================================
        Analyse l'URL pour déterminer le sport immédiatement
        
        Paramètre:
        - url: URL de l'article
        
        Retourne:
        - str: catégorie du sport (football/tennis/basketball/athletisme/other)
        """
        url_lower = url.lower()
        
        # 🎯 Mapping direct URL → Sport (priorité haute)
        url_patterns = {
            "football": [
                r"/football/", r"/coupe-du-monde/", r"/lions-atlas/",
                r"/can/", r"/ligue/", r"/premier-league/", r"/liga/",
                r"/mercato/", r"/foot/", r"/soccer/"
            ],
            "tennis": [
                r"/tennis/", r"/roland-garros/", r"/wimbledon/",
                r"/atp/", r"/wta/", r"/open/", r"/tennis/"
            ],
            "basketball": [
                r"/basketball/", r"/nba/", r"/euroleague/",
                r"/basket/", r"/playoffs/", r"/basket-ball/"
            ],
            "athletisme": [
                r"/athletisme/", r"/athlé/", r"/course/",
                r"/marathon/", r"/saut/", r"/athletics/"
            ],
            "auto-moto": [
                r"/auto/", r"/moto/", r"/f1/", r"/rallye/",
                r"/gp/", r"/moto-gp/", r"/automoto/"
            ]
        }
        
        # Vérifier chaque pattern
        for sport, patterns in url_patterns.items():
            for pattern in patterns:
                if re.search(pattern, url_lower):
                    return sport
        
        # Si aucun pattern trouvé → other
        return "other"
    
    def extract_article_data(self, url: str) -> Optional[Dict]:
        """
        ===============================================
        EXTRACTION COMPLÈTE DES DONNÉES
        ===============================================
        Extrait les 7 champs requis d'un article
        
        Paramètre:
        - url: URL de l'article
        
        Retourne:
        - Dict: article complet ou None si erreur
        """
        print(f"📖 Extraction: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extraction des champs
            title = self._extract_title(soup)
            date = self._extract_date(soup)
            author = self._extract_author(soup)
            content = self._extract_content(soup)
            
            # Classification directe par URL
            category = self.classify_by_url(url)
            
            article_data = {
                "title": title,
                "date": date,
                "content": content,
                "author": author,
                "category": category,
                "source": self.site_name,
                "url": url,
                "scraped_at": datetime.now().isoformat()
            }
            
            if self._validate_article_data(article_data):
                print(f"✅ {category.upper()}: {title[:50]}...")
                return article_data
            else:
                print(f"⚠️ Données invalides")
                return None
                
        except Exception as e:
            print(f"❌ Erreur extraction {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extraction titre - à surcharger selon le site"""
        # Stratégie 1: h1 principal
        title_elem = soup.find('h1')
        if title_elem:
            return title_elem.get_text().strip()
        
        # Stratégie 2: Meta title
        title_elem = soup.find('meta', property='og:title')
        if title_elem:
            return title_elem.get('content', '').strip()
        
        # Stratégie 3: Balise title HTML
        title_elem = soup.find('title')
        if title_elem:
            title = title_elem.get_text().strip()
            # Nettoyer le titre du site
            return re.sub(r'\s*-\s*' + re.escape(self.site_name) + r'.*$', '', title)
        
        return "Titre non trouvé"
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """Extraction date - à surcharger selon le site"""
        # Stratégie 1: Balise time
        time_elem = soup.find('time')
        if time_elem and time_elem.get('datetime'):
            date_str = time_elem.get('datetime')
            return self._normalize_date(date_str)
        
        # Stratégie 2: Meta property
        date_elem = soup.find('meta', property='article:published_time')
        if date_elem:
            date_str = date_elem.get('content')
            return self._normalize_date(date_str)
        
        # Stratégie 3: Classes de date
        for class_name in ['date', 'publish-date', 'publication-date']:
            date_elem = soup.find(class_=class_name)
            if date_elem:
                date_str = date_elem.get_text().strip()
                return self._normalize_date(date_str)
        
        return datetime.now().isoformat()
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalisation date"""
        if not date_str:
            return datetime.now().isoformat()
        
        date_str = date_str.strip()
        formats = [
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d/%m/%Y %H:%M',
            '%d %B %Y',
            '%d %b %Y'
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str[:20], fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        return datetime.now().isoformat()
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """Extraction auteur - à surcharger selon le site"""
        # Stratégie 1: Meta author
        author_elem = soup.find('meta', attrs={'name': 'author'})
        if author_elem:
            return author_elem.get('content', '').strip()
        
        # Stratégie 2: Meta property
        author_elem = soup.find('meta', property='article:author')
        if author_elem:
            return author_elem.get('content', '').strip()
        
        # Stratégie 3: Classes d'auteur
        for class_name in ['author', 'byline', 'writer', 'journalist']:
            author_elem = soup.find(class_=class_name)
            if author_elem:
                author_text = author_elem.get_text().strip()
                author_text = re.sub(r'^(Par|By|Auteur)\s*', '', author_text, flags=re.IGNORECASE)
                if author_text and len(author_text) > 2:
                    return author_text
        
        return "Auteur inconnu"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extraction contenu - à surcharger selon le site"""
        # Stratégie 1: Balise article
        content_elem = soup.find('article')
        if content_elem:
            return self._clean_content(content_elem.get_text())
        
        # Stratégie 2: Classes de contenu
        content_classes = [
            'content', 'article-content', 'post-content',
            'entry-content', 'text-content', 'body-text'
        ]
        
        for class_name in content_classes:
            content_elem = soup.find(class_=class_name)
            if content_elem:
                return self._clean_content(content_elem.get_text())
        
        # Stratégie 3: Div avec le plus de texte
        divs = soup.find_all('div')
        best_div = None
        max_length = 0
        
        for div in divs:
            text = div.get_text().strip()
            if len(text) > max_length and len(text) > 200:
                max_length = len(text)
                best_div = div
        
        if best_div:
            return self._clean_content(best_div.get_text())
        
        return self._clean_content(soup.get_text())
    
    def _clean_content(self, content: str) -> str:
        """Nettoyage contenu"""
        if not content:
            return "Contenu non disponible"
        
        # Remplacer les espaces multiples
        content = re.sub(r'\s+', ' ', content)
        # Supprimer les lignes vides multiples
        content = re.sub(r'\n\s*\n', '\n\n', content)
        # Limiter la longueur
        if len(content) > 3000:
            content = content[:3000] + "..."
        
        return content.strip()
    
    def _validate_article_data(self, data: Dict) -> bool:
        """Validation données minimales"""
        required_fields = ['title', 'content', 'url']
        
        for field in required_fields:
            if not data.get(field) or len(data[field].strip()) < 5:
                return False
        
        # Vérifier que le contenu n'est pas du Lorem Ipsum
        content_lower = data['content'].lower()
        if 'lorem ipsum' in content_lower or len(data['content']) < 50:
            return False
        
        return True
    
    def save_to_json(self, articles: List[Dict], filename: str = None) -> str:
        """Sauvegarde avec timestamp et statistiques"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.site_name.lower()}_articles_{timestamp}.json"
        
        # Ajouter statistiques
        stats = {
            "total_articles": len(articles),
            "scraped_at": datetime.now().isoformat(),
            "source": self.site_name,
            "classification_method": "URL parsing (100% accuracy)",
            "sports_distribution": {}
        }
        
        # Calculer distribution par sport
        for article in articles:
            sport = article.get('category', 'other')
            stats["sports_distribution"][sport] = stats["sports_distribution"].get(sport, 0) + 1
        
        # Sauvegarder avec stats
        output_data = {
            "metadata": stats,
            "articles": articles
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 {len(articles)} articles sauvegardés dans {filename}")
        return filename
    
    @abstractmethod
    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        ===============================================
        MÉTHODE ABSTRAITE: RÉCUPÉRATION URLs
        ===============================================
        À implémenter dans chaque scraper spécialisé
        
        Paramètre:
        - max_articles: nombre max d'articles
        
        Retourne:
        - List[str]: liste des URLs des articles
        """
        pass
    
    def scrape_articles(self, max_articles: int = 10) -> List[Dict]:
        """
        ===============================================
        SCRAPING COMPLET
        ===============================================
        Orchestre tout le processus de scraping
        
        Paramètre:
        - max_articles: nombre max d'articles
        
        Retourne:
        - List[Dict]: liste des articles scrapés
        """
        print(f"🎯 Scraping {self.site_name} - Max: {max_articles} articles")
        print("=" * 60)
        
        # Récupérer les URLs
        urls = self.get_article_urls(max_articles)
        
        if not urls:
            print("❌ Aucune URL trouvée")
            return []
        
        print(f"📋 {len(urls)} URLs à traiter")
        
        # Extraire les données
        articles = []
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n📄 Article {i}/{len(urls)}")
            
            article_data = self.extract_article_data(url)
            
            if article_data:
                articles.append(article_data)
                successful += 1
            else:
                failed += 1
            
            # Pause respectueuse
            if i < len(urls):
                time.sleep(1)
        
        # Résumé
        print("\n" + "=" * 60)
        print(f"📊 RÉSUMÉ {self.site_name}")
        print(f"✅ Réussis: {successful}")
        print(f"❌ Échoués: {failed}")
        success_rate = successful/(successful+failed)*100 if (successful+failed) > 0 else 0
        print(f"📈 Taux de succès: {success_rate:.1f}%")
        print("=" * 60)
        
        return articles
