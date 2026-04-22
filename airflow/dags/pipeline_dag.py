"""
Airflow DAG for sports data pipeline.

Task order:
1) scraping_task
2) cleaning_task
3) classification_task
4) gold_task
5) load_to_db

Implementation note:
- We use BashOperator to run local python scripts mounted in /opt/project.
- This keeps the DAG easy to read for students and easy to debug.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

DEFAULT_ARGS = {
    "owner": "data-team",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="sports_data_pipeline",
    description="End-to-end sports news data engineering pipeline",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2026, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["sports", "data-engineering", "batch"],
) as dag:
    scraping_task = BashOperator(
        task_id="scraping_task",
        bash_command="cd /opt/project && python ingestion/batch_pipeline.py",
    )

    cleaning_task = BashOperator(
        task_id="cleaning_task",
        bash_command="cd /opt/project && python processing/cleaning.py",
    )

    classification_task = BashOperator(
        task_id="classification_task",
        bash_command="cd /opt/project && python processing/classification.py",
    )

    gold_task = BashOperator(
        task_id="gold_task",
        bash_command="cd /opt/project && python processing/gold_analytics.py",
    )

    load_to_db = BashOperator(
        task_id="load_to_db",
        bash_command="cd /opt/project && python warehouse/load_to_postgres.py",
    )

    scraping_task >> cleaning_task >> classification_task >> gold_task >> load_to_db
