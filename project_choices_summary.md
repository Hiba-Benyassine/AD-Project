# Résumé des choix validés - Projet ETL Sport

## 🎯 Domaine principal
**Sport** - Plateforme Big Data pour les articles sportifs

## 🏷️ Sous-catégories choisies
- **Football** ⚽
- **Basketball** 🏀  
- **Tennis** 🎾

*Objectif: Filtrage précis et analyses ciblées*

## 🌍 Sources de données choisies (5 sources)

### 🇲🇦 Sites marocains
1. **360Sport.ma** - Site spécialisé sport marocain
2. **MSport.ma** - Actualités sportives marocaines  
3. **Le Matin.ma** - Journal généraliste avec section sport

### 🌍 Sites internationaux
4. **L'Équipe** (france.fr) - Leader sportif européen
5. **ESPN** (espn.com) - Géant sportif américain

## 🏗️ Objectif du projet
Construire une plateforme Big Data complète :

1. **Scraping automatique** des articles sportifs
2. **Stockage** dans Data Lake (MinIO)
3. **Nettoyage** et transformation des données
4. **Classification** automatique par sport
5. **Analyses** : tendances, volume, fréquence
6. **Dashboard** pour visualisation

## 📊 Structure de données attendue
```json
{
  "title": "Titre de l'article",
  "author": "Nom de l'auteur", 
  "date": "2024-01-15T10:30:00",
  "content": "Contenu de l'article...",
  "category": "football|basketball|tennis|other",
  "source": "360Sport|MSport|LeMatin|LEquipe|ESPN",
  "url": "https://...",
  "scraped_at": "2024-01-15T10:35:00"
}
```

## 🚀 Plan d'exécution prioritaire

### Étape 1 (Priorité absolue) 🔥
**Créer le Scraper Test**
- Site cible: 360Sport.ma ou LeMatin.ma
- Modèle réutilisable pour tous les autres sites

### Ordre de travail séquentiel
1. ✅ Définition périmètre  
2. 🔄 **Scraper test** (EN COURS)
3. Scraping des 5 sites
4. Stockage Bronze (Data Lake)
5. Nettoyage Silver
6. Classification sport  
7. Analyse Gold
8. PostgreSQL
9. Dashboard
10. Airflow
11. Finalisation + Présentation

## ⚠️ Règles importantes
- **NE PAS** passer à Airflow/Kafka/Dashboard avant scraping fonctionnel
- **FOCUS** sur le scraper test comme priorité #1
- **VALIDATION** du modèle avant duplication aux autres sources

---
*Document validé par l'équipe - Date: 23/04/2026*
