from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import init_db
from app.routers import forms, pages


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Wywołuje init_db() przy starcie — tworzy tabele SQLite."""
    await init_db()
    yield


app = FastAPI(
    title="FastAPI Formularz App",
    description="Formularze sync i async z Celery + Redis (Upstash)",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(pages.router)
app.include_router(forms.router)
