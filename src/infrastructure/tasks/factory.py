from celery import Celery
from kombu import Exchange, Queue

from src.setup.common import app_config as config


celery_app = Celery(
    "tasks",
    broker=config.celery.broker_url,
    backend=config.celery.result_backend,
    include=["src.infrastructure.tasks.tasks"],
)

celery_app.conf.update(
    # Security
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    # Worker settings
    worker_prefetch_multiplier=config.celery.worker_prefetch_multiplier,
    worker_max_tasks_per_child=config.celery.worker_max_tasks_per_child,
    worker_disable_rate_limits=False,
    # Timeouts
    task_time_limit=config.celery.task_time_limit,
    task_soft_time_limit=config.celery.task_soft_time_limit,
    broker_connection_retry_on_startup=True,
    # Results
    result_expires=config.celery.result_expires,
    result_backend_transport_options={
        "master_name": "mymaster",
        "retry_on_timeout": True,
    },
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
    # Queues with priorities
    task_queues=(
        Queue("default", Exchange("default"), routing_key="default"),
        Queue("high_priority", Exchange("high_priority"), routing_key="high_priority"),
        Queue("low_priority", Exchange("low_priority"), routing_key="low_priority")
    ),
    task_default_queue="default",
    task_default_exchange="default",
    task_default_routing_key="default",
    # Logging
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
    # Timezone
    timezone="UTC",
    enable_utc=True,
)
