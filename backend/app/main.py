"""
Modulo: main.py
Descrizione: Entry point principale dell'applicazione FastAPI
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.core.database import check_database_health
from app.core.exceptions import (
    AIStrategyHubException,
    aistrategyhub_exception_handler,
    generic_exception_handler,
    http_exception_handler,
)

# Import routers
from app.api.routes import (
    admin,
    auth,
    chat,
    cms,
    contact,
    errors,
    files,
    homepage,
    invoices,
    knowledge_base,
    newsletter,
    orders,
    packages,
    services,
    users,
)

# Setup logging configurazione
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Lifecycle manager per FastAPI.
    Gestisce startup e shutdown dell'applicazione.
    """
    # Startup
    logger.info("=" * 80)
    logger.info("AI Strategy Hub - Backend Starting")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("=" * 80)

    # Inizializza connessioni database, cache, etc.
    # TODO: Aggiungere init database pool, redis connection

    yield

    # Shutdown
    logger.info("AI Strategy Hub - Backend Shutting Down")
    # TODO: Chiudi connessioni database, cache, etc.


# =============================================================================
# FastAPI Application Instance
# =============================================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API Backend per AI Strategy Hub - Piattaforma E-Commerce Servizi Consulenza",
    version=settings.VERSION,
    docs_url="/docs" if settings.DEBUG else None,  # Swagger UI solo in debug
    redoc_url="/redoc" if settings.DEBUG else None,  # ReDoc solo in debug
    openapi_url="/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan,
)

# =============================================================================
# Middleware Configuration
# =============================================================================

# CORS Middleware - Configurazione esplicita per frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # http://localhost:3000, https://aistrategyhub.eu
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Content-Type",
        "Authorization",
        "X-Requested-With",
        "Accept",
        "Origin",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
    ],
    expose_headers=["X-Request-ID", "Content-Length", "Content-Type"],
    max_age=600,  # Cache preflight per 10 minuti
)

# Gzip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# TODO: Aggiungere altri middleware
# - Rate limiting
# - Request ID tracking
# - Security headers
# - Authentication


# =============================================================================
# Health Check Endpoint
# =============================================================================


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint per monitoring e load balancer.

    Verifica:
    - API is responsive
    - Database connection
    - Redis connection (TODO)
    - External services status (TODO)
    """
    # Log richiesta health check (livello debug per non riempire log)
    logger.debug("Health check requested")

    # Check database
    db_status = "ok" if await check_database_health() else "down"

    # Overall status
    overall_status = "healthy" if db_status == "ok" else "degraded"

    health_status = {
        "status": overall_status,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "api": "ok",
            "database": db_status,
            # TODO: Aggiungere check per redis, etc.
            # "redis": await check_redis(),
        },
    }

    return JSONResponse(content=health_status)


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - Informazioni base API.
    """
    return {
        "message": "AI Strategy Hub - Backend API",
        "version": settings.VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled",
        "health": "/health",
    }


# =============================================================================
# API Router Registration
# =============================================================================

# Registra tutti i router con prefix /api/v1
API_V1_PREFIX = "/api/v1"

app.include_router(auth.router, prefix=API_V1_PREFIX, tags=["Authentication"])
app.include_router(users.router, prefix=API_V1_PREFIX, tags=["Users"])
app.include_router(services.router, prefix=API_V1_PREFIX, tags=["Services"])
app.include_router(orders.router)  # Orders router già include prefix /api/v1
app.include_router(files.router)  # Files router già include prefix /api/v1
app.include_router(invoices.router)  # Invoices router già include prefix /api/v1
app.include_router(cms.router, prefix=API_V1_PREFIX, tags=["CMS"])  # ✅ CMS Headless completo
app.include_router(chat.router, prefix=API_V1_PREFIX, tags=["Chat"])  # ✅ AI Chatbot & RAG
app.include_router(knowledge_base.router, prefix=API_V1_PREFIX, tags=["Knowledge Base"])  # ✅ Knowledge Base Management
app.include_router(errors.router, prefix=API_V1_PREFIX, tags=["Errors"])  # ✅ Error Reporting & Email Notifications
app.include_router(newsletter.router, prefix=API_V1_PREFIX, tags=["Newsletter"])  # ✅ Newsletter Management
app.include_router(contact.router, prefix=API_V1_PREFIX, tags=["Contact"])  # ✅ Contact Form
app.include_router(admin.router, prefix=API_V1_PREFIX, tags=["Admin"])  # ✅ Admin CMS & User Management
app.include_router(homepage.router, prefix=API_V1_PREFIX, tags=["Homepage"])  # ✅ Homepage Banners & Content
app.include_router(packages.router, prefix=API_V1_PREFIX, tags=["Packages"])  # ✅ Consulting Packages

# TODO: Registra altri routers:
# - Webhooks (/api/v1/webhooks) - Stripe webhooks
# - Support (/api/v1/support) - Support tickets
# - Notifications (/api/v1/notifications) - In-app notifications

logger.info("API routers registered successfully")


# =============================================================================
# Exception Handlers
# =============================================================================

# Custom exception handlers
from fastapi import HTTPException

app.add_exception_handler(AIStrategyHubException, aistrategyhub_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

logger.info("Exception handlers registered")


# =============================================================================
# Startup Event Log
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    # Log startup con configurazione
    logger.info("Starting uvicorn server directly")
    logger.info(f"Host: 0.0.0.0, Port: 8000")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
