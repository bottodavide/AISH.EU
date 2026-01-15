# ðŸš€ Sito Web Consulenza E-Commerce

**Progetto**: Piattaforma completa vendita servizi consulenza  
**Cliente**: Davide (DPO, ISO 27001 Lead Auditor)  
**Deployment**: Linode VPS + ArchLinux + Docker + Nginx HTTPS  
**Inizio Progetto**: 2026-01-15

---

## ðŸ“‹ DOCUMENTAZIONE PROGETTO

Questo progetto utilizza un **sistema di memoria persistente** basato su file Markdown per mantenere continuitÃ  durante lo sviluppo con Claude.

### File Core (âš ï¸ LEGGERE QUESTI PRIMA)

1. **[GUIDA_MEMORIA_PERSISTENTE.md](./GUIDA_MEMORIA_PERSISTENTE.md)** ðŸ“–
   - â­ **INIZIA DA QUI** - Spiega come usare la documentazione
   - Come mantenere Claude informato tra sessioni
   - Workflow consigliato
   - Best practices

2. **[PROJECT_REQUIREMENTS.md](./PROJECT_REQUIREMENTS.md)** ðŸ“
   - **Single source of truth** per requisiti
   - Stack tecnologico completo
   - FunzionalitÃ  richieste
   - Security & compliance (GDPR)
   - Coding standards
   - Deployment specs

3. **[ARCHITECTURE.md](./ARCHITECTURE.md)** ðŸ—ï¸
   - Architettura sistema completo
   - Database schema
   - API design
   - Integration patterns
   - Security architecture
   - Deployment architecture

4. **[DEVELOPMENT_LOG.md](./DEVELOPMENT_LOG.md)** ðŸ“…
   - Diario di bordo sviluppo
   - Log cronologico progressi
   - Decisioni tecniche e rationale
   - Issues & risoluzioni
   - Meeting notes

5. **[TODO.md](./TODO.md)** âœ…
   - Task tracking completo
   - Organizzato per fasi sviluppo
   - PrioritÃ  e dipendenze
   - Bug tracker
   - Backlog funzionalitÃ 

---

## ðŸŽ¯ OVERVIEW PROGETTO

### Obiettivo
Creare **AI Strategy Hub** (aistrategyhub.eu) - piattaforma completa per vendita servizi di consulenza su AI, GDPR e Cybersecurity con:
- âœ… Vendita servizi consulenza (pacchetti, custom quote, abbonamenti)
- âœ… Backend amministrativo completo
- âœ… CMS headless per gestione tutti i contenuti frontend
- âœ… Blog con newsletter automatica
- âœ… Area cliente con dashboard
- âœ… AI Chatbot con knowledge base (RAG + Claude API)
- âœ… Fatturazione elettronica italiana (XML SDI + PEC)
- âœ… Integrazioni: Stripe, Microsoft Graph API, Claude API
- âœ… Deployment production-ready (container singolo Docker)

### Stack Tecnologico

**Frontend**:
- Next.js 14 (App Router) âœ…
- TypeScript (strict mode) âœ…
- TailwindCSS + shadcn/ui âœ…
- React Hook Form + Zod âœ…
- TipTap o Lexical (rich text editor)

**Backend**:
- FastAPI (Python 3.11+) âœ… **CONFERMATO**
- PostgreSQL 15+ (con pgvector per RAG) âœ…
- Redis 7+ (sessions, cache, queue) âœ…
- SQLAlchemy 2.0 ORM âœ…
- Pydantic v2 validation âœ…

**DevOps**:
- Docker container singolo monolitico âœ…
- Supervisord (gestione processi) âœ…
- Nginx reverse proxy (SSL) âœ…
- Let's Encrypt SSL âœ…
- GitHub Actions CI/CD

**Integrazioni**:
- **Microsoft Graph API** (email - noreply@aistrategyhub.eu) âœ…
- **Stripe** (pagamenti + abbonamenti) âœ…
- **Claude API Sonnet 4.5** (chatbot RAG) âœ…
- **Sistema di Interscambio** SDI (fatture elettroniche) âœ…

---

## ðŸš¦ STATO ATTUALE

**Fase**: Setup & Pianificazione Completa  
**Completion**: 10% (Documentazione completa)  
**Ultimo Update**: 2026-01-15

### âœ… Completato
- Documentazione completa progetto (aggiornata)
- Requisiti finali definiti
- Architettura progettata (container singolo)
- Database schema completo (45+ tabelle)
- TODO strutturato per 7 settimane
- Stack tecnologico confermato

### ðŸ”„ In Progress
- Nessun task in corso

### â­ï¸ Next Steps
1. Creare struttura progetto (frontend + backend)
2. Dockerfile multi-stage
3. Database setup con Alembic migrations
4. Configurare MS Graph API (Azure AD)
5. Implementare autenticazione (JWT + MFA + email verification)

---

## ðŸƒ QUICK START

### Per Claude (riprendere progetto)
```
"Carica PROJECT_REQUIREMENTS.md e DEVELOPMENT_LOG.md 
 per riprendere il contesto del progetto sito e-commerce"
```

### Per Sviluppatore
1. Leggi `GUIDA_MEMORIA_PERSISTENTE.md`
2. Review `PROJECT_REQUIREMENTS.md`
3. Check `TODO.md` per prossimi task
4. Consulta `ARCHITECTURE.md` per design decisions

---

## ðŸ“ STRUTTURA PROGETTO (Futura)

```
project/
â”œâ”€â”€ docs/                           # â† Siamo qui
â”‚   â”œâ”€â”€ README.md                   # Questo file
â”‚   â”œâ”€â”€ GUIDA_MEMORIA_PERSISTENTE.md
â”‚   â”œâ”€â”€ PROJECT_REQUIREMENTS.md
â”‚   â”œâ”€â”€ ARCHITECTURE.md
â”‚   â”œâ”€â”€ DEVELOPMENT_LOG.md
â”‚   â””â”€â”€ TODO.md
â”‚
â”œâ”€â”€ frontend/                       # Next.js app
â”‚   â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ public/
â”‚   â”œâ”€â”€ Dockerfile
â”‚   â””â”€â”€ package.json
â”‚
â”œâ”€â”€ backend/                        # FastAPI/Node app
â”‚   â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ migrations/
â”‚   â”œâ”€â”€ Dockerfile
â”‚   â””â”€â”€ requirements.txt
â”‚
â”œâ”€â”€ nginx/                          # Reverse proxy config
â”‚   â”œâ”€â”€ nginx.conf
â”‚   â””â”€â”€ conf.d/
â”‚
â”œâ”€â”€ scripts/                        # Utility scripts
â”‚   â”œâ”€â”€ backup.sh
â”‚   â””â”€â”€ deploy.sh
â”‚
â”œâ”€â”€ docker-compose.yml              # Dev environment
â”œâ”€â”€ docker-compose.prod.yml         # Production
â””â”€â”€ .env.example                    # Template variabili ambiente
```

---

## ðŸ” SECURITY & COMPLIANCE

Questo progetto implementa:

- âœ… **GDPR Compliance** (Davide Ã¨ DPO)
  - Privacy by design
  - Data minimization
  - Right to erasure
  - Audit logging

- âœ… **Security Best Practices**
  - HTTPS only
  - JWT authentication
  - Input validation
  - SQL injection prevention
  - XSS protection
  - CSRF tokens
  - Rate limiting

- âœ… **ISO 27001 Aligned** (Davide Ã¨ Lead Auditor)
  - Access control (RBAC)
  - Encryption at rest/transit
  - Backup strategy
  - Incident response

---

## ðŸ¤ WORKFLOW SVILUPPO

### Convenzioni
- **Git**: Feature branch workflow
- **Commits**: Conventional Commits
- **Code Review**: Required prima di merge
- **Testing**: Unit tests obbligatori
- **Documentation**: Aggiorna docs/ per ogni feature

### Codice
```python
# Tutti i file devono avere:

# 1. Header descrittivo
"""
Modulo: nome_modulo.py
Descrizione: Cosa fa
Autore: Generato da Claude per Davide
Data: YYYY-MM-DD
"""

# 2. Commenti inline dettagliati
# 3. Logging esteso per debugging
# 4. Error handling robusto
# 5. Type hints (Python) / Types (TypeScript)
```

Vedi `PROJECT_REQUIREMENTS.md` sezione 6 per standard completi.

---

## ðŸ“ž CONTACTS & SUPPORT

**Cliente**: Davide  
**Specializzazioni**: DPO, ISO 27001, Cybersecurity, GDPR  
**Tools preferiti**: n8n, Zapier, Azure, MCP connectors

**Preferenze Claude**:
- Fonti sempre citate
- Niente invenzioni
- Codice con commenti inline
- Log dettagliati
- Soluzioni AI-powered quando possibile

---

## ðŸ“š RISORSE

### Documentazione Tecnica
- [Next.js Docs](https://nextjs.org/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Stripe API](https://stripe.com/docs/api)
- [n8n Docs](https://docs.n8n.io/)
- [Docker Docs](https://docs.docker.com/)

### Best Practices
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [12 Factor App](https://12factor.net/)
- [API Design Guidelines](https://github.com/microsoft/api-guidelines)

---

## ðŸ“Š MILESTONES

| Fase | Descrizione | Timeline | Status |
|------|-------------|----------|--------|
| 1 | Setup & Infrastruttura | Settimana 1 | ðŸ“‹ Planned |
| 2 | Backend Core | Settimana 2-3 | ðŸ“‹ Planned |
| 3 | Frontend | Settimana 3-4 | ðŸ“‹ Planned |
| 4 | CMS & Admin | Settimana 4-5 | ðŸ“‹ Planned |
| 5 | Integrazioni | Settimana 5-6 | ðŸ“‹ Planned |
| 6 | Testing & Deploy | Settimana 6-7 | ðŸ“‹ Planned |

Dettagli completi in `TODO.md`

---

## âš ï¸ IMPORTANTE

Questa documentazione Ã¨ il **sistema nervoso centrale** del progetto.

**Mantenila aggiornata**:
- âœ… Ogni sessione di sviluppo
- âœ… Ogni decisione tecnica
- âœ… Ogni feature completata
- âœ… Ogni issue risolto

**PerchÃ©**:
- Claude non ha memoria persistente
- Previene perdita contesto
- Accelera onboarding
- Documenta decisioni

Vedi `GUIDA_MEMORIA_PERSISTENTE.md` per workflow completo.

---

## ðŸ“ CHANGELOG

### 2026-01-15 - Inizializzazione
- Creata documentazione completa progetto
- Definiti requisiti e architettura
- Setup sistema memoria persistente
- Strutturato TODO per tutte le fasi

---

## ðŸ“„ LICENSE

[Da definire]

---

**Versione**: 0.1.0  
**Status**: Planning  
**Next Review**: Post-Fase 1 completion

---

ðŸ”— **Link Rapidi**:
- [ðŸ“– Guida Memoria](./GUIDA_MEMORIA_PERSISTENTE.md)
- [ðŸ“ Requisiti](./PROJECT_REQUIREMENTS.md)
- [ðŸ—ï¸ Architettura](./ARCHITECTURE.md)
- [ðŸ“… Dev Log](./DEVELOPMENT_LOG.md)
- [âœ… TODO](./TODO.md)
