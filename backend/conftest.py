"""
Modulo: conftest.py
Descrizione: Pytest fixtures globali per test suite
Autore: Claude per Davide
Data: 2026-01-18

Fixtures disponibili:
- test_engine: SQLAlchemy async engine per test database
- db_session: AsyncSession con rollback automatico
- client: FastAPI TestClient
- test_user: User fixture standard
- admin_user: Admin user fixture
- authenticated_client: TestClient con JWT token
- mock_stripe: Mock Stripe API service
- mock_ms_graph: Mock Microsoft Graph API
- mock_claude: Mock Claude API service
"""

import asyncio
import logging
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch
import uuid

import pytest
import pytest_asyncio
import sqlalchemy
import asyncpg
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.database import get_async_db
from app.core.security import create_access_token, hash_password
from app.main import app
from app.models.base import Base
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

# =============================================================================
# PYTEST CONFIGURATION
# =============================================================================

# Configura asyncio event loop per pytest
@pytest.fixture(scope="session")
def event_loop():
    """
    Crea event loop per l'intera sessione test.
    Necessario per fixture async con scope="session".
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


# =============================================================================
# DATABASE FIXTURES
# =============================================================================

@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Crea async engine per test database.

    Usa un database separato per i test con nome univoco per evitare
    conflitti con run precedenti in CI.

    Yields:
        AsyncEngine: SQLAlchemy async engine
    """
    # URL database di test con nome univoco basato su timestamp
    # Questo garantisce che ogni workflow run usi un DB completamente nuovo
    import time
    unique_suffix = str(int(time.time() * 1000))  # millisecond timestamp
    test_db_name = f"{settings.POSTGRES_DB}_test_{unique_suffix}"

    test_database_url = settings.DATABASE_URL.replace(
        settings.POSTGRES_DB,
        test_db_name
    ).replace("postgresql://", "postgresql+asyncpg://")

    logger.info(f"Creating test engine for database: {test_db_name}")

    # Crea engine con NullPool per test (no connection pooling)
    engine = create_async_engine(
        test_database_url,
        poolclass=NullPool,
        echo=False,  # Disabilita SQL logging nei test per performance
    )

    # Crea database univoco e tabelle
    # Usa raw asyncpg per garantire pulizia completa senza problemi di transazioni
    try:
        logger.info("Creating unique test database...")

        # Estrai parametri connessione dal database URL
        # Format: postgresql://user:pass@host:port/dbname
        db_url_parts = test_database_url.replace("postgresql+asyncpg://", "").split("@")
        user_pass = db_url_parts[0].split(":")
        host_port_db = db_url_parts[1].split("/")
        host_port = host_port_db[0].split(":")

        #  Connetti al database 'postgres' per creare il test database
        admin_conn = await asyncpg.connect(
            user=user_pass[0],
            password=user_pass[1] if len(user_pass) > 1 else "",
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            database="postgres"  # Connetti al database admin
        )

        try:
            # Crea database di test univoco
            await admin_conn.execute(f"CREATE DATABASE {test_db_name}")
            logger.info(f"Created test database: {test_db_name}")
        finally:
            await admin_conn.close()

        # Ora connetti al nuovo database per creare lo schema
        conn = await asyncpg.connect(
            user=user_pass[0],
            password=user_pass[1] if len(user_pass) > 1 else "",
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            database=test_db_name  # Connetti al database di test appena creato
        )

        try:
            # DROP SCHEMA CASCADE (rimuove TUTTO: tables, indexes, types, sequences, etc.)
            await conn.execute("DROP SCHEMA IF EXISTS public CASCADE")
            logger.info("Dropped public schema")

            # Ricrea schema pubblico
            await conn.execute("CREATE SCHEMA public")
            logger.info("Recreated public schema")

            # Grant permissions
            await conn.execute("GRANT ALL ON SCHEMA public TO postgres")
            await conn.execute("GRANT ALL ON SCHEMA public TO public")
            logger.info("Granted schema permissions")

        finally:
            await conn.close()
            logger.info("Closed raw asyncpg connection")

        # Dispose engine to clear any pooled connections
        await engine.dispose()
        logger.info("Disposed old engine to clear connection pool")

        # Create fresh engine to ensure no cached metadata
        engine = create_async_engine(
            test_database_url,
            poolclass=NullPool,
            echo=False,
            isolation_level="AUTOCOMMIT",  # Force autocommit for DDL
        )
        logger.info("Created fresh engine with AUTOCOMMIT isolation")

        # Ora crea tutte le tabelle usando SQLAlchemy (in una connessione veramente pulita)
        async with engine.connect() as conn:
            logger.info("Creating database tables and indexes...")
            # Usa run_sync_sync per eseguire DDL
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Successfully created database schema")

        logger.info("Test database schema ready")

    except Exception as e:
        logger.error(f"Failed to setup test database: {e}", exc_info=True)
        raise

    yield engine

    # Cleanup: Drop entire test database
    try:
        logger.info("Dropping test database...")

        # Estrai parametri connessione
        db_url_parts = test_database_url.replace("postgresql+asyncpg://", "").split("@")
        user_pass = db_url_parts[0].split(":")
        host_port_db = db_url_parts[1].split("/")
        host_port = host_port_db[0].split(":")

        # Connetti al database 'postgres' per droppare il test database
        admin_conn = await asyncpg.connect(
            user=user_pass[0],
            password=user_pass[1] if len(user_pass) > 1 else "",
            host=host_port[0],
            port=int(host_port[1]) if len(host_port) > 1 else 5432,
            database="postgres"  # Connetti al database admin
        )

        try:
            # Drop test database (chiude tutte le connessioni)
            await admin_conn.execute(f"DROP DATABASE IF EXISTS {test_db_name} WITH (FORCE)")
            logger.info(f"Dropped test database: {test_db_name}")
        finally:
            await admin_conn.close()

    except Exception as e:
        logger.warning(f"Error during cleanup: {e}")

    await engine.dispose()
    logger.info("Test engine disposed")


@pytest_asyncio.fixture
async def db_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """
    Crea AsyncSession con rollback automatico.

    Ogni test ottiene una session isolata che viene rollback al termine,
    garantendo che i test non interferiscano tra loro.

    Args:
        test_engine: Engine dal fixture test_engine

    Yields:
        AsyncSession: Session database con rollback automatico
    """
    # Crea connessione
    async with test_engine.connect() as connection:
        # Inizia transazione
        transaction = await connection.begin()

        # Crea session maker
        TestSessionLocal = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        # Crea session
        async with TestSessionLocal() as session:
            logger.debug("Test database session created")

            yield session

            # Rollback automatico al termine del test
            await transaction.rollback()
            logger.debug("Test database session rolled back")


# =============================================================================
# FASTAPI CLIENT FIXTURES
# =============================================================================

@pytest.fixture
def client(db_session: AsyncSession) -> Generator[TestClient, None, None]:
    """
    Crea FastAPI TestClient con database mockato.

    Override della dependency get_async_db per usare il database di test.

    Args:
        db_session: Session database dal fixture db_session

    Yields:
        TestClient: Client per testare endpoints FastAPI
    """
    # Override database dependency
    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_async_db

    # Crea test client
    with TestClient(app) as test_client:
        logger.debug("FastAPI TestClient created")
        yield test_client

    # Cleanup: rimuovi override
    app.dependency_overrides.clear()
    logger.debug("FastAPI TestClient closed")


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Crea AsyncClient per test asincroni.

    Utile per testare endpoints con streaming response o
    operazioni che richiedono async context.

    Args:
        db_session: Session database dal fixture db_session

    Yields:
        AsyncClient: HTTPX async client
    """
    # Override database dependency
    async def override_get_async_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_async_db

    # Crea async client
    async with AsyncClient(app=app, base_url="http://test") as ac:
        logger.debug("AsyncClient created")
        yield ac

    # Cleanup
    app.dependency_overrides.clear()
    logger.debug("AsyncClient closed")


# =============================================================================
# USER FIXTURES
# =============================================================================

@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    Crea user standard per test.

    User con ruolo CUSTOMER, email verificata, attivo.

    Args:
        db_session: Session database

    Returns:
        User: User fixture standard
    """
    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        role=UserRole.CUSTOMER,
        is_active=True,
        is_email_verified=True,
        mfa_enabled=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    logger.info(f"Test user created: {user.email}")
    return user


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """
    Crea admin user per test.

    User con ruolo ADMIN, email verificata, attivo.

    Args:
        db_session: Session database

    Returns:
        User: Admin user fixture
    """
    user = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        password_hash=hash_password("AdminPassword123!"),
        role=UserRole.ADMIN,
        is_active=True,
        is_email_verified=True,
        mfa_enabled=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    logger.info(f"Admin user created: {user.email}")
    return user


@pytest_asyncio.fixture
async def super_admin_user(db_session: AsyncSession) -> User:
    """
    Crea super admin user per test.

    User con ruolo SUPER_ADMIN, email verificata, attivo.

    Args:
        db_session: Session database

    Returns:
        User: Super admin user fixture
    """
    user = User(
        id=uuid.uuid4(),
        email="superadmin@example.com",
        password_hash=hash_password("SuperAdminPass123!"),
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        is_email_verified=True,
        mfa_enabled=False,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    logger.info(f"Super admin user created: {user.email}")
    return user


# =============================================================================
# AUTHENTICATED CLIENT FIXTURES
# =============================================================================

@pytest.fixture
def authenticated_client(
    client: TestClient,
    test_user: User
) -> TestClient:
    """
    TestClient con JWT token per user standard.

    Aggiunge header Authorization con access token valido.

    Args:
        client: FastAPI TestClient
        test_user: User fixture

    Returns:
        TestClient: Client autenticato
    """
    # Crea access token
    access_token = create_access_token(
        subject=str(test_user.id),
        additional_claims={
            "email": test_user.email,
            "role": test_user.role.value,
        }
    )

    # Aggiungi header Authorization
    client.headers["Authorization"] = f"Bearer {access_token}"

    logger.debug(f"Authenticated client created for user: {test_user.email}")
    return client


@pytest.fixture
def authenticated_admin_client(
    client: TestClient,
    admin_user: User
) -> TestClient:
    """
    TestClient con JWT token per admin user.

    Args:
        client: FastAPI TestClient
        admin_user: Admin user fixture

    Returns:
        TestClient: Client autenticato come admin
    """
    # Crea access token
    access_token = create_access_token(
        subject=str(admin_user.id),
        additional_claims={
            "email": admin_user.email,
            "role": admin_user.role.value,
        }
    )

    # Aggiungi header Authorization
    client.headers["Authorization"] = f"Bearer {access_token}"

    logger.debug(f"Authenticated admin client created for user: {admin_user.email}")
    return client


# =============================================================================
# MOCK EXTERNAL SERVICES
# =============================================================================

@pytest.fixture
def mock_stripe():
    """
    Mock Stripe API service.

    Returns:
        Mock: Mock object per Stripe API
    """
    with patch("app.services.stripe_service.stripe") as mock:
        # Mock Payment Intent creation
        mock.PaymentIntent.create.return_value = Mock(
            id="pi_test_123456789",
            client_secret="pi_test_123456789_secret_abc",
            amount=10000,
            currency="eur",
            status="requires_payment_method",
        )

        # Mock Payment Intent retrieve
        mock.PaymentIntent.retrieve.return_value = Mock(
            id="pi_test_123456789",
            status="succeeded",
            amount=10000,
            currency="eur",
        )

        # Mock webhook event construction
        mock.Webhook.construct_event.return_value = Mock(
            id="evt_test_123",
            type="payment_intent.succeeded",
            data=Mock(
                object=Mock(
                    id="pi_test_123456789",
                    status="succeeded",
                    amount=10000,
                )
            ),
        )

        logger.info("Stripe API mocked")
        yield mock


@pytest.fixture
def mock_ms_graph():
    """
    Mock Microsoft Graph API service.

    Returns:
        Mock: Mock object per MS Graph API
    """
    with patch("app.services.email_service.MSGraphService") as mock:
        # Mock email sending
        mock_instance = Mock()
        mock_instance.send_email.return_value = True
        mock.return_value = mock_instance

        logger.info("Microsoft Graph API mocked")
        yield mock


@pytest.fixture
def mock_claude():
    """
    Mock Claude API service.

    Returns:
        Mock: Mock object per Claude API
    """
    with patch("app.services.claude_service.ClaudeService") as mock:
        # Mock chat completion
        mock_instance = Mock()
        mock_instance.chat_completion.return_value = {
            "content": "This is a test response from Claude.",
            "usage": {"input_tokens": 10, "output_tokens": 20},
        }
        mock.return_value = mock_instance

        logger.info("Claude API mocked")
        yield mock


@pytest.fixture
def mock_all_external_services(mock_stripe, mock_ms_graph, mock_claude):
    """
    Fixture convenienza per mockare tutti i servizi esterni.

    Returns:
        dict: Dictionary con tutti i mock services
    """
    return {
        "stripe": mock_stripe,
        "ms_graph": mock_ms_graph,
        "claude": mock_claude,
    }


# =============================================================================
# UTILITY FIXTURES
# =============================================================================

@pytest.fixture
def test_logger():
    """
    Logger configurato per test con output verbose.

    Returns:
        logging.Logger: Logger per test
    """
    test_logger = logging.getLogger("test")
    test_logger.setLevel(logging.DEBUG)

    # Aggiungi handler se non presente
    if not test_logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        test_logger.addHandler(handler)

    return test_logger


logger.info("Conftest fixtures loaded successfully")
