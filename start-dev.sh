#!/bin/bash

# =============================================================================
# AI Strategy Hub - Development Startup Script
# =============================================================================

set -e

echo "🚀 Starting AI Strategy Hub Development Environment"
echo "=================================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker Desktop.${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# Start Docker containers
echo -e "${YELLOW}📦 Starting PostgreSQL and Redis containers...${NC}"
docker-compose up -d

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
until docker exec aistrategyhub-postgres pg_isready -U aistrategyhub &> /dev/null; do
    sleep 1
done
echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"

# Wait for Redis to be ready
echo -e "${YELLOW}⏳ Waiting for Redis to be ready...${NC}"
until docker exec aistrategyhub-redis redis-cli ping &> /dev/null; do
    sleep 1
done
echo -e "${GREEN}✅ Redis is ready!${NC}"

# Run database migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
cd backend
source venv/bin/activate
alembic upgrade head
cd ..
echo -e "${GREEN}✅ Database migrations completed!${NC}"

echo ""
echo "=================================================="
echo -e "${GREEN}✅ Development environment is ready!${NC}"
echo "=================================================="
echo ""
echo "To start the backend:"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload"
echo ""
echo "To start the frontend:"
echo "  cd frontend"
echo "  npm run dev"
echo ""
echo "To stop the containers:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
