"""
Modulo: database.py
Descrizione: Database connection e session management
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.core.config import settings

logger = logging.getLogger(__name__)

# =============================================================================
# SYNC ENGINE (per migrations, seed, background tasks)
# =============================================================================

logger.info(f"Creating sync engine for database: {settings.POSTGRES_DB}")

sync_engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verifica connessione prima di usarla
    pool_size=5,
    max_overflow=10,
    echo=settings.ENVIRONMENT == "development",  # SQL logging in dev
)

# Session factory per sync operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine,
)

logger.debug("Sync engine and session factory created")


# =============================================================================
# ASYNC ENGINE (per FastAPI endpoints)
# =============================================================================

# Convert postgres:// to postgresql+asyncpg://
async_database_url = settings.DATABASE_URL.replace(
    "postgresql://", "postgresql+asyncpg://"
)

logger.info("Creating async engine for FastAPI")

async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.ENVIRONMENT == "development",
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

logger.debug("Async engine and session factory created")


# =============================================================================
# DEPENDENCY FUNCTIONS
# =============================================================================

def get_db() -> Generator[Session, None, None]:
    """
    Dependency per ottenere sessione database SYNC.

    Usata principalmente per background tasks e operazioni batch.

    Yields:
        Session: SQLAlchemy session

    Example:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
    """
    db = SessionLocal()
    logger.debug("Sync database session opened")

    try:
        yield db
        logger.debug("Sync database session successful")
    except Exception as e:
        logger.error(f"Database error in sync session: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("Sync database session closed")


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency per ottenere sessione database ASYNC.

    Usata per tutti gli endpoints FastAPI.

    Yields:
        AsyncSession: SQLAlchemy async session

    Example:
        @app.get("/example")
        async def example(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(User))
            users = result.scalars().all()
            return users
    """
    async with AsyncSessionLocal() as session:
        logger.debug("Async database session opened")

        try:
            yield session
            await session.commit()
            logger.debug("Async database session committed successfully")
        except Exception as e:
            logger.error(f"Database error in async session: {str(e)}", exc_info=True)
            await session.rollback()
            logger.warning("Async database session rolled back")
            raise
        finally:
            await session.close()
            logger.debug("Async database session closed")


# =============================================================================
# EVENT LISTENERS (per logging e monitoring)
# =============================================================================

@event.listens_for(sync_engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Log quando viene creata una nuova connessione al database."""
    logger.debug("New database connection established")


@event.listens_for(sync_engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log quando una connessione viene presa dal pool."""
    logger.debug("Connection checked out from pool")


# =============================================================================
# HEALTH CHECK
# =============================================================================

async def check_database_health() -> bool:
    """
    Verifica salute connessione database.

    Returns:
        bool: True se database è raggiungibile, False altrimenti
    """
    try:
        async with AsyncSessionLocal() as session:
            # Test semplice query
            await session.execute(text("SELECT 1"))
            logger.info("Database health check: OK")
            return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}", exc_info=True)
        return False


def check_database_health_sync() -> bool:
    """
    Verifica salute connessione database (versione sync).

    Returns:
        bool: True se database è raggiungibile, False altrimenti
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database health check (sync): OK")
        return True
    except Exception as e:
        logger.error(f"Database health check (sync) failed: {str(e)}", exc_info=True)
        return False


logger.info("Database module initialized")
