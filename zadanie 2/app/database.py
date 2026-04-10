from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from config import settings

# Async engine dla SQLite przez aiosqlite
engine = create_async_engine(
    settings.database_url,
    echo=True,
    connect_args={"check_same_thread": False},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    """Dependency Injection — dostarcza AsyncSession do endpointu FastAPI."""
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    """Tworzy wszystkie tabele przy starcie aplikacji."""
    async with engine.begin() as conn:
        from app import models  # noqa: F401 — rejestruje modele w metadanych
        await conn.run_sync(Base.metadata.create_all)
