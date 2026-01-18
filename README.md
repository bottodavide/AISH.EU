# AI Strategy Hub

**Piattaforma E-Commerce per Servizi di Consulenza**
AI, GDPR, Cybersecurity & Compliance

[![Test Suite](https://github.com/bottodavide/AISH.EU/workflows/Test%20Suite/badge.svg)](https://github.com/bottodavide/AISH.EU/actions/workflows/test.yml)
[![Code Quality](https://github.com/bottodavide/AISH.EU/workflows/Code%20Quality/badge.svg)](https://github.com/bottodavide/AISH.EU/actions/workflows/lint.yml)
[![codecov](https://codecov.io/gh/bottodavide/AISH.EU/branch/main/graph/badge.svg)](https://codecov.io/gh/bottodavide/AISH.EU)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Node 20+](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Panoramica

AI Strategy Hub è una piattaforma completa per la vendita di servizi di consulenza con:

- 🛒 **E-Commerce Servizi**: Pacchetti fissi, custom quote, abbonamenti
- 🎨 **CMS Headless**: Gestione completa contenuti frontend
- 📝 **Blog & Newsletter**: Con automazione email
- 🤖 **AI Chatbot**: Knowledge base con RAG (Claude API)
- 💳 **Pagamenti Stripe**: Payment Intents + Subscriptions
- 📄 **Fatturazione Elettronica**: XML SDI + PEC (Italia)
- 👥 **Area Cliente**: Dashboard, ordini, fatture, ticket support
- 🔐 **Auth Completa**: JWT + MFA (TOTP) + Email verification

## Stack Tecnologico

### Frontend
- Next.js 14 (App Router)
- TypeScript (strict mode)
- TailwindCSS + shadcn/ui
- React Hook Form + Zod
- TipTap (rich text editor)

### Backend
- FastAPI (Python 3.11+)
- SQLAlchemy 2.0 (ORM)
- Pydantic v2 (validation)
- PostgreSQL 15 + pgvector (RAG)
- Redis 7 (cache/sessions)

### Deployment
- Docker (container singolo monolitico)
- Supervisord (gestione processi)
- Nginx (reverse proxy + SSL)
- Linode VPS + ArchLinux

### Integrazioni
- **Microsoft Graph API** (email: noreply@aistrategyhub.eu)
- **Stripe** (pagamenti + abbonamenti)
- **Claude API Sonnet 4.5** (chatbot RAG)
- **Sistema di Interscambio SDI** (fatture elettroniche)

## Quick Start

### Prerequisiti

```bash
# Verifica installazioni
node --version    # v20+
python3 --version # 3.11+
docker --version  # 24+
```

### Setup Locale

```bash
# Clone repository (se necessario)
git clone <repository-url>
cd aistrategyhub

# Esegui setup automatico
./scripts/setup.sh

# Configura variabili ambiente
cp .env.example .env
# Modifica .env con i tuoi valori reali
```

### Sviluppo Backend

```bash
cd backend

# Crea virtual environment
python3 -m venv venv
source venv/bin/activate

# Installa dipendenze
pip install -r requirements.txt

# Esegui migrations database
alembic upgrade head

# Avvia server development
uvicorn app.main:app --reload --port 8000
```

### Sviluppo Frontend

```bash
cd frontend

# Installa dipendenze
npm install

# Avvia development server
npm run dev

# Frontend disponibile su http://localhost:3000
```

### Database Locale

```bash
# PostgreSQL
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=aistrategyhub \
  -p 5432:5432 \
  postgres:15

# Redis
docker run -d --name redis \
  -p 6379:6379 \
  redis:7
```

## Struttura Progetto

```
aistrategyhub/
├── frontend/              # Next.js 14 application
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # Utilities, API client
│   │   └── styles/       # CSS/Tailwind
│   ├── public/           # Static assets
│   └── package.json
├── backend/              # FastAPI application
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Config, security, auth
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Business logic
│   │   └── workers/      # Background tasks
│   ├── migrations/       # Alembic migrations
│   └── requirements.txt
├── nginx/                # Nginx configuration
├── scripts/              # Utility scripts (setup, deploy, backup)
├── docs/                 # Documentation
│   ├── ARCHITECTURE.md
│   ├── PROJECT_REQUIREMENTS.md
│   └── TODO.md
├── Dockerfile            # Multi-stage monolith
├── supervisord.conf      # Process manager config
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Documentazione

- **[CLAUDE.md](./CLAUDE.md)** - Contesto rapido per Claude Code
- **[docs/PROJECT_REQUIREMENTS.md](./docs/PROJECT_REQUIREMENTS.md)** - Requisiti completi
- **[docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)** - Architettura dettagliata
- **[docs/TODO.md](./docs/TODO.md)** - Task tracking
- **[docs/DEVELOPMENT_LOG.md](./docs/DEVELOPMENT_LOG.md)** - Log sviluppo

## API Endpoints

### Autenticazione
```
POST   /api/v1/auth/register          - Registrazione + email verification
POST   /api/v1/auth/login             - Login + MFA challenge
POST   /api/v1/auth/refresh           - Refresh JWT token
POST   /api/v1/auth/verify-email      - Verifica email con token
POST   /api/v1/auth/mfa/setup         - Setup TOTP MFA
```

### Servizi & Ordini
```
GET    /api/v1/services               - Lista servizi consulenza
GET    /api/v1/services/:slug         - Dettaglio servizio
POST   /api/v1/quote-requests         - Richiesta preventivo
POST   /api/v1/orders                 - Crea ordine
POST   /api/v1/checkout/payment       - Processa pagamento Stripe
```

### Admin
```
GET    /api/v1/admin/dashboard        - Metriche admin
GET    /api/v1/admin/users            - Gestione utenti
GET    /api/v1/admin/invoices         - Gestione fatture
POST   /api/v1/admin/cms/*            - CMS endpoints
```

Documentazione API completa disponibile su `/api/docs` (Swagger UI).

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

## Deploy Production

```bash
# Build Docker image
docker build -t aistrategyhub:latest .

# Run container
docker run -d \
  --name aistrategyhub \
  --restart unless-stopped \
  -p 80:80 -p 443:443 \
  -v aistrategyhub-data:/app/data \
  -v aistrategyhub-uploads:/app/uploads \
  --env-file .env.production \
  aistrategyhub:latest

# Oppure usa lo script
./scripts/deploy.sh
```

## Security & Compliance

- ✅ **GDPR Compliant** (Privacy by design, Right to erasure)
- ✅ **ISO 27001 Aligned** (Access control, Encryption, Audit logs)
- ✅ **OWASP Top 10** (SQL injection prevention, XSS protection, CSRF tokens)
- ✅ **HTTPS Only** (TLS 1.2+, Strong cipher suites, HSTS)
- ✅ **Rate Limiting** (API protection, DDoS prevention)

## Contribuire

1. Fork il repository
2. Crea feature branch (`git checkout -b feature/nome-feature`)
3. Commit con conventional commits (`git commit -m "feat: descrizione"`)
4. Push al branch (`git push origin feature/nome-feature`)
5. Apri Pull Request

## License

[Da definire]

## Support

- **Email**: support@aistrategyhub.eu
- **Documentation**: [docs/](./docs/)
- **Issues**: [GitHub Issues](https://github.com/yourusername/aistrategyhub/issues)

---

**Versione**: 0.1.0
**Status**: Development
**Ultimo Update**: 2026-01-15

Sviluppato con ❤️ da Claude Code per Davide Botto
