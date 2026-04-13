from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "scopeguard",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.task_routes = {"app.tasks.scan_tasks.run_scan_task": {"queue": "scans"}}

