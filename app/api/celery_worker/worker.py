import os
from db import pg_db, mongo_db
from celery import Celery
from celery_worker.celeryconfig import CeleryConfig
from celery.signals import worker_process_init, worker_process_shutdown

if os.getenv("WORKER_IS_CLIENT", 0) == 1 or os.getenv("WORKER_IS_BEAT", 0) == 1:
    import celery_pool_asyncio # noqa


celery_app = Celery(__name__)
celery_app.config_from_object(
    CeleryConfig(),
    force=True
)


@worker_process_init.connect
async def init_worker(**kwargs):
    await pg_db.connect()


@worker_process_shutdown.connect
async def shutdown_worker(**kwargs):
    if pg_db.is_connected:
        await pg_db.disconnect()
    mongo_db.close()
