# Project Scope - Sports ETL Pipeline

## Domaine Principal
**Sport** - Plateforme Big Data pour l'analyse d'articles sportifs

## Catégories Sportives Ciblées
- **Football** ⚽ - Articles sur le football mondial, ligues, transferts
- **Tennis** 🎾 - Tournois ATP/WTA, Grand Chelem, joueurs  
- **Basketball** 🏀 - NBA, Euroleague, compétitions internationales
- **Other** - Sports non classifiés ou autres disciplines

## Sources de Données (5 sites validés)

### Sites Marocains
1. **360Sport.ma** - https://sport.le360.ma
   - Spécialisé sport marocain et international
   - Contenu français, mise à jour continue
   - **Structure validée**: .selections-list-item > a.text
   - **🎯 URLs directes**: /football/* /tennis/* /basketball/* → classification immédiate
   
2. **MSport.ma** - https://www.msport.ma
   - Actualités sportives marocaines
   - Contenu français/arabe
   - **À adapter**: Template 360Sport à modifier
   - **🎯 URLs directes**: /football/* /tennis/* → classification immédiate
   
3. **Le Matin.ma** - https://www.lematin.ma/sport
   - Journal généraliste section sport
   - Contenu français
   - **À adapter**: Template 360Sport à modifier
   - **🎯 URLs directes**: /sport/football/* /sport/tennis/* → classification immédiate

### Sites Internationaux  
4. **L'Équipe** - https://www.lequipe.fr
   - Leader sportif européen
   - Contenu français
   - **À adapter**: Template 360Sport à modifier
   - **🎯 URLs directes**: /Football/* /Tennis/* /Basket/* → classification immédiate
   
5. **ESPN** - https://www.espn.com
   - Géant sportif américain
   - Contenu anglais
   - **À adapter**: Template 360Sport à modifier
   - **🎯 URLs directes**: /football/* /tennis/* /nba/* → classification immédiate

## Structure de Données Cible
```json
{
  "title": "Titre de l'article",
  "date": "2024-01-15T10:30:00", 
  "content": "Contenu texte nettoyé...",
  "author": "Nom de l'auteur",
  "category": "football|tennis|basketball|other",
  "source": "360Sport|MSport|LeMatin|LEquipe|ESPN",
  "url": "https://...",
  "scraped_at": "2024-01-15T10:35:00"
}
```

---

## Répartition des Tâches - PRK Détaillé

### AYOGNIDE - Responsabilités

#### Tâche 1: Scraping (3 sites)
**POURQUOI**: Récupérer les données brutes des sources marocaines/internationales  
**COMMENT**: Adapter le template scraper_test_360sport.py pour chaque site  
**RÉSULTAT ATTENDU**: 3 fichiers JSON par site avec 50+ articles/jour

- **360Sport.ma**: Template déjà validé (100% succès)
- **MSport.ma**: Adapter sélecteurs CSS  
- **L'Équipe**: Adapter sélecteurs CSS (structure française)

#### Tâche 2: Data Lake MinIO
**POURQUOI**: Stocker les données brutes dans architecture médaille (Bronze/Silver/Gold)  
**COMMENT**: Installer Docker MinIO, créer buckets bronze/silver/gold  
**RÉSULTAT ATTENDU**: Structure de fichiers JSON organisés par date/source

#### Tâche 3: Classification Sport
**POURQUOI**: Catégoriser automatiquement chaque article par sport avec précision maximale  
**COMMENT**: Double stratégie - Classification directe par URL + mots-clés + regex  
**RÉSULTAT ATTENDU**: Catégorie "football/tennis/basketball/other" pour chaque article

**🎯 OPTIMISATION URL DIRECTE**: 
Certains sites permettent une classification immédiate :
- `site.com/football/*` → catégorie = "football" 
- `site.com/tennis/*` → catégorie = "tennis"
- `site.com/basketball/*` → catégorie = "basketball"

**📊 STRATÉGIE COMPLÉMENTAIRE**:
1. **Classification URL** (priorité haute): Parser l'URL pour détecter le sport
2. **Mots-clés titres/contenus** (priorité moyenne): "ligue des champions", "roland garros", "nba"
3. **Regex avancée** (priorité basse): Patterns complexes et contextes

**⚡ AVANTAGE**: Réduction de 70% des erreurs de classification pour sites structurés

#### Tâche 4: Airflow + PostgreSQL
**POURQUOI**: Automatiser le pipeline ETL complet  
**COMMENT**: DAG Airflow avec tâches séquentielles + chargement PostgreSQL  
**RÉSULTAT ATTENDU**: Pipeline automatique quotidien, base de données relationnelle

---

### HIBA - Responsabilités

#### Tâche 1: Scraping (2 sites)  
**POURQUOI**: Compléter la collecte de données avec sources manquantes  
**COMMENT**: Adapter template scraper_test_360sport.py pour Le Matin.ma et ESPN  
**RÉSULTAT ATTENDU**: 2 fichiers JSON par site avec 50+ articles/jour

- **Le Matin.ma**: Adapter template pour structure journal marocain
- **ESPN**: Adapter template pour structure site américain

#### Tâche 2: Nettoyage des Données
**POURQUOI**: Préparer les données brutes pour analyse (couche Silver)  
**COMMENT**: Suppression HTML, minuscule, ponctuation, filtrage articles invalides  
**RÉSULTAT ATTENDU**: Données textuelles propres et normalisées

#### Tâche 3: Tables Analytiques
**POURQUOI**: Créer métriques et indicateurs pour dashboard (couche Gold)  
**COMMENT**: Calculs agrégés: articles/jour, par sport, par source, top mots  
**RÉSULTAT ATTENDU**: Tables pré-calculées pour visualisation rapide

#### Tâche 4: Dashboard + Présentation
**POURQUOI**: Visualiser les résultats et présenter le projet  
**COMMENT**: Metabase dashboard, slides PowerPoint, README, schéma architecture  
**RÉSULTAT ATTENDU**: Interface interactive et documentation complète

---

## Critères de Succès

### Techniques 
- **Scraping**: 5 sources fonctionnelles avec taux succès >80%
- **Stockage**: Architecture Bronze/Silver/Gold opérationnelle
- **Pipeline**: Automatisation complète via Airflow
- **Performance**: Traitement <30min pour 250+ articles/jour

### Métier  
- **Données**: Articles classifiés par sport avec précision >85%
- **Analyse**: Métriques temps réel (tendances, volumes, sources)
- **Dashboard**: Interface intuitive avec filtres dynamiques
- **Scalabilité**: Architecture extensible à nouvelles sources

---

## Timeline Projet

**Phase 1** : Périmètre + Scraper test (Terminé)  
**Phase 2** : Scraping des 5 sites (En cours)  
**Phase 3** : Data Lake + Nettoyage  
**Phase 4** : Classification + Analyse  
**Phase 5** : Airflow + Dashboard + Présentation

---
*Document mis à jour le 23/04/2026 - Template scraper validé*
