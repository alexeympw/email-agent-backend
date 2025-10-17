from celery import Celery

from .config import settings


def _build_celery() -> Celery:
    broker_url = settings.redis_url
    backend_url = settings.redis_url

    celery_app = Celery(
        "email_agent",
        broker=broker_url,
        backend=backend_url,
        include=["app.tasks"],
    )

    celery_app.conf.update(
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
    )
    return celery_app


celery = _build_celery()
