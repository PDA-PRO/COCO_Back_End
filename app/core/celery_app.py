from dotenv import load_dotenv
load_dotenv(verbose=True,override=True)
from celery import Celery
import os
celery_task = Celery(
    'app',
    broker=f"redis://{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}",
    include=['app.core.celery_worker']
)