from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from celery import Celery
from config import Config
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()
db = SQLAlchemy()
celery = Celery()
limiter = Limiter(key_func=get_remote_address)


def make_celery(app: Flask) -> None:
    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        broker_use_ssl=app.config.get("CELERY_BROKER_USE_SSL"),
        redis_backend_use_ssl=app.config.get("CELERY_REDIS_BACKEND_USE_SSL"),
    )
    celery.set_default()

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    csrf.init_app(app)
    db.init_app(app)
    make_celery(app)
    limiter.init_app(app)
    
    from app.routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app