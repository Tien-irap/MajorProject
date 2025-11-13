# core/celery_app.py
from celery import Celery
from .config import settings

# backend/app/core/celery_app.py
from celery import Celery
from .config import settings

celery_app = Celery(
    "chess_analysis_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True
)

# --- REPLACE THIS LINE ---
# celery_app.autodiscover_tasks(['backend.app.tasks.celery_worker'])

# --- WITH THIS LINE ---
# This explicitly imports the module, forcing its global-scope code
# (like model training) to run when the worker starts.
from ..tasks import celery_worker 
# ---------------------