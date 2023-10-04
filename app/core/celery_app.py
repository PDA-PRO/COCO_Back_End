from celery import Celery
import os
celery_task = Celery(
    'app',
    broker=f"{os.getenv('REDIS_HOST')}://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}",
    include=['app.core.celery_worker']
)