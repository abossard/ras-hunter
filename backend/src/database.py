"""
Database module for Ras's Deep Treasure backend.

Provides SQLAlchemy async engine, session factory, and declarative base.
Constitution: Explicit connection management with proper lifecycle handling.
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from src.config import Settings, get_settings


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


def create_engine(settings: Settings):
    """
    Create async SQLAlchemy engine.

    Args:
        settings: Application settings with database_url.

    Returns:
        AsyncEngine: Configured async database engine.
    """
    return create_async_engine(
        settings.database_url,
        echo=settings.log_level == "DEBUG",
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
    )


def create_session_factory(settings: Settings):
    """
    Create async session factory.

    Args:
        settings: Application settings with database_url.

    Returns:
        async_sessionmaker: Session factory for creating database sessions.
    """
    engine = create_engine(settings)
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


# Global session factory (initialized at app startup)
SessionFactory: async_sessionmaker[AsyncSession] | None = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database session.

    Yields:
        AsyncSession: Database session for request scope.

    Raises:
        RuntimeError: If SessionFactory is not initialized.
    """
    if SessionFactory is None:
        raise RuntimeError("SessionFactory not initialized. Call init_db() at app startup.")

    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# Type alias for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]


async def init_db() -> None:
    """
    Initialize database connection pool.

    Must be called during application startup (lifespan context).
    """
    global SessionFactory
    settings = get_settings()
    SessionFactory = create_session_factory(settings)


async def close_db() -> None:
    """
    Close database connection pool.

    Must be called during application shutdown (lifespan context).
    """
    global SessionFactory
    if SessionFactory:
        engine = SessionFactory.kw["bind"]
        await engine.dispose()
        SessionFactory = None
