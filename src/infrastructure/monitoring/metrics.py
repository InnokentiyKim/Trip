from prometheus_client import Counter, Histogram, Gauge, Summary
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI
from functools import wraps
import time
from typing import Callable


# HTTP metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Database metrics
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['operation', 'table']
)

db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_query_total = Counter(
    'db_query_total',
    'Total number of database queries executed',
    ['operation', 'table', 'status']
)

# Cache metrics
cache_operations_total = Counter(
    'cache_operations_total',
    'Total number of cache operations',
    ['operation', 'status']
)

cache_hit_rate = Gauge(
    'cache_hit_rate',
    'Cache hit rate percentage'
)

# Business metrics
bookings_total = Counter(
    'bookings_total',
    'Total number of bookings made',
    ['status', 'hotel_id']
)

active_users = Gauge(
    'active_users',
    'Number of active users in the system'
)

revenue_total = Counter(
    'revenue_total',
    'Total revenue in cents',
    ['currency']
)

# Celery metrics
celery_tasks_total = Counter(
    'celery_tasks_total',
    'Total number of Celery tasks executed',
    ['task_name', 'status']
)

celery_task_duration_seconds = Summary(
    'celery_task_duration_seconds',
    'Celery task duration in seconds',
    ['task_name']
)


def setup_metrics(app: FastAPI) -> None:
    """Set up Prometheus metrics for the FastAPI application."""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_group_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics", "/health"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="http_requests_inprogress",
        inprogress_labels=True,
    )

    instrumentator.instrument(app).expose(app, endpoint="/metrics")


def track_database_query(operation: str, table: str) -> Callable:
    """Decorator to track database query metrics."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "failure"
                raise
            finally:
                duration = time.time() - start_time
                db_query_duration_seconds.labels(
                    operation=operation,
                    table=table,
                ).observe(duration)
                db_query_total.labels(
                    operation=operation,
                    table=table,
                    status=status,
                ).inc()

        return wrapper
    return decorator


def track_cache_operation(operation: str) -> Callable:
    """Decorator to track cache operation metrics."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            status = "miss" if operation == "get" else "success"

            try:
                result = await func(*args, **kwargs)
                if operation == "get" and result is not None:
                    status = "hit"
                return result
            except Exception:
                status = "failure"
                raise
            finally:
                cache_operations_total.labels(
                    operation=operation,
                    status=status,
                ).inc()
        return wrapper
    return decorator