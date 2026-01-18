# External Integrations

**Analysis Date:** 2026-01-18

## APIs & External Services

**AI Services:**
- Anthropic Claude API - AI chatbot with RAG pipeline
  - SDK/Client: `anthropic==0.12.0`
  - Model: claude-sonnet-4-5-20250929
  - Auth: `ANTHROPIC_API_KEY` environment variable
  - Used for: Customer support chatbot with context-aware responses
  - Config: `/Users/davidebotto/aistrategyhub/backend/app/services/claude_service.py`

- OpenAI API - Embeddings generation for vector search
  - SDK/Client: `openai==1.12.0`
  - Auth: API key via environment variable
  - Used for: Creating embeddings for RAG knowledge base chunks
  - Storage: pgvector extension in PostgreSQL

**Email Service:**
- Microsoft Graph API - Email sending via Microsoft 365
  - SDK/Client: `msal==1.26.0` (Microsoft Authentication Library)
  - Auth: OAuth 2.0 client credentials flow
    - `MS_GRAPH_TENANT_ID`
    - `MS_GRAPH_CLIENT_ID`
    - `MS_GRAPH_CLIENT_SECRET`
  - Sender: `noreply@aistrategyhub.eu` (configured in `MS_GRAPH_SENDER_EMAIL`)
  - Endpoint: `https://graph.microsoft.com/v1.0/users/{user-id}/sendMail`
  - Permissions: Mail.Send
  - Implementation: `/Users/davidebotto/aistrategyhub/backend/app/services/ms_graph.py`
  - Used for: Email verification, password reset, order confirmations, invoice notifications

**Payment Processing:**
- Stripe - Payment processing and subscriptions
  - SDK/Client: `stripe==7.11.0` (Python), `@stripe/stripe-js==2.4.0` (JavaScript)
  - Auth:
    - `STRIPE_SECRET_KEY` (backend)
    - `STRIPE_PUBLISHABLE_KEY` (frontend)
    - `STRIPE_WEBHOOK_SECRET` (webhook signature verification)
  - Features: Payment Intents, Subscriptions, 3D Secure (SCA) compliance
  - Currency: EUR (`STRIPE_CURRENCY=eur`)
  - Webhooks: `payment_intent.succeeded`, `customer.subscription.*`
  - Implementation: `/Users/davidebotto/aistrategyhub/backend/app/services/stripe_service.py`

**Italian E-Invoicing:**
- Sistema di Interscambio (SDI) - Italian electronic invoicing system
  - Format: XML PA 1.2.1 (Fatturazione Elettronica)
  - Delivery: PEC email to SDI
  - PEC Account: `SDI_PEC_EMAIL` and `SDI_PEC_PASSWORD`
  - XML generation: `/Users/davidebotto/aistrategyhub/backend/app/services/invoice_xml.py`
  - PDF generation: `/Users/davidebotto/aistrategyhub/backend/app/services/invoice_pdf.py`
  - Requirements: 10-year retention, tracking (sent/accepted/rejected)
  - Seller data configured via environment variables (`SELLER_*` prefix)

## Data Storage

**Databases:**
- PostgreSQL 15+
  - Connection: `DATABASE_URL` or constructed from `POSTGRES_*` env vars
  - Client: SQLAlchemy 2.0.25 (ORM) with asyncpg 0.29.0 (async) and psycopg2-binary 2.9.9 (sync)
  - Extensions: pgvector 0.2.4 for vector similarity search
  - Migrations: Alembic 1.13.1 (`/Users/davidebotto/aistrategyhub/backend/migrations/`)
  - Default credentials: `POSTGRES_USER=aistrategyhub`, `POSTGRES_PASSWORD` (env var)
  - Port: 5432 (internal in Docker, exposed for development)

**File Storage:**
- Local filesystem
  - Upload directory: `UPLOAD_DIR=/app/uploads`
  - Max size: `MAX_UPLOAD_SIZE_MB=10`
  - Allowed extensions: pdf, docx, doc, txt, md, png, jpg, jpeg, gif, webp
  - Implementation: `/Users/davidebotto/aistrategyhub/backend/app/services/file_storage.py`
  - File types: User uploads, knowledge base documents, invoice PDFs/XMLs

**Caching:**
- Redis 7
  - Connection: `REDIS_URL` or constructed from `REDIS_*` env vars
  - Client: `redis==5.0.1` with `hiredis==2.3.2`
  - Port: 6379 (internal in Docker)
  - Used for: Session storage, API response caching
  - TTL: `SESSION_TTL_SECONDS=604800` (7 days)

**Vector Database:**
- pgvector (PostgreSQL extension)
  - Version: 0.2.4
  - Used for: RAG (Retrieval Augmented Generation) similarity search
  - Tables: `knowledge_base_documents`, `knowledge_base_chunks`
  - Embeddings stored as vector columns

## Authentication & Identity

**Auth Provider:**
- Custom JWT-based authentication
  - Implementation: `/Users/davidebotto/aistrategyhub/backend/app/core/security.py`
  - Token type: JWT with HS256 algorithm
  - Secrets: `JWT_SECRET_KEY` (env var, min 32 chars)
  - Token expiry:
    - Access token: 15 minutes (`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`)
    - Refresh token: 7 days (`JWT_REFRESH_TOKEN_EXPIRE_DAYS`)
  - Password hashing: Argon2 via `passlib[argon2]==1.7.4`

**Multi-Factor Authentication:**
- TOTP (Time-based One-Time Password)
  - Library: `pyotp==2.9.0`
  - QR code generation: `qrcode[pil]==7.4.2`, `qrcode.react==4.2.0` (frontend)
  - Issuer: `MFA_ISSUER_NAME="AI Strategy Hub"`
  - Backup codes: 10 codes (`MFA_BACKUP_CODES_COUNT=10`)
  - Setup flow: `/Users/davidebotto/aistrategyhub/frontend/src/app/setup-mfa/page.tsx`

**Email Verification:**
- Token-based email verification
  - Tokens expire in 24 hours (`EMAIL_VERIFICATION_EXPIRE_HOURS=24`)
  - Sent via Microsoft Graph API
  - Templates: Jinja2 in `/Users/davidebotto/aistrategyhub/backend/app/templates/`

**Password Reset:**
- Token-based password reset
  - Tokens expire in 1 hour (`PASSWORD_RESET_EXPIRE_HOURS=1`)
  - Sent via Microsoft Graph API

## Monitoring & Observability

**Error Tracking:**
- None (optional Sentry configuration commented out)
  - Placeholder: `SENTRY_DSN` in environment template

**Logs:**
- Structured JSON logging via `python-json-logger==2.0.7`
  - Configuration: `/Users/davidebotto/aistrategyhub/backend/app/core/logging_config.py`
  - Log directory: `LOG_DIR=/app/logs`
  - Log level: `LOG_LEVEL=DEBUG` (development), INFO/WARNING (production)
  - Format: `LOG_FORMAT=json`
  - Database logging: `audit_logs` and `system_logs` tables
  - Implementation: `/Users/davidebotto/aistrategyhub/backend/app/core/system_logger.py`

**Application Logs:**
- Supervisord logs: `/app/logs/supervisord.log`
- Backend logs: `/app/logs/backend.out.log`, `/app/logs/backend.err.log`
- Frontend logs: `/app/logs/frontend.out.log`, `/app/logs/frontend.err.log`
- PostgreSQL logs: `/app/logs/postgresql.out.log`, `/app/logs/postgresql.err.log`
- Redis logs: `/app/logs/redis.out.log`, `/app/logs/redis.err.log`

## CI/CD & Deployment

**Hosting:**
- Linode VPS with ArchLinux
  - Single Docker container deployment
  - Domain: aistrategyhub.eu
  - SSL/TLS: Let's Encrypt via Nginx

**CI Pipeline:**
- GitHub Actions (configured but not detailed in codebase)
  - Repository: GitHub (implied by GitHub Actions reference)

**Build Process:**
- Docker multi-stage build
  - Stage 1: Frontend build (Node 20 Alpine) → `/Users/davidebotto/aistrategyhub/Dockerfile` lines 19-29
  - Stage 2: Backend dependencies (Python 3.11 Slim) → lines 34-48
  - Stage 3: Final monolithic container → lines 53-215
  - Entry point: `/Users/davidebotto/aistrategyhub/scripts/entrypoint.sh`
  - Process manager: Supervisord manages all services

**Deployment Scripts:**
- `/Users/davidebotto/aistrategyhub/scripts/deploy.sh`
- `/Users/davidebotto/aistrategyhub/scripts/backup.sh`
- `/Users/davidebotto/aistrategyhub/start-dev.sh` (development)

## Environment Configuration

**Required env vars:**

**Critical (must be set):**
- `SECRET_KEY` - Application secret (min 32 chars)
- `JWT_SECRET_KEY` - JWT signing key (min 32 chars)
- `POSTGRES_PASSWORD` - Database password
- `ANTHROPIC_API_KEY` - Claude API key
- `STRIPE_SECRET_KEY` - Stripe secret key
- `STRIPE_WEBHOOK_SECRET` - Stripe webhook signature verification
- `MS_GRAPH_CLIENT_SECRET` - Microsoft Graph API secret

**Optional but recommended:**
- `REDIS_PASSWORD` - Redis password (empty for development)
- `SDI_PEC_PASSWORD` - PEC email password for e-invoicing
- `SENTRY_DSN` - Error tracking (if enabled)

**Secrets location:**
- Development: `.env` file in project root (gitignored)
- Backend-specific: `/Users/davidebotto/aistrategyhub/backend/.env`
- Frontend-specific: `/Users/davidebotto/aistrategyhub/frontend/.env.local`
- Examples: `.env.example` files in root and subdirectories
- Production: Environment variables in Docker container

## Webhooks & Callbacks

**Incoming:**
- Stripe Webhooks
  - Endpoint: `/api/v1/webhooks/stripe` (TODO - referenced but not yet implemented)
  - Events: `payment_intent.succeeded`, `customer.subscription.*`
  - Verification: Stripe webhook signature (`STRIPE_WEBHOOK_SECRET`)

**Outgoing:**
- Email notifications via Microsoft Graph API
  - Registration confirmation
  - Email verification
  - Password reset
  - Order confirmations
  - Invoice generation notifications
  - Newsletter campaigns

- SDI (Sistema di Interscambio) for e-invoices
  - PEC email delivery to Italian tax authority
  - XML format PA 1.2.1
  - Tracking: invoice status updates (accepted/rejected)

## Cross-Origin Resource Sharing (CORS)

**Configuration:**
- Allowed origins: `CORS_ORIGINS` environment variable
  - Development: `http://localhost:3000`
  - Production: `https://aistrategyhub.eu`, `https://www.aistrategyhub.eu`
- Credentials: Enabled (`allow_credentials=True`)
- Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
- Implementation: `/Users/davidebotto/aistrategyhub/backend/app/main.py` lines 96-112

## Rate Limiting

**Configuration:**
- Per minute: `RATE_LIMIT_PER_MINUTE=60`
- Burst: `RATE_LIMIT_BURST=10`
- Implementation: TODO (referenced in config but not yet implemented)

---

*Integration audit: 2026-01-18*
