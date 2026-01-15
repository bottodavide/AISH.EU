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

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
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
    - Database connection (TODO)
    - Redis connection (TODO)
    - External services status (TODO)
    """
    # Log richiesta health check (livello debug per non riempire log)
    logger.debug("Health check requested")

    health_status = {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {
            "api": "ok",
            # TODO: Aggiungere check per database, redis, etc.
            # "database": await check_database(),
            # "redis": await check_redis(),
            # "ms_graph": await check_ms_graph_token(),
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

# TODO: Registra routers per:
# - Authentication (/api/v1/auth)
# - Services (/api/v1/services)
# - Orders (/api/v1/orders)
# - Invoices (/api/v1/invoices)
# - Admin (/api/v1/admin)
# - CMS (/api/v1/cms)
# - Chat/AI (/api/v1/chat)
# - Webhooks (/api/v1/webhooks)

# from app.api.v1.api import api_router
# app.include_router(api_router, prefix="/api/v1")


# =============================================================================
# Exception Handlers
# =============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler per gestire errori non catturati.
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "url": str(request.url),
            "method": request.method,
            "client": request.client.host if request.client else None,
        },
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred" if not settings.DEBUG else str(exc),
            },
        },
    )


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
