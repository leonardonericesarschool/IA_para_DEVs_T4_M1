"""Database configuration and session management"""
from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from typing import Generator, Optional
from src.config import get_settings

# SQLAlchemy Base for all models
Base = declarative_base()

# Import models to register them with Base
# This must be done after Base is created
from src.models.database_models import UserModel, PixKeyModel, PixKeyAuditModel  # noqa: E402, F401

# Sync engine/session (for migrations and simple operations)
_engine: Optional[Engine] = None
_SessionLocal: Optional[sessionmaker] = None


def get_engine() -> Engine:
    """Get or create synchronous database engine"""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            echo=settings.database_echo,
            pool_pre_ping=True
        )
    return _engine


def get_session_local() -> sessionmaker:
    """Get sessionmaker for sync sessions"""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency injection for sync database session"""
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async engine/session (for FastAPI)
_async_engine: Optional[AsyncEngine] = None
_AsyncSessionLocal: Optional[sessionmaker] = None


async def get_async_engine() -> AsyncEngine:
    """Get or create async database engine"""
    global _async_engine
    if _async_engine is None:
        settings = get_settings()
        # Convert postgresql:// to postgresql+asyncpg://
        async_db_url = settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )
        _async_engine = create_async_engine(
            async_db_url,
            echo=settings.database_echo,
            pool_pre_ping=True
        )
    return _async_engine


async def get_async_session_local() -> sessionmaker:
    """Get sessionmaker for async sessions"""
    global _AsyncSessionLocal
    if _AsyncSessionLocal is None:
        engine = await get_async_engine()
        _AsyncSessionLocal = sessionmaker(
            engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    return _AsyncSessionLocal


async def get_async_db() -> AsyncSession:
    """Dependency injection for async database session"""
    SessionLocal = await get_async_session_local()
    async with SessionLocal() as session:
        yield session


def create_db_and_tables() -> None:
    """Create database tables from models"""
    engine = get_engine()
    Base.metadata.create_all(engine)


def drop_db_and_tables() -> None:
    """Drop all database tables"""
    engine = get_engine()
    Base.metadata.drop_all(engine)
