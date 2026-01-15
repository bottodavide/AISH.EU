#!/bin/bash
# =============================================================================
# AI STRATEGY HUB - Setup Script
# =============================================================================
# Questo script verifica e configura l'ambiente di sviluppo
# Esegui con: ./scripts/setup.sh
# =============================================================================

set -e  # Esci in caso di errore

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funzioni helper
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

check_command() {
    if command -v "$1" &> /dev/null; then
        print_success "$1 è installato"
        return 0
    else
        print_error "$1 non trovato"
        return 1
    fi
}

# =============================================================================
# INIZIO SCRIPT
# =============================================================================

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          AI STRATEGY HUB - Environment Setup                  ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# -----------------------------------------------------------------------------
# 1. Verifica prerequisiti
# -----------------------------------------------------------------------------
print_header "Verifica Prerequisiti"

MISSING_DEPS=0

# Node.js
if check_command node; then
    NODE_VERSION=$(node --version)
    echo "  Versione: $NODE_VERSION"
else
    MISSING_DEPS=1
    echo "  Installa con: brew install node"
fi

# npm
if check_command npm; then
    NPM_VERSION=$(npm --version)
    echo "  Versione: $NPM_VERSION"
fi

# Python
if check_command python3; then
    PYTHON_VERSION=$(python3 --version)
    echo "  Versione: $PYTHON_VERSION"
else
    MISSING_DEPS=1
    echo "  Installa con: brew install python@3.11"
fi

# pip
if check_command pip3; then
    PIP_VERSION=$(pip3 --version | cut -d' ' -f2)
    echo "  Versione: $PIP_VERSION"
fi

# Docker
if check_command docker; then
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3)
    echo "  Versione: $DOCKER_VERSION"
else
    print_warning "Docker non trovato (opzionale per dev locale)"
    echo "  Installa da: https://www.docker.com/products/docker-desktop/"
fi

# Git
if check_command git; then
    GIT_VERSION=$(git --version | cut -d' ' -f3)
    echo "  Versione: $GIT_VERSION"
else
    MISSING_DEPS=1
    echo "  Installa con: xcode-select --install"
fi

# Claude Code
echo ""
if check_command claude; then
    CLAUDE_VERSION=$(claude --version 2>/dev/null || echo "unknown")
    echo "  Versione: $CLAUDE_VERSION"
else
    print_warning "Claude Code non trovato"
    echo "  Installa con: npm install -g @anthropic-ai/claude-code"
    echo "  Oppure: brew install claude-code"
fi

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    print_error "Alcuni prerequisiti mancano. Installali prima di continuare."
    exit 1
fi

# -----------------------------------------------------------------------------
# 2. Verifica struttura progetto
# -----------------------------------------------------------------------------
print_header "Verifica Struttura Progetto"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Directory progetto: $PROJECT_DIR"

# Verifica file essenziali
ESSENTIAL_FILES=(
    "CLAUDE.md"
    ".env.example"
    ".gitignore"
    "docs/PROJECT_REQUIREMENTS.md"
    "docs/ARCHITECTURE.md"
    "docs/TODO.md"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$PROJECT_DIR/$file" ]; then
        print_success "$file esiste"
    else
        print_error "$file mancante!"
    fi
done

# Crea directory se mancanti
DIRECTORIES=(
    "frontend/src"
    "backend/app"
    "nginx"
    "scripts"
    "docs"
)

for dir in "${DIRECTORIES[@]}"; do
    if [ ! -d "$PROJECT_DIR/$dir" ]; then
        mkdir -p "$PROJECT_DIR/$dir"
        print_success "Creata directory: $dir"
    fi
done

# -----------------------------------------------------------------------------
# 3. Configurazione .env
# -----------------------------------------------------------------------------
print_header "Configurazione Environment"

if [ -f "$PROJECT_DIR/.env" ]; then
    print_success ".env esiste già"
else
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        print_warning ".env creato da .env.example"
        echo "  ⚠️  IMPORTANTE: Modifica .env con i tuoi valori reali!"
    else
        print_error ".env.example non trovato"
    fi
fi

# -----------------------------------------------------------------------------
# 4. Setup Backend Python
# -----------------------------------------------------------------------------
print_header "Setup Backend (Python)"

BACKEND_DIR="$PROJECT_DIR/backend"

if [ -d "$BACKEND_DIR" ]; then
    cd "$BACKEND_DIR"
    
    # Crea virtual environment se non esiste
    if [ ! -d "venv" ]; then
        echo "Creazione virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment creato"
    else
        print_success "Virtual environment esiste già"
    fi
    
    # Attiva venv e installa dipendenze se requirements.txt esiste
    if [ -f "requirements.txt" ]; then
        echo "Installazione dipendenze Python..."
        source venv/bin/activate
        pip install -r requirements.txt --quiet
        print_success "Dipendenze Python installate"
        deactivate
    else
        print_warning "requirements.txt non trovato (verrà creato durante lo sviluppo)"
    fi
    
    cd "$PROJECT_DIR"
else
    print_warning "Directory backend non trovata"
fi

# -----------------------------------------------------------------------------
# 5. Setup Frontend Node.js
# -----------------------------------------------------------------------------
print_header "Setup Frontend (Next.js)"

FRONTEND_DIR="$PROJECT_DIR/frontend"

if [ -d "$FRONTEND_DIR" ]; then
    cd "$FRONTEND_DIR"
    
    if [ -f "package.json" ]; then
        echo "Installazione dipendenze Node.js..."
        npm install --silent
        print_success "Dipendenze Node.js installate"
    else
        print_warning "package.json non trovato (verrà creato durante lo sviluppo)"
    fi
    
    cd "$PROJECT_DIR"
else
    print_warning "Directory frontend non trovata"
fi

# -----------------------------------------------------------------------------
# 6. Verifica Claude Code
# -----------------------------------------------------------------------------
print_header "Configurazione Claude Code"

if command -v claude &> /dev/null; then
    print_success "Claude Code è pronto"
    echo ""
    echo "Per iniziare lo sviluppo:"
    echo -e "  ${GREEN}cd $PROJECT_DIR${NC}"
    echo -e "  ${GREEN}claude${NC}"
    echo ""
    echo "Claude Code leggerà automaticamente CLAUDE.md per il contesto."
else
    print_warning "Claude Code non installato"
    echo ""
    echo "Per installare Claude Code:"
    echo -e "  ${YELLOW}npm install -g @anthropic-ai/claude-code${NC}"
    echo ""
    echo "Poi configura la API key:"
    echo -e "  ${YELLOW}claude config set apiKey sk-ant-...${NC}"
fi

# -----------------------------------------------------------------------------
# 7. Riepilogo
# -----------------------------------------------------------------------------
print_header "Riepilogo Setup"

echo "Progetto: AI Strategy Hub"
echo "Directory: $PROJECT_DIR"
echo ""
echo "Prossimi passi:"
echo "  1. Modifica .env con i tuoi valori reali"
echo "  2. Configura Azure AD per MS Graph API"
echo "  3. Configura Stripe (test mode)"
echo "  4. Avvia sviluppo con: cd $PROJECT_DIR && claude"
echo ""

echo -e "${GREEN}✓ Setup completato!${NC}"
echo ""
