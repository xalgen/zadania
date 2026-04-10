from app import create_app, celery  # noqa: F401  — celery eksportowane dla CLI

flask_app = create_app()
# celery jest konfigurowane wewnątrz create_app() → make_celery()
