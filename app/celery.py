from celery import Celery
from app.settings import  REDIS_URL


celery = Celery(
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=['app.workers.ingestion']
) 


celery.autodiscover_tasks()