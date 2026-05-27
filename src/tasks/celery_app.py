"""Celery application for Lucky Number scheduled tasks."""

import os

from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "lucky_number",
    broker=os.getenv("CELERY_BROKER_URL", f"{redis_url}/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", f"{redis_url}/1"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
