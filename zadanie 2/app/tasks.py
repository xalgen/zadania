# WAŻNE: Celery worker działa synchronicznie — używamy sync SQLAlchemy,
# bo aiosqlite (async) nie działa w zwykłym workerze Celery.

from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# Osobny sync engine dla zadań Celery
sync_engine = create_engine(
    "sqlite:///./users.db",
    connect_args={"check_same_thread": False},
)
SyncSession = sessionmaker(bind=sync_engine)

celery_app = Celery(
    "tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)
celery_app.conf.broker_use_ssl = settings.celery_broker_use_ssl
celery_app.conf.redis_backend_use_ssl = settings.celery_redis_backend_use_ssl


@celery_app.task(name="tasks.save_user_async")
def save_user_async(first_name: str, last_name: str) -> dict:
    """Zapisuje użytkownika do bazy w tle (poza event loopem FastAPI)."""
    from app.models import User  # import wewnątrz, by uniknąć circular imports

    with SyncSession() as session:
        user = User(first_name=first_name, last_name=last_name, source="async")
        session.add(user)
        session.commit()

    return {"status": "saved", "user": f"{first_name} {last_name}"}
