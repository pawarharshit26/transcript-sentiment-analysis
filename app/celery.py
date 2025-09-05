from celery import Celery
import os
from app.settings import  REDIS_URL


celery = Celery(
    broker=REDIS_URL,
    backend=REDIS_URL,
) 


celery.autodiscover_tasks()