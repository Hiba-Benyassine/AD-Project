#!/usr/bin/env python3
"""
===============================================
SCRAPER TEST - 360Sport.ma
===============================================
Auteur: Équipe ETL Sport
Date: 23/04/2026
Objectif: Créer un modèle de scraper fonctionnel pour tous les sites sportifs

Ce scraper servira de TEMPLATE pour tous les autres scrapers du projet.
Il récupère les 7 champs essentiels définis dans le cahier des charges.
"""

# Import des bibliothèques nécessaires
import requests          # Pour les requêtes HTTP
from bs4 import BeautifulSoup  # Pour parser le HTML
import json              # Pour sauvegarder en JSON
from datetime import datetime  # Pour gérer les dates
import time              # Pour les pauses entre requêtes
import re                # Pour les expressions régulières
from typing import Dict, Optional, List  # Pour le typage

class Sport360Scraper:
    """
    ===============================================
    CLASSE PRINCIPALE DU SCRAPER
    ===============================================
    Cette classe encapsule toute la logique de scraping pour 360Sport.ma
    Elle est conçue pour être facilement adaptable aux autres sites.
    """
    
    def __init__(self):
        """
        CONSTRUCTEUR - Initialisation du scraper
        ===============================================
        Configure les URLs de base et les en-têtes HTTP
        L'en-tête User-Agent simule un navigateur réel pour éviter le blocage
        """
        # URL principale du site - CORRECTION: sport.le360.ma est la vraie URL
        self.base_url = "https://sport.le360.ma"
        
        # URL de la section sport (généralement la page d'accueil pour ce site)
        self.sports_url = "https://sport.le360.ma"
        
        # En-têtes HTTP pour simuler un navigateur Chrome
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Session HTTP pour maintenir la connexion et réutiliser les cookies
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        print("🚀 Scraper 360Sport.ma initialisé")
    
    def get_article_urls(self, max_articles: int = 10) -> List[str]:
        """
        ===============================================
        MÉTHODE: Récupération des URLs d'articles
        ===============================================
        Objectif: Parcourir la page d'accueil et extraire les liens des articles
        
        Paramètre:
        - max_articles: nombre maximum d'articles à récupérer (pour tests)
        
        Retourne:
        - List[str]: liste des URLs complets des articles
        """
        print(f"🔍 Recherche des articles sur {self.sports_url}")
        
        try:
            # ÉTAPE 1: Récupérer le contenu de la page
            response = self.session.get(self.sports_url, timeout=10)
            response.raise_for_status()  # Lève une exception si erreur HTTP
            
            # ÉTAPE 2: Parser le HTML avec BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []
            
            # ÉTAPE 3: Trouver les liens d'articles
            # STRATÉGIE: Utiliser la structure HTML exacte de sport.le360.ma
            # Basé sur l'HTML fourni par l'utilisateur
            
            # Pattern PRINCIPAL: Liens dans les cartes d'articles .selections-list-item
            article_links = soup.find_all('div', class_='selections-list-item')
            all_links = []
            
            # Extraire les liens de chaque carte d'article
            for item in article_links:
                # Chercher le lien principal (généralement le premier avec class="text")
                text_link = item.find('a', class_='text')
                if text_link and text_link.get('href'):
                    all_links.append(text_link)
                else:
                    # Alternative: chercher n'importe quel lien dans l'item
                    link = item.find('a')
                    if link and link.get('href'):
                        all_links.append(link)
            
            # Pattern 2: Si aucun résultat, chercher tous les liens dans la section main
            if not all_links:
                main_section = soup.find('section', role='main')
                if main_section:
                    all_links = main_section.find_all('a', href=re.compile(r'/'))
            
            print(f"📊 {len(all_links)} liens potentiels trouvés")
            
            # ÉTAPE 4: Nettoyer et dédupliquer les URLs
            for link in all_links[:max_articles * 2]:  # Prendre plus pour filtrer
                href = link.get('href')
                if href and self._is_valid_article_url(href):
                    # Construire l'URL complet si nécessaire
                    if href.startswith('/'):
                        full_url = self.base_url + href
                    elif not href.startswith('http'):
                        full_url = self.base_url + '/' + href
                    else:
                        full_url = href
                    
                    # Éviter les doublons
                    if full_url not in articles and len(articles) < max_articles:
                        articles.append(full_url)
            
            print(f"✅ {len(articles)} URLs valides extraites")
            return articles
            
        except requests.RequestException as e:
            print(f"❌ Erreur HTTP lors de la récupération des URLs: {e}")
            return []
        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return []
    
    def _is_valid_article_url(self, url: str) -> bool:
        """
        ===============================================
        MÉTHODE PRIVÉE: Validation des URLs
        ===============================================
        Filtre les URLs pour ne garder que les articles pertinents
        """
        # Exclure les pages non-articles
        exclude_patterns = [
            r'/category/', r'/tag/', r'/author/', r'/page/',
            r'/contact', r'/about', r'/#', r'javascript:',
            r'.jpg', r'.png', r'.pdf', r'.css', r'.js'
        ]
        
        for pattern in exclude_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        # Inclure les patterns d'articles
        include_patterns = [
            r'\d{4}/\d{2}/',  # Dates dans URL
            r'article', r'news', r'match', r'football'
        ]
        
        # Si aucun pattern d'inclusion, on accepte quand même
        return True
    
    def extract_article_data(self, url: str) -> Optional[Dict]:
        """
        ===============================================
        MÉTHODE: Extraction des données d'un article
        ===============================================
        Objectif: Extraire les 7 champs requis d'un article
        
        Paramètre:
        - url: URL de l'article à scraper
        
        Retourne:
        - Dict: dictionnaire avec les 7 champs ou None si erreur
        """
        print(f"📖 Extraction: {url}")
        
        try:
            # ÉTAPE 1: Récupérer la page de l'article
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # ÉTAPE 2: Parser le HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ÉTAPE 3: Extraire chaque champ avec stratégies multiples
            
            # CHAMP 1: TITRE
            title = self._extract_title(soup)
            
            # CHAMP 2: DATE
            date = self._extract_date(soup)
            
            # CHAMP 3: AUTEUR  
            author = self._extract_author(soup)
            
            # CHAMP 4: CONTENU
            content = self._extract_content(soup)
            
            # CHAMP 5: CATÉGORIE (sera classifiée plus tard)
            category = "other"  # Valeur par défaut, sera surchargée par classification
            
            # CHAMP 6: SOURCE
            source = "360Sport"
            
            # CHAMP 7: URL
            article_url = url
            
            # CHAMP 8: TIMESTAMP DE SCRAPING
            scraped_at = datetime.now().isoformat()
            
            # ÉTAPE 4: Construire le dictionnaire final
            article_data = {
                "title": title,
                "date": date,
                "content": content,
                "author": author,
                "category": category,
                "source": source,
                "url": article_url,
                "scraped_at": scraped_at
            }
            
            # ÉTAPE 5: Valider les données minimales
            if self._validate_article_data(article_data):
                print(f"✅ Données extraites: {title[:50]}...")
                return article_data
            else:
                print(f"⚠️ Données invalides, article ignoré")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Erreur HTTP {url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur extraction {url}: {e}")
            return None
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """
        ===============================================
        EXTRACTION: TITRE
        ===============================================
        Stratégies multiples pour trouver le titre de l'article
        Adapté spécifiquement pour sport.le360.ma
        """
        # Stratégie 1: Balise h1 avec classe le360-titre-title
        title_elem = soup.find('h1', class_='le360-titre-title')
        if title_elem:
            return title_elem.get_text().strip()
        
        # Stratégie 2: Balise h1 principale
        title_elem = soup.find('h1')
        if title_elem:
            return title_elem.get_text().strip()
        
        # Stratégie 3: Meta title
        title_elem = soup.find('meta', property='og:title')
        if title_elem:
            return title_elem.get('content', '').strip()
        
        # Stratégie 4: Balise title HTML
        title_elem = soup.find('title')
        if title_elem:
            title = title_elem.get_text().strip()
            # Nettoyer le titre du site
            return re.sub(r'\s*-\s*sport\.le360\.ma.*$', '', title)
        
        # Stratégie 5: Classes communes
        for class_name in ['title', 'headline', 'article-title']:
            title_elem = soup.find(class_=class_name)
            if title_elem:
                return title_elem.get_text().strip()
        
        return "Titre non trouvé"
    
    def _extract_date(self, soup: BeautifulSoup) -> str:
        """
        ===============================================
        EXTRACTION: DATE
        ===============================================
        Extraction et normalisation de la date de publication
        """
        # Stratégie 1: Balise time avec attribut datetime
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
        
        # Stratégie 4: Recherche par regex dans le texte
        text_content = soup.get_text()
        date_patterns = [
            r'\d{2}/\d{2}/\d{4}',  # JJ/MM/AAAA
            r'\d{4}-\d{2}-\d{2}',  # AAAA-MM-JJ
            r'\d{2}\s*\w+\s*\d{4}'  # JJ Mois AAAA
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text_content)
            if match:
                return self._normalize_date(match.group())
        
        # Par défaut: date actuelle
        return datetime.now().isoformat()
    
    def _normalize_date(self, date_str: str) -> str:
        """
        ===============================================
        NORMALISATION: DATE
        ===============================================
        Convertit divers formats de date en ISO standard
        """
        if not date_str:
            return datetime.now().isoformat()
        
        # Nettoyer la chaîne
        date_str = date_str.strip()
        
        # Formats à essayer
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
        
        # Si aucun format ne correspond, retourner la date actuelle
        return datetime.now().isoformat()
    
    def _extract_author(self, soup: BeautifulSoup) -> str:
        """
        ===============================================
        EXTRACTION: AUTEUR
        ===============================================
        Recherche du nom de l'auteur de l'article
        """
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
                # Nettoyer les préfixes communs
                author_text = re.sub(r'^(Par|By|Auteur)\s*', '', author_text, flags=re.IGNORECASE)
                if author_text and len(author_text) > 2:
                    return author_text
        
        # Stratégie 4: Recherche par regex
        text_content = soup.get_text()
        author_patterns = [
            r'Par\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'By\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
        
        for pattern in author_patterns:
            match = re.search(pattern, text_content)
            if match:
                return match.group(1)
        
        return "Auteur inconnu"
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        ===============================================
        EXTRACTION: CONTENU
        ===============================================
        Extraction du corps principal de l'article
        """
        # Stratégie 1: Balise article HTML5
        content_elem = soup.find('article')
        if content_elem:
            return self._clean_content(content_elem.get_text())
        
        # Stratégie 2: Classes de contenu communes
        content_classes = [
            'content', 'article-content', 'post-content',
            'entry-content', 'text-content', 'body-text'
        ]
        
        for class_name in content_classes:
            content_elem = soup.find(class_=class_name)
            if content_elem:
                return self._clean_content(content_elem.get_text())
        
        # Stratégie 3: Div principale avec beaucoup de texte
        divs = soup.find_all('div')
        best_div = None
        max_length = 0
        
        for div in divs:
            text = div.get_text().strip()
            if len(text) > max_length and len(text) > 200:  # Seuil minimum
                max_length = len(text)
                best_div = div
        
        if best_div:
            return self._clean_content(best_div.get_text())
        
        # Stratégie 4: Dernier recours - tout le body
        return self._clean_content(soup.get_text())
    
    def _clean_content(self, content: str) -> str:
        """
        ===============================================
        NETTOYAGE: CONTENU
        ===============================================
        Nettoie le texte extrait pour le rendre lisible
        """
        if not content:
            return "Contenu non disponible"
        
        # Remplacer les espaces multiples par des espaces simples
        content = re.sub(r'\s+', ' ', content)
        
        # Supprimer les lignes vides multiples
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Limiter la longueur pour éviter les articles trop longs
        if len(content) > 3000:
            content = content[:3000] + "..."
        
        return content.strip()
    
    def _validate_article_data(self, data: Dict) -> bool:
        """
        ===============================================
        VALIDATION: DONNÉES
        ===============================================
        Vérifie que les données minimales sont présentes
        """
        # Champs obligatoires
        required_fields = ['title', 'content', 'url']
        
        for field in required_fields:
            if not data.get(field) or len(data[field].strip()) < 5:
                return False
        
        # Vérifier que le contenu n'est pas juste du "Lorem Ipsum"
        content_lower = data['content'].lower()
        if 'lorem ipsum' in content_lower or len(data['content']) < 50:
            return False
        
        return True
    
    def scrape_articles(self, max_articles: int = 5) -> List[Dict]:
        """
        ===============================================
        MÉTHODE PRINCIPALE: SCRAPING COMPLET
        ===============================================
        Orchestre tout le processus de scraping
        
        Paramètre:
        - max_articles: nombre maximum d'articles à scraper
        
        Retourne:
        - List[Dict]: liste des articles scrapés
        """
        print(f"🎯 DÉBUT DU SCRAPING 360Sport.ma - Max: {max_articles} articles")
        print("=" * 60)
        
        # ÉTAPE 1: Récupérer la liste des URLs
        urls = self.get_article_urls(max_articles)
        
        if not urls:
            print("❌ Aucune URL trouvée - arrêt du scraping")
            return []
        
        print(f"📋 {len(urls)} URLs à traiter")
        
        # ÉTAPE 2: Extraire les données de chaque article
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
            
            # Pause respectueuse entre les requêtes
            if i < len(urls):
                print("⏳ Pause de 2 secondes...")
                time.sleep(2)
        
        # ÉTAPE 3: Résumé du scraping
        print("\n" + "=" * 60)
        print(f"📊 RÉSUMÉ DU SCRAPING")
        print(f"✅ Réussis: {successful}")
        print(f"❌ Échoués: {failed}")
        print(f"📈 Taux de succès: {successful/(successful+failed)*100:.1f}%")
        print("=" * 60)
        
        return articles
    
    def save_to_json(self, articles: List[Dict], filename: str = None) -> str:
        """
        ===============================================
        SAUVEGARDE: FICHIER JSON
        ===============================================
        Sauvegarde les articles dans un fichier JSON
        
        Paramètres:
        - articles: liste des articles à sauvegarder
        - filename: nom du fichier (généré automatiquement si None)
        
        Retourne:
        - str: nom du fichier créé
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"360sport_articles_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, ensure_ascii=False, indent=2)
            
            print(f"💾 {len(articles)} articles sauvegardés dans {filename}")
            return filename
            
        except Exception as e:
            print(f"❌ Erreur lors de la sauvegarde: {e}")
            return ""

def main():
    """
    ===============================================
    FONCTION PRINCIPALE - POINT D'ENTRÉE
    ===============================================
    Fonction de test pour valider le scraper
    """
    print("🚀 LANCEMENT DU SCRAPER TEST - 360Sport.ma")
    print("🎯 Objectif: Valider le modèle pour tous les sites")
    print("=" * 60)
    
    # Créer l'instance du scraper
    scraper = Sport360Scraper()
    
    # Lancer le scraping (limité à 3 articles pour le test)
    articles = scraper.scrape_articles(max_articles=3)
    
    if articles:
        # Sauvegarder les résultats
        filename = scraper.save_to_json(articles)
        
        # Afficher un exemple d'article
        print(f"\n📋 EXEMPLE D'ARTICLE:")
        print("-" * 40)
        print(json.dumps(articles[0], ensure_ascii=False, indent=2))
        
        print(f"\n🎉 SCRAPER TEST FONCTIONNEL!")
        print(f"📁 Fichier créé: {filename}")
        print(f"✅ Prêt à être adapté pour les autres sites")
        
    else:
        print("\n❌ ÉCHEC DU SCRAPER TEST")
        print("🔧 Vérifier la structure HTML du site et ajuster les sélecteurs")

if __name__ == "__main__":
    main()
