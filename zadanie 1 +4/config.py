import os
from dotenv import load_dotenv

load_dotenv()


def _build_redis_url() -> str:
    """Buduje rediss:// URL z Upstash REST credentials lub zwraca UPSTASH_REDIS_URL."""
    rest_url = os.getenv("UPSTASH_REDIS_REST_URL", "")
    token = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")
    if rest_url and token:
        host = rest_url.replace("https://", "").replace("http://", "").rstrip("/")
        return f"rediss://:{token}@{host}:6379?ssl_cert_reqs=CERT_NONE"
    return os.getenv("UPSTASH_REDIS_URL", "")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    WTF_CSRF_ENABLED = True          # ← dodaj tę linię
    SQLALCHEMY_DATABASE_URI = "sqlite:///users.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    _REDIS_URL = _build_redis_url()
    CELERY_BROKER_URL = _REDIS_URL
    CELERY_RESULT_BACKEND = _REDIS_URL
    CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": None}
    CELERY_REDIS_BACKEND_USE_SSL = {"ssl_cert_reqs": None}
