# 🚀 AI Strategy Hub - Setup Guide

Guida completa per configurare e avviare il progetto in ambiente di sviluppo.

## 📋 Prerequisiti

### Obbligatori
- **Node.js** 18+ (per frontend Next.js)
- **Python** 3.11+ (per backend FastAPI)
- **Docker Desktop** (per PostgreSQL + Redis)

### Verifiche
```bash
node --version    # v18.x o superiore
python3 --version # 3.11.x o superiore
docker --version  # Qualsiasi versione recente
```

---

## ⚡ Quick Start (Metodo Consigliato)

### 1. Avvia il database
```bash
./start-dev.sh
```

Questo script:
- ✅ Avvia PostgreSQL con pgvector
- ✅ Avvia Redis
- ✅ Esegue le migrazioni del database
- ✅ Verifica che tutto sia pronto

### 2. Avvia il backend
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload
```

Disponibile su: http://localhost:8000

### 3. Avvia il frontend
```bash
cd frontend
npm run dev
```

Disponibile su: http://localhost:3000

---

## 🔧 Setup Dettagliato

### Backend Setup

1. **Crea virtual environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

2. **Installa dipendenze**
```bash
pip install -r requirements.txt
```

3. **Configura variabili ambiente**

Il file `.env` è già configurato con:
- ✅ Claude API Key (chatbot)
- ✅ OpenAI API Key (embeddings)
- ✅ Database credentials
- ✅ Microsoft Graph API (email)

### Frontend Setup

1. **Installa dipendenze**
```bash
cd frontend
npm install
```

2. **Verifica configurazione**

Il file `.env.local` dovrebbe contenere:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🗄️ Database

### Con Docker (Consigliato)

```bash
# Avvia containers
docker-compose up -d

# Verifica status
docker-compose ps

# Logs
docker-compose logs -f postgres

# Stop
docker-compose down
```

### Senza Docker

Se preferisci installare PostgreSQL nativo:

1. Installa PostgreSQL 16+
2. Installa estensione pgvector:
```bash
# macOS con Homebrew
brew install pgvector

# Abilita in database
psql -U aistrategyhub -d aistrategyhub -c "CREATE EXTENSION vector;"
```

### Migrazioni Database

```bash
cd backend
source venv/bin/activate

# Applica tutte le migrazioni
alembic upgrade head

# Crea nuova migrazione (se necessario)
alembic revision --autogenerate -m "descrizione"

# Rollback ultima migrazione
alembic downgrade -1
```

---

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

---

## 🔑 Chiavi API Configurate

Il progetto è già configurato con le seguenti API:

### Claude API (Anthropic) ✅
- **Uso**: Chatbot conversazionale
- **Modello**: claude-sonnet-4-5-20250929
- **Key**: Configurata in `.env`

### OpenAI API ✅
- **Uso**: Embeddings per RAG
- **Modello**: text-embedding-3-small
- **Key**: Configurata in `.env`

### Microsoft Graph API ✅
- **Uso**: Invio email (noreply@aistrategyhub.eu)
- **Tenant**: Configurato
- **Credentials**: Configurate in `.env`

### Stripe API ⚠️
- **Uso**: Pagamenti (opzionale per sviluppo)
- **Status**: Non configurato
- **Nota**: Lasciato vuoto, puoi testare senza

---

## 📂 Struttura Progetto

```
aistrategyhub/
├── backend/                 # FastAPI Backend
│   ├── app/
│   │   ├── api/routes/     # Endpoints API
│   │   ├── core/           # Config, security, database
│   │   ├── models/         # SQLAlchemy models
│   │   ├── services/       # Business logic
│   │   └── main.py         # App entry point
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── .env                # Environment variables ✅
│
├── frontend/               # Next.js Frontend
│   ├── src/
│   │   ├── app/           # App Router pages
│   │   ├── components/    # React components
│   │   ├── contexts/      # React contexts
│   │   └── lib/           # Utilities
│   ├── package.json       # Node dependencies
│   └── .env.local         # Frontend env vars
│
├── docker-compose.yml     # Database containers
├── start-dev.sh          # Quick start script ✅
└── SETUP.md              # This file
```

---

## 🎯 Features Implementate

### ✅ Backend
- [x] Authentication & Authorization (JWT + MFA)
- [x] User Management (CRUD, roles, MFA)
- [x] Services Catalog (CRUD, categories, pricing)
- [x] Orders & Checkout (Stripe integration)
- [x] Invoicing System (Italian e-invoicing)
- [x] CMS Headless (Blog, FAQs, Case Studies)
- [x] File Upload & Management
- [x] AI Chatbot with RAG (Claude + pgvector)
- [x] Knowledge Base Management
- [x] Guardrails System (rate limiting, content filtering)
- [x] Email Service (Microsoft Graph API)

### ✅ Frontend
- [x] Landing Page
- [x] Authentication Pages (login, register, MFA)
- [x] User Dashboard
- [x] Admin Dashboard
- [x] Services Catalog
- [x] Checkout Flow
- [x] Blog CMS
- [x] Admin CRUD Interfaces
- [x] Rich Text Editor (TipTap)
- [x] AI Chat Widget (floating button)
- [x] Knowledge Base Admin UI

---

## 🐛 Troubleshooting

### Port già in uso
```bash
# Trova processo che usa la porta
lsof -ti:8000  # Backend
lsof -ti:3000  # Frontend
lsof -ti:5432  # PostgreSQL

# Kill processo
kill -9 <PID>
```

### Database connection error
```bash
# Verifica che PostgreSQL sia in running
docker-compose ps

# Riavvia container
docker-compose restart postgres

# Verifica logs
docker-compose logs postgres
```

### Frontend build errors
```bash
# Pulisci cache e reinstalla
cd frontend
rm -rf .next node_modules package-lock.json
npm install
```

### Python package errors
```bash
# Ricrea virtual environment
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 API Documentation

Quando il backend è in running, visita:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🔒 Security Notes

### Development
- Il file `.env` contiene credenziali reali ma è per sviluppo locale
- Non committare mai `.env` in Git (già in `.gitignore`)

### Production
- Usa variabili ambiente del server (non file `.env`)
- Ruota tutte le chiavi API
- Abilita HTTPS
- Configura CORS correttamente
- Abilita rate limiting più aggressivo

---

## 📞 Support

Per problemi o domande:
- GitHub Issues: [repository]
- Email: support@aistrategyhub.eu

---

**Ultima modifica**: 2026-01-15
**Versione**: 0.1.0
