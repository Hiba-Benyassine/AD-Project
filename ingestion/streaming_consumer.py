import json
import os
import sys
import uuid
from pathlib import Path
from datetime import datetime

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kafka import KafkaConsumer
import boto3
from botocore.client import Config
import psycopg2
from dateutil import parser as date_parser

BRONZE_DIR = Path("data/bronze")

def get_pg_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "postgres"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "sports_warehouse"),
        user=os.getenv("PGUSER", "sports_user"),
        password=os.getenv("PGPASSWORD", "sports_pass"),
    )

def to_timestamp(value: str) -> datetime:
    try:
        return date_parser.parse(value)
    except Exception:
        return datetime.utcnow()

def save_to_postgres(article):
    try:
        conn = get_pg_connection()
        query = """
            INSERT INTO articles_clean
            (source, url, title, content, published_at, scraped_at, language, category, keywords)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (url) DO NOTHING;
        """
        with conn.cursor() as cur:
            cur.execute(
                query,
                (
                    article.get("source", "unknown"),
                    article.get("url", ""),
                    article.get("title", ""),
                    article.get("content", ""),
                    to_timestamp(article.get("published_at", "")),
                    to_timestamp(article.get("scraped_at", "")),
                    article.get("language", "unknown"),
                    article.get("category", "other"),
                    article.get("keywords", ""),
                ),
            )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[streaming] Erreur insertion Postgres: {e}")
        return False

def get_s3_client():
    endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
    access_key = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
    secret_key = os.getenv("MINIO_SECRET_KEY", "minioadmin")

    return boto3.client(
        "s3",
        endpoint_url=f"http://{endpoint}",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

def main():
    print("[streaming] Démarrage du Kafka Consumer...")
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Try to connect to Kafka (it might take a few seconds to boot)
    consumer = None
    import time
    for _ in range(10):
        try:
            consumer = KafkaConsumer(
                "news_stream",
                bootstrap_servers=["kafka:29092"],
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                group_id="news_consumer_group",
                value_deserializer=lambda x: json.loads(x.decode("utf-8")),
            )
            break
        except Exception as e:
            print(f"[streaming] Kafka pas encore prêt: {e}")
            time.sleep(5)
            
    if not consumer:
        print("[streaming] Erreur fatale: Impossible de se connecter à Kafka.")
        sys.exit(1)

    print("[streaming] Connecté à Kafka. En attente de messages...")
    s3 = get_s3_client()
    bucket = os.getenv("MINIO_BUCKET", "bronze")

    for message in consumer:
        article = message.value
        article_id = str(uuid.uuid4())
        
        # Save locally to Bronze
        filename = f"stream_{article_id}.json"
        filepath = BRONZE_DIR / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(article, f, ensure_ascii=False)
            
        print(f"[streaming] Reçu et sauvegardé: {article.get('title', 'Sans Titre')}")
        
        # Upload to MinIO
        try:
            s3.upload_file(str(filepath), bucket, filename)
            print(f"[streaming] Envoyé sur MinIO: {filename}")
        except Exception as e:
            print(f"[streaming] Erreur upload MinIO: {e}")
            
        # Real-time update to Postgres for Metabase
        if save_to_postgres(article):
            print(f"[streaming] ✅ Article inséré en temps réel dans PostgreSQL")

if __name__ == "__main__":
    main()
