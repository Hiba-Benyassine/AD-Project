# Trame de Présentation : Plateforme Big Data d'Actualités Sportives

*(Ce document est un plan détaillé pour vous aider à créer vos slides PowerPoint/Canva pour la soutenance)*

---

## Slide 1 : Titre
**Titre :** Conception d'une Plateforme Big Data d'Actualités Sportives
**Sous-titre :** Projet d'Architecture de Données - EMSI
**Noms :** [Vos Noms]
**Date :** 10 Mai 2026

---

## Slide 2 : Contexte et Objectifs
- **Le besoin :** Collecter, stocker et analyser des milliers d'articles de presse sportive (L'Équipe, ESPN, Sport360, Le Matin).
- **L'objectif :** Mettre en place une architecture distribuée moderne (Data Lake, Data Warehouse) capable de gérer le Batch et le Streaming.
- **Les cas d'usage :** Suivi des tendances, top sujets par sport, analyse de l'activité médiatique.

---

## Slide 3 : Architecture Globale
*(Insérer ici un schéma visuel de l'architecture si possible)*
- **Ingestion :** Scrapers Python (BeautifulSoup) + Apache Kafka (Streaming).
- **Stockage Brut (Data Lake) :** MinIO (S3-compatible).
- **Transformation :** Architecture Médaillon (Python/Pandas).
- **Stockage Analytique (Data Warehouse) :** PostgreSQL.
- **Orchestration :** Apache Airflow.
- **Visualisation :** Metabase.

---

## Slide 4 : Ingestion Hybride (Batch & Streaming)
- **Batch (Airflow) :** Scraping automatisé planifié toutes les heures. Idéal pour récupérer l'historique massif.
- **Streaming (Kafka) :** Ingestion à faible latence (quelques secondes).
- **Dédoublonnement Intelligent :** Vérification systématique contre PostgreSQL avant envoi vers Kafka pour éviter les doublons.
- **Ingestion Directe :** Le Consumer Kafka écrit directement dans PostgreSQL pour bypasser les délais d'Airflow.

---

## Slide 5 : L'Architecture Médaillon
- **Couche Bronze :** Stockage immuable de l'historique brut dans MinIO (`.json`).
- **Couche Silver :** Nettoyage (suppression HTML, normalisation texte, détection de langue).
- **Couche Gold (Enrichissement) :** Extraction automatique de **Mots-clés (Keywords)** pour l'analyse sémantique.
- **Data Backfill :** Script de récupération historique des 4 derniers jours pour peupler le dashboard immédiatement.

---

## Slide 6 : Analytique Temps Réel & Mots-clés
- **Fonctionnalité :** Détection automatique des sujets brûlants.
- **Keywords :** "mercato", "victoire", "transfert", "penalty", etc.
- **Visualisation :** Top mots les plus fréquents par sport et par source.
- **Rattrapage :** Script dédié pour enrichir les données anciennes rétroactivement.

---

## Slide 7 : Monitoring & Fiabilité
- **Start Dashboard :** Scripts de démarrage automatisés (`start.sh` / `start.bat`).
- **Health Checks :** Validation automatique de la connectivité (Postgres, Kafka, MinIO).
- **Rapport Qualité :** Monitoring des taux de complétude et de rejet en temps réel.

---

## Slide 7 : Orchestration & Tableaux de bord
- **Airflow :** Un DAG (`sports_data_pipeline`) gère tout le cycle de vie de la donnée avec des alertes et des reprises sur erreur.
- **Metabase :** Tableaux de bord en temps réel connectés à PostgreSQL.
*(Insérer des captures d'écran du DAG Airflow et de vos dashboards Metabase)*

---

## Slide 8 : Conclusion & Perspectives
- **Conclusion :** Objectifs atteints. Plateforme robuste, scalable et monitorée.
- **Améliorations futures :**
  - Ajout de PySpark pour scaler le nettoyage Silver si le volume explose.
  - Mise en place d'un modèle de Machine Learning pour détecter automatiquement les "fake news".
  - Déploiement sur le Cloud (AWS EMR / S3).

---
*Fin de la présentation*
