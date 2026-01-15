# REQUISITI PROGETTO - Sito Web Consulenza con E-Commerce

**Data Creazione**: 2026-01-15  
**Committente**: Davide (DPO, ISO 27001 Lead Auditor, IT Consultant)  
**Deployment Target**: Linode VPS - ArchLinux + Docker + Nginx HTTPS

---

## 1. AMBIENTE DI DEPLOYMENT

### 1.1 Infrastruttura Server
- **Provider**: Linode VPS
- **OS**: ArchLinux (ultima versione stabile)
- **Containerizzazione**: Docker (singolo container monolitico)
- **Reverse Proxy**: Nginx con configurazione HTTPS
- **Certificati SSL**: Let's Encrypt (gestione automatica rinnovo)
- **Architettura**: Monolite containerizzato (frontend + backend + db in unico container)

### 1.2 Requisiti Docker
```yaml
# Container monolitico deve avere:
- Dockerfile multi-stage ottimizzato
- PostgreSQL + Redis embedded nel container
- Supervisord per gestione processi multipli
- Health checks configurati
- Resource limits (CPU/RAM)
- Restart policy: unless-stopped
- Volume mounts per:
  - Database data
  - Upload files
  - Log files
- Secrets management (env variables)
```

### 1.3 Configurazione Nginx
```nginx
# Requisiti minimi:
- HTTPS only (redirect HTTP â†’ HTTPS)
- HTTP/2 abilitato
- SSL protocols: TLSv1.2, TLSv1.3 only
- Strong cipher suites
- HSTS headers
- Rate limiting per endpoint API
- Proxy pass a container Docker
- Gzip compression
- Static file caching
- Security headers (CSP, X-Frame-Options, etc.)
```

---

## 2. STACK TECNOLOGICO

### 2.1 Frontend
- **Framework**: Next.js 14+ (App Router)
- **Linguaggio**: TypeScript (strict mode)
- **UI Library**: React 18+
- **Styling**: TailwindCSS + shadcn/ui
- **CMS Integration**: Headless CMS per gestione contenuti
- **State Management**: React Context + Zustand
- **Forms**: React Hook Form + Zod validation
- **HTTP Client**: Axios con interceptors
- **Rich Text Editor**: TipTap o Lexical (per blog/CMS)

### 2.2 Backend
- **Framework**: FastAPI (Python 3.11+)
- **Architettura**: Monolite modulare (non microservices)
- **API Style**: RESTful
- **ORM**: SQLAlchemy 2.0
- **Task Queue**: Background tasks FastAPI + PostgreSQL queue
- **Process Manager**: Supervisord (gestione processi multipli in container)

### 2.3 Database & Cache
- **Primary DB**: PostgreSQL 15+ (embedded in container)
- **Cache Layer**: Redis 7+ (embedded in container, sessioni + cache)
- **File Storage**: Volume mount locale (uploads, documenti, immagini)
- **Search**: PostgreSQL Full-Text Search

### 2.4 CMS Headless
- **Tipo**: Custom headless CMS integrato
- **Gestione Contenuti**:
  - Pagine frontend (hero, sezioni, testi, immagini)
  - Blog posts
  - Servizi/Prodotti
  - FAQ
  - Testimonials
  - Media library
- **Editor**: WYSIWYG per contenuti rich text
- **Versioning**: Bozze e pubblicazioni
- **Multi-lingua**: Predisposto (italiano prioritario)

### 2.4 Autenticazione & Autorizzazione
- **Auth Strategy**: JWT (access + refresh tokens)
- **Password Hashing**: Argon2 (piÃ¹ sicuro di bcrypt)
- **Session Management**: Redis-backed sessions
- **Email Verification**: Link verifica con token time-limited
- **MFA (Multi-Factor Authentication)**: 
  - TOTP (Time-based One-Time Password)
  - Google Authenticator / Microsoft Authenticator compatible
  - Backup codes per recovery
- **OAuth2**: Opzionale (Google, Microsoft)
- **RBAC**: Role-Based Access Control
  - Ruoli: Super Admin, Admin, Editor, Cliente Registrato, Guest

### 2.5 Email System (Microsoft 365)
- **Provider**: Microsoft 365 (Office 365)
- **Account**: noreply@aistrategyhub.eu
- **Protocollo**: Microsoft Graph API (NO SMTP)
- **Authentication**: OAuth 2.0 client credentials flow
- **FunzionalitÃ **:
  - Email verification registrazione
  - Password reset
  - Notifiche ordini/fatture
  - Newsletter blog
  - Comunicazioni amministrative
  - Ticket support updates
- **Template Engine**: Jinja2 per email HTML responsive
- **Queue**: PostgreSQL-based email queue per retry automatico
- **Tracking**: Open tracking, click tracking (opzionale, GDPR-compliant)

---

## 3. FUNZIONALITÃ€ CORE

### 3.1 Sistema Vendita Servizi Consulenza
- **Catalogo Servizi**:
  - CRUD completo servizi consulenza
  - Tipologie: Pacchetti fissi, Custom quote, Abbonamenti
  - Categorie: AI & Compliance, Cybersecurity & NIS2, Toolkit & Formazione
  - Pricing: Range o "Quote su misura"
  - Scheduling: DisponibilitÃ  consulente (opzionale)

- **Richiesta Preventivo**:
  - Form personalizzato per servizio
  - Questionario pre-qualifica (se necessario)
  - Sistema quote: Generazione preventivo PDF
  - Invio via email automatico
  - Dashboard admin per gestione richieste

- **Acquisto Diretto** (per pacchetti a prezzo fisso):
  - Aggiungi al carrello
  - Checkout semplificato (no shipping)
  - Solo billing information
  - Calcolo automatico IVA italiana

- **Pagamenti**:
  - **Stripe Integration** (prioritaria)
    - Payment Intents API
    - Webhooks per eventi
    - 3D Secure (SCA compliance)
    - Recurring billing per abbonamenti
  - Fatturazione elettronica italiana (XML SDI)
  - Supporto PEC per invio fatture

### 3.2 CMS Headless Completo
- **Content Management**:
  - **Pagine Frontend** (modificabili da admin):
    - Homepage: Hero, Value proposition, Servizi (3 colonne), Risultati, Come lavoriamo, Risorse recenti
    - Pagine Servizi: Tutti i campi (hero, problema, soluzione, pricing, FAQ)
    - About, Contatti, Privacy Policy, Cookie Policy
  - **Blog/News**:
    - Editor rich text (WYSIWYG)
    - Featured image
    - SEO metadata (title, description, keywords)
    - Categorie e tag
    - Pubblicazione programmata
    - Bozze vs Pubblicati
  - **Servizi/Prodotti Digitali**:
    - Gestione completa da admin
    - Testi, immagini, prezzi, FAQ
  - **Media Library**:
    - Upload immagini/documenti
    - Organizzazione per folder
    - Crop/resize automatico
    - CDN-ready (future-proof)
  - **Componenti Riutilizzabili**:
    - Testimonials
    - FAQ blocks
    - Call-to-Action boxes
    - Features grids

- **Versioning & Workflow**:
  - Salva come bozza
  - Anteprima pre-pubblicazione
  - Pubblicazione immediata o programmata
  - Storico modifiche (audit trail)

### 3.3 Blog & Newsletter
- **Blog Pubblico**:
  - Lista articoli con filtri (categoria, tag, data)
  - Singolo articolo con related posts
  - Commenti disabilitati (o moderazione pesante)
  - Share social (LinkedIn, Twitter/X)
  - RSS feed

- **Newsletter Automatica**:
  - Iscrizione newsletter (form + double opt-in)
  - Invio automatico nuovi articoli blog
  - Gestione iscritti (subscribe/unsubscribe)
  - Template email personalizzabile
  - Statistiche aperture/click (GDPR-compliant)

### 3.4 AI Agent / Chatbot
- **Knowledge Base**:
  - Caricamento documenti nel backend (PDF, DOCX, TXT)
  - Gestione "knowledge base" per topic
  - Indicizzazione contenuti per RAG (Retrieval-Augmented Generation)

- **Chatbot Frontend**:
  - Widget integrato in tutte le pagine
  - Conversazione naturale
  - Context-aware (pagina corrente, storico conversazione)

- **Backend AI**:
  - **Claude API Integration** (Anthropic)
  - RAG pipeline: Query â†’ Ricerca knowledge base â†’ Generazione risposta
  - **Guardrail System**:
    - Topic whitelist (solo AI, GDPR, Cybersecurity, NIS2, consulenza)
    - Content filtering (no risposte off-topic)
    - Disclaimer automatico ("Consulta un professionista per situazioni specifiche")
    - Rate limiting per utente
  - Salvataggio conversazioni (GDPR-compliant, opt-in)
  - Handoff to human (crea ticket support se richiesto)

- **Admin Panel per AI**:
  - Upload/gestione knowledge base
  - Configurazione guardrail
  - Review conversazioni (analytics)
  - Fine-tuning prompts di sistema

### 3.5 Area Cliente (Customer Portal)
- **Registrazione & Login**:
  - Form registrazione completo
  - Email verification (link con token)
  - MFA setup (TOTP)
  - Login con email + password + codice MFA
  - Password recovery

- **Dashboard Personale**:
  - Overview servizi acquistati
  - Storico ordini con dettagli
  - Fatture scaricabili (PDF + XML)
  - Documenti condivisi (deliverable consulenza)
  - Ticket support aperti
  - Notifiche in-app

- **Gestione Profilo**:
  - Dati anagrafici
  - Dati fatturazione (Ragione sociale, P.IVA, CF, PEC, Codice SDI)
  - Preferenze email
  - Gestione MFA (enable/disable, reset)
  - Elimina account (GDPR right to erasure)

- **Support Tickets**:
  - Crea nuovo ticket
  - Lista ticket con status
  - Conversazione ticket (messaggi bidirezionali)
  - Upload allegati

### 3.6 Fatturazione Elettronica Italiana
- **Generazione Fatture**:
  - Numero progressivo automatico per anno
  - Formato XML PA (Sistema di Interscambio)
  - Dati obbligatori: Cedente, Cessionario, Dettaglio righe, IVA, Totali
  - Regime fiscale configurabile
  - Split payment se applicabile

- **Invio SDI**:
  - Firma digitale XML (se richiesto)
  - Invio a Sistema di Interscambio (SDI)
  - Tracking stato fattura (inviata, accettata, rifiutata)
  - Gestione notifiche SDI

- **Invio PEC**:
  - Copia cortesia fattura via PEC cliente
  - Allegati: PDF + XML
  - Ricevuta PEC tracking

- **Storage Fatture**:
  - Conservazione sostitutiva (10 anni)
  - PDF generato automaticamente da XML
  - Download per cliente e admin

### 3.7 Sistema di Notifiche
- **Email Notifications** (via MS Graph):
  - Email verification registrazione
  - Password reset
  - Nuovo ordine (cliente + admin)
  - Pagamento confermato
  - Fattura disponibile
  - Nuovo articolo blog (newsletter)
  - Ticket update (nuovo messaggio)
  - Reminder scadenze abbonamento

- **In-App Notifications**:
  - Real-time via WebSocket (opzionale) o polling
  - Centro notifiche in dashboard
  - Badge contatore non lette
  - Mark as read/unread

- **Admin Notifications**:
  - Nuova richiesta preventivo
  - Nuovo ordine
  - Nuovo ticket support
  - Errori sistema critici

---

## 4. INTEGRAZIONI & API ESTERNE

### 4.1 Microsoft Graph API (Office 365)
- **Email Service**:
  - Account: noreply@aistrategyhub.eu
  - Send Mail API endpoint
  - OAuth 2.0 client credentials
  - Retry logic per failed sends
  - Queue system con PostgreSQL

- **Setup Requirements**:
  - Azure AD App Registration
  - API Permissions: Mail.Send
  - Client ID e Client Secret in env variables
  - Token refresh automatico

### 4.2 Claude API (Anthropic)
- **AI Chatbot Integration**:
  - Claude Sonnet 4.5 model
  - RAG (Retrieval-Augmented Generation)
  - Streaming responses
  - Context window management
  - Token usage tracking e costi

- **Knowledge Base Management**:
  - Document parsing (PDF, DOCX, TXT, MD)
  - Text chunking per embedding
  - Vector search (PostgreSQL pgvector extension)
  - Similarity search per retrieval

- **Guardrail Implementation**:
  - System prompts con topic restrictions
  - Input filtering
  - Output validation
  - Content moderation
  - Escalation to human per richieste complesse

### 4.3 Stripe Payment Platform
- **Payment Processing**:
  - Payment Intents API
  - Customer objects
  - Payment methods storage (opzionale)
  - 3D Secure (SCA)
  - Webhooks handling

- **Subscription Management** (per abbonamenti):
  - Subscription API
  - Recurring billing
  - Proration
  - Cancellation handling
  - Failed payment retry

- **Invoicing**:
  - Stripe invoice generation
  - Automatic collection
  - Receipt emails (via MS Graph, non Stripe)

### 4.4 Sistema di Interscambio (SDI) Italia
- **Fatturazione Elettronica**:
  - Generazione XML PA formato 1.2.1
  - Validazione XSD schema
  - Firma digitale (se richiesta)
  - Invio PEC a SDI
  - Ricezione notifiche (accettazione/scarto)
  - Conservazione sostitutiva

- **Implementazione**:
  - Library: `fatturapa` (Python) o equivalente
  - PEC integration per invio
  - Storage XML firmati
  - Tracking stato fatture

---

## 5. BACKEND AMMINISTRATIVO

### 5.1 Dashboard Principale
- **Metriche Overview**:
  - **Accessi**:
    - Utenti online ora
    - Accessi ultimi 7/30 giorni (grafico)
    - Nuove registrazioni per periodo
    - Tasso conversione visitatori â†’ registrati
  
  - **Fatturazione**:
    - Revenue totale (mese corrente vs precedente)
    - Grafico revenue per mese (ultimi 12 mesi)
    - Ordini in attesa pagamento
    - Fatture emesse (mese corrente)
    - Valore medio ordine
  
  - **Iscrizioni & Engagement**:
    - Iscritti newsletter totali
    - Nuovi iscritti settimana/mese
    - Tasso apertura email (media)
    - Articoli blog pubblicati (mese)
  
  - **Support & Tickets**:
    - Ticket aperti vs chiusi
    - Tempo medio risposta
    - Ticket per prioritÃ  (high/medium/low)
  
  - **Sistema**:
    - Spazio disco utilizzato
    - Numero file in media library
    - Ultimo backup database
    - Errori critici ultimi 7 giorni

- **Widget Azioni Rapide**:
  - Ultimi 5 ordini
  - Ticket in attesa risposta
  - Bozze articoli da pubblicare
  - Richieste preventivo da processare

### 5.2 Gestione Utenti
- **Lista Utenti**:
  - Tabella con filtri:
    - Ruolo (Admin, Editor, Cliente, Guest)
    - Status (Attivo, Sospeso, Eliminato)
    - Data registrazione
    - Email verificata (SÃ¬/No)
    - MFA abilitato (SÃ¬/No)
  - Search: Nome, Email, Azienda
  - Bulk actions: Sospendi, Elimina, Esporta CSV

- **Dettaglio Utente**:
  - Dati anagrafici (edit)
  - Dati fatturazione
  - Storico ordini
  - Fatture emesse
  - Ticket aperti
  - Log attivitÃ  (login, azioni)
  - Gestione ruoli e permessi
  - Azioni admin:
    - Resetta password
    - Disabilita MFA
    - Sospendi/Riattiva account
    - Impersonate user (accesso come utente)
    - Elimina account (GDPR)

- **Audit Log Utenti**:
  - Storico login (IP, user agent, data/ora)
  - Azioni eseguite (acquisti, download, modifiche profilo)
  - Failed login attempts
  - Esportazione dati (GDPR requests)

### 5.3 Gestione Fatture
- **Lista Fatture**:
  - Filtri:
    - Status (Bozza, Emessa, Pagata, Annullata)
    - Periodo (range date)
    - Cliente
    - Importo (range)
  - Colonne:
    - Numero fattura
    - Data emissione
    - Cliente (ragione sociale)
    - Imponibile + IVA + Totale
    - Status SDI (Inviata, Accettata, Rifiutata)
    - Status PEC
  - Azioni:
    - Visualizza PDF
    - Download XML
    - Reinvia PEC
    - Annulla fattura (genera nota credito)

- **Crea Fattura Manuale**:
  - Selezione cliente
  - Aggiungi righe (descrizione, quantitÃ , prezzo unitario, IVA)
  - Calcolo automatico totali
  - Note e causale
  - Genera e invia

- **Notifiche SDI**:
  - Log ricevute SDI
  - Notifiche scarto con motivazione
  - Re-invio automatico dopo correzione

- **Note di Credito**:
  - Genera da fattura esistente
  - Invio automatico SDI e PEC

### 5.4 Sistema Ticket Support
- **Dashboard Ticket**:
  - Kanban board per status:
    - Nuovo
    - In lavorazione
    - In attesa cliente
    - Risolto
    - Chiuso
  - Filtri:
    - PrioritÃ  (Urgente, Alta, Media, Bassa)
    - Assegnato a (admin/editor)
    - Cliente
    - Tag/Categoria

- **Dettaglio Ticket**:
  - Informazioni ticket (ID, data apertura, cliente, subject)
  - Timeline conversazione (messaggi bidirezionali)
  - Reply form (rich text)
  - Allegati (upload/download)
  - Azioni:
    - Cambia status
    - Cambia prioritÃ 
    - Assegna a utente
    - Aggiungi tag
    - Chiudi ticket
  - Internal notes (non visibili al cliente)

- **Auto-Assignment Rules** (opzionale):
  - Round-robin tra admin
  - Per categoria/tag
  - Load balancing

- **SLA Tracking**:
  - Tempo prima risposta
  - Tempo risoluzione
  - Alert se SLA superato

### 5.5 Log di Sistema
- **Accesso Centralizzato ai Log**:
  - Filtri:
    - Livello (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    - Modulo (auth, payment, email, cms, api)
    - Periodo (data/ora)
    - User ID (se applicabile)
    - IP address
  - Search full-text

- **Tipologie Log Tracciati**:
  - **Application Logs**:
    - Richieste API (endpoint, metodo, status, latency)
    - Errori applicazione (stack trace)
    - Background tasks (status, durata)
  
  - **Security Logs**:
    - Login attempts (success/failed)
    - MFA verification
    - Password changes
    - Permission changes
    - Accessi admin panel
  
  - **Business Logs**:
    - Ordini creati/pagati
    - Fatture generate/inviate
    - Email inviate (tipo, destinatario, status)
    - Ticket aperti/chiusi
  
  - **System Logs**:
    - Database queries lente (>1s)
    - External API calls (MS Graph, Stripe, Claude)
    - Backup success/failure
    - Disk space warnings

- **Export & Retention**:
  - Download log (JSON, CSV)
  - Retention policy: 90 giorni default
  - Archive vecchi log (S3/MinIO)

### 5.6 CMS per Frontend
- **Gestione Pagine**:
  - Lista tutte le pagine (Home, Servizi, About, etc.)
  - Edit mode:
    - **Homepage**:
      - Hero: Headline, Sub-headline, CTA primaria/secondaria, Immagine background
      - Micro-lista "Per chi" (3 bullet)
      - Sezione "Cosa facciamo" (3 colonne: titolo, testo, link, icona)
      - Sezione "Risultati" (titolo, 4 bullet, micro-case)
      - Sezione "Come lavoriamo" (3 step: numero, titolo, descrizione)
      - Sezione "Risorse recenti" (auto-popolata da blog)
    
    - **Pagina Servizio** (template):
      - Hero: Titolo, Sottotitolo, CTA, Immagine
      - Per chi Ã¨ / Non Ã¨ (2 colonne, bullet points)
      - Il Problema (paragrafo + 3 bullet rischi)
      - La Soluzione (metodo in 3-4 step, timeline schema)
      - Cosa include (lista puntata dettagliata)
      - Pricing (range o custom, form quote)
      - CTA + Testimonials (1-2)
      - FAQ (accordion 5-7 domande)
    
    - **About, Contatti, etc.**: 
      - Rich text editor completo
      - SEO metadata

- **Visual Page Builder** (opzionale fase 2):
  - Drag & drop sections
  - Live preview
  - Componenti pre-built

- **Media Library CMS**:
  - Upload immagini (drag & drop)
  - Crop & resize
  - Alt text per accessibilitÃ 
  - Organizzazione folder
  - Search & filter
  - Bulk actions

- **Gestione Servizi/Prodotti**:
  - CRUD servizi consulenza
  - Tutti i campi modificabili da UI
  - Preview servizio prima pubblicazione

- **Gestione Blog**:
  - Lista articoli (bozze, pubblicati, programmati)
  - Editor rich text (TipTap/Lexical)
  - Featured image
  - Excerpt (sommario)
  - SEO fields (title, description, keywords)
  - Categorie e tag (gestibili)
  - Pubblicazione immediata o programmata
  - Duplicate post

- **Componenti Globali**:
  - Footer: Link, social, testo copyright
  - Header/Navigation: Logo, menu items
  - CTA Boxes riutilizzabili
  - Testimonials pool

### 5.7 Gestione Newsletter & Lead Magnet
- **Iscritti Newsletter**:
  - Lista completa (email, nome, data iscrizione, source)
  - Filtri: Attivi, Disiscritti, Bounce
  - Export CSV
  - Segmentazione (per interesse, comportamento)

- **Invio Manuale Newsletter**:
  - Editor email HTML
  - Preview
  - Test send
  - Programmazione invio
  - A/B testing subject (opzionale)

- **Lead Magnet / Opt-in Pages**:
  - Gestione landing pages per checklist/guide
  - Form builder integrato
  - Thank you page con download link
  - Tracking conversioni

- **Email Analytics**:
  - Tasso apertura
  - Click-through rate
  - Unsubscribe rate
  - Bounce rate
  - Per singola campagna e aggregato

### 5.8 Gestione AI Agent / Knowledge Base
- **Upload Documenti**:
  - Upload multipli (PDF, DOCX, TXT, MD)
  - Parsing automatico testo
  - Chunking per RAG
  - Embedding generation
  - Indicizzazione

- **Organizzazione Knowledge Base**:
  - Categorie/Topic (AI, GDPR, NIS2, Cybersecurity)
  - Tag per documento
  - Versioning documenti
  - Abilita/Disabilita documento

- **Configurazione Guardrail**:
  - Topic whitelist/blacklist
  - System prompt personalizzabile
  - Temperature setting
  - Max tokens per risposta
  - Content filters

- **Conversazioni & Analytics**:
  - Log tutte le conversazioni
  - User query analysis
  - Top domande
  - Risposte generate
  - Feedback utenti (thumbs up/down)
  - Conversazioni che hanno generato ticket

- **Test & Debug**:
  - Chat playground (test risposte)
  - Simulate user queries
  - Debug RAG retrieval

### 5.9 Settings & Configurazioni
- **Impostazioni Generali**:
  - Nome sito
  - Logo upload
  - Favicon
  - Meta tag default (SEO)
  - Google Analytics ID (opzionale)
  - Contact email

- **Impostazioni Fatturazione**:
  - Dati cedente (Ragione sociale, P.IVA, Indirizzo)
  - Regime fiscale
  - PEC aziendale
  - Codice SDI (se intermediario)
  - Numerazione fatture (prefisso, prossimo numero)

- **Impostazioni Email**:
  - Mittente default (name + email)
  - Reply-to email
  - Template personalizzazioni (logo, colori, footer)

- **Impostazioni Stripe**:
  - Publishable key
  - Secret key
  - Webhook secret
  - Test mode on/off

- **Impostazioni MS Graph**:
  - Tenant ID
  - Client ID
  - Client Secret
  - Scopes

- **Impostazioni Claude API**:
  - API Key
  - Model selection
  - Default temperature
  - Max tokens

- **GDPR & Privacy**:
  - Cookie policy text
  - Privacy policy text
  - Consensi tracking (checkboxes obbligatori)
  - Data retention policies
  - Right to erasure automation

### 5.10 User Roles & Permissions
- **Ruoli Predefiniti**:
  - **Super Admin**: Accesso totale
  - **Admin**: Tutti i moduli eccetto settings critici
  - **Editor**: Blog, CMS, view-only fatture/utenti
  - **Support**: Solo ticket e utenti (no fatture, no settings)

- **Granular Permissions**:
  - Dashboard: View
  - Utenti: View, Create, Edit, Delete
  - Fatture: View, Create, Edit, Delete, Send
  - Ticket: View, Create, Edit, Close, Assign
  - Blog: View, Create, Edit, Publish, Delete
  - CMS: View, Edit
  - Settings: View, Edit
  - Logs: View, Export

### 5.1 Security Requirements
- **Input Validation**:
  - Sanitizzazione tutti input utente
  - SQL Injection prevention (ORM parametrized queries)
  - XSS prevention (CSP headers, output encoding)
  - CSRF tokens

- **API Security**:
  - Rate limiting (Redis)
  - Request size limits
  - CORS configuration strict
  - JWT validation robusta
  - API keys per servizi esterni (encrypted in env)

- **File Upload**:
  - Whitelist estensioni permesse
  - Virus scanning (ClamAV in Docker)
  - Size limits
  - Storage isolato

- **Logging & Monitoring**:
  - Structured logging (JSON)
  - Log rotation
  - Audit trail azioni admin
  - Error tracking (Sentry O self-hosted Glitchtip)
  - Metriche performance

### 5.2 GDPR Compliance
- **Data Protection** (Davide Ã¨ DPO):
  - Privacy Policy & Cookie Policy
  - Consensi granulari
  - Right to access (export dati utente)
  - Right to erasure (cancellazione account)
  - Data minimization
  - Encryption at rest (database)
  - Encryption in transit (TLS)
  - Data retention policies
  - Breach notification system

- **Cookie Management**:
  - Cookie consent banner
  - Categorizzazione (necessari/statistici/marketing)
  - Opt-in per non essenziali

---

## 6. CODICE & DEVELOPMENT STANDARDS

### 6.1 Coding Standards
```python
# OGNI FILE CODICE DEVE AVERE:

# 1. Header con descrizione
"""
Modulo: nome_modulo.py
Descrizione: Cosa fa questo modulo
Autore: Generato da Claude per Davide
Data: YYYY-MM-DD
"""

# 2. Commenti in linea dettagliati
def process_payment(order_id: int, stripe_token: str) -> dict:
    """
    Processa pagamento via Stripe.
    
    Args:
        order_id: ID ordine database
        stripe_token: Token Stripe da frontend
        
    Returns:
        dict con status, transaction_id, errors
        
    Raises:
        StripeError: Se pagamento fallisce
    """
    # Log inizio operazione
    logger.info(f"Processing payment for order {order_id}")
    
    try:
        # Recupera ordine da database
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            logger.error(f"Order {order_id} not found")
            raise OrderNotFoundError()
            
        # Crea payment intent Stripe
        logger.debug(f"Creating Stripe payment intent for {order.total_amount}")
        intent = stripe.PaymentIntent.create(
            amount=int(order.total_amount * 100),  # Converti EUR a centesimi
            currency="eur",
            payment_method=stripe_token,
            confirm=True
        )
        
        # Log successo
        logger.info(f"Payment successful: {intent.id}")
        
        return {
            "status": "success",
            "transaction_id": intent.id,
            "amount": order.total_amount
        }
        
    except stripe.error.CardError as e:
        # Log errore carta
        logger.warning(f"Card declined for order {order_id}: {e.user_message}")
        return {
            "status": "declined",
            "error": e.user_message
        }
        
    except Exception as e:
        # Log errore generico
        logger.error(f"Payment processing failed: {str(e)}", exc_info=True)
        raise
```

### 6.2 Logging Configuration
```python
# Configurazione logging dettagliato
import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configura sistema logging con:
    - Console output (development)
    - File rotation (production)
    - JSON formatting per parsing
    """
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    console_handler.setLevel(logging.DEBUG)
    
    # File handler con rotation
    file_handler = RotatingFileHandler(
        '/var/log/app/application.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(logging.INFO)
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

### 6.3 Error Handling
```python
# Ogni operazione critica deve avere try-except con logging
# Pattern standard:

try:
    # Operazione
    logger.info("Starting operation X")
    result = perform_operation()
    logger.info(f"Operation completed: {result}")
    
except SpecificException as e:
    # Errore specifico gestito
    logger.error(f"Specific error: {str(e)}", exc_info=True)
    # Recovery action
    
except Exception as e:
    # Errore generico
    logger.critical(f"Unexpected error: {str(e)}", exc_info=True)
    # Notifica admin
    raise
    
finally:
    # Cleanup sempre eseguito
    logger.debug("Cleanup completed")
```

---

## 7. DEPLOYMENT & DEVOPS

### 7.1 Struttura Docker (Container Singolo)
```
project/
â”œâ”€â”€ Dockerfile                  # Multi-stage monolite
â”œâ”€â”€ supervisord.conf            # Gestione processi multipli
â”œâ”€â”€ .env.example                # Template variabili ambiente
â”œâ”€â”€ .dockerignore
â”œâ”€â”€ frontend/                   # Next.js app
â”‚   â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ public/
â”‚   â””â”€â”€ package.json
â”œâ”€â”€ backend/                    # FastAPI app
â”‚   â”œâ”€â”€ app/
â”‚   â”œâ”€â”€ migrations/
â”‚   â””â”€â”€ requirements.txt
â”œâ”€â”€ nginx/
â”‚   â””â”€â”€ nginx.conf              # Configurazione interna al container
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ entrypoint.sh          # Script avvio container
â”‚   â”œâ”€â”€ backup.sh              # Backup database
â”‚   â””â”€â”€ deploy.sh              # Deploy production
â””â”€â”€ docs/                       # Documentazione progetto
```

### 7.2 Dockerfile Multi-Stage
```dockerfile
# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Build Backend Dependencies
FROM python:3.11-slim AS backend-builder
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Final Container
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-15 \
    redis-server \
    nginx \
    supervisor \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy built frontend
COPY --from=frontend-builder /app/frontend/.next /app/frontend/.next
COPY --from=frontend-builder /app/frontend/public /app/frontend/public
COPY frontend/package*.json /app/frontend/

# Copy backend
COPY --from=backend-builder /app/backend /app/backend
COPY backend/ /app/backend/

# Copy configs
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Setup volumes
VOLUME ["/app/data", "/app/uploads", "/app/logs"]

# Expose ports
EXPOSE 80 443

# Entrypoint
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
```

### 7.3 Supervisord Configuration
```ini
[supervisord]
nodaemon=true
user=root

[program:postgresql]
command=/usr/lib/postgresql/15/bin/postgres -D /app/data/postgres
autostart=true
autorestart=true
stderr_logfile=/app/logs/postgresql.err.log
stdout_logfile=/app/logs/postgresql.out.log

[program:redis]
command=redis-server /etc/redis/redis.conf
autostart=true
autorestart=true
stderr_logfile=/app/logs/redis.err.log
stdout_logfile=/app/logs/redis.out.log

[program:backend]
command=uvicorn app.main:app --host 0.0.0.0 --port 8000
directory=/app/backend
autostart=true
autorestart=true
stderr_logfile=/app/logs/backend.err.log
stdout_logfile=/app/logs/backend.out.log

[program:frontend]
command=npm start
directory=/app/frontend
autostart=true
autorestart=true
environment=PORT="3000"
stderr_logfile=/app/logs/frontend.err.log
stdout_logfile=/app/logs/frontend.out.log

[program:nginx]
command=nginx -g 'daemon off;'
autostart=true
autorestart=true
stderr_logfile=/app/logs/nginx.err.log
stdout_logfile=/app/logs/nginx.out.log

[program:background_tasks]
command=python -m app.workers.task_runner
directory=/app/backend
autostart=true
autorestart=true
stderr_logfile=/app/logs/tasks.err.log
stdout_logfile=/app/logs/tasks.out.log
```

### 7.4 Deploy su Linode
```bash
# Script deploy.sh

#!/bin/bash
set -e

echo "ðŸš€ Deploying to Linode..."

# 1. Build immagine Docker
docker build -t aistrategyhub:latest .

# 2. Stop container esistente
docker stop aistrategyhub || true
docker rm aistrategyhub || true

# 3. Start nuovo container
docker run -d \
  --name aistrategyhub \
  --restart unless-stopped \
  -p 80:80 \
  -p 443:443 \
  -v aistrategyhub-data:/app/data \
  -v aistrategyhub-uploads:/app/uploads \
  -v aistrategyhub-logs:/app/logs \
  --env-file .env.production \
  aistrategyhub:latest

# 4. Health check
sleep 10
curl -f http://localhost/health || exit 1

echo "âœ… Deploy completed successfully"
```

### 7.5 Backup Strategy
```bash
# Script backup.sh (cron daily)

#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup (dentro container)
docker exec aistrategyhub pg_dump -U postgres appdb | gzip > \
    $BACKUP_DIR/db_backup_$DATE.sql.gz

# Uploads backup
docker cp aistrategyhub:/app/uploads $BACKUP_DIR/uploads_$DATE

# Retention: 7 giorni local, poi remote
find $BACKUP_DIR -type f -mtime +7 -delete

# Upload to cloud (Backblaze/S3)
# rclone copy $BACKUP_DIR remote:backups/

logger "Backup completed: $DATE"
```

### 7.6 Monitoring & Health Checks
```python
# Health endpoint backend
@app.get("/health")
async def health_check():
    checks = {
        "database": check_postgres(),
        "redis": check_redis(),
        "disk_space": check_disk_space(),
        "ms_graph": check_ms_graph_token(),
    }
    
    status = "healthy" if all(checks.values()) else "degraded"
    
    return {
        "status": status,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }
```

### 7.7 CI/CD Pipeline (GitHub Actions)
```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker Image
        run: docker build -t aistrategyhub:${{ github.sha }} .
      
      - name: Run Tests
        run: docker run aistrategyhub:${{ github.sha }} pytest
      
      - name: Deploy to Linode
        run: |
          ssh user@linode-ip './deploy.sh'
```

### 7.3 Backup Strategy
- **Database**: 
  - Backup giornaliero automatico (cron job)
  - Retention: 7 giorni locali + S3/Backblaze remote
  - Script restore testato

- **File Storage**:
  - Sync incrementale upload folder
  - Versioning abilitato

- **Configurazioni**:
  - Git repository privato per config
  - Secrets in encrypted format

### 7.4 Monitoring & Alerts
- **Health Checks**:
  - Endpoint `/health` per ogni servizio
  - Docker healthcheck configurato
  - Uptime monitoring (UptimeRobot o self-hosted)

- **Logs**:
  - Aggregazione logs Docker (docker logs)
  - Opzionale: ELK stack o Grafana Loki

- **Metriche**:
  - Prometheus + Grafana (opzionale)
  - Metriche applicazione custom

---

## 8. TESTING & QUALITY

### 8.1 Testing Requirements
- **Unit Tests**: Coverage minimo 70%
- **Integration Tests**: API endpoints principali
- **E2E Tests**: Flussi critici (checkout, login, etc.)
- **Security Tests**: OWASP Top 10 checks

### 8.2 CI/CD Pipeline
```yaml
# GitHub Actions workflow (esempio)
on: [push, pull_request]

jobs:
  test:
    - Linting (ESLint, Flake8)
    - Type checking (TypeScript, mypy)
    - Unit tests
    - Build test
    
  build:
    - Build immagini Docker
    - Push su registry (GitHub Container Registry)
    - Tag versioning semantico
    
  deploy:
    - Deploy su Linode (SSH)
    - Pull immagini
    - Docker compose up
    - Health check post-deploy
```

---

## 9. PERFORMANCE REQUIREMENTS

### 9.1 Metriche Target
- **Page Load**: < 3 secondi (LCP)
- **API Response**: < 200ms (95th percentile)
- **Database Queries**: < 100ms (media)
- **Concurrent Users**: 100+ simultanei

### 9.2 Ottimizzazioni
- **Frontend**:
  - Code splitting
  - Image optimization (Next.js Image)
  - Static generation dove possibile
  - CDN per assets statici

- **Backend**:
  - Query optimization (indexes)
  - Caching strategico (Redis)
  - Connection pooling database
  - Async operations per I/O

- **Database**:
  - Indexes su colonne ricerca frequente
  - Partitioning per tabelle grandi
  - VACUUM regolare

---

## 10. DOCUMENTAZIONE

### 10.1 Documentazione Richiesta
- **README.md**: Setup locale, deployment, troubleshooting
- **API_DOCS.md**: OpenAPI/Swagger specification
- **DEPLOYMENT.md**: Istruzioni step-by-step deploy Linode
- **ARCHITECTURE.md**: Diagrammi architettura, decisioni design
- **CHANGELOG.md**: Versioning e modifiche

### 10.2 Commenti Codice
- **Ogni funzione**: Docstring con Args, Returns, Raises
- **Logica complessa**: Commenti inline spiegazione
- **TODOs**: Tag `# TODO:` con descrizione e prioritÃ 
- **FIXME**: Tag `# FIXME:` per bug noti

---

## 11. MILESTONE & DELIVERABLES

### Fase 1: Setup & Infrastruttura (Settimana 1)
- [ ] Struttura progetto completa
- [ ] Dockerfile monolitico funzionante locale
- [ ] Database schema iniziale + migrations
- [ ] MS Graph API setup e test
- [ ] Claude API setup e test

### Fase 2: Backend Core (Settimana 2-3)
- [ ] API autenticazione (JWT + MFA + email verification)
- [ ] CRUD servizi consulenza
- [ ] Integrazione Stripe
- [ ] Sistema email (MS Graph)
- [ ] Fatturazione elettronica (XML SDI + PEC)

### Fase 3: CMS Headless & Admin (Settimana 3-4)
- [ ] CMS backend API
- [ ] Admin panel layout
- [ ] Gestione pagine frontend
- [ ] Gestione blog
- [ ] Media library
- [ ] Dashboard analytics

### Fase 4: Frontend Pubblico (Settimana 4-5)
- [ ] Layout e navigazione
- [ ] Homepage (struttura da documento)
- [ ] Pagine servizi (template)
- [ ] Blog listing e singolo articolo
- [ ] Area cliente con dashboard
- [ ] Checkout flow

### Fase 5: AI Agent & Advanced Features (Settimana 5-6)
- [ ] RAG pipeline (upload docs, embedding, retrieval)
- [ ] Claude API chatbot frontend
- [ ] Guardrail system
- [ ] Newsletter automation
- [ ] Sistema ticket support
- [ ] Gestione log centralizzata

### Fase 6: Testing & Deploy (Settimana 6-7)
- [ ] Test completi (unit, integration, E2E)
- [ ] Security audit
- [ ] Performance optimization
- [ ] Documentazione finale
- [ ] Deploy production Linode
- [ ] Monitoring setup
- [ ] Backup automation

---

## 12. NOTE AGGIUNTIVE

### 12.1 Preferenze Davide
- **Fonti**: Sempre citate, niente invenzioni
- **Codice**: Commenti inline obbligatori
- **Logging**: Dettagliato per debugging
- **AI Solutions**: Prioritarie dove possibile
- **Tools**: Zapier, n8n, MCP connectors, Azure
- **Relazioni**: Precise e discorsive

### 12.2 Decisioni da Finalizzare
- [ ] Backend: FastAPI vs Node.js/Express
- [ ] CMS: Custom vs Payload CMS
- [ ] Email Provider: SendGrid vs Amazon SES
- [ ] Monitoring: Self-hosted vs SaaS
- [ ] Analytics: Custom vs Google Analytics

---

**ULTIMO AGGIORNAMENTO**: 2026-01-15
**PROSSIMA REVISIONE**: In base a progressi sviluppo
