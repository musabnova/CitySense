"""
TASK-028: Celery Worker Application & Task Routing Setup
=========================================================
Stage: Backend / Async Orchestration
Objective: Initialize Celery task application backed by Redis broker.

NOTE: Since Redis is unavailable (Docker not installed on this host),
this module provides a synchronous in-process fallback executor that
mirrors the Celery task interface. When Redis becomes available, the
real Celery worker activates automatically.

Clearly labelled: [SYNC FALLBACK - Celery unavailable]
"""

import os
import logging

logger = logging.getLogger("citysense.tasks")

# ── Attempt to import Celery (graceful fallback) ─────────────────────────────
_CELERY_AVAILABLE = False
celery_app = None

try:
    from celery import Celery

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    celery_app = Celery(
        "citysense_tasks",
        broker=REDIS_URL,
        backend=REDIS_URL,
    )

    celery_app.conf.update(
        task_serializer="json",
        accept_content=["json"],
        result_serializer="json",
        timezone="UTC",
        enable_utc=True,
        worker_concurrency=2,
        task_soft_time_limit=30,
        task_time_limit=60,
        task_default_queue="citysense_understand",
        task_routes={
            "apps.api.tasks.pipeline.process_incident_report_task": {
                "queue": "citysense_understand"
            }
        },
    )
    _CELERY_AVAILABLE = True
    logger.info("Celery application configured with broker=%s", REDIS_URL)

except ImportError:
    logger.warning(
        "[SYNC FALLBACK - Celery unavailable] "
        "Running tasks synchronously in-process."
    )


# ── Synchronous fallback task decorator ──────────────────────────────────────
class _SyncTask:
    """Minimal Celery-compatible task wrapper for synchronous execution."""

    def __init__(self, func):
        self.func = func
        self.name = f"{func.__module__}.{func.__qualname__}"

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def delay(self, *args, **kwargs):
        """Synchronous fallback for Celery .delay()"""
        logger.info("[SYNC FALLBACK] Executing %s synchronously", self.name)
        return self.func(*args, **kwargs)

    def apply_async(self, args=None, kwargs=None, **options):
        """Synchronous fallback for Celery .apply_async()"""
        logger.info("[SYNC FALLBACK] Executing %s synchronously", self.name)
        return self.func(*(args or ()), **(kwargs or {}))


def shared_task(func):
    """Decorator that registers a shared Celery task or wraps it for sync execution."""
    if _CELERY_AVAILABLE and celery_app is not None:
        return celery_app.task(bind=False, name=f"{func.__module__}.{func.__qualname__}")(func)
    return _SyncTask(func)

