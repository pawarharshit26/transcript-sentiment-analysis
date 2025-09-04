from celery import Celery
import os
from app.settings import  REDIS_URL


celery = Celery(
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.ingestion", "app.workers.insights"],
) 



celery.conf.task_routes = {
    "app.workers.ingestion.ingest_call": {"queue": "ingestion"},
    "app.workers.insights.analyze_call": {"queue": "insights"},
}