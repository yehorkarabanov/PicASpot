import os

from celery import Celery

from app.core.logging import setup_logging
from app.settings import settings

# Initialize logging for Celery worker
setup_logging(use_file_logging=True)

celery = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery.autodiscover_tasks(["app.celery.tasks.email_tasks.tasks"])
