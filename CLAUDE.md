# CLAUDE.md - Contesto Progetto AI Strategy Hub

## Panoramica Progetto

**Nome**: AI Strategy Hub (aistrategyhub.eu)
**Tipo**: Piattaforma consulenza AI/GDPR/Cybersecurity con e-commerce servizi
**Cliente**: Davide (DPO, ISO 27001 Lead Auditor)
**Deployment**: Linode VPS + ArchLinux + Docker (container singolo) + Nginx HTTPS

---

## Stack Tecnologico Confermato

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript (strict mode)
- **Styling**: TailwindCSS + shadcn/ui
- **Forms**: React Hook Form + Zod
- **Rich Text**: TipTap
- **State**: React Context + Zustand

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic v2
- **Auth**: JWT + MFA (TOTP) + Email Verification
- **Background Tasks**: PostgreSQL queue + worker

### Database
- **Primary**: PostgreSQL 15+ con pgvector (per RAG)
- **Cache/Sessions**: Redis 7+

### Integrazioni Esterne
- **Email**: Microsoft Graph API (noreply@aistrategyhub.eu)
- **Payments**: Stripe (Payment Intents + Subscriptions)
- **AI Chatbot**: Claude API Sonnet 4.5 (RAG pipeline)
- **Fatturazione**: Sistema di Interscambio SDI (XML PA + PEC)

### DevOps
- **Container**: Docker singolo monolitico
- **Process Manager**: Supervisord
- **Reverse Proxy**: Nginx (SSL Let's Encrypt)
- **CI/CD**: GitHub Actions

---

## Architettura Container Singolo

```
[Docker Container - aistrategyhub]
├── Supervisord (gestisce tutti i processi)
├── PostgreSQL 15 (:5432 interno)
├── Redis 7 (:6379 interno)
├── FastAPI Backend (:8000)
├── Next.js Frontend (:3000)
├── Nginx interno (:80 → routing)
└── Background Tasks Worker
```

---

## Struttura Directory Progetto

```
aistrategyhub/
├── CLAUDE.md                 # Questo file
├── Dockerfile                # Multi-stage monolite
├── supervisord.conf          # Gestione processi
├── .env.example              # Template variabili
├── frontend/                 # Next.js 14
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   ├── components/       # React components
│   │   ├── lib/              # Utilities, API client
│   │   └── styles/           # CSS/Tailwind
│   ├── public/
│   └── package.json
├── backend/                  # FastAPI
│   ├── app/
│   │   ├── api/              # Endpoints
│   │   ├── core/             # Config, security
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── services/         # Business logic
│   │   └── workers/          # Background tasks
│   ├── migrations/           # Alembic
│   └── requirements.txt
├── nginx/
│   └── nginx.conf
├── scripts/
│   ├── entrypoint.sh
│   ├── backup.sh
│   └── deploy.sh
└── docs/                     # Documentazione
    ├── ARCHITECTURE.md
    ├── PROJECT_REQUIREMENTS.md
    ├── DEVELOPMENT_LOG.md
    └── TODO.md
```

---

## Coding Standards (OBBLIGATORI)

### 1. Ogni file deve avere header descrittivo
```python
"""
Modulo: nome_modulo.py
Descrizione: Cosa fa questo modulo
Autore: Claude per Davide
Data: YYYY-MM-DD
"""
```

### 2. Commenti inline dettagliati
```python
# Verifica che l'utente esista nel database
user = db.query(User).filter(User.email == email).first()
if not user:
    # Log tentativo accesso con email inesistente
    logger.warning(f"Login attempt with unknown email: {email}")
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

### 3. Logging esteso per debugging
```python
import logging
logger = logging.getLogger(__name__)

# Usa livelli appropriati:
logger.debug("Detailed info for debugging")
logger.info("General operational info")
logger.warning("Something unexpected but handled")
logger.error("Error that needs attention", exc_info=True)
logger.critical("System failure")
```

### 4. Error handling robusto
```python
try:
    result = perform_operation()
    logger.info(f"Operation completed: {result}")
except SpecificException as e:
    logger.error(f"Known error: {e}", exc_info=True)
    # Recovery action
except Exception as e:
    logger.critical(f"Unexpected error: {e}", exc_info=True)
    raise
finally:
    # Cleanup
    pass
```

### 5. Type hints sempre
```python
def process_payment(
    order_id: int, 
    stripe_token: str,
    user: User
) -> PaymentResult:
    """Processa pagamento via Stripe."""
    ...
```

---

## Database Schema Principale (45+ tabelle)

### Tabelle Core
- `users` - Utenti con email verification e MFA
- `user_profiles` - Dati anagrafici e fatturazione
- `sessions` - JWT sessions in Redis backup
- `services` - Servizi consulenza
- `service_content` - CMS contenuti servizio
- `quote_requests` - Richieste preventivo
- `orders` + `order_items` - Ordini
- `payments` - Pagamenti Stripe
- `invoices` + `invoice_lines` - Fatture elettroniche
- `pages` - CMS pagine frontend
- `blog_posts` - Blog
- `newsletter_subscribers` - Newsletter
- `knowledge_base_documents` + `knowledge_base_chunks` - RAG
- `chat_conversations` + `chat_messages` - AI Chatbot
- `support_tickets` + `ticket_messages` - Support
- `audit_logs` + `system_logs` - Logging

### Extension PostgreSQL
- `pgvector` - Vector similarity search per RAG

---

## API Endpoints Principali

### Auth
```
POST /api/v1/auth/register      - Registrazione + email verification
POST /api/v1/auth/login         - Login + MFA challenge
POST /api/v1/auth/refresh       - Refresh JWT
POST /api/v1/auth/verify-email  - Verifica email token
POST /api/v1/auth/mfa/setup     - Setup TOTP
POST /api/v1/auth/mfa/verify    - Verifica codice MFA
```

### Services
```
GET  /api/v1/services           - Lista servizi
GET  /api/v1/services/:slug     - Dettaglio servizio
POST /api/v1/quote-requests     - Richiesta preventivo
```

### Orders & Payments
```
POST /api/v1/orders             - Crea ordine
POST /api/v1/checkout/payment   - Processa pagamento Stripe
POST /api/v1/webhooks/stripe    - Webhook Stripe
```

### Invoices
```
GET  /api/v1/invoices           - Lista fatture utente
GET  /api/v1/invoices/:id/pdf   - Download PDF
GET  /api/v1/invoices/:id/xml   - Download XML SDI
```

### AI Chatbot
```
POST /api/v1/chat/message       - Invia messaggio (streaming response)
GET  /api/v1/chat/conversations - Storico conversazioni
```

### Admin (ruoli admin/editor)
```
/api/v1/admin/dashboard         - Metriche
/api/v1/admin/users             - Gestione utenti
/api/v1/admin/invoices          - Gestione fatture
/api/v1/admin/cms/*             - CMS endpoints
/api/v1/admin/ai/*              - Gestione knowledge base
```

---

## Integrazioni Chiave

### Microsoft Graph API (Email)
```python
# OAuth 2.0 client credentials flow
# Endpoint: https://graph.microsoft.com/v1.0/users/{user-id}/sendMail
# Account: noreply@aistrategyhub.eu
# Richiede: Azure AD App con Mail.Send permission
```

### Stripe
```python
# Payment Intents per pagamenti singoli
# Subscriptions per abbonamenti
# Webhooks: payment_intent.succeeded, customer.subscription.*
# 3D Secure (SCA) compliance
```

### Claude API (RAG Chatbot)
```python
# Model: claude-sonnet-4-5-20250929
# RAG: Query → pgvector similarity search → Context injection → Response
# Guardrails: Topic whitelist, content filtering, disclaimers
```

### Sistema di Interscambio (Fatture)
```python
# Formato XML PA 1.2.1
# Invio via PEC a SDI
# Tracking: inviata → accettata/rifiutata
# Conservazione 10 anni
```

---

## Fasi Sviluppo

### FASE 1: Setup (Settimana 1) ← INIZIARE QUI
- [ ] Struttura progetto completa
- [ ] Dockerfile multi-stage
- [ ] Database schema + Alembic
- [ ] Configurazione MS Graph, Stripe, Claude API

### FASE 2: Backend Core (Settimana 2-3)
- [ ] Autenticazione (JWT + MFA + email verification)
- [ ] CRUD servizi
- [ ] Ordini + Stripe
- [ ] Fatturazione elettronica

### FASE 3: CMS & Admin (Settimana 3-4)
- [ ] CMS headless API
- [ ] Admin panel completo
- [ ] Gestione utenti, fatture, ticket

### FASE 4: Frontend (Settimana 4-5)
- [ ] Homepage + pagine servizi
- [ ] Blog
- [ ] Area cliente
- [ ] Checkout

### FASE 5: AI & Advanced (Settimana 5-6)
- [ ] RAG pipeline
- [ ] Chatbot frontend
- [ ] Newsletter automation

### FASE 6: Testing & Deploy (Settimana 6-7)
- [ ] Testing completo
- [ ] Security audit
- [ ] Deploy Linode

---

## Comandi Utili

### Sviluppo locale
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Database
docker run -d --name postgres -e POSTGRES_PASSWORD=dev -p 5432:5432 postgres:15
docker run -d --name redis -p 6379:6379 redis:7
```

### Docker build
```bash
docker build -t aistrategyhub:latest .
docker run -d --name aistrategyhub -p 80:80 -p 443:443 --env-file .env aistrategyhub:latest
```

### Alembic migrations
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## Note per Claude Code

1. **Sempre** includere commenti inline dettagliati
2. **Sempre** aggiungere logging appropriato
3. **Sempre** usare type hints
4. **Mai** hardcodare secrets (usa env variables)
5. **Mai** saltare error handling
6. **Aggiornare** docs/DEVELOPMENT_LOG.md dopo ogni sessione significativa
7. **Verificare** TODO.md per i prossimi task

---

## File di Riferimento

- `docs/PROJECT_REQUIREMENTS.md` - Requisiti completi
- `docs/ARCHITECTURE.md` - Architettura dettagliata
- `docs/TODO.md` - Task tracking
- `docs/DEVELOPMENT_LOG.md` - Log sviluppo

---

**Ultimo Update**: 2026-01-15
**Fase Corrente**: Setup iniziale
