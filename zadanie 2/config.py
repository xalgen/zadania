from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    secret_key: str = "dev-secret-key"
    database_url: str = "sqlite+aiosqlite:///./users.db"

    # Oba pola czytają tę samą zmienną środowiskową UPSTASH_REDIS_URL
    celery_broker_url: str = Field(
        default="", validation_alias="UPSTASH_REDIS_URL"
    )
    celery_result_backend: str = Field(
        default="", validation_alias="UPSTASH_REDIS_URL"
    )

    # SSL wymagane przez Upstash (rediss://)
    celery_broker_use_ssl: dict = {"ssl_cert_reqs": None}
    celery_redis_backend_use_ssl: dict = {"ssl_cert_reqs": None}

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


settings = Settings()
