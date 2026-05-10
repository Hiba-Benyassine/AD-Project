# Rapport de Projet : Plateforme Big Data d'Actualités Sportives

## 1. Introduction
Ce projet implémente une plateforme Big Data de bout en bout capable d'ingérer, stocker, transformer et analyser des articles de presse. Nous nous sommes concentrés sur la verticale "Sport" (L'Équipe, ESPN, Sport360, Le Matin) pour extraire des tendances claires. La plateforme répond à 100% des exigences de l'architecture de données distribuée demandée.

## 2. Architecture de Données

### 2.1. Ingestion (Batch & Streaming)
- **Batch** : Des scrapers automatisés (Python + BeautifulSoup) s'exécutent toutes les heures pour collecter massivement les articles sur nos sources sportives.
- **Streaming** : Nous avons implémenté **Apache Kafka** et **Zookeeper**. Cette partie est entièrement automatisée via un conteneur dédié (`kafka-producer`). Chaque article publié est capturé en temps réel (via une écoute continue des flux RSS). Un mécanisme de **dédoublonnement intelligent** est intégré : avant chaque envoi vers Kafka, le système vérifie l'existence de l'URL dans le Data Warehouse (PostgreSQL) pour éviter toute duplication inutile de données. Les messages sont ensuite interceptés par un Consumer Kafka qui les sauvegarde instantanément dans le Data Lake.

### 2.2. Data Lake
Toutes les données brutes sont ingérées et stockées de manière persistante sur un Data Lake S3-compatible : **MinIO**. Les fichiers sont historisés dans le bucket `bronze`.

### 2.3. Architecture Médaillon
Le traitement des données suit strictement l'approche Médaillon :
- **Bronze** : Données brutes (JSON/JSONL) stockées dans MinIO.
- **Silver** : Données nettoyées (script `cleaning.py`). Suppression des balises HTML, normalisation Unicode du texte, détection de la langue d'origine, et application des règles de Qualité.
- **Gold** : Données enrichies (scripts de classification et d'analytique). Catégorisation des sports, **extraction automatique de mots-clés (Keywords)** pour l'analyse de fréquences, puis chargement dans le Data Warehouse.

### 2.4. Orchestration
L'ensemble des pipelines (Scraping -> Cleaning -> Classification -> Gold -> Load_to_DB) est orchestré par **Apache Airflow**. Un DAG (Directed Acyclic Graph) gère la planification horaire et la reprise sur erreur.

### 2.5. Data Warehouse & Visualisation
- **Data Warehouse** : PostgreSQL est utilisé pour stocker les tables analytiques (Articles par jour, Tendances, Sources).
- **Visualisation** : Metabase est connecté au Data Warehouse pour exposer les tableaux de bord décisionnels.

## 3. Qualité des Données et Gouvernance

Une étape critique de la couche "Silver" est la validation de la qualité des données. 
Nous évaluons trois dimensions principales :
- **Complétude** : Un article doit obligatoirement avoir un titre et une URL source.
- **Validité** : Une date de publication ou de scraping au format ISO 8601 doit être présente.
- **Cohérence** : Le contenu de l'article doit être pertinent (minimum 100 caractères).

**Traçabilité et Monitoring :**
Toutes les anomalies détectées lors du traitement Silver sont quantifiées et enregistrées dans un rapport généré automatiquement : `data/silver/data_quality_report.json`. Ce fichier garantit la gouvernance et permet un audit transparent sur le volume d'articles rejetés et leurs raisons (titre manquant, contenu trop court, date invalide).

## 4. Guide de Démarrage Rapide (Automatisé)

1. Lancer l'infrastructure complète et surveiller l'état de santé du système :
   ```bash
   ./start.sh
   ```
   *(Ou `.\start.bat` sous Windows PowerShell)*
   Ce script garantit que **PostgreSQL**, **Kafka** et le **Streaming** sont prêts avant de vous rendre la main.

2. Accéder aux outils :
   - Airflow : `http://localhost:8080` (admin/admin).
   - Metabase : `http://localhost:3000` (Analyses en temps réel).
   - MinIO : `http://localhost:9001` (Exploration du Data Lake).

3. Visualisation des Top Mots :
   Grâce à la nouvelle colonne `keywords`, vous pouvez désormais grouper par mots-clés dans Metabase pour identifier instantanément les sujets brûlants (ex: transfert, penalty, victoire).
