"""
Batch ingestion entrypoint.

Responsibilities:
1) Trigger each source scraper.
2) Ensure Bronze files are generated.
3) Optionally upload Bronze artifacts to MinIO (S3-compatible storage).

This file is designed to be called manually or from Airflow.
"""

from __future__ import annotations

import importlib
import os
from pathlib import Path
from typing import List

import boto3
from botocore.client import Config

SCRAPER_MODULES: List[str] = [
    "scrapers.hespress",
    "scrapers.lematin",
    "scrapers.cnn",
]

BRONZE_DIR = Path("data/bronze")


def run_scrapers() -> None:
    """Dynamically import and execute each scraper's run() function."""
    for module_name in SCRAPER_MODULES:
        module = importlib.import_module(module_name)
        if hasattr(module, "run"):
            collected = module.run()
            print(f"[batch] {module_name} collected={collected}")


def upload_to_minio() -> None:
    """
    Upload Bronze files to MinIO if endpoint env vars are configured.

    Required env vars:
    - MINIO_ENDPOINT (e.g. localhost:9000)
    - MINIO_ACCESS_KEY
    - MINIO_SECRET_KEY
    - MINIO_BUCKET (default: bronze)
    """
    endpoint = os.getenv("MINIO_ENDPOINT")
    access_key = os.getenv("MINIO_ACCESS_KEY")
    secret_key = os.getenv("MINIO_SECRET_KEY")
    bucket = os.getenv("MINIO_BUCKET", "bronze")

    if not endpoint or not access_key or not secret_key:
        print("[batch] MinIO upload skipped (missing env vars)")
        return

    s3 = boto3.client(
        "s3",
        endpoint_url=f"http://{endpoint}",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )

    for file_path in BRONZE_DIR.glob("*.json"):
        key = file_path.name
        s3.upload_file(str(file_path), bucket, key)
        print(f"[batch] uploaded bronze/{key}")


def main() -> None:
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)
    run_scrapers()
    upload_to_minio()


if __name__ == "__main__":
    main()
