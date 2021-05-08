import os
from celery.schedules import crontab


class CeleryConfig:
    imports = ["celery_worker.tasks_periodic", "celery_worker.tasks_full", "celery_worker.tasks_latest"]

    broker_url = (
        f"redis://:@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"
        f"/{os.getenv('REDIS_WORKER_DB')}"
    )
    result_backend = (
        f"redis://:@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}"
        f"/{os.getenv('REDIS_RESULTS_DB')}"
    )
    
    task_acks_late = True
    task_acks_on_failure_or_timeout = False
    task_track_started = True
    task_queue_max_priority = 10
    task_default_priority = 5
    
    worker_max_tasks_per_child = 1
    worker_prefetch_multiplier = 1
    
    task_serializer = "pickle"
    accept_content = ["pickle"]
    broker_heartbeat = 60

    beat_schedule = {
        "update_daily": {
            "task": "update_daily",
            "schedule": crontab(minute=0, hour=3)
        },
        "update_weekly_periodic": {
            "task": "update_weekly",
            "schedule": crontab(minute=0, hour=3, day_of_week=0)
        },
        "update_monthly": {
            "task": "update_monthly",
            "schedule": crontab(minute=0, hour=3, day_of_month=1)
        }
    }
