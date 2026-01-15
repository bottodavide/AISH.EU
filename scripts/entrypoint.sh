#!/bin/bash
# =============================================================================
# AI STRATEGY HUB - DOCKER ENTRYPOINT SCRIPT
# =============================================================================
# Questo script viene eseguito all'avvio del container e:
# 1. Inizializza PostgreSQL database
# 2. Esegue migrations database
# 3. Verifica configurazioni
# 4. Avvia supervisord con tutti i servizi
#
# Autore: Claude per Davide
# Data: 2026-01-15
# =============================================================================

set -e  # Exit on error

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni helper
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# =============================================================================
# INIZIO SCRIPT
# =============================================================================

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          AI STRATEGY HUB - Container Starting                 ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# -----------------------------------------------------------------------------
# 1. Verifica Environment Variables
# -----------------------------------------------------------------------------
log_info "Verifying environment variables..."

REQUIRED_VARS=(
    "DATABASE_URL"
    "REDIS_URL"
    "SECRET_KEY"
    "JWT_SECRET_KEY"
)

MISSING_VARS=0
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        log_error "Missing required environment variable: $var"
        MISSING_VARS=1
    fi
done

if [ $MISSING_VARS -eq 1 ]; then
    log_error "Some required environment variables are missing!"
    log_warning "Please check your .env file or docker environment settings"
    exit 1
fi

log_success "Environment variables verified"

# -----------------------------------------------------------------------------
# 2. Crea Directory se non esistono
# -----------------------------------------------------------------------------
log_info "Creating required directories..."

mkdir -p /app/data/postgres
mkdir -p /app/data/redis
mkdir -p /app/uploads
mkdir -p /app/logs
mkdir -p /backups

chown -R postgres:postgres /var/lib/postgresql/15/main
chown -R redis:redis /var/lib/redis

log_success "Directories created"

# -----------------------------------------------------------------------------
# 3. Inizializza PostgreSQL
# -----------------------------------------------------------------------------
log_info "Initializing PostgreSQL..."

# Avvia PostgreSQL temporaneamente come postgres user
su - postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main -l /app/logs/postgresql-init.log start"

# Aspetta che PostgreSQL sia pronto
log_info "Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if su - postgres -c "psql -c 'SELECT 1' > /dev/null 2>&1"; then
        log_success "PostgreSQL is ready"
        break
    fi

    if [ $i -eq 30 ]; then
        log_error "PostgreSQL failed to start within 30 seconds"
        cat /app/logs/postgresql-init.log
        exit 1
    fi

    sleep 1
done

# Crea database se non esiste
DB_NAME=${POSTGRES_DB:-aistrategyhub}
DB_USER=${POSTGRES_USER:-aistrategyhub}
DB_PASSWORD=${POSTGRES_PASSWORD:-changeme}

log_info "Creating database '$DB_NAME' if not exists..."

su - postgres -c "psql -tc \"SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'\" | grep -q 1 || psql -c \"CREATE DATABASE $DB_NAME\""

# Crea user se non esiste
su - postgres -c "psql -tc \"SELECT 1 FROM pg_user WHERE usename = '$DB_USER'\" | grep -q 1 || psql -c \"CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD'\""

# Concedi permessi
su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER\""

# Installa estensione pgvector per RAG
log_info "Installing pgvector extension..."
su - postgres -c "psql -d $DB_NAME -c 'CREATE EXTENSION IF NOT EXISTS vector'"

log_success "PostgreSQL initialized"

# Ferma PostgreSQL temporaneo (verrà riavviato da supervisord)
su - postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main stop"

# -----------------------------------------------------------------------------
# 4. Esegui Database Migrations
# -----------------------------------------------------------------------------
log_info "Running database migrations..."

cd /app/backend

# Verifica se Alembic è configurato
if [ -f "alembic.ini" ]; then
    # Avvia PostgreSQL di nuovo temporaneamente per migrations
    su - postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main -l /app/logs/postgresql-migration.log start"

    # Aspetta che sia pronto
    sleep 5

    # Esegui migrations
    if alembic upgrade head; then
        log_success "Database migrations completed"
    else
        log_warning "Database migrations failed or not needed"
    fi

    # Ferma PostgreSQL di nuovo
    su - postgres -c "/usr/lib/postgresql/15/bin/pg_ctl -D /var/lib/postgresql/15/main stop"
else
    log_warning "Alembic not configured yet, skipping migrations"
fi

# -----------------------------------------------------------------------------
# 5. Verifica Nginx Configuration
# -----------------------------------------------------------------------------
log_info "Testing Nginx configuration..."

if nginx -t 2>/dev/null; then
    log_success "Nginx configuration is valid"
else
    log_error "Nginx configuration test failed"
    nginx -t
    exit 1
fi

# -----------------------------------------------------------------------------
# 6. Genera Secret Key se mancante (solo per dev)
# -----------------------------------------------------------------------------
if [ "$ENVIRONMENT" = "development" ] && [ -z "$SECRET_KEY" ]; then
    log_warning "Generating random SECRET_KEY for development"
    export SECRET_KEY=$(openssl rand -hex 32)
fi

# -----------------------------------------------------------------------------
# 7. Display Configuration Summary
# -----------------------------------------------------------------------------
log_info "Configuration Summary:"
echo "  Environment: ${ENVIRONMENT:-production}"
echo "  Database: PostgreSQL 15"
echo "  Cache: Redis 7"
echo "  Backend: FastAPI (port 8000)"
echo "  Frontend: Next.js (port 3000)"
echo "  Nginx: Internal routing (port 80)"

# -----------------------------------------------------------------------------
# 8. Health Check Script
# -----------------------------------------------------------------------------
log_info "Creating health check endpoint..."

cat > /tmp/health_check.sh << 'EOF'
#!/bin/bash
# Simple health check script

# Check if all services are running
SERVICES=("postgresql" "redis" "backend" "frontend" "nginx")

for service in "${SERVICES[@]}"; do
    if ! supervisorctl status $service | grep -q RUNNING; then
        echo "Service $service is not running"
        exit 1
    fi
done

# Check HTTP endpoints
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend health check failed"
    exit 1
fi

if ! curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "Frontend health check failed"
    exit 1
fi

echo "All services healthy"
exit 0
EOF

chmod +x /tmp/health_check.sh

# -----------------------------------------------------------------------------
# 9. Avvia Supervisord
# -----------------------------------------------------------------------------
log_success "Initialization completed successfully!"
echo ""
log_info "Starting all services via supervisord..."
echo ""

# Esegui il comando passato (default: supervisord)
exec "$@"
