from celery import Celery
from src.config.settings import settings

celery = Celery(
    'worker',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['src.celery_conf.tasks']
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_always_eager=False,
    broker_connection_retry_on_startup=True
)
