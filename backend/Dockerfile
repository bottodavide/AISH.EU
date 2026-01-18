# =============================================================================
# AI STRATEGY HUB - BACKEND DOCKERFILE (FastAPI)
# =============================================================================
# Dockerfile per il servizio backend FastAPI in produzione
#
# Autore: Claude per Davide
# Data: 2026-01-18
# =============================================================================

# Stage 1: Builder - Compila dipendenze Python
FROM python:3.11-slim AS builder

WORKDIR /app

# Installa dipendenze di sistema per compilazione
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Immagine finale production
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# Variabili ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    TZ=Europe/Rome

WORKDIR /app

# Installa solo runtime dependencies (non build tools)
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia dipendenze Python dallo stage builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Crea user non-root per sicurezza
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/logs /app/uploads && \
    chown -R appuser:appuser /app

# Copia application code
COPY --chown=appuser:appuser . .

# Switch a user non-root
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Esponi porta FastAPI
EXPOSE 8000

# Comando di avvio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
