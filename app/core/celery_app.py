from celery import Celery
celery_task = Celery(
    'app',
    broker="redis://redis:6379",
    include=['core.celery_worker']
)