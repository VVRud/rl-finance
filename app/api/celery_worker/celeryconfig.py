import os
from celery.schedules import crontab


class CeleryConfig:
    imports = ["celery_worker.tasks_periodic", "celery_worker.tasks_full", "celery_worker.tasks_latest"]

    broker_url = (
        f"amqp://{os.getenv('RABBIT_USERNAME')}:{os.getenv('RABBIT_PASSWORD')}@"
        f"{os.getenv('RABBIT_HOST')}:{os.getenv('RABBIT_PORT')}/"
    )
    result_backend = (
        f"redis://:@{os.getenv('REDIS_HOST')}:{os.getenv('REDIS_PORT')}/0"
    )
    task_acks_late = True
    task_acks_on_failure_or_timeout = False
    task_track_started = True
    task_serializer = "pickle"
    accept_content = ["pickle"]

    beat_schedule = {
        "update_daily": {
            "task": "update_daily",
            "schedule": crontab(minute=0, hour=5)
        },
        "update_weekly_periodic": {
            "task": "update_weekly",
            "schedule": crontab(minute=0, hour=5, day_of_week=0)
        },
        "update_monthly": {
            "task": "update_monthly",
            "schedule": crontab(minute=0, hour=5, day_of_month=1)
        }
    }
