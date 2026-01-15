# TODO & TASK TRACKING

**Progetto**: Sito Web Consulenza E-Commerce  
**Ultimo Update**: 2026-01-15 (Notte - Fase 3 - Admin CRUD Complete)

---

## 📊 STATO PROGETTO (Aggiornato)

**Completamento Complessivo**: 80% 🎉🎉

- ✅ Backend Core: 90% (Auth, Users, Services, Orders, Invoices, Files, CMS complete)
- ⚠️ Backend Advanced: 10% (AI, Webhooks, Workers mancanti)
- ✅ Frontend Public Pages: 100% (Homepage, Services, Blog complete ✨)
- ✅ Frontend Protected Pages: 100% (Dashboard, Admin complete ✨)
- ✅ Frontend Admin CRUD UIs: 95% (Services, Blog, Users, Orders complete ✨✨)
- ⚠️ DevOps: 60% (config pronte, CI/CD mancante)
- ❌ Testing: 0%

**Ultimo Commit**: ed9662e - Admin CRUD interfaces complete (7 pagine, +2,773 righe)
**Endpoints Totali**: 71 (21 CMS + 50 core APIs)
**Lines of Code**: ~17,500 backend + ~8,800 frontend = ~26,300 totale

---

## 🔥 PRIORITÀ IMMEDIATE (Prossime Sessioni)

### 1. Admin CRUD Interfaces ✅ COMPLETATO
- [x] Services editor (create/edit form)
- [x] Blog post editor (HTML textarea - TipTap da integrare)
- [x] Categories & Tags management UI
- [x] Users management interface (roles, activate/deactivate)
- [x] Orders management (status updates)
- **Status**: ✅ COMPLETATO (7 pagine, 2,773 righe)
- **Commit**: ed9662e
- **Nota**: Blog editor usa textarea HTML, TipTap da integrare come enhancement

### 2. AI Chatbot & RAG System (CORE FEATURE)
- [ ] Claude API service wrapper
- [ ] RAG pipeline con pgvector
- [ ] Knowledge base upload/processing
- [ ] Vector embeddings generation
- [ ] Similarity search implementation
- [ ] Guardrails system
- [ ] Chat API endpoints
- [ ] Chat widget UI component
- **Blocca**: Funzionalità differenziante del prodotto
- **Tempo stimato**: 2-3 giorni

### 3. Stripe Webhook Handler (CRITICAL)
- [ ] Implementare POST /webhooks/stripe
- [ ] Signature verification
- [ ] Event processing (payment_intent.succeeded)
- [ ] Update order status
- [ ] Idempotency handling
- **Blocca**: Pagamenti funzionanti
- **Tempo stimato**: 4-6 ore

### 4. CMS Headless Backend ✅ COMPLETATO
- [x] CMS API routes (pages, blog, media)
- [x] Page CRUD completo (7 endpoints)
- [x] Blog CRUD completo (14 endpoints: posts + categories + tags)
- [x] Media library (usa /files esistenti)
- [x] Publishing workflow (publish/unpublish)
- [x] SEO metadata handling (completo)
- **Status**: ✅ COMPLETATO (21 endpoints, 2,000+ righe)
- **Commit**: fd59d9e

### 5. Frontend Pages ✅ COMPLETATO
- [x] Homepage pubblica completa (6 sections + footer)
- [x] Login page + MFA flow
- [x] Register page + email verification
- [x] Services listing + detail pages
- [x] Blog listing + post detail pages
- [x] Customer dashboard (orders, invoices, profile)
- [x] Admin dashboard (stats, quick actions, management)
- [x] Auth context/state management
- [x] Navigation component con auth status
- [x] UI components base (Button, Input, Card, Alert, Label)
- **Status**: ✅ COMPLETATO (6 pagine, 2,373 righe)
- **Commit**: d82a6d7

---

## DECISIONI DA PRENDERE

### PrioritÃ  ALTA
- [x] **Backend Framework**: FastAPI âœ… CONFERMATO
- [x] **Architettura**: Container singolo monolitico âœ… CONFERMATO
- [x] **Email Service**: Microsoft Graph API (noreply@aistrategyhub.eu) âœ… CONFERMATO
- [ ] **Rich Text Editor**: TipTap vs Lexical vs Slate
  - TipTap: Pro modular, extensible
  - Lexical: Pro Facebook-backed, moderne
  - Decisione richiesta per CMS blog editor

### PrioritÃ  MEDIA
- [ ] **Vector Database per RAG**: 
  - pgvector (PostgreSQL extension): Pro zero costi, integrated
  - Pinecone: Pro managed, scalabile
  - Raccomandazione: pgvector per iniziare
  
- [ ] **Monitoring & Error Tracking**:
  - Self-hosted: Grafana + Loki (Pro no costi, privacy)
  - SaaS: Sentry (Pro setup rapido, features avanzate)
  
- [ ] **Backup Cloud Storage**:
  - Backblaze B2: Pro costi bassi
  - AWS S3: Pro ecosystem, affidabilitÃ 
  - Google Cloud Storage: Pro pricing

---

## FASE 1: SETUP & INFRASTRUTTURA

### Setup Progetto (Settimana 1)
- [ ] Inizializza repository Git
  - [ ] .gitignore configurato (Python, Node, env, uploads)
  - [ ] README.md con istruzioni setup
  - [ ] Branch strategy (main, develop, feature/*)
  - [ ] Commit conventional commits
  
- [ ] Struttura directory progetto
  ```
  project/
  â”œâ”€â”€ frontend/              # Next.js 14
  â”œâ”€â”€ backend/               # FastAPI
  â”œâ”€â”€ nginx/                 # Config Nginx interno
  â”œâ”€â”€ scripts/               # Deploy, backup, entrypoint
  â”œâ”€â”€ docs/                  # Documentazione aggiornata
  â”œâ”€â”€ Dockerfile             # Multi-stage monolite
  â”œâ”€â”€ supervisord.conf       # Gestione processi
  â””â”€â”€ .env.example
  ```

- [ ] Docker Setup
  - [ ] Dockerfile multi-stage (frontend build + backend + postgres + redis)
  - [ ] supervisord.conf per gestione processi
  - [ ] scripts/entrypoint.sh
  - [ ] scripts/deploy.sh per produzione
  - [ ] .env.example con TUTTE le variabili richieste
  
- [ ] Database Setup
  - [ ] Schema PostgreSQL completo (45+ tabelle)
  - [ ] Alembic migrations setup
  - [ ] pgvector extension install
  - [ ] Seed data per development
  - [ ] Indici ottimizzati

- [ ] Configurazioni Esterne
  - [ ] Azure AD App Registration per MS Graph
  - [ ] Stripe account setup (test mode)
  - [ ] Claude API key (Anthropic)
  - [ ] Domain DNS configurato (aistrategyhub.eu giÃ  fatto?)

### CI/CD Pipeline
- [ ] GitHub Actions workflow
  - [ ] Linting (Black, Flake8, ESLint)
  - [ ] Type checking (mypy, TypeScript)
  - [ ] Unit tests
  - [ ] Build Docker image
  - [ ] Security scan (Trivy)
  - [ ] Deploy to Linode on main push

---

## FASE 2: BACKEND CORE

### Autenticazione & Users (Giorni 1-4)
- [ ] User model completo + user_profiles
- [ ] Password hashing (Argon2)
- [ ] Email verification con token
  - [ ] Generate token + send email MS Graph
  - [ ] Verify endpoint
  - [ ] Resend verification email
- [ ] MFA TOTP implementation
  - [ ] Generate secret + QR code
  - [ ] Verify TOTP code
  - [ ] Backup codes generation
  - [ ] MFA challenge on login
- [ ] JWT token generation/validation
  - [ ] Access token (15 min)
  - [ ] Refresh token (7 giorni, stored in Redis)
- [ ] API Endpoints autenticazione completi
- [ ] RBAC middleware implementation
- [ ] Login attempts tracking (security)
- [ ] Unit tests autenticazione

### Microsoft Graph Email Integration (Giorni 5-6)
- [ ] MS Graph OAuth client setup
- [ ] Token acquisition & refresh
- [ ] Send Mail API implementation
- [ ] Email templates (Jinja2)
  - [ ] Email verification
  - [ ] Password reset
  - [ ] Order confirmation
  - [ ] Invoice ready
  - [ ] Newsletter
  - [ ] Ticket update
- [ ] Email queue (PostgreSQL table + worker)
- [ ] Retry logic failed sends
- [ ] Error tracking & logging

### Servizi Consulenza (Giorni 7-9)
- [ ] Service model completo + service_content
- [ ] service_faqs, service_images
- [ ] API Endpoints:
  - [ ] GET /services (filtri: category, type, active)
  - [ ] GET /services/:slug
  - [ ] POST /services (admin only)
  - [ ] PATCH /services/:id (admin)
  - [ ] DELETE /services/:id (admin)
- [ ] Quote request system
  - [ ] POST /quote-requests
  - [ ] Admin review & quote generation
  - [ ] Email notification

### Ordini & Pagamenti (Giorni 10-13)
- [ ] Order model + order_items
- [ ] Cart session (Redis per guest, DB per logged)
- [ ] Order status state machine
- [ ] Stripe Integration:
  - [ ] Payment Intent creation
  - [ ] Webhooks setup (payment.succeeded, etc.)
  - [ ] 3D Secure handling
  - [ ] Subscriptions (per abbonamenti)
  - [ ] Refund processing
- [ ] API Endpoints ordini
- [ ] Email notifications (order created, paid, completed)

### Fatturazione Elettronica (Giorni 14-17)
- [ ] Invoice model + invoice_lines
- [ ] XML PA generation (formato 1.2.1)
  - [ ] Library fatturapa o custom
  - [ ] Validazione XSD
  - [ ] Dati cedente da settings
  - [ ] Dati cessionario da order
- [ ] PDF generation da XML
- [ ] PEC sending integration
  - [ ] Allegati PDF + XML
  - [ ] Delivery receipt tracking
- [ ] SDI status tracking
- [ ] Credit notes implementation
- [ ] API Endpoints:
  - [ ] GET /invoices
  - [ ] POST /invoices (manual creation)
  - [ ] GET /invoices/:id/pdf
  - [ ] GET /invoices/:id/xml
  - [ ] POST /invoices/:id/resend-pec

---

## FASE 3: CMS HEADLESS & ADMIN (Settimana 3-4)

### CMS Backend API (Giorni 1-3)
- [ ] Pages model + page_versions
- [ ] Blog model (posts, categories, tags)
- [ ] Media library model
- [ ] API Endpoints:
  - [ ] Pages: CRUD, versioning, publish
  - [ ] Blog: CRUD, schedule, SEO
  - [ ] Media: Upload, crop, organize
  - [ ] Components: Testimonials, FAQ, CTA

### Rich Text Editor Integration (Giorni 4)
- [ ] Scegli editor (TipTap raccomandato)
- [ ] Backend: Store HTML + sanitize
- [ ] Frontend admin: Editor component
- [ ] Image upload inline
- [ ] Link management

### Admin Panel - Dashboard (Giorni 5-6)
- [ ] Layout admin (sidebar, header, breadcrumbs)
- [ ] Dashboard principale:
  - [ ] Metriche accessi (chart)
  - [ ] Revenue charts
  - [ ] Iscrizioni newsletter
  - [ ] Ticket open/closed
  - [ ] System health widget
- [ ] Quick actions cards

### Admin Panel - Gestione Utenti (Giorni 7-8)
- [ ] Lista utenti (tabella con filtri)
- [ ] Dettaglio utente (edit, audit log)
- [ ] Actions: Suspend, Delete, Reset password, Disable MFA
- [ ] Impersonate user (accedi come utente)
- [ ] Bulk actions
- [ ] Export CSV

### Admin Panel - Gestione Fatture (Giorni 9-10)
- [ ] Lista fatture (filtri: status, date, cliente)
- [ ] Dettaglio fattura
- [ ] Create manual invoice
- [ ] SDI/PEC status tracking display
- [ ] Resend PEC action
- [ ] Generate credit note
- [ ] Export fatture (CSV)

### Admin Panel - Sistema Ticket (Giorni 11-12)
- [ ] Kanban board ticket (drag & drop status)
- [ ] Filtri prioritÃ , assigned, customer
- [ ] Dettaglio ticket:
  - [ ] Timeline conversazione
  - [ ] Reply form (rich text)
  - [ ] Attachments upload/download
  - [ ] Status/priority change
  - [ ] Assignment
  - [ ] Internal notes
- [ ] Auto-assignment rules (opzionale)
- [ ] SLA tracking & alerts

### Admin Panel - Log System (Giorni 13)
- [ ] Centralized log viewer
- [ ] Filtri: Level, Module, Date range, User, IP
- [ ] Full-text search logs
- [ ] Export logs (JSON, CSV)
- [ ] Log retention management

### Admin Panel - CMS Frontend Manager (Giorni 14-15)
- [ ] Homepage editor:
  - [ ] Hero section fields
  - [ ] Micro-lista "Per chi"
  - [ ] "Cosa facciamo" 3 columns
  - [ ] "Risultati" section
  - [ ] "Come lavoriamo" 3 steps
- [ ] Service page template editor
- [ ] About/Contact pages editor
- [ ] Media library UI
- [ ] Preview mode
- [ ] Publish/unpublish

### Admin Panel - Newsletter & Lead Magnet (Giorni 16)
- [ ] Subscriber list management
- [ ] Manual newsletter creation & send
- [ ] Lead magnet landing page builder
- [ ] Analytics dashboard (open rate, CTR)

---

## FASE 4: FRONTEND PUBBLICO (Settimana 4-5)

### Setup & Layout (Giorni 1-2)
- [ ] Next.js 14 project init con App Router
- [ ] TypeScript + TailwindCSS + shadcn/ui
- [ ] Layout components:
  - [ ] Header/Navigation (logo, menu CMS-driven)
  - [ ] Footer (links, social CMS-driven)
  - [ ] SEO component (meta tags)
- [ ] API client (Axios + interceptors)
- [ ] Auth context (JWT handling)

### Homepage (Giorni 3)
- [ ] Hero section (CMS-driven)
- [ ] Micro-lista "Per chi" (CMS)
- [ ] "Cosa facciamo" 3 columns (CMS)
- [ ] "Risultati" section (CMS)
- [ ] "Come lavoriamo" 3 steps (CMS)
- [ ] "Risorse recenti" (auto da blog)
- [ ] Responsive design
- [ ] Performance optimization (lazy load images)

### Pagine Servizi (Giorni 4-5)
- [ ] Template pagina servizio:
  - [ ] Hero (title, subtitle, CTA, image)
  - [ ] Per chi Ã¨ / Non Ã¨ (2 columns)
  - [ ] Il Problema (paragrafo + bullets)
  - [ ] La Soluzione (steps + timeline)
  - [ ] Cosa include (lista)
  - [ ] Pricing section (range o custom)
  - [ ] CTA + Testimonials
  - [ ] FAQ accordion
- [ ] Lista servizi page
- [ ] Filtri categoria
- [ ] Quote request form integration

### Blog (Giorni 6-7)
- [ ] Blog listing page
  - [ ] Filtri categoria/tag
  - [ ] Pagination
  - [ ] Featured posts
- [ ] Single blog post
  - [ ] Rich text rendering
  - [ ] Featured image
  - [ ] Author info
  - [ ] Related posts
  - [ ] Social share
  - [ ] Newsletter CTA
- [ ] RSS feed generation

### Area Cliente (Giorni 8-10)
- [ ] Login page (email + password + MFA)
- [ ] Register page (con email verification flow)
- [ ] Password recovery
- [ ] MFA setup page (QR code, backup codes)
- [ ] Dashboard cliente:
  - [ ] Overview servizi acquistati
  - [ ] Recent orders
  - [ ] Quick links
- [ ] My Orders page (lista + dettaglio)
- [ ] My Invoices page (download PDF/XML)
- [ ] Profile settings (edit dati, fatturazione)
- [ ] Support tickets:
  - [ ] Create ticket form
  - [ ] Ticket list
  - [ ] Ticket conversation
- [ ] Notifications center
- [ ] Delete account (GDPR)

### Checkout Flow (Giorni 11-12)
- [ ] Cart review
- [ ] Billing info form
- [ ] Stripe Elements integration (payment)
- [ ] 3D Secure handling
- [ ] Order confirmation page
- [ ] Error handling (payment failed)

### Altre Pagine (Giorni 13)
- [ ] About page (CMS-driven)
- [ ] Contact page (form + info)
- [ ] Privacy Policy (CMS + GDPR compliance)
- [ ] Cookie Policy + banner
- [ ] Terms of Service

---

## FASE 5: AI AGENT & ADVANCED FEATURES (Settimana 5-6)

### Knowledge Base Backend (Giorni 1-2)
- [ ] Document upload API
- [ ] File parsing (PDF, DOCX, TXT, MD)
  - [ ] Libraries: PyPDF2, python-docx, markdown
- [ ] Text chunking algorithm (1000-1500 tokens/chunk)
- [ ] Embedding generation (OpenAI text-embedding-3-large or local)
- [ ] pgvector storage & indexing
- [ ] Document management API (CRUD, enable/disable)

### RAG Pipeline (Giorni 3-4)
- [ ] Query processing
- [ ] Similarity search (pgvector cosine similarity)
- [ ] Context retrieval (top-k chunks)
- [ ] Prompt construction with retrieved context
- [ ] Claude API call (streaming)
- [ ] Response generation
- [ ] Citation tracking (quale chunk usato)

### Guardrail System (Giorni 5)
- [ ] Topic whitelist/blacklist enforcement
- [ ] Input content filtering
- [ ] Output validation
- [ ] Disclaimer injection
- [ ] Rate limiting per user/IP
- [ ] Escalation to ticket se fuori scope

### AI Chatbot Frontend (Giorni 6-7)
- [ ] Chat widget UI component
- [ ] Conversation state management
- [ ] Streaming response display (typing effect)
- [ ] Message history
- [ ] Feedback buttons (thumbs up/down)
- [ ] Create ticket from chat action
- [ ] Mobile responsive

### Admin AI Management (Giorni 8)
- [ ] Knowledge base upload UI
- [ ] Document list & organization
- [ ] Guardrail config UI
- [ ] System prompt editor
- [ ] Temperature/max tokens sliders
- [ ] Conversation logs viewer
- [ ] Analytics: Top queries, Feedback stats
- [ ] Test playground (simulate queries)

### Newsletter Automation (Giorni 9)
- [ ] Blog publish trigger â†’ newsletter queue
- [ ] Email generation from blog post
- [ ] Send to all active subscribers
- [ ] Unsubscribe link handling
- [ ] Open/click tracking (GDPR-compliant)
- [ ] Analytics dashboard

### Background Tasks Worker (Giorni 10)
- [ ] PostgreSQL-based task queue
- [ ] Email sending worker (MS Graph)
- [ ] Invoice generation worker
- [ ] Newsletter worker
- [ ] Backup worker (database dumps)
- [ ] Log rotation worker
- [ ] Health monitoring

---

## FASE 6: TESTING & DEPLOY (Settimana 6-7)

### Testing Backend (Giorni 1-2)
- [ ] Unit tests:
  - [ ] Auth services (login, MFA, email verification)
  - [ ] Payment processing (Stripe mocks)
  - [ ] Invoice generation (XML validation)
  - [ ] RAG pipeline (embedding, retrieval)
  - [ ] Email services (MS Graph mocks)
- [ ] Integration tests:
  - [ ] API endpoints (FastAPI TestClient)
  - [ ] Database operations
  - [ ] External API mocks
- [ ] Coverage report (target: 70%+)

### Testing Frontend (Giorni 3)
- [ ] Component tests (Vitest + Testing Library)
- [ ] E2E tests (Playwright):
  - [ ] User registration + email verification
  - [ ] Login + MFA flow
  - [ ] Service purchase + checkout + Stripe
  - [ ] Admin: Create blog post
  - [ ] Admin: Manage users
  - [ ] Chatbot conversation

### Security Audit (Giorni 4)
- [ ] OWASP ZAP automated scan
- [ ] SQL injection tests
- [ ] XSS prevention tests
- [ ] CSRF token validation
- [ ] Rate limiting verification
- [ ] Dependency vulnerability scan (pip-audit, npm audit)
- [ ] Docker image scan (Trivy)
- [ ] Secrets detection (TruffleHog)

### Performance Optimization (Giorni 5)
- [ ] Frontend:
  - [ ] Lighthouse audit (score 90+)
  - [ ] Image optimization (Next.js Image)
  - [ ] Code splitting
  - [ ] Lazy loading
- [ ] Backend:
  - [ ] Database query optimization
  - [ ] N+1 query prevention
  - [ ] Redis caching strategy
  - [ ] API response compression
- [ ] Load testing (K6):
  - [ ] 100 concurrent users
  - [ ] API response time <200ms (p95)

### Deploy Produzione Linode (Giorni 6)
- [ ] Linode VPS provisioning
- [ ] ArchLinux install & hardening
- [ ] Docker install
- [ ] Nginx setup (esterno, SSL Let's Encrypt)
- [ ] Firewall rules (ufw: 22, 80, 443 only)
- [ ] Fail2ban setup
- [ ] Build & deploy container
- [ ] Health check verification
- [ ] DNS final configuration
- [ ] SSL certificate install & auto-renewal

### Monitoring & Backup (Giorni 7)
- [ ] Uptime monitoring (UptimeRobot free tier)
- [ ] Error tracking (Sentry o self-hosted)
- [ ] Log aggregation (optional: Grafana Loki)
- [ ] Alert setup:
  - [ ] Downtime
  - [ ] Error rate spike
  - [ ] Disk space >80%
  - [ ] Database connection failures
- [ ] Backup automation:
  - [ ] Daily database dumps
  - [ ] Weekly full backup (uploads + config)
  - [ ] Remote backup (Backblaze B2)
  - [ ] Test restore procedure

### Documentazione Finale (Giorni 7)
- [ ] README.md aggiornato con:
  - [ ] Setup locale completo
  - [ ] Variabili ambiente required
  - [ ] Deploy instructions
  - [ ] Troubleshooting
- [ ] API documentation (OpenAPI/Swagger auto-gen)
- [ ] Admin user guide (screenshots workflow)
- [ ] GDPR compliance documentation
- [ ] Disaster recovery plan

---

## POST-LAUNCH

### Immediate (Settimana 1)
- [ ] Monitor error rates daily
- [ ] Monitor performance metrics
- [ ] Gather user feedback
- [ ] Quick bug fixes
- [ ] Tweak AI guardrails based on real queries

### Short-term (Mese 1)
- [ ] Analytics review (GA4 o self-hosted)
- [ ] Conversion funnel analysis
- [ ] A/B test CTA homepage
- [ ] SEO optimization (search console)
- [ ] Content marketing (primi 5 blog posts)

### Long-term (Mese 3+)
- [ ] Multi-language support (inglese)
- [ ] Advanced AI features (document upload chat)
- [ ] Webinar integration
- [ ] Partner/reseller program
- [ ] Mobile app (opzionale)
  
- [ ] Database Setup
  - [ ] Schema PostgreSQL iniziale
  - [ ] Migration tool setup (Alembic/Prisma)
  - [ ] Seed data per development
  - [ ] Database indexes ottimizzati

### CI/CD Pipeline
- [ ] GitHub Actions workflow
  - [ ] Linting (ESLint, Flake8/Black)
  - [ ] Type checking
  - [ ] Unit tests
  - [ ] Build test
  - [ ] Container build & push

---

## FASE 2: BACKEND CORE

### Autenticazione & Users (Giorni 1-3)
- [ ] User model e database schema
- [ ] Password hashing (bcrypt/Argon2)
- [ ] JWT token generation/validation
  - [ ] Access token (15 min)
  - [ ] Refresh token (7 giorni)
- [ ] Redis session storage
- [ ] API Endpoints:
  - [ ] POST /auth/register
  - [ ] POST /auth/login
  - [ ] POST /auth/refresh
  - [ ] POST /auth/logout
  - [ ] POST /auth/forgot-password
  - [ ] POST /auth/reset-password
- [ ] Email verification flow
- [ ] RBAC middleware implementation
- [ ] Unit tests autenticazione

### Products & Catalog (Giorni 4-6)
- [ ] Product model completo
- [ ] Categories & relationships
- [ ] Image handling (upload, resize, storage)
- [ ] API Endpoints:
  - [ ] GET /products (filtri, pagination)
  - [ ] GET /products/:id
  - [ ] POST /products (admin)
  - [ ] PATCH /products/:id (admin)
  - [ ] DELETE /products/:id (admin)
  - [ ] GET /categories
- [ ] Search functionality (PostgreSQL full-text)
- [ ] Product variations (se necessario)

### Cart & Orders (Giorni 7-10)
- [ ] Cart model (user + guest sessions)
- [ ] Order model e workflow
- [ ] Order status state machine
- [ ] API Endpoints:
  - [ ] GET /cart
  - [ ] POST /cart/items
  - [ ] PATCH /cart/items/:id
  - [ ] DELETE /cart/items/:id
  - [ ] POST /checkout/calculate
  - [ ] POST /checkout/create-order
  - [ ] GET /orders/:id
- [ ] Price calculation logic (tasse, sconti)
- [ ] Inventory management (se applicabile)

### Stripe Integration (Giorni 11-13)
- [ ] Stripe SDK setup
- [ ] Payment Intent creation
- [ ] Webhook endpoint configuration
  - [ ] Signature verification
  - [ ] Event handling (payment.succeeded, etc.)
- [ ] Payment error handling & retry logic
- [ ] 3D Secure support
- [ ] Test con Stripe test mode
- [ ] API Endpoint:
  - [ ] POST /checkout/payment
  - [ ] POST /webhooks/stripe

### Invoice Generation (Giorni 14-15)
- [ ] Invoice model
- [ ] PDF generation (ReportLab/wkhtmltopdf)
- [ ] Fattura elettronica XML (Italian format)
- [ ] Numero fattura sequenziale
- [ ] Storage invoices (MinIO/filesystem)
- [ ] API Endpoint:
  - [ ] GET /orders/:id/invoice

---

## FASE 3: FRONTEND

### Setup & Layout (Giorni 1-2)
- [ ] Next.js 14 project init
- [ ] TypeScript configuration
- [ ] TailwindCSS setup
- [ ] shadcn/ui components installation
- [ ] Layout structure
  - [ ] Header/Navigation
  - [ ] Footer
  - [ ] Sidebar (dashboard)
- [ ] Routing setup
- [ ] API client configuration (Axios)

### Public Pages (Giorni 3-5)
- [ ] Homepage
- [ ] Product listing page
  - [ ] Filters & search
  - [ ] Pagination
- [ ] Product detail page
- [ ] Shopping cart page
- [ ] Checkout flow
  - [ ] Step 1: Review cart
  - [ ] Step 2: Billing info
  - [ ] Step 3: Payment (Stripe Elements)
  - [ ] Step 4: Confirmation
- [ ] About/Contact pages

### Authentication UI (Giorni 6-7)
- [ ] Login page
- [ ] Register page
- [ ] Forgot password page
- [ ] Reset password page
- [ ] Email verification page
- [ ] Auth context/state management
- [ ] Protected route wrapper

### Customer Dashboard (Giorni 8-10)
- [ ] Dashboard home (overview)
- [ ] My Orders page
  - [ ] Order list with filters
  - [ ] Order detail view
- [ ] My Invoices page
- [ ] Profile settings
- [ ] Support tickets
  - [ ] Create ticket
  - [ ] Ticket list
  - [ ] Ticket detail & messages
- [ ] Notifications center

### Forms & Validation (Trasversale)
- [ ] React Hook Form setup
- [ ] Zod schemas per validazione
- [ ] Error handling UI
- [ ] Loading states
- [ ] Success notifications (toast)

---

## FASE 4: CMS & ADMIN

### Admin Layout (Giorni 1-2)
- [ ] Admin dashboard layout
- [ ] Sidebar navigation
- [ ] Top bar with user menu
- [ ] Breadcrumbs
- [ ] Access control (solo admin/editor)

### Dashboard Analytics (Giorni 3-4)
- [ ] Sales overview widget
- [ ] Recent orders widget
- [ ] Revenue charts (Chart.js/Recharts)
- [ ] Top products widget
- [ ] Customer stats widget

### Product Management (Giorni 5-7)
- [ ] Product list table
  - [ ] Search & filters
  - [ ] Bulk actions
- [ ] Create product form
  - [ ] Image upload (multiple)
  - [ ] Rich text editor
  - [ ] Category selection
  - [ ] Pricing
- [ ] Edit product
- [ ] Product variations (se necessario)

### Order Management (Giorni 8-9)
- [ ] Orders table
  - [ ] Status filters
  - [ ] Date range filters
  - [ ] Export CSV
- [ ] Order detail view
- [ ] Update order status
- [ ] Refund processing
- [ ] Print/Download invoice

### Content Management (Giorni 10-12)
- [ ] Blog post list
- [ ] Create/Edit blog post
  - [ ] WYSIWYG editor (TipTap/Slate)
  - [ ] Featured image
  - [ ] SEO metadata
  - [ ] Publish scheduling
- [ ] Pages management
- [ ] Media library
  - [ ] File upload
  - [ ] File browser
  - [ ] Image editing tools

### User Management (Giorni 13-14)
- [ ] User list table
- [ ] User detail/edit
- [ ] Role assignment
- [ ] User activity logs
- [ ] Ban/Suspend user

---

## FASE 5: INTEGRAZIONI

### n8n Workflows (Giorni 1-3)
- [ ] n8n Docker container setup
- [ ] Workflow: New Order Processing
  - [ ] Webhook trigger
  - [ ] HubSpot deal creation
  - [ ] Email confirmation (SendGrid)
  - [ ] Admin notification (Slack/Telegram)
- [ ] Workflow: Lead Nurturing
  - [ ] Form submission trigger
  - [ ] HubSpot contact creation
  - [ ] Email sequence
- [ ] Workflow: Backup Automation
  - [ ] Schedule trigger (daily)
  - [ ] Database backup
  - [ ] Upload to cloud storage

### HubSpot CRM (Giorni 4-5)
- [ ] HubSpot API credentials setup
- [ ] MCP connector configuration
- [ ] Sync users â†’ Contacts
- [ ] Sync orders â†’ Deals
- [ ] Sync products â†’ Products
- [ ] Webhook bidirectional sync
- [ ] Conflict resolution strategy

### Claude API Chatbot (Giorni 6-8)
- [ ] Claude API key setup
- [ ] Chat widget UI (frontend)
- [ ] Backend chat endpoint
  - [ ] Conversation history storage
  - [ ] Context injection (user data, FAQs)
  - [ ] Response streaming
- [ ] Intent classification
- [ ] Fallback to human support
- [ ] Chat analytics

### Email System (Giorni 9-10)
- [ ] SendGrid/SES integration
- [ ] Email templates HTML
  - [ ] Order confirmation
  - [ ] Payment receipt
  - [ ] Invoice ready
  - [ ] Password reset
  - [ ] Welcome email
- [ ] Email queue (Celery/Bull)
- [ ] Retry logic per failed sends
- [ ] Unsubscribe handling

### Notifications (Giorni 11-12)
- [ ] In-app notification system
  - [ ] Database table
  - [ ] API endpoints
  - [ ] Frontend component
- [ ] Real-time push (WebSocket/SSE)
- [ ] Email notifications (conditional)
- [ ] Notification preferences

---

## FASE 6: TESTING & QUALITY

### Backend Testing (Giorni 1-3)
- [ ] Unit tests
  - [ ] Auth services
  - [ ] Payment processing
  - [ ] Order logic
  - [ ] Email sending
- [ ] Integration tests
  - [ ] API endpoints
  - [ ] Database operations
  - [ ] External API mocks
- [ ] Coverage report (target: 70%+)

### Frontend Testing (Giorni 4-5)
- [ ] Component tests (Jest/Vitest)
- [ ] E2E tests (Playwright)
  - [ ] User registration flow
  - [ ] Login flow
  - [ ] Add to cart flow
  - [ ] Checkout flow
  - [ ] Admin product creation
- [ ] Accessibility tests (a11y)

### Security Testing (Giorni 6-7)
- [ ] OWASP ZAP scan
- [ ] SQL injection tests
- [ ] XSS prevention verification
- [ ] CSRF token validation
- [ ] Rate limiting tests
- [ ] Dependency vulnerability scan
  - [ ] npm audit
  - [ ] pip-audit / safety
- [ ] Docker image scanning (Trivy)

### Performance Testing (Giorni 8-9)
- [ ] Load testing (K6/Artillery)
  - [ ] API endpoints
  - [ ] Database queries
  - [ ] Concurrent users
- [ ] Frontend performance
  - [ ] Lighthouse scores
  - [ ] Core Web Vitals
- [ ] Optimization identificate
- [ ] Caching effectiveness

---

## FASE 7: DEPLOYMENT & GO-LIVE

### Linode VPS Setup (Giorni 1-2)
- [ ] Provision Linode VPS
- [ ] Install ArchLinux
- [ ] Hardening sistema
  - [ ] SSH key-only auth
  - [ ] Firewall rules (ufw)
  - [ ] Fail2ban
  - [ ] Automatic updates
- [ ] Install Docker & Docker Compose
- [ ] Setup user non-root per Docker

### Nginx & SSL (Giorni 3)
- [ ] Install Nginx
- [ ] Configurazione reverse proxy
- [ ] Let's Encrypt Certbot setup
- [ ] SSL certificates generati
- [ ] Auto-renewal configurato
- [ ] Security headers verificati
- [ ] Rate limiting configurato

### Database Production (Giorni 4)
- [ ] PostgreSQL production config
  - [ ] Performance tuning
  - [ ] Connection pooling
  - [ ] Logging configuration
- [ ] Redis production config
  - [ ] Persistence (RDB + AOF)
  - [ ] Memory limits
- [ ] Database migration run
- [ ] Seed production data (minimal)

### Application Deployment (Giorni 5-6)
- [ ] Transfer Docker images
- [ ] Environment variables configurate
- [ ] Secrets management (Docker secrets)
- [ ] Docker Compose up production
- [ ] Health checks verificati
- [ ] Logs aggregation verificata

### Monitoring Setup (Giorni 7)
- [ ] Uptime monitoring (UptimeRobot)
- [ ] Log aggregation (ELK/Loki opzionale)
- [ ] Error tracking (Sentry/Glitchtip)
- [ ] Alert setup
  - [ ] Downtime alerts
  - [ ] Error rate alerts
  - [ ] Disk space alerts
- [ ] Backup verification
  - [ ] Test restore procedure
  - [ ] Remote backup working

### Final Checks (Giorni 8-9)
- [ ] Security audit finale
- [ ] Performance benchmark
- [ ] Browser compatibility (Chrome, Firefox, Safari, Edge)
- [ ] Mobile responsiveness
- [ ] SSL Labs test (A+ rating)
- [ ] GDPR compliance checklist
  - [ ] Privacy policy live
  - [ ] Cookie banner
  - [ ] Data export function
  - [ ] Account deletion
- [ ] Documentation finale
  - [ ] User guide
  - [ ] Admin guide
  - [ ] API documentation

### Go-Live (Giorno 10)
- [ ] DNS configuration
- [ ] Final smoke tests
- [ ] Monitoring active
- [ ] Backup strategy active
- [ ] Support channels ready
- [ ] Announcement/Launch

---

## POST-LAUNCH

### Immediate (Settimana 1)
- [ ] Monitor error rates
- [ ] Monitor performance
- [ ] Gather user feedback
- [ ] Quick bug fixes

### Short-term (Mese 1)
- [ ] User analytics review
- [ ] Conversion funnel analysis
- [ ] Performance optimization
- [ ] Feature requests triage

### Long-term (Mese 3+)
- [ ] Horizontal scaling se necessario
- [ ] CDN implementation
- [ ] Advanced analytics
- [ ] Mobile app (opzionale)

---

## BACKLOG (FunzionalitÃ  Future)

### Alta PrioritÃ 
- [ ] Multi-language support (i18n)
- [ ] Advanced search (Elasticsearch)
- [ ] Product recommendations AI
- [ ] Subscription/recurring payments
- [ ] Discount codes & promotions

### Media PrioritÃ 
- [ ] Customer reviews & ratings
- [ ] Wishlist functionality
- [ ] Gift cards
- [ ] Referral program
- [ ] Mobile app (React Native)

### Bassa PrioritÃ 
- [ ] Social login (Google, Facebook)
- [ ] Live chat support (oltre chatbot)
- [ ] Advanced analytics dashboard
- [ ] A/B testing framework
- [ ] Multi-currency support

---

## BUG TRACKER

### Critical (Blocca funzionalitÃ )
_Nessuno al momento_

### High (Degrada esperienza)
_Nessuno al momento_

### Medium (Minor issues)
_Nessuno al momento_

### Low (Nice to have)
_Nessuno al momento_

---

## NOTES & REMINDERS

- **Code Review**: Ogni feature deve essere reviewed prima di merge
- **Documentation**: Aggiorna docs/ per ogni nuova funzionalitÃ 
- **Testing**: No merge senza tests passing
- **Changelog**: Aggiorna CHANGELOG.md per ogni release
- **Security**: Dependency updates settimanali
- **Backup**: Verifica backup restore ogni mese

---

**ULTIMO UPDATE**: 2026-01-15 (Notte - Fase 2)
**COMPLETION**: 70% (Frontend Pages Complete ✅)
**PROSSIMO MILESTONE**: Admin CRUD UIs + AI Chatbot
