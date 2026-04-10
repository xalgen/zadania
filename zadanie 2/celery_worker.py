from app.tasks import celery_app  # noqa: F401 — eksportuje celery_app dla CLI

# Uruchamiasz przez:
# celery -A celery_worker.celery_app worker --loglevel=info
