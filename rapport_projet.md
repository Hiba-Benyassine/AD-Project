# Rapport de Projet : Plateforme Big Data d'Actualités Sportives

## 1. Introduction
Ce projet implémente une plateforme Big Data de bout en bout capable d'ingérer, stocker, transformer et analyser des articles de presse. Nous nous sommes concentrés sur la verticale "Sport" (L'Équipe, ESPN, Sport360, Le Matin) pour extraire des tendances claires. La plateforme répond à 100% des exigences de l'architecture de données distribuée demandée.

## 2. Architecture de Données

### 2.1. Ingestion (Batch & Streaming)
- **Batch** : Des scrapers automatisés (Python + BeautifulSoup) s'exécutent toutes les heures pour collecter massivement les articles sur nos sources sportives.
- **Streaming (Temps Réel)** : Utilisation d'**Apache Kafka** pour une ingestion à faible latence. Le `kafka-producer` interroge les sources sportives en continu. Pour garantir l'intégrité, chaque article est dédoublonné en temps réel contre la base PostgreSQL avant d'être envoyé dans le topic `news_stream`. Le `kafka-consumer` intercepte ces messages, les stocke dans le Data Lake (MinIO) et les injecte **instantanément** dans le Data Warehouse (PostgreSQL) pour une visualisation immédiate dans Metabase.

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

## 3. Fonctionnalités Avancées (Analytique & Monitoring)

### 3.1. Extraction de Mots-clés en Temps Réel
Pour répondre au besoin d'analyse des "Top sujets", nous avons intégré un module d'extraction de mots-clés (`extract_keywords`). Ce module analyse le contenu de chaque article pour identifier les termes sportifs prépondérants (ex: *mercato, but, victoire, penalty*). Ces mots-clés sont stockés dans une colonne dédiée, permettant des analyses de fréquence immédiates dans Metabase.

### 3.2. Backfill Historique
Afin de ne pas démarrer avec une plateforme vide, un script de **Backfill** (`backfill_last_4_days.py`) a été développé. Il permet de remonter sur les 4 derniers jours de publications pour toutes les sources, garantissant une richesse de données dès le premier jour.

### 3.3. Dashboard de Santé et Monitoring
Le déploiement est sécurisé par un script de monitoring (`start.sh` / `start.bat`) qui :
1. Lance l'infrastructure Docker.
2. Teste la disponibilité de PostgreSQL, Kafka et MinIO.
3. Valide le bon fonctionnement du flux de streaming avant de confirmer l'état "Opérationnel" du système.

## 4. Qualité des Données et Gouvernance
Une étape critique de la couche "Silver" est la validation de la qualité des données. 
Nous évaluons trois dimensions principales :
- **Complétude** : Un article doit obligatoirement avoir un titre et une URL source.
- **Validité** : Une date de publication ou de scraping au format ISO 8601 doit être présente.
- **Cohérence** : Le contenu de l'article doit être pertinent (minimum 100 caractères).

**Traçabilité et Monitoring :**
Toutes les anomalies détectées lors du traitement Silver sont quantifiées et enregistrées dans un rapport généré automatiquement : `data/silver/data_quality_report.json`.

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
