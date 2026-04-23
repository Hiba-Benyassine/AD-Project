# 📁 Structure des Scrapers - Architecture Modulaire

## 🏗️ Architecture

```
scrapers/
├── base_scraper.py          # 📋 Classe mère (logique commune)
├── sport360_scraper.py      # ✅ 360Sport.ma (fonctionnel)
├── msport_scraper.py        # 🔄 MSport.ma (template à adapter)
├── lematin_scraper.py       # 🔄 LeMatin.ma (template à adapter)
├── lequipe_scraper.py       # 🔄 L'Équipe.fr (template à adapter)
├── espn_scraper.py          # 🔄 ESPN.com (template à adapter)
└── README.md                # 📖 Ce fichier
```

## 🎯 Avantages de cette structure

### ✅ Séparation des métiers
- **BaseScraper**: Logique commune (HTTP, extraction, validation)
- **Scrapers spécialisés**: 50-100 lignes par site (vs 474 lignes!)
- **Maintenance facile**: Changer un site ne casse pas les autres

### 🔄 Héritage optimisé
```python
class Sport360Scraper(BaseScraper):
    def __init__(self):
        super().__init__("360Sport", "https://sport.le360.ma")
    
    def get_article_urls(self, max_articles=10):
        # Seule la logique spécifique au site
```

### 📊 Fonctionnalités héritées automatiquement
- Classification directe par URL (100% précision)
- Extraction des 7 champs requis
- Nettoyage et validation
- Sauvegarde JSON avec statistiques
- Gestion des erreurs

## 📋 État des scrapers

| Site | Fichier | État | Lignes | Qui adapte |
|------|---------|------|--------|------------|
| **360Sport.ma** | `sport360_scraper.py` | ✅ **FONCTIONNEL** | 120 | - |
| **MSport.ma** | `msport_scraper.py` | 🔄 **TEMPLATE** | 95 | AYOGNIDE |
| **L'Équipe.fr** | `lequipe_scraper.py` | 🔄 **À CRÉER** | - | AYOGNIDE |
| **LeMatin.ma** | `lematin_scraper.py` | 🔄 **TEMPLATE** | 90 | HIBA |
| **ESPN.com** | `espn_scraper.py` | 🔄 **À CRÉER** | - | HIBA |

## 🔧 Comment adapter un scraper template

### Étape 1: Inspecter le HTML
```bash
# Ouvrir le site dans le navigateur
# F12 → Elements → Analyser la structure
# Chercher les sélecteurs CSS pour:
# - Liens d'articles
# - Titres (h1, .title, etc.)
# - Dates (time, .date, etc.)
# - Auteurs (.author, etc.)
```

### Étape 2: Adapter les sélecteurs
```python
def get_article_urls(self, max_articles=10):
    # Remplacer ces sélecteurs par les bons
    article_selectors = [
        'a[href*="/article/"]',    # 👈 Adapter
        '.article-title a',        # 👈 Adapter
        'h3 a'                     # 👈 Adapter
    ]
```

### Étape 3: Tester
```bash
python msport_scraper.py
```

### Étape 4: Valider
- Taux de succès > 80%
- Classification directe fonctionne
- 7 champs extraits correctement

## 🚀 Lancement rapide

### Scraper fonctionnel (360Sport)
```bash
python sport360_scraper.py
# Résultat: 360sport_articles_YYYYMMDD_HHMMSS.json
```

### Templates à adapter
```bash
python msport_scraper.py      # AYOGNIDE
python lematin_scraper.py    # HIBA
```

## 📊 Structure de données générée

```json
{
  "metadata": {
    "total_articles": 5,
    "scraped_at": "2026-04-23T17:36:00",
    "source": "360Sport",
    "classification_method": "URL parsing (100% accuracy)",
    "sports_distribution": {"football": 5}
  },
  "articles": [
    {
      "title": "Titre de l'article",
      "date": "2026-04-23T00:00:00",
      "content": "Contenu texte...",
      "author": "Auteur",
      "category": "football",
      "source": "360Sport", 
      "url": "https://...",
      "scraped_at": "2026-04-23T17:36:00"
    }
  ]
}
```

## 🎯 Prochaines étapes

### AYOGNIDE (3 scrapers)
1. ✅ 360Sport.ma - **TERMINÉ**
2. 🔄 MSport.ma - Adapter template (95 lignes)
3. 🔄 L'Équipe.fr - Créer depuis template

### HIBA (2 scrapers)  
1. 🔄 LeMatin.ma - Adapter template (90 lignes)
2. 🔄 ESPN.com - Créer depuis template

## 💡 Tips d'adaptation

### URLs directes par sport
```python
self.sport_urls = {
    "football": "https://site.com/football",
    "tennis": "https://site.com/tennis", 
    "basketball": "https://site.com/basketball"
}
```

### Sélecteurs CSS communs
```python
# Articles
'article a', '.post a', '.news-item a', 'h2 a', 'h3 a'

# Titres  
'h1', '.title', '.article-title', '.post-title'

# Dates
'time', '.date', '.publish-date', '.post-date'

# Auteurs
'.author', '.byline', '.writer', '.post-author'
```

---
**Structure optimisée**: 474 lignes → 5 fichiers de 90-120 lignes chacun ! 🚀
