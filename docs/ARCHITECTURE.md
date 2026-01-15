# ARCHITETTURA SISTEMA

**Progetto**: Sito Web Consulenza E-Commerce  
**Data**: 2026-01-15  
**Versione**: 1.0

---

## 1. PANORAMICA ARCHITETTURA

### 1.1 Architecture Pattern
**Architettura**: Monolite modulare containerizzato

```
Internet
    ↓
[Linode VPS - ArchLinux]
    ↓
[Nginx Reverse Proxy] ← Let's Encrypt SSL
    ↓
[Single Docker Container - aistrategyhub]
    ↓
┌─────────────────────────────────────────────────────┐
│  Supervisord (Process Manager)                      │
├─────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Nginx      │  │   Frontend   │  │  Backend  │ │
│  │  (Internal)  │  │   Next.js    │  │  FastAPI  │ │
│  │    :80       │  │    :3000     │  │   :8000   │ │
│  └──────┬───────┘  └──────────────┘  └─────┬─────┘ │
│         │                                   │        │
│  ┌──────┴───────────────────────────────────┴────┐  │
│  │         PostgreSQL 15                         │  │
│  │         :5432 (interno)                       │  │
│  │  - Tables: users, services, orders, invoices │  │
│  │  - Extensions: pgvector (per RAG)            │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │         Redis 7                                │  │
│  │         :6379 (interno)                        │  │
│  │  - Sessions, Cache, Email queue               │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │    Background Tasks Worker                     │  │
│  │  - Email sending (MS Graph)                    │  │
│  │  - Invoice generation (XML SDI)                │  │
│  │  - Newsletter automation                       │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
    ↓
[External Services]
┌──────────┬────────────┬──────────┬──────────┐
│  Stripe  │ MS Graph   │  Claude  │   SDI    │
│    API   │  (Email)   │   API    │  (PEC)   │
└──────────┴────────────┴──────────┴──────────┘
```

### 1.2 Componenti Principali

#### Nginx (Interno Container)
- **Port**: 80 (bind interno)
- **Responsabilità**:
  - Reverse proxy frontend (:3000) e backend (:8000)
  - Serve static files (uploads, media)
  - Gzip compression
  - Request routing interno

#### Frontend (Next.js 14)
- **Port**: 3000 (interno container)
- **Responsabilità**:
  - UI/UX interfaccia pubblica e area cliente
  - SSR/SSG per SEO
  - CMS frontend consumption
  - Blog rendering
  - AI Chatbot widget
- **Comunicazione**: HTTP con backend API (:8000)

#### Backend (FastAPI)
- **Port**: 8000 (interno container)
- **Responsabilità**:
  - Business logic servizi consulenza
  - API RESTful
  - Autenticazione (JWT + MFA)
  - Admin panel backend
  - CMS headless API
  - RAG pipeline per AI Agent
  - Stripe webhook handler
  - Fatturazione elettronica (XML SDI)
  - MS Graph email sender
- **Comunicazione**: 
  - DB via SQLAlchemy ORM
  - Cache via Redis
  - External APIs (Stripe, MS Graph, Claude, SDI)

#### Database (PostgreSQL 15)
- **Port**: 5432 (interno container, non esposto)
- **Responsabilità**:
  - Persistenza dati strutturati
  - Transazioni ACID
  - Full-Text Search
  - Vector storage (pgvector per RAG)
- **Extensions**:
  - pgvector: Vector similarity search
  - pg_trgm: Fuzzy text search
- **Backup**: Volume mount + automated dumps

#### Cache (Redis 7)
- **Port**: 6379 (interno container, non esposto)
- **Responsabilità**:
  - Session storage (JWT refresh tokens)
  - API response caching
  - Rate limiting counters
  - Email queue (pending send)
  - Task queue (background jobs)
- **Persistenza**: RDB + AOF su volume mount

#### Background Tasks Worker
- **Processo**: Python script in loop
- **Gestione**: Supervisord
- **Responsabilità**:
  - Email sending via MS Graph (con retry)
  - Invoice generation (PDF + XML)
  - Newsletter automation
  - Backup scheduling
  - Log rotation

#### Nginx Reverse Proxy (Esterno)
- **Ports**: 80 (redirect), 443 (HTTPS)
- **Responsabilità**:
  - SSL/TLS termination (Let's Encrypt)
  - Request routing al container
  - Rate limiting
  - Security headers
  - DDoS protection (basic)

---

## 2. DATA MODEL

### 2.1 Entities Principali

```sql
-- Schema completo database (PostgreSQL 15+)

-- ============================================
-- UTENTI E AUTENTICAZIONE
-- ============================================

Table: users
- id (UUID, PK)
- email (VARCHAR(255), UNIQUE, NOT NULL)
- password_hash (VARCHAR(255), NOT NULL)
- role (ENUM: super_admin, admin, editor, support, customer, guest)
- is_active (BOOLEAN, DEFAULT true)
- email_verified (BOOLEAN, DEFAULT false)
- email_verification_token (VARCHAR(255), NULLABLE)
- email_verification_expires (TIMESTAMP, NULLABLE)
- mfa_enabled (BOOLEAN, DEFAULT false)
- mfa_secret (VARCHAR(255), NULLABLE) -- TOTP secret
- backup_codes (TEXT[], NULLABLE) -- Array di codici backup
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())
- last_login (TIMESTAMP, NULLABLE)
- last_login_ip (INET, NULLABLE)

Table: user_profiles
- id (UUID, PK)
- user_id (UUID, FK → users, UNIQUE)
- first_name (VARCHAR(100))
- last_name (VARCHAR(100))
- phone (VARCHAR(20))
- company_name (VARCHAR(255), NULLABLE)
- vat_number (VARCHAR(20), NULLABLE) -- Partita IVA
- fiscal_code (VARCHAR(16), NULLABLE) -- Codice Fiscale
- pec_email (VARCHAR(255), NULLABLE) -- Email PEC
- sdi_code (VARCHAR(7), NULLABLE) -- Codice SDI destinatario
- billing_address (JSONB) -- {street, city, zip, province, country}
- language (VARCHAR(5), DEFAULT 'it_IT')
- timezone (VARCHAR(50), DEFAULT 'Europe/Rome')

Table: sessions
- id (UUID, PK)
- user_id (UUID, FK → users)
- access_token (VARCHAR(500), UNIQUE)
- refresh_token (VARCHAR(500), UNIQUE)
- expires_at (TIMESTAMP)
- refresh_expires_at (TIMESTAMP)
- ip_address (INET)
- user_agent (TEXT)
- created_at (TIMESTAMP, DEFAULT NOW())

Table: login_attempts
- id (UUID, PK)
- email (VARCHAR(255))
- ip_address (INET)
- success (BOOLEAN)
- failure_reason (VARCHAR(100), NULLABLE)
- attempted_at (TIMESTAMP, DEFAULT NOW())

-- ============================================
-- SERVIZI CONSULENZA (NO PRODOTTI FISICI)
-- ============================================

Table: services
- id (UUID, PK)
- slug (VARCHAR(255), UNIQUE, NOT NULL)
- name (VARCHAR(255), NOT NULL)
- category (ENUM: ai_compliance, cybersecurity_nis2, toolkit_formazione)
- type (ENUM: pacchetto_fisso, custom_quote, abbonamento)
- short_description (TEXT)
- long_description (TEXT) -- Rich text HTML
- pricing_type (ENUM: fixed, range, custom)
- price_min (DECIMAL(10,2), NULLABLE)
- price_max (DECIMAL(10,2), NULLABLE)
- currency (VARCHAR(3), DEFAULT 'EUR')
- is_active (BOOLEAN, DEFAULT true)
- is_featured (BOOLEAN, DEFAULT false)
- sort_order (INTEGER, DEFAULT 0)
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())
- published_at (TIMESTAMP, NULLABLE)

Table: service_content
-- CMS content per pagina servizio
- id (UUID, PK)
- service_id (UUID, FK → services, UNIQUE)
- hero_title (VARCHAR(255))
- hero_subtitle (TEXT)
- hero_image_url (VARCHAR(500))
- hero_cta_text (VARCHAR(100))
- hero_cta_url (VARCHAR(500))
- problem_section (TEXT) -- HTML rich text
- solution_section (TEXT) -- HTML rich text
- what_includes (TEXT) -- Bullet list HTML
- for_who_section (TEXT) -- HTML
- not_for_who_section (TEXT) -- HTML
- process_steps (JSONB) -- Array: [{number, title, description}]
- testimonials (JSONB) -- Array: [{text, author, company}]

Table: service_faqs
- id (UUID, PK)
- service_id (UUID, FK → services)
- question (VARCHAR(500))
- answer (TEXT)
- sort_order (INTEGER, DEFAULT 0)

Table: service_images
- id (UUID, PK)
- service_id (UUID, FK → services)
- image_url (VARCHAR(500))
- alt_text (VARCHAR(255))
- is_primary (BOOLEAN, DEFAULT false)
- sort_order (INTEGER)

-- ============================================
-- RICHIESTE PREVENTIVO & ORDINI
-- ============================================

Table: quote_requests
- id (UUID, PK)
- request_number (VARCHAR(50), UNIQUE) -- QR-2026-00001
- user_id (UUID, FK → users, NULLABLE)
- service_id (UUID, FK → services)
- contact_name (VARCHAR(255))
- contact_email (VARCHAR(255))
- contact_phone (VARCHAR(20))
- company_name (VARCHAR(255), NULLABLE)
- message (TEXT)
- custom_fields (JSONB) -- Risposte questionario
- status (ENUM: new, in_review, quoted, accepted, rejected)
- quoted_amount (DECIMAL(10,2), NULLABLE)
- quoted_at (TIMESTAMP, NULLABLE)
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())

Table: orders
- id (UUID, PK)
- order_number (VARCHAR(50), UNIQUE) -- ORD-2026-00001
- user_id (UUID, FK → users)
- quote_request_id (UUID, FK → quote_requests, NULLABLE)
- status (ENUM: pending, awaiting_payment, paid, processing, completed, cancelled, refunded)
- subtotal (DECIMAL(10,2))
- tax_rate (DECIMAL(5,2)) -- Es: 22.00 per IVA 22%
- tax_amount (DECIMAL(10,2))
- total (DECIMAL(10,2))
- currency (VARCHAR(3), DEFAULT 'EUR')
- billing_data (JSONB) -- Snapshot dati fatturazione
- notes (TEXT, NULLABLE)
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())
- paid_at (TIMESTAMP, NULLABLE)
- completed_at (TIMESTAMP, NULLABLE)

Table: order_items
- id (UUID, PK)
- order_id (UUID, FK → orders)
- service_id (UUID, FK → services)
- service_name (VARCHAR(255)) -- Snapshot
- description (TEXT)
- quantity (INTEGER, DEFAULT 1)
- unit_price (DECIMAL(10,2))
- tax_rate (DECIMAL(5,2))
- total_price (DECIMAL(10,2))

Table: payments
- id (UUID, PK)
- order_id (UUID, FK → orders)
- stripe_payment_intent_id (VARCHAR(255), UNIQUE)
- amount (DECIMAL(10,2))
- currency (VARCHAR(3))
- status (ENUM: pending, succeeded, failed, refunded, cancelled)
- payment_method_type (VARCHAR(50)) -- card, sepa_debit, etc.
- failure_reason (TEXT, NULLABLE)
- metadata (JSONB)
- created_at (TIMESTAMP, DEFAULT NOW())
- processed_at (TIMESTAMP, NULLABLE)

-- ============================================
-- FATTURAZIONE ELETTRONICA ITALIANA
-- ============================================

Table: invoices
- id (UUID, PK)
- invoice_number (VARCHAR(50), UNIQUE) -- 2026/00001
- invoice_year (INTEGER)
- invoice_progressive (INTEGER)
- order_id (UUID, FK → orders, UNIQUE)
- user_id (UUID, FK → users)
- issue_date (DATE, NOT NULL)
- due_date (DATE, NULLABLE)
-
-- Dati Cedente (configurati in settings)
- seller_name (VARCHAR(255))
- seller_vat (VARCHAR(20))
- seller_fiscal_code (VARCHAR(16))
- seller_address (JSONB)
- seller_regime_fiscale (VARCHAR(10)) -- RF01, RF02, etc.

-- Dati Cessionario
- buyer_name (VARCHAR(255))
- buyer_vat (VARCHAR(20), NULLABLE)
- buyer_fiscal_code (VARCHAR(16), NULLABLE)
- buyer_pec (VARCHAR(255), NULLABLE)
- buyer_sdi_code (VARCHAR(7), NULLABLE)
- buyer_address (JSONB)

-- Totali
- subtotal (DECIMAL(10,2))
- tax_amount (DECIMAL(10,2))
- total (DECIMAL(10,2))
- currency (VARCHAR(3), DEFAULT 'EUR')

-- File generati
- pdf_url (VARCHAR(500), NULLABLE)
- xml_url (VARCHAR(500), NULLABLE)
- xml_signed_url (VARCHAR(500), NULLABLE)

-- Status SDI
- sdi_status (ENUM: draft, generated, sent, accepted, rejected, delivered)
- sdi_sent_at (TIMESTAMP, NULLABLE)
- sdi_accepted_at (TIMESTAMP, NULLABLE)
- sdi_rejection_reason (TEXT, NULLABLE)

-- Status PEC
- pec_sent (BOOLEAN, DEFAULT false)
- pec_sent_at (TIMESTAMP, NULLABLE)
- pec_delivery_receipt (TEXT, NULLABLE)

- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())

Table: invoice_lines
- id (UUID, PK)
- invoice_id (UUID, FK → invoices)
- line_number (INTEGER)
- description (TEXT)
- quantity (DECIMAL(10,2))
- unit_price (DECIMAL(10,2))
- tax_rate (DECIMAL(5,2))
- tax_amount (DECIMAL(10,2))
- total (DECIMAL(10,2))

Table: credit_notes
- id (UUID, PK)
- credit_note_number (VARCHAR(50), UNIQUE)
- original_invoice_id (UUID, FK → invoices)
- issue_date (DATE)
- reason (TEXT)
- amount (DECIMAL(10,2))
- xml_url (VARCHAR(500), NULLABLE)
- pdf_url (VARCHAR(500), NULLABLE)
- sdi_status (ENUM: draft, sent, accepted, rejected)
- created_at (TIMESTAMP, DEFAULT NOW())

-- ============================================
-- CMS HEADLESS
-- ============================================

Table: pages
- id (UUID, PK)
- slug (VARCHAR(255), UNIQUE, NOT NULL)
- title (VARCHAR(255))
- page_type (ENUM: homepage, service, about, contact, custom)
- content_blocks (JSONB) -- Array di blocchi content
- seo_title (VARCHAR(255), NULLABLE)
- seo_description (TEXT, NULLABLE)
- seo_keywords (TEXT, NULLABLE)
- og_image (VARCHAR(500), NULLABLE)
- status (ENUM: draft, published, archived)
- published_at (TIMESTAMP, NULLABLE)
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())
- created_by (UUID, FK → users)
- updated_by (UUID, FK → users)

Table: page_versions
-- History/versioning per rollback
- id (UUID, PK)
- page_id (UUID, FK → pages)
- version_number (INTEGER)
- content_snapshot (JSONB)
- created_by (UUID, FK → users)
- created_at (TIMESTAMP, DEFAULT NOW())

Table: blog_posts
- id (UUID, PK)
- slug (VARCHAR(255), UNIQUE, NOT NULL)
- title (VARCHAR(255), NOT NULL)
- excerpt (TEXT)
- content (TEXT) -- HTML from rich text editor
- featured_image (VARCHAR(500), NULLABLE)
- author_id (UUID, FK → users)
- category_id (UUID, FK → blog_categories, NULLABLE)
- status (ENUM: draft, published, archived)
- published_at (TIMESTAMP, NULLABLE)
- scheduled_publish_at (TIMESTAMP, NULLABLE)
- view_count (INTEGER, DEFAULT 0)
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())
- seo_title (VARCHAR(255), NULLABLE)
- seo_description (TEXT, NULLABLE)

Table: blog_categories
- id (UUID, PK)
- name (VARCHAR(100), UNIQUE)
- slug (VARCHAR(100), UNIQUE)
- description (TEXT, NULLABLE)
- sort_order (INTEGER, DEFAULT 0)

Table: blog_tags
- id (UUID, PK)
- name (VARCHAR(50), UNIQUE)
- slug (VARCHAR(50), UNIQUE)

Table: blog_post_tags
- blog_post_id (UUID, FK → blog_posts)
- blog_tag_id (UUID, FK → blog_tags)
- PRIMARY KEY (blog_post_id, blog_tag_id)

Table: media_library
- id (UUID, PK)
- filename (VARCHAR(255))
- original_filename (VARCHAR(255))
- file_path (VARCHAR(500))
- file_url (VARCHAR(500))
- mime_type (VARCHAR(100))
- file_size (BIGINT) -- bytes
- width (INTEGER, NULLABLE) -- for images
- height (INTEGER, NULLABLE)
- alt_text (VARCHAR(255), NULLABLE)
- uploaded_by (UUID, FK → users)
- folder (VARCHAR(255), DEFAULT '/')
- created_at (TIMESTAMP, DEFAULT NOW())

-- ============================================
-- NEWSLETTER & EMAIL
-- ============================================

Table: newsletter_subscribers
- id (UUID, PK)
- email (VARCHAR(255), UNIQUE, NOT NULL)
- first_name (VARCHAR(100), NULLABLE)
- last_name (VARCHAR(100), NULLABLE)
- status (ENUM: pending, active, unsubscribed, bounced)
- subscribed_at (TIMESTAMP, DEFAULT NOW())
- confirmed_at (TIMESTAMP, NULLABLE)
- unsubscribed_at (TIMESTAMP, NULLABLE)
- source (VARCHAR(100)) -- web_form, manual, import
- user_id (UUID, FK → users, NULLABLE) -- Se è anche utente registrato
- confirmation_token (VARCHAR(255), NULLABLE)

Table: email_campaigns
- id (UUID, PK)
- name (VARCHAR(255))
- subject (VARCHAR(255))
- from_name (VARCHAR(255))
- from_email (VARCHAR(255))
- html_content (TEXT)
- text_content (TEXT)
- status (ENUM: draft, scheduled, sending, sent, failed)
- scheduled_at (TIMESTAMP, NULLABLE)
- sent_at (TIMESTAMP, NULLABLE)
- total_recipients (INTEGER, DEFAULT 0)
- total_sent (INTEGER, DEFAULT 0)
- total_opened (INTEGER, DEFAULT 0)
- total_clicked (INTEGER, DEFAULT 0)
- created_by (UUID, FK → users)
- created_at (TIMESTAMP, DEFAULT NOW())

Table: email_sends
- id (UUID, PK)
- campaign_id (UUID, FK → email_campaigns, NULLABLE)
- subscriber_id (UUID, FK → newsletter_subscribers, NULLABLE)
- user_id (UUID, FK → users, NULLABLE)
- email_to (VARCHAR(255))
- email_type (ENUM: transactional, newsletter, notification)
- subject (VARCHAR(255))
- status (ENUM: queued, sending, sent, failed, bounced)
- ms_graph_message_id (VARCHAR(255), NULLABLE)
- opened_at (TIMESTAMP, NULLABLE)
- clicked_at (TIMESTAMP, NULLABLE)
- error_message (TEXT, NULLABLE)
- queued_at (TIMESTAMP, DEFAULT NOW())
- sent_at (TIMESTAMP, NULLABLE)

-- ============================================
-- AI AGENT & KNOWLEDGE BASE
-- ============================================

Table: knowledge_base_documents
- id (UUID, PK)
- title (VARCHAR(255))
- filename (VARCHAR(255))
- file_path (VARCHAR(500))
- file_type (VARCHAR(50)) -- pdf, docx, txt, md
- file_size (BIGINT)
- content_text (TEXT) -- Extracted plain text
- topic (ENUM: ai, gdpr, nis2, cybersecurity, general)
- is_active (BOOLEAN, DEFAULT true)
- uploaded_by (UUID, FK → users)
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())

Table: knowledge_base_chunks
-- Per RAG (Retrieval-Augmented Generation)
- id (UUID, PK)
- document_id (UUID, FK → knowledge_base_documents)
- chunk_index (INTEGER)
- chunk_text (TEXT)
- embedding (VECTOR(1536)) -- pgvector, dimensione per text-embedding-ada-002 o simile
- token_count (INTEGER)
- metadata (JSONB) -- {page_number, section, etc.}

CREATE INDEX ON knowledge_base_chunks USING ivfflat (embedding vector_cosine_ops);

Table: chat_conversations
- id (UUID, PK)
- user_id (UUID, FK → users, NULLABLE) -- NULL per guest
- session_id (VARCHAR(255)) -- Browser session tracking
- started_at (TIMESTAMP, DEFAULT NOW())
- ended_at (TIMESTAMP, NULLABLE)
- total_messages (INTEGER, DEFAULT 0)
- user_feedback (ENUM: thumbs_up, thumbs_down, none, NULLABLE)

Table: chat_messages
- id (UUID, PK)
- conversation_id (UUID, FK → chat_conversations)
- role (ENUM: user, assistant, system)
- content (TEXT)
- retrieved_chunks (JSONB, NULLABLE) -- Array di chunk IDs usati per RAG
- claude_message_id (VARCHAR(255), NULLABLE)
- token_count (INTEGER, NULLABLE)
- created_at (TIMESTAMP, DEFAULT NOW())

Table: ai_guardrails_config
- id (UUID, PK)
- config_key (VARCHAR(100), UNIQUE)
- config_value (JSONB)
- description (TEXT)
- updated_by (UUID, FK → users)
- updated_at (TIMESTAMP, DEFAULT NOW())

-- Esempi config_key:
-- 'topic_whitelist', 'system_prompt', 'temperature', 'max_tokens', 'content_filters'

-- ============================================
-- SUPPORT TICKETS
-- ============================================

Table: support_tickets
- id (UUID, PK)
- ticket_number (VARCHAR(50), UNIQUE) -- TKT-2026-00001
- user_id (UUID, FK → users)
- subject (VARCHAR(255))
- description (TEXT)
- status (ENUM: new, in_progress, waiting_customer, resolved, closed)
- priority (ENUM: urgent, high, medium, low)
- category (VARCHAR(100), NULLABLE)
- assigned_to (UUID, FK → users, NULLABLE)
- created_at (TIMESTAMP, DEFAULT NOW())
- updated_at (TIMESTAMP, DEFAULT NOW())
- resolved_at (TIMESTAMP, NULLABLE)
- closed_at (TIMESTAMP, NULLABLE)
- first_response_at (TIMESTAMP, NULLABLE)

Table: ticket_messages
- id (UUID, PK)
- ticket_id (UUID, FK → support_tickets)
- user_id (UUID, FK → users)
- message (TEXT)
- is_internal (BOOLEAN, DEFAULT false) -- Note interne admin
- created_at (TIMESTAMP, DEFAULT NOW())

Table: ticket_attachments
- id (UUID, PK)
- ticket_id (UUID, FK → support_tickets)
- message_id (UUID, FK → ticket_messages, NULLABLE)
- filename (VARCHAR(255))
- file_path (VARCHAR(500))
- file_size (BIGINT)
- uploaded_by (UUID, FK → users)
- created_at (TIMESTAMP, DEFAULT NOW())

-- ============================================
-- NOTIFICATIONS
-- ============================================

Table: notifications
- id (UUID, PK)
- user_id (UUID, FK → users)
- type (VARCHAR(50)) -- order_update, invoice_ready, ticket_reply, blog_new, etc.
- title (VARCHAR(255))
- message (TEXT)
- action_url (VARCHAR(500), NULLABLE)
- is_read (BOOLEAN, DEFAULT false)
- read_at (TIMESTAMP, NULLABLE)
- created_at (TIMESTAMP, DEFAULT NOW())

-- ============================================
-- AUDIT & LOGGING
-- ============================================

Table: audit_logs
- id (UUID, PK)
- user_id (UUID, FK → users, NULLABLE)
- action (VARCHAR(100)) -- LOGIN, LOGOUT, CREATE, UPDATE, DELETE, EXPORT, etc.
- entity_type (VARCHAR(50)) -- orders, users, invoices, blog_posts, etc.
- entity_id (UUID, NULLABLE)
- changes (JSONB, NULLABLE) -- Before/After values
- ip_address (INET, NULLABLE)
- user_agent (TEXT, NULLABLE)
- created_at (TIMESTAMP, DEFAULT NOW())

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at);

Table: system_logs
-- Logs applicazione (separato da audit utente)
- id (UUID, PK)
- level (ENUM: debug, info, warning, error, critical)
- module (VARCHAR(100)) -- auth, payment, email, cms, api, etc.
- message (TEXT)
- stack_trace (TEXT, NULLABLE)
- context (JSONB, NULLABLE) -- Extra metadata
- user_id (UUID, FK → users, NULLABLE)
- ip_address (INET, NULLABLE)
- created_at (TIMESTAMP, DEFAULT NOW())

CREATE INDEX idx_system_logs_level ON system_logs(level);
CREATE INDEX idx_system_logs_module ON system_logs(module);
CREATE INDEX idx_system_logs_created ON system_logs(created_at);

-- ============================================
-- SETTINGS & CONFIGURATIONS
-- ============================================

Table: site_settings
- id (UUID, PK)
- setting_key (VARCHAR(100), UNIQUE)
- setting_value (JSONB)
- description (TEXT)
- updated_by (UUID, FK → users)
- updated_at (TIMESTAMP, DEFAULT NOW())

-- Esempi setting_key:
-- 'site_name', 'site_logo', 'contact_email', 'seller_info', 
-- 'stripe_keys', 'ms_graph_config', 'claude_api_key', etc.
```

### 2.2 Relazioni Chiave

```
users 1──────* orders
users 1──────* quote_requests
users 1──────* invoices
users 1──────* support_tickets
users 1──────* blog_posts (as author)
users 1──────* sessions
users 1──────1 user_profiles

orders 1──────* order_items
orders 1──────* payments
orders 1──────1 invoices

services 1──────* order_items
services 1──────* quote_requests
services 1──────1 service_content
services 1──────* service_faqs

blog_posts *──────* blog_tags (many-to-many)
blog_posts *──────1 blog_categories

support_tickets 1──────* ticket_messages
support_tickets *──────1 users (assigned_to)

knowledge_base_documents 1──────* knowledge_base_chunks
chat_conversations 1──────* chat_messages

email_campaigns 1──────* email_sends
newsletter_subscribers 1──────* email_sends
```

Table: user_profiles
- id (UUID, PK)
- user_id (UUID, FK → users)
- first_name (VARCHAR)
- last_name (VARCHAR)
- phone (VARCHAR)
- company_name (VARCHAR)
- vat_number (VARCHAR)
- fiscal_code (VARCHAR)
- billing_address (JSONB)
- shipping_address (JSONB)

Table: sessions
- id (UUID, PK)
- user_id (UUID, FK → users)
- token (VARCHAR, UNIQUE)
- refresh_token (VARCHAR, UNIQUE)
- expires_at (TIMESTAMP)
- ip_address (INET)
- user_agent (TEXT)

-- Prodotti/Servizi Consulenza
Table: products
- id (UUID, PK)
- sku (VARCHAR, UNIQUE)
- name (VARCHAR)
- slug (VARCHAR, UNIQUE)
- description (TEXT)
- long_description (TEXT)
- price (DECIMAL)
- price_type (ENUM: hourly, daily, project, subscription)
- is_active (BOOLEAN)
- category_id (UUID, FK → categories)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

Table: categories
- id (UUID, PK)
- name (VARCHAR)
- slug (VARCHAR)
- parent_id (UUID, FK → categories, nullable)
- sort_order (INTEGER)

Table: product_images
- id (UUID, PK)
- product_id (UUID, FK → products)
- image_url (VARCHAR)
- alt_text (VARCHAR)
- is_primary (BOOLEAN)
- sort_order (INTEGER)

-- Carrello e Ordini
Table: cart_items
- id (UUID, PK)
- user_id (UUID, FK → users, nullable) -- NULL per guest
- session_id (VARCHAR, nullable) -- Per guest users
- product_id (UUID, FK → products)
- quantity (INTEGER)
- price_snapshot (DECIMAL) -- Prezzo al momento aggiunta carrello
- created_at (TIMESTAMP)

Table: orders
- id (UUID, PK)
- order_number (VARCHAR, UNIQUE) -- es: ORD-2026-00001
- user_id (UUID, FK → users)
- status (ENUM: pending, paid, processing, completed, cancelled, refunded)
- subtotal (DECIMAL)
- tax (DECIMAL)
- discount (DECIMAL)
- total (DECIMAL)
- currency (VARCHAR, default: EUR)
- billing_address (JSONB)
- notes (TEXT)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- paid_at (TIMESTAMP, nullable)

Table: order_items
- id (UUID, PK)
- order_id (UUID, FK → orders)
- product_id (UUID, FK → products)
- product_name (VARCHAR) -- Snapshot
- quantity (INTEGER)
- unit_price (DECIMAL)
- total_price (DECIMAL)

Table: payments
- id (UUID, PK)
- order_id (UUID, FK → orders)
- stripe_payment_intent_id (VARCHAR, UNIQUE)
- amount (DECIMAL)
- currency (VARCHAR)
- status (ENUM: pending, succeeded, failed, refunded)
- payment_method (VARCHAR) -- card, sepa, etc.
- created_at (TIMESTAMP)
- processed_at (TIMESTAMP, nullable)

Table: invoices
- id (UUID, PK)
- invoice_number (VARCHAR, UNIQUE)
- order_id (UUID, FK → orders)
- user_id (UUID, FK → users)
- issue_date (DATE)
- due_date (DATE)
- total (DECIMAL)
- tax (DECIMAL)
- status (ENUM: draft, issued, paid, overdue, cancelled)
- pdf_url (VARCHAR)
- xml_url (VARCHAR) -- Fattura elettronica XML

-- CMS Content
Table: blog_posts
- id (UUID, PK)
- title (VARCHAR)
- slug (VARCHAR, UNIQUE)
- excerpt (TEXT)
- content (TEXT)
- author_id (UUID, FK → users)
- featured_image (VARCHAR)
- status (ENUM: draft, published, archived)
- published_at (TIMESTAMP, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- seo_title (VARCHAR)
- seo_description (VARCHAR)

Table: pages
- id (UUID, PK)
- title (VARCHAR)
- slug (VARCHAR, UNIQUE)
- content (TEXT)
- template (VARCHAR) -- Nome template layout
- status (ENUM: draft, published)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

-- Customer Portal
Table: support_tickets
- id (UUID, PK)
- ticket_number (VARCHAR, UNIQUE)
- user_id (UUID, FK → users)
- subject (VARCHAR)
- description (TEXT)
- status (ENUM: open, in_progress, waiting_customer, resolved, closed)
- priority (ENUM: low, medium, high, urgent)
- assigned_to (UUID, FK → users, nullable)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)

Table: ticket_messages
- id (UUID, PK)
- ticket_id (UUID, FK → support_tickets)
- user_id (UUID, FK → users)
- message (TEXT)
- is_internal (BOOLEAN) -- Note interne admin
- created_at (TIMESTAMP)

Table: notifications
- id (UUID, PK)
- user_id (UUID, FK → users)
- type (VARCHAR) -- order_update, ticket_reply, etc.
- title (VARCHAR)
- message (TEXT)
- is_read (BOOLEAN)
- action_url (VARCHAR, nullable)
- created_at (TIMESTAMP)

-- Audit & Logging
Table: audit_logs
- id (UUID, PK)
- user_id (UUID, FK → users, nullable)
- action (VARCHAR) -- CREATE, UPDATE, DELETE, LOGIN, etc.
- entity_type (VARCHAR) -- orders, users, products, etc.
- entity_id (UUID)
- changes (JSONB) -- Before/After values
- ip_address (INET)
- user_agent (TEXT)
- created_at (TIMESTAMP)
```

### 2.2 Relazioni Chiave

```
users 1──────* orders
users 1──────* support_tickets
users 1──────* sessions
users 1──────1 user_profiles

orders 1──────* order_items
orders 1──────* payments
orders 1──────1 invoices

products 1──────* order_items
products 1──────* cart_items
products *──────1 categories

support_tickets 1──────* ticket_messages
```

---

## 3. API DESIGN

### 3.1 Endpoint Structure

**Base URL**: `https://yourdomain.com/api/v1`

#### Authentication & Users
```
POST   /auth/register          - Registrazione nuovo utente
POST   /auth/login             - Login (JWT tokens)
POST   /auth/refresh           - Refresh access token
POST   /auth/logout            - Logout (invalidate token)
POST   /auth/forgot-password   - Reset password request
POST   /auth/reset-password    - Reset password confirm

GET    /users/me               - Profilo utente corrente
PATCH  /users/me               - Aggiorna profilo
DELETE /users/me               - Cancella account (GDPR)
GET    /users/me/orders        - Ordini utente
GET    /users/me/invoices      - Fatture utente
```

#### Products & Catalog
```
GET    /products               - Lista prodotti (paginato, filtri)
GET    /products/:id           - Dettaglio prodotto
GET    /products/slug/:slug    - Prodotto by slug
GET    /categories             - Lista categorie
GET    /categories/:id         - Categoria con prodotti
```

#### Cart & Checkout
```
GET    /cart                   - Visualizza carrello
POST   /cart/items             - Aggiungi al carrello
PATCH  /cart/items/:id         - Aggiorna quantità
DELETE /cart/items/:id         - Rimuovi da carrello
DELETE /cart                   - Svuota carrello

POST   /checkout/calculate     - Calcola totale + tasse
POST   /checkout/create-order  - Crea ordine
POST   /checkout/payment       - Process payment (Stripe)
```

#### Orders
```
GET    /orders                 - Lista ordini (admin)
GET    /orders/:id             - Dettaglio ordine
PATCH  /orders/:id/status      - Aggiorna status (admin)
GET    /orders/:id/invoice     - Download PDF fattura
```

#### CMS & Content
```
GET    /blog                   - Lista articoli blog
GET    /blog/:slug             - Articolo blog
GET    /pages/:slug            - Pagina statica
```

#### Support
```
GET    /tickets                - Lista ticket utente
POST   /tickets                - Crea nuovo ticket
GET    /tickets/:id            - Dettaglio ticket
POST   /tickets/:id/messages   - Aggiungi messaggio
PATCH  /tickets/:id/status     - Aggiorna status
```

#### Admin
```
GET    /admin/dashboard        - Stats e metriche
GET    /admin/users            - Gestione utenti
GET    /admin/products         - CRUD prodotti
GET    /admin/orders           - Gestione ordini
GET    /admin/analytics        - Analytics dati
```

#### Webhooks
```
POST   /webhooks/stripe        - Stripe webhook events
POST   /webhooks/n8n           - n8n webhook trigger
```

### 3.2 Response Format

**Success Response**:
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "name": "Product Name",
    ...
  },
  "meta": {
    "timestamp": "2026-01-15T10:30:00Z",
    "request_id": "req-uuid"
  }
}
```

**Error Response**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Invalid email format"],
      "password": ["Password too short"]
    }
  },
  "meta": {
    "timestamp": "2026-01-15T10:30:00Z",
    "request_id": "req-uuid"
  }
}
```

**Paginated Response**:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 150,
    "page": 1,
    "per_page": 20,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  }
}
```

---

## 4. SECURITY ARCHITECTURE

### 4.1 Layers di Sicurezza

```
Layer 1: Network
  └── Firewall Linode (solo 80, 443, 22)
  
Layer 2: Reverse Proxy
  └── Nginx: Rate limiting, SSL/TLS, Headers
  
Layer 3: Application
  └── JWT Auth, RBAC, Input validation
  
Layer 4: Data
  └── Encryption at rest, Encrypted backups
```

### 4.2 Authentication Flow

```
1. User Login
   │
   ├─→ POST /api/v1/auth/login
   │   Body: { email, password }
   │
   ├─→ Backend verifica credentials
   │   - Retrieve user from DB
   │   - Bcrypt verify password
   │   - Check if user active
   │
   ├─→ Generate JWT tokens
   │   - Access Token (15min TTL)
   │   - Refresh Token (7 days TTL)
   │
   ├─→ Store session in Redis
   │   Key: session:{user_id}
   │   Value: { token, refresh_token, metadata }
   │   TTL: 7 days
   │
   └─→ Return tokens to client
       Response: {
         access_token: "...",
         refresh_token: "...",
         expires_in: 900
       }

2. Authenticated Request
   │
   ├─→ Client sends: Authorization: Bearer {access_token}
   │
   ├─→ Backend verifies token
   │   - Decode JWT
   │   - Verify signature
   │   - Check expiration
   │   - Validate session exists in Redis
   │
   └─→ Process request OR return 401

3. Token Refresh
   │
   ├─→ POST /api/v1/auth/refresh
   │   Body: { refresh_token }
   │
   ├─→ Verify refresh token validity
   │
   ├─→ Generate new access token
   │
   └─→ Return new access token
```

### 4.3 RBAC Permissions

```python
# Role-Based Access Control Matrix

ROLES = {
    'guest': {
        'permissions': ['view_products', 'view_blog'],
    },
    'customer': {
        'inherits': 'guest',
        'permissions': [
            'create_order',
            'view_own_orders',
            'create_ticket',
            'view_own_tickets',
            'update_profile',
        ],
    },
    'editor': {
        'inherits': 'customer',
        'permissions': [
            'create_blog_post',
            'edit_blog_post',
            'publish_blog_post',
            'manage_pages',
        ],
    },
    'admin': {
        'inherits': 'editor',
        'permissions': [
            'manage_users',
            'manage_products',
            'manage_orders',
            'view_analytics',
            'system_settings',
            '*',  # All permissions
        ],
    },
}
```

---

## 5. INTEGRATION ARCHITECTURE

### 5.1 Stripe Integration

```
Checkout Flow:
1. Frontend: User clicks "Pay"
   └─→ POST /api/v1/checkout/create-order
       - Validate cart
       - Calculate totals
       - Create order (status: pending)
       
2. Backend: Create Stripe Payment Intent
   └─→ Stripe API: Create PaymentIntent
       - amount: order.total * 100
       - currency: "eur"
       - metadata: { order_id, user_id }
       
3. Return client_secret to frontend
   └─→ Frontend: Show Stripe Elements form
   
4. User completes payment
   └─→ Stripe processes payment
   
5. Stripe sends webhook
   └─→ POST /api/v1/webhooks/stripe
       Event: payment_intent.succeeded
       
6. Backend processes webhook
   ├─→ Verify signature
   ├─→ Update order status: paid
   ├─→ Create payment record
   ├─→ Generate invoice
   └─→ Trigger n8n workflow (email confirmation)
```

### 5.2 n8n Workflow Integration

```
Workflow: New Order Processing
Trigger: Webhook from backend

Steps:
1. Receive order data
   ├─ Order ID
   ├─ Customer info
   ├─ Products
   └─ Total amount

2. Create HubSpot Deal
   └─→ HubSpot API: Create Deal
       - dealname: Order #{order_number}
       - amount: order.total
       - dealstage: "closedwon"

3. Create/Update HubSpot Contact
   └─→ HubSpot API: Upsert Contact
       - email: customer.email
       - properties: { name, phone, company }

4. Send Confirmation Email
   └─→ SendGrid API: Send Email
       - template: order_confirmation
       - to: customer.email
       - dynamic_data: { order_details }

5. Notify Admin
   └─→ Slack/Telegram: Send notification
       "New order #123 - €500"

6. Schedule Follow-up
   └─→ n8n Schedule: Send feedback request
       Delay: 7 days after order completion
```

### 5.3 Claude API Integration

```
Use Cases:

1. Customer Support Chatbot
   Frontend: Chat widget
   ├─→ User sends message
   ├─→ POST /api/v1/chat/message
   ├─→ Backend: Query Claude API
   │   Prompt: "You are a customer support assistant..."
   │   Context: User's order history, FAQs
   └─→ Stream response to frontend

2. Order Intent Analysis
   Admin receives custom request
   ├─→ Paste request in admin panel
   ├─→ Claude API analyzes
   │   - Extract requirements
   │   - Suggest products/services
   │   - Estimate cost
   └─→ Generate draft proposal

3. Content Generation
   Editor creates blog post
   ├─→ Provide topic + keywords
   ├─→ Claude generates outline
   ├─→ Editor reviews & refines
   └─→ Publish
```

### 5.4 HubSpot CRM Sync

```
Entities Mapping:
├─ users → HubSpot Contacts
├─ orders → HubSpot Deals
├─ products → HubSpot Products
└─ support_tickets → HubSpot Tickets

Sync Strategy:
- Real-time: Webhooks for critical events (new order, new user)
- Batch: Nightly sync for updates (n8n scheduled workflow)
- On-demand: Manual sync button in admin panel
```

---

## 6. DEPLOYMENT ARCHITECTURE

### 6.1 Docker Compose Stack

```yaml
# docker-compose.prod.yml (semplificato)

version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - static_files:/var/www/static:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped

  frontend:
    build: ./frontend
    expose:
      - "3000"
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com
    restart: unless-stopped

  backend:
    build: ./backend
    expose:
      - "8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/dbname
      - REDIS_URL=redis://redis:6379
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=ecommerce
      - POSTGRES_USER=${DB_USER}
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    volumes:
      - n8n_data:/home/node/.n8n
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD}
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  n8n_data:
  static_files:

networks:
  default:
    driver: bridge
```

### 6.2 Nginx Configuration

```nginx
# /etc/nginx/conf.d/default.conf

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256...';
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req zone=api_limit burst=20 nodelay;

    # Frontend (Next.js)
    location / {
        proxy_pass http://frontend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static Files
    location /static {
        alias /var/www/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

---

## 7. MONITORING & OBSERVABILITY

### 7.1 Health Checks

```python
# Backend health endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint per Docker e monitoring.
    Verifica connettività DB, Redis, e servizi esterni.
    """
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": APP_VERSION,
        "checks": {}
    }
    
    # Check Database
    try:
        db.execute("SELECT 1")
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    # Check Redis
    try:
        redis_client.ping()
        health_status["checks"]["redis"] = "ok"
    except Exception as e:
        health_status["checks"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
    
    return health_status
```

### 7.2 Logging Strategy

```python
# Structured logging per Docker logs aggregation

import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """
    Formatter per log in formato JSON per parsing automatico.
    """
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Aggiungi exception info se presente
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        
        # Aggiungi custom fields
        if hasattr(record, 'user_id'):
            log_obj["user_id"] = record.user_id
        if hasattr(record, 'request_id'):
            log_obj["request_id"] = record.request_id
            
        return json.dumps(log_obj)
```

### 7.3 Metrics Collection

```python
# Metriche applicazione custom (Prometheus-compatible)

from prometheus_client import Counter, Histogram, Gauge

# Request metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint']
)

# Business metrics
orders_created = Counter('orders_created_total', 'Total orders created')
payments_processed = Counter('payments_processed_total', 'Total payments')
payment_amount = Histogram('payment_amount_eur', 'Payment amounts')

# System metrics
active_users = Gauge('active_users', 'Currently active users')
cart_items = Gauge('cart_items_total', 'Total items in all carts')
```

---

## 8. SCALABILITY CONSIDERATIONS

### 8.1 Horizontal Scaling (Futuro)

```
Load Balancer (Nginx)
    │
    ├──→ Frontend Instance 1
    ├──→ Frontend Instance 2
    └──→ Frontend Instance 3
    
    ├──→ Backend Instance 1
    ├──→ Backend Instance 2
    └──→ Backend Instance 3
    
    └──→ Shared: PostgreSQL, Redis
```

### 8.2 Caching Strategy

```
1. Redis Caching Layers:
   ├─ Session Cache (TTL: token expiry)
   ├─ API Response Cache (TTL: 5-60 min)
   ├─ Product Catalog (TTL: 1 hour)
   └─ User Data (TTL: 15 min)

2. CDN (Futuro):
   ├─ Static assets (CSS, JS, images)
   └─ Product images

3. Database Query Optimization:
   ├─ Proper indexes
   ├─ Query result caching
   └─ Connection pooling
```

---

## 9. DISASTER RECOVERY

### 9.1 Backup Strategy

```bash
# Automated backup script (cron daily)

#!/bin/bash
# /opt/scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
docker exec postgres pg_dump -U $DB_USER $DB_NAME | gzip > \
    $BACKUP_DIR/db_backup_$DATE.sql.gz

# Redis backup
docker exec redis redis-cli SAVE
cp /var/lib/docker/volumes/redis_data/_data/dump.rdb \
    $BACKUP_DIR/redis_backup_$DATE.rdb

# File storage backup
tar -czf $BACKUP_DIR/files_backup_$DATE.tar.gz /var/www/uploads

# Upload to remote (S3/Backblaze)
rclone copy $BACKUP_DIR remote:backups/

# Cleanup old backups (keep 7 days local)
find $BACKUP_DIR -type f -mtime +7 -delete

# Log backup completion
logger "Backup completed: $DATE"
```

### 9.2 Restore Procedure

```bash
# Restore from backup

# 1. Stop services
docker-compose down

# 2. Restore database
gunzip < db_backup_YYYYMMDD.sql.gz | \
    docker exec -i postgres psql -U $DB_USER $DB_NAME

# 3. Restore Redis
docker cp redis_backup_YYYYMMDD.rdb redis:/data/dump.rdb

# 4. Restore files
tar -xzf files_backup_YYYYMMDD.tar.gz -C /

# 5. Restart services
docker-compose up -d

# 6. Verify
curl https://yourdomain.com/api/v1/health
```

---

**VERSIONE DOCUMENTO**: 1.0  
**ULTIMA MODIFICA**: 2026-01-15  
**PROSSIMA REVISIONE**: Post-implementazione backend framework
