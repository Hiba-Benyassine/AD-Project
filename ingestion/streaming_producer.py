import json
import time
from datetime import datetime
import sys
from pathlib import Path

# Ajouter le chemin racine pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from kafka import KafkaProducer

# Import all scrapers
from scrapers.national.sport360_scraper import Sport360Scraper
from scrapers.national.lematin_scraper import LeMatinScraper
from scrapers.international.lequipe_scraper import LequipeScraper
from scrapers.international.espn_scraper import ESPNScraper

def main():
    print("[streaming] Démarrage du Kafka Producer (Scraping Multi-Sources en temps réel)...")
    
    producer = None
    for _ in range(10):
        try:
            # Note: We use localhost:9092 because this producer will run on the host machine
            producer = KafkaProducer(
                bootstrap_servers=["localhost:9092"],
                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            break
        except Exception as e:
            print(f"[streaming] En attente de Kafka: {e}")
            time.sleep(5)
            
    if not producer:
        print("Erreur: Impossible de se connecter à Kafka (localhost:9092).")
        return

    # Instantiate all scrapers
    scrapers = [
        LequipeScraper(),
        Sport360Scraper(),
        LeMatinScraper(),
        ESPNScraper()
    ]
    
    # Keep track of seen URLs globally to avoid duplicate processing
    seen_urls = set()
    
    print("[streaming] Écoute en direct des sources: L'Équipe, Sport360, Le Matin, ESPN...")
    
    while True:
        try:
            for scraper in scrapers:
                source_name = scraper.__class__.__name__
                # 1. On récupère les dernières URLs (on limite à 5 pour le temps réel pour ne pas surcharger)
                try:
                    urls = scraper.get_article_urls(max_articles=5)
                except Exception as e:
                    print(f"[streaming] Erreur lors de la récupération des URLs pour {source_name}: {e}")
                    continue
                
                # 2. On filtre pour ne garder que les nouveaux articles
                new_urls = [url for url in urls if url not in seen_urls]
                
                if not new_urls:
                    print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Aucun nouvel article détecté sur {source_name}.")
                else:
                    for url in new_urls:
                        print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Nouvel article détecté sur {source_name} ! Extraction: {url}")
                        try:
                            article = scraper.extract_article_data(url)
                        except Exception as e:
                            print(f"[streaming] Erreur d'extraction pour {url}: {e}")
                            article = None
                        
                        if article:
                            # Envoyer à Kafka
                            producer.send("news_stream", article)
                            producer.flush()
                            
                            seen_urls.add(url)
                            print(f"[streaming] ✅ Article envoyé au topic Kafka: {article['title']}")
                            
                            # Petite pause pour ne pas spammer le serveur cible
                            time.sleep(2)
                            
            # Attendre 60 secondes avant le prochain check de TOUTES les sources (Polling)
            print(f"[{datetime.utcnow().strftime('%H:%M:%S')}] Fin du cycle de vérification. Pause de 60s...")
            time.sleep(60)
            
        except Exception as e:
            print(f"[streaming] Erreur de polling globale: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
