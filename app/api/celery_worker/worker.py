import os
from celery import Celery
from celery_worker.celeryconfig import CeleryConfig

if os.getenv("WORKER_IS_CLIENT", 0) == 1 or os.getenv("WORKER_IS_BEAT", 0) == 1:
    import celery_pool_asyncio # noqa


celery_app = Celery(__name__)
celery_app.config_from_object(
    CeleryConfig(),
    force=True
)
