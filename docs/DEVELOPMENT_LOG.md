# DEVELOPMENT LOG

**Progetto**: Sito Web Consulenza E-Commerce  
**Inizio Progetto**: 2026-01-15

---

## LOG CRONOLOGICO

### 2026-01-15 - Inizializzazione Progetto

#### Setup Iniziale
- âœ… Creato `PROJECT_REQUIREMENTS.md` con requisiti completi iniziali
- âœ… Definito stack tecnologico: Next.js 14 + FastAPI + PostgreSQL + Redis
- âœ… Pianificato deployment: Linode VPS + ArchLinux + Docker + Nginx HTTPS
- âœ… Identificate integrazioni: Stripe, MS Graph (email), Claude API

#### Decisioni Architetturali Iniziali
1. **Containerizzazione microservices**: Servizi separati in Docker Compose
2. **Database**: PostgreSQL come primary DB + Redis per caching
3. **Autenticazione**: JWT con refresh tokens, storage sessioni in Redis

---

### 2026-01-15 (Pomeriggio) - Revisione Completa Requisiti

#### Modifiche Sostanziali ai Requisiti

**1. Architettura: Da Microservices a Monolite**
- âŒ **RIMOSSO**: Docker Compose con container multipli
- âœ… **NUOVO**: Container Docker singolo monolitico
- **Rationale**: 
  - Semplificazione deployment
  - Riduzione overhead networking
  - PiÃ¹ semplice da mantenere per team piccolo
  - Supervisord gestisce processi multipli nel container

**2. Automazione: Rimosso n8n**
- âŒ **RIMOSSO**: n8n per workflow automation
- âŒ **RIMOSSO**: HubSpot CRM integration
- âœ… **NUOVO**: Background tasks worker integrato (Python)
- **Rationale**: 
  - Non serve orchestratore esterno per pochi workflow
  - Background tasks Python con PostgreSQL queue sufficiente
  - Riduce complessitÃ  stack

**3. Email: Microsoft Graph API (NO SMTP)**
- âŒ **RIMOSSO**: SendGrid / Amazon SES
- âœ… **NUOVO**: Microsoft Graph API con account noreply@aistrategyhub.eu
- **Rationale**:
  - Cliente ha giÃ  Office 365
  - Zero costi aggiuntivi
  - API piÃ¹ robusta di SMTP
  - OAuth 2.0 authentication

**4. Focus: Servizi Consulenza (NO E-commerce Prodotti)**
- âŒ **RIMOSSO**: Sistema carrello per prodotti fisici
- âŒ **RIMOSSO**: Gestione shipping
- âœ… **NUOVO**: Richieste preventivo + Quote system
- âœ… **NUOVO**: Vendita diretta pacchetti a prezzo fisso
- âœ… **NUOVO**: Abbonamenti ricorrenti (Stripe Subscriptions)
- **Rationale**: Business model basato su consulenza, non vendita prodotti

**5. CMS Headless Completo**
- âœ… **NUOVO**: CMS custom built-in per gestire:
  - Tutte le pagine frontend (hero, sezioni, testi, immagini)
  - Blog con rich text editor
  - Servizi/Prodotti
  - FAQ, Testimonials
  - Media library
- **Rationale**: Massima flessibilitÃ  vs Payload CMS o Strapi

**6. Registrazione Utenti: Email Verification + MFA**
- âœ… **NUOVO**: Link verifica email (token time-limited)
- âœ… **NUOVO**: MFA obbligatorio con TOTP (Google/Microsoft Authenticator)
- âœ… **NUOVO**: Backup codes per recovery
- **Rationale**: Security-first approach (cliente Ã¨ ISO 27001 Lead Auditor)

**7. Backend Amministrativo Completo**
- âœ… **NUOVO**: Dashboard con metriche accessi, fatturazione, iscrizioni
- âœ… **NUOVO**: Gestione utenti completa (edit, suspend, impersonate, MFA reset)
- âœ… **NUOVO**: Gestione fatture (lista, crea manuale, tracking SDI/PEC)
- âœ… **NUOVO**: Sistema ticket support (Kanban, assegnazione, SLA tracking)
- âœ… **NUOVO**: Pagina log centralizzata (application, security, business, system)
- âœ… **NUOVO**: CMS per modificare frontend da admin panel
- âœ… **NUOVO**: Gestione newsletter & lead magnet
- âœ… **NUOVO**: Gestione AI Agent knowledge base
- **Rationale**: Piattaforma self-service per gestione autonoma

**8. Blog & Newsletter Automation**
- âœ… **NUOVO**: Blog pubblico con SEO optimization
- âœ… **NUOVO**: Newsletter automatica su nuovo articolo pubblicato
- âœ… **NUOVO**: Double opt-in per iscritti
- âœ… **NUOVO**: Analytics aperture/click (GDPR-compliant)

**9. AI Agent / Chatbot**
- âœ… **NUOVO**: Knowledge base caricabile (PDF, DOCX, TXT, MD)
- âœ… **NUOVO**: RAG pipeline con PostgreSQL pgvector
- âœ… **NUOVO**: Claude API integration (Sonnet 4.5)
- âœ… **NUOVO**: Guardrail system (topic whitelist, content filtering)
- âœ… **NUOVO**: Admin panel per configurazione AI
- âœ… **NUOVO**: Conversazioni log & analytics
- **Rationale**: Fornire supporto automatico su AI, GDPR, NIS2, Cybersecurity

**10. Fatturazione Elettronica Italiana**
- âœ… **NUOVO**: Generazione XML PA (formato 1.2.1)
- âœ… **NUOVO**: Invio Sistema di Interscambio (SDI)
- âœ… **NUOVO**: Invio PEC con allegati (PDF + XML)
- âœ… **NUOVO**: Tracking status fatture (inviata, accettata, rifiutata)
- âœ… **NUOVO**: Note di credito
- âœ… **NUOVO**: Conservazione sostitutiva (10 anni)
- **Rationale**: Compliance normativa italiana obbligatoria

#### Database Schema Ridefinito

**Tabelle Principali Aggiunte/Modificate**:
- `services` + `service_content` + `service_faqs` (vs vecchio `products`)
- `quote_requests` (nuova - sistema preventivi)
- `invoices` + `invoice_lines` + `credit_notes` (vs semplice fattura)
- `pages` + `page_versions` (CMS headless)
- `blog_posts` + `blog_categories` + `blog_tags`
- `media_library` (gestione file centralizzata)
- `newsletter_subscribers` + `email_campaigns` + `email_sends`
- `knowledge_base_documents` + `knowledge_base_chunks` (RAG)
- `chat_conversations` + `chat_messages`
- `support_tickets` + `ticket_messages` + `ticket_attachments`
- `ai_guardrails_config`
- `system_logs` (separato da audit_logs)
- `site_settings` (configurazioni sistema)

**Indici & Extensions**:
- pgvector extension per similarity search (RAG)
- Indici ivfflat su embeddings
- Indici multicolonna su audit_logs e system_logs

#### Stack Tecnologico Finale Confermato

**Frontend**:
- Next.js 14 (App Router)
- TypeScript strict mode
- TailwindCSS + shadcn/ui
- TipTap o Lexical (rich text editor)
- React Hook Form + Zod

**Backend**:
- FastAPI (Python 3.11+) âœ… CONFERMATO
- SQLAlchemy 2.0 ORM
- Pydantic v2 validation
- Background tasks con PostgreSQL queue
- Supervisord process manager

**Database**:
- PostgreSQL 15+ con pgvector extension
- Redis 7+ (sessions, cache, email queue)

**Integrazioni Esterne**:
- Microsoft Graph API (email)
- Stripe (payments & subscriptions)
- Claude API Sonnet 4.5 (chatbot)
- Sistema di Interscambio SDI (fatture)

**DevOps**:
- Docker container singolo
- Nginx (esterno per SSL, interno per routing)
- Let's Encrypt SSL
- GitHub Actions CI/CD

#### Prossimi Step
- [ ] Creare struttura progetto completa
- [ ] Implementare Dockerfile multi-stage
- [ ] Setup database schema con migrations (Alembic)
- [ ] Configurare MS Graph API (Azure AD App Registration)
- [ ] Implementare autenticazione (JWT + MFA + email verification)

#### Decisioni Tecniche Pendenti
- [ ] Rich Text Editor: TipTap vs Lexical vs Slate
- [ ] Monitoring: Self-hosted Grafana vs SaaS (Sentry)
- [ ] Backup Cloud: Backblaze B2 vs AWS S3
- [ ] PostgreSQL pgvector vs Pinecone (esterno) per RAG

---

## ISSUES & RISOLUZIONI

### Issue #1: [PLACEHOLDER]
**Descrizione**: 
**Root Cause**: 
**Soluzione**: 
**Data Risoluzione**: 

---

## CODE SNIPPETS & ESEMPI

### Logging Configuration
```python
# Vedi PROJECT_REQUIREMENTS.md sezione 6.2
```

### Docker Health Check
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

---

## METRICHE & PERFORMANCE

### Baseline (Da misurare post-deploy)
- Page Load Time: TBD
- API Response Time: TBD
- Database Query Time: TBD
- Memory Usage: TBD
- CPU Usage: TBD

---

## SECURITY AUDIT LOG

### Vulnerability Scans
- [ ] OWASP ZAP scan
- [ ] Dependency audit (npm audit / pip-audit)
- [ ] Docker image scanning
- [ ] SSL/TLS configuration test

### Compliance Checks
- [ ] GDPR consent flows
- [ ] Cookie policy
- [ ] Data retention
- [ ] Encryption at rest/transit

---

## DEPLOYMENT HISTORY

### Deployment #1: [DATA]
- **Commit**: 
- **Changes**: 
- **Issues**: 
- **Rollback**: 

---

## MEETING NOTES & FEEDBACK

### Session 2026-01-15
- Cliente (Davide) richiede:
  - Tracciamento memoria persistente su .MD files
  - Codice sempre commentato in linea
  - Log dettagliati per debugging
  - Preferenza soluzioni AI-powered
  - Deployment su Linode con ArchLinux + Docker + Nginx
  
- Requisiti chiariti:
  - Sistema completo vendita consulenza
  - Backend + CMS custom
  - Gestione account clienti
  - Stripe payments
  - Email notifications
  - Integrazioni: n8n, HubSpot, Azure, MCP

---

## LESSONS LEARNED

### Best Practices Identificate
1. File .MD per memoria persistente prevengono perdita contesto
2. Logging strutturato facilita debugging production
3. Health checks Docker sono essenziali per monitoring
4. Backup automatici database sono critici

### Cose da Evitare
1. Hardcoded secrets in codice
2. Missing error handling in API endpoints
3. Non testare restore backup

---

## RISORSE & RIFERIMENTI

### Documentazione Consultata
- [Next.js Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Stripe API Docs](https://stripe.com/docs/api)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Nginx Docs](https://nginx.org/en/docs/)

### Tools Utilizzati
- VS Code + Extensions
- Docker Desktop
- Postman (API testing)
- DBeaver (database management)

---

**ULTIMO UPDATE**: 2026-01-15  
**PROSSIMO UPDATE**: Dopo decisione backend framework
