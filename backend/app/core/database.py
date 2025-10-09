"""
Database utilities: minimal async init and session provider.
"""
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession as AsyncSession  # re-exported for typing

from config.settings import get_db_settings


_engine = None  # Lazily initialized
_SessionLocal: Optional[sessionmaker] = None


async def init_db() -> None:
    """Initialize database resources (no-op for tests/dev).
    Avoid outbound connections at import/startup; tests override sessions.
    """
    global _engine, _SessionLocal
    if _engine is not None:
        return
    # Do not connect here to avoid dependency on external DB during tests
    # Users can initialize their own engine/session elsewhere if needed
    db_url = get_db_settings().url
    try:
        _engine = create_engine(db_url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
    except Exception:
        # Silently defer initialization until first real use
        _engine = None
        _SessionLocal = None


async def get_db_session() -> AsyncGenerator[Session, None]:
    """Yield a database session. Overridden in tests.
    Returns a sync Session for simplicity; callers should not rely on async features.
    """
    global _SessionLocal
    if _SessionLocal is None:
        # Attempt lazy init without raising if it fails
        try:
            await init_db()
        except Exception:
            pass
    session: Optional[Session] = _SessionLocal() if _SessionLocal else None
    try:
        yield session  # type: ignore[misc]
    finally:
        if session is not None:
            session.close()
