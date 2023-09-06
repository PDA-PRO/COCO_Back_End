from celery import Celery
celery_task = Celery(
    'app',
    broker="redis://127.0.0.1:6379/0",
    include=['core.celery_worker']
)