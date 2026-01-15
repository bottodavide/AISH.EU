# =============================================================================
# AI STRATEGY HUB - DOCKERFILE MULTI-STAGE MONOLITICO
# =============================================================================
# Container singolo che include:
# - Frontend Next.js (build statico)
# - Backend FastAPI
# - PostgreSQL 15
# - Redis 7
# - Nginx (routing interno)
# - Supervisord (gestione processi)
#
# Autore: Claude per Davide
# Data: 2026-01-15
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1: Build Frontend (Next.js)
# -----------------------------------------------------------------------------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copia package files e installa dipendenze
COPY frontend/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copia source code e build
COPY frontend/ ./
RUN npm run build

# -----------------------------------------------------------------------------
# STAGE 2: Build Backend Dependencies (Python)
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS backend-builder

WORKDIR /app/backend

# Installa dipendenze di build
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements e installa dipendenze Python
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# STAGE 3: Final Container Monolitico
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# Imposta variabili ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=Europe/Rome

WORKDIR /app

# -----------------------------------------------------------------------------
# Installa System Dependencies
# -----------------------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    # PostgreSQL
    postgresql-15 \
    postgresql-client-15 \
    postgresql-contrib-15 \
    # Redis
    redis-server \
    redis-tools \
    # Nginx
    nginx \
    # Supervisord
    supervisor \
    # Node.js per Next.js runtime
    nodejs \
    npm \
    # Utilities
    curl \
    wget \
    vim \
    less \
    procps \
    # Build tools per alcune librerie Python
    gcc \
    g++ \
    libpq-dev \
    # Per file handling
    imagemagick \
    # Per PDF generation
    wkhtmltopdf \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# Copia Backend Dependencies da builder
# -----------------------------------------------------------------------------
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# -----------------------------------------------------------------------------
# Copia Backend Application
# -----------------------------------------------------------------------------
COPY backend/ /app/backend/
WORKDIR /app/backend

# -----------------------------------------------------------------------------
# Copia Frontend Build da builder
# -----------------------------------------------------------------------------
COPY --from=frontend-builder /app/frontend/.next /app/frontend/.next
COPY --from=frontend-builder /app/frontend/public /app/frontend/public
COPY --from=frontend-builder /app/frontend/package*.json /app/frontend/
COPY --from=frontend-builder /app/frontend/next.config.* /app/frontend/

# Installa solo production dependencies per Next.js runtime
WORKDIR /app/frontend
RUN npm ci --only=production && npm cache clean --force

# -----------------------------------------------------------------------------
# Copia Configurazioni
# -----------------------------------------------------------------------------
WORKDIR /app

# Supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/conf.d/ /etc/nginx/conf.d/ 2>/dev/null || true

# Scripts
COPY scripts/entrypoint.sh /app/scripts/entrypoint.sh
COPY scripts/backup.sh /app/scripts/backup.sh 2>/dev/null || true
RUN chmod +x /app/scripts/*.sh

# -----------------------------------------------------------------------------
# Setup PostgreSQL
# -----------------------------------------------------------------------------
USER postgres

# Inizializza database cluster
RUN /usr/lib/postgresql/15/bin/initdb -D /var/lib/postgresql/15/main

# Configura PostgreSQL per accettare connessioni locali
RUN echo "host all all 127.0.0.1/32 trust" >> /var/lib/postgresql/15/main/pg_hba.conf && \
    echo "host all all ::1/128 trust" >> /var/lib/postgresql/15/main/pg_hba.conf && \
    echo "listen_addresses = 'localhost'" >> /var/lib/postgresql/15/main/postgresql.conf

USER root

# -----------------------------------------------------------------------------
# Setup Redis
# -----------------------------------------------------------------------------
# Crea directory per Redis data
RUN mkdir -p /var/lib/redis && \
    chown redis:redis /var/lib/redis

# Configura Redis
RUN echo "dir /var/lib/redis" >> /etc/redis/redis.conf && \
    echo "appendonly yes" >> /etc/redis/redis.conf && \
    echo "appendfilename 'appendonly.aof'" >> /etc/redis/redis.conf && \
    echo "save 900 1" >> /etc/redis/redis.conf && \
    echo "save 300 10" >> /etc/redis/redis.conf && \
    echo "save 60 10000" >> /etc/redis/redis.conf

# -----------------------------------------------------------------------------
# Create Directories & Volumes
# -----------------------------------------------------------------------------
RUN mkdir -p \
    /app/data/postgres \
    /app/data/redis \
    /app/uploads \
    /app/logs \
    /backups && \
    chmod -R 755 /app

# Link PostgreSQL data directory
RUN ln -s /var/lib/postgresql/15/main /app/data/postgres

# -----------------------------------------------------------------------------
# Expose Ports
# -----------------------------------------------------------------------------
# Port 80 per Nginx (interno)
EXPOSE 80

# Health check ports (opzionali, per debug)
# EXPOSE 3000 8000 5432 6379

# -----------------------------------------------------------------------------
# Volumes
# -----------------------------------------------------------------------------
VOLUME ["/app/data", "/app/uploads", "/app/logs", "/backups"]

# -----------------------------------------------------------------------------
# Health Check
# -----------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# -----------------------------------------------------------------------------
# Entrypoint
# -----------------------------------------------------------------------------
ENTRYPOINT ["/app/scripts/entrypoint.sh"]

# Default command: run supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

# -----------------------------------------------------------------------------
# Metadata
# -----------------------------------------------------------------------------
LABEL maintainer="Davide Botto <davide@aistrategyhub.eu>"
LABEL description="AI Strategy Hub - Monolithic container with Frontend, Backend, PostgreSQL, Redis"
LABEL version="0.1.0"
