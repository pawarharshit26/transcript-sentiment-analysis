from celery import Celery
from app.settings import REDIS_URL

# Create Celery instance
celery = Celery(
    'app',
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        'app.workers.ingestion',
        'app.workers.insights'
    ]
)
