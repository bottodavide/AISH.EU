# Codebase Structure

**Analysis Date:** 2026-01-18

## Directory Layout

```
aistrategyhub/
├── backend/                   # FastAPI Python backend
│   ├── app/                   # Application code
│   │   ├── api/               # API route handlers
│   │   │   └── routes/        # Organized by domain
│   │   ├── core/              # Infrastructure & config
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic validation schemas
│   │   ├── services/          # Business logic & integrations
│   │   ├── workers/           # Background tasks
│   │   ├── static/            # Static assets
│   │   └── templates/         # Email templates (Jinja2)
│   ├── migrations/            # Alembic database migrations
│   │   └── versions/          # Migration scripts
│   ├── scripts/               # Utility scripts
│   ├── uploads/               # User-uploaded files
│   │   ├── attachments/
│   │   ├── avatars/
│   │   ├── documents/
│   │   ├── images/
│   │   ├── invoices/
│   │   └── temp/
│   ├── venv/                  # Python virtual environment
│   └── requirements.txt       # Python dependencies
├── frontend/                  # Next.js 14 frontend
│   ├── src/
│   │   ├── app/               # Next.js App Router pages
│   │   │   ├── admin/         # Admin panel routes
│   │   │   ├── dashboard/     # User dashboard routes
│   │   │   ├── blog/          # Blog pages
│   │   │   ├── servizi/       # Services pages
│   │   │   └── ...            # Other routes
│   │   ├── components/        # React components
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── contexts/          # React Context providers
│   │   ├── lib/               # Utilities & API client
│   │   └── styles/            # CSS/Tailwind styles
│   ├── public/                # Static assets
│   ├── .next/                 # Next.js build output (generated)
│   ├── node_modules/          # npm dependencies (generated)
│   ├── uploads/               # Symlinked uploads directory
│   └── package.json           # Node.js dependencies
├── nginx/                     # Nginx configuration
│   └── nginx.conf
├── scripts/                   # Deployment & utility scripts
│   ├── entrypoint.sh
│   ├── backup.sh
│   └── deploy.sh
├── docs/                      # Project documentation
├── .planning/                 # GSD planning documents
│   └── codebase/              # Codebase analysis docs
├── Dockerfile                 # Multi-stage container build
├── docker-compose.yml         # Local development compose
├── supervisord.conf           # Process manager config
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # Project overview
```

## Directory Purposes

**backend/app/api/routes/:**
- Purpose: FastAPI route handlers organized by domain
- Contains: Router modules for each API resource
- Key files:
  - `auth.py`: Authentication (login, register, MFA, password reset)
  - `users.py`: User management
  - `services.py`: Service catalog
  - `orders.py`: Order & checkout
  - `invoices.py`: Invoice generation & retrieval
  - `cms.py`: Headless CMS endpoints (pages, blog)
  - `chat.py`: AI chatbot with RAG
  - `knowledge_base.py`: Knowledge base document management
  - `admin.py`: Admin panel endpoints
  - `files.py`: File upload/download
  - `newsletter.py`: Newsletter subscriptions
  - `contact.py`: Contact form
  - `homepage.py`: Homepage banners
  - `packages.py`: Consulting packages
  - `use_cases.py`: Use cases/success stories
  - `about.py`: About page content
  - `analytics.py`: Analytics & logs
  - `errors.py`: Error reporting

**backend/app/core/:**
- Purpose: Infrastructure layer - configuration, database, security
- Contains: Cross-cutting concerns
- Key files:
  - `config.py`: Settings and environment variables (Pydantic Settings)
  - `database.py`: SQLAlchemy engine, session factories (sync + async)
  - `security.py`: JWT generation/validation, password hashing, MFA utilities
  - `dependencies.py`: FastAPI dependencies (auth, RBAC, pagination)
  - `exceptions.py`: Custom exception classes and handlers
  - `logging_config.py`: Centralized logging configuration
  - `system_logger.py`: System-wide logging utilities

**backend/app/models/:**
- Purpose: SQLAlchemy ORM models (database schema)
- Contains: Table definitions with relationships
- Key files:
  - `base.py`: Base model class with common fields
  - `user.py`: User, UserProfile, UserRole, Session, LoginAttempt
  - `service.py`: Service, ServiceCategory, ServiceType, PricingType
  - `order.py`: Order, OrderItem, OrderStatus, Payment
  - `invoice.py`: Invoice, InvoiceLine, InvoiceStatus
  - `cms.py`: Page, BlogPost, BlogCategory
  - `chat.py`: ChatConversation, ChatMessage
  - `knowledge_base.py`: KnowledgeBaseDocument, KnowledgeBaseChunk (with pgvector)
  - `file.py`: File (uploaded files tracking)
  - `newsletter.py`: NewsletterSubscriber
  - `notification.py`: Notification
  - `support.py`: SupportTicket, TicketMessage
  - `audit.py`: AuditLog, SystemLog
  - `package.py`: ConsultingPackage
  - `use_case.py`: UseCase
  - `about_page.py`: AboutPage, TeamMember
  - `homepage.py`: HomepageBanner
  - `settings.py`: SystemSettings

**backend/app/schemas/:**
- Purpose: Pydantic models for request/response validation
- Contains: API contracts mirroring models
- Key files: Match models directory (e.g., `user.py`, `service.py`, `auth.py`)

**backend/app/services/:**
- Purpose: Business logic and external service integrations
- Contains: Reusable service classes
- Key files:
  - `email_service.py`: MS Graph API email sending
  - `email_templates.py`: Email template generation
  - `ms_graph.py`: Microsoft Graph authentication
  - `stripe_service.py`: Stripe payment processing
  - `claude_service.py`: Anthropic Claude API integration
  - `rag_service.py`: RAG pipeline (embeddings + similarity search)
  - `guardrails_service.py`: AI response safety checks
  - `invoice_xml.py`: Italian electronic invoice XML generation (PA format)
  - `invoice_pdf.py`: Invoice PDF generation
  - `file_storage.py`: File upload/storage management

**backend/migrations/:**
- Purpose: Alembic database migration scripts
- Contains: Versioned schema changes
- Key files: `versions/` contains timestamped migration files

**frontend/src/app/:**
- Purpose: Next.js App Router pages
- Contains: Route definitions (directories = URL paths)
- Key structure:
  - `page.tsx`: Homepage
  - `layout.tsx`: Root layout with providers
  - `admin/`: Admin panel (role-restricted)
  - `dashboard/`: Customer dashboard
  - `login/`, `register/`: Auth pages
  - `servizi/[slug]/`: Dynamic service pages
  - `blog/[slug]/`: Dynamic blog posts
  - `ordini/[id]/`: Order detail pages

**frontend/src/components/:**
- Purpose: Reusable React components
- Contains: UI building blocks
- Key files:
  - `Navigation.tsx`: Site navigation bar
  - `Footer.tsx`: Site footer
  - `ChatWidget.tsx`: AI chatbot widget
  - `AdminSidebar.tsx`: Admin navigation
  - `UserSidebar.tsx`: Customer dashboard navigation
  - `ImageUpload.tsx`: Image upload component
  - `RichTextEditor.tsx`: TipTap WYSIWYG editor
  - `StripeCheckoutForm.tsx`: Stripe payment form
  - `NewsletterForm.tsx`: Newsletter subscription
  - `ErrorBoundary.tsx`: React error boundary
  - `CookieBanner.tsx`: Cookie consent banner
  - `MFAEnforcer.tsx`: MFA requirement enforcer
  - `ui/`: shadcn/ui components (button, card, dialog, etc.)

**frontend/src/contexts/:**
- Purpose: React Context providers for global state
- Contains: Context definitions
- Key files:
  - `AuthContext.tsx`: Authentication state (user, login, logout, tokens)

**frontend/src/lib/:**
- Purpose: Frontend utilities and shared logic
- Contains: Helper functions and clients
- Key files:
  - `api-client.ts`: Axios-based API client with auth interceptors
  - `utils.ts`: Utility functions (cn for classnames)
  - `cookies.ts`: Cookie management
  - `error-handler.ts`: Error handling utilities

## Key File Locations

**Entry Points:**
- Backend: `backend/app/main.py`
- Frontend: `frontend/src/app/layout.tsx` and `frontend/src/app/page.tsx`

**Configuration:**
- Backend: `backend/app/core/config.py` (loads from .env)
- Frontend: `frontend/next.config.js`, `frontend/tailwind.config.ts`
- Environment: `.env.example` (template)
- Docker: `Dockerfile`, `docker-compose.yml`
- Process manager: `supervisord.conf`
- Web server: `nginx/nginx.conf`

**Core Logic:**
- Backend business logic: `backend/app/services/`
- API route handlers: `backend/app/api/routes/`
- Database models: `backend/app/models/`
- Frontend API interaction: `frontend/src/lib/api-client.ts`
- Authentication logic: `backend/app/core/security.py`, `frontend/src/contexts/AuthContext.tsx`

**Testing:**
- Backend tests: Not yet implemented (pytest config in requirements.txt)
- Frontend tests: `frontend/jest.config.js` configured but no test files present

## Naming Conventions

**Files:**
- Python backend: `snake_case.py` (e.g., `email_service.py`, `knowledge_base.py`)
- TypeScript frontend: `PascalCase.tsx` for components (e.g., `ChatWidget.tsx`), `kebab-case.ts` for utilities (e.g., `api-client.ts`)
- Route files: Always `page.tsx` for pages, `layout.tsx` for layouts (Next.js convention)
- Config files: Various conventions (`requirements.txt`, `package.json`, `tsconfig.json`)

**Directories:**
- Backend: `snake_case` (e.g., `knowledge_base`, `api/routes`)
- Frontend routes: `kebab-case` (e.g., `setup-mfa`, `password-reset`)
- Frontend components: No specific pattern, usually descriptive names

**Functions:**
- Python: `snake_case` (e.g., `get_current_user`, `send_verification_email`)
- TypeScript: `camelCase` (e.g., `getErrorMessage`, `isAuthenticated`)
- React components: `PascalCase` (e.g., `Navigation`, `ChatWidget`)

**Variables:**
- Python: `snake_case` (e.g., `current_user`, `access_token`)
- TypeScript: `camelCase` (e.g., `currentUser`, `accessToken`)

**Types:**
- Python: `PascalCase` for classes (e.g., `User`, `OrderStatus`)
- TypeScript: `PascalCase` for interfaces/types (e.g., `ApiError`, `PaginatedResponse`)

## Where to Add New Code

**New API Endpoint:**
- Primary code: `backend/app/api/routes/{domain}.py` (add to existing or create new router)
- Register router: `backend/app/main.py` (include_router)
- Schema: `backend/app/schemas/{domain}.py`
- If new model needed: `backend/app/models/{domain}.py`
- If external integration: `backend/app/services/{service}_service.py`

**New Frontend Page:**
- Implementation: `frontend/src/app/{route-name}/page.tsx`
- Layout (if needed): `frontend/src/app/{route-name}/layout.tsx`
- Dynamic routes: `frontend/src/app/{route-name}/[param]/page.tsx`
- Metadata: Export `metadata` object in page.tsx

**New Component:**
- Reusable UI: `frontend/src/components/{ComponentName}.tsx`
- shadcn/ui: `frontend/src/components/ui/{component-name}.tsx` (add via CLI)
- Page-specific: Colocate in `frontend/src/app/{route}/` if not reusable

**New Database Model:**
- Model definition: `backend/app/models/{domain}.py`
- Import in: `backend/app/models/__init__.py` (for Alembic detection)
- Schema: `backend/app/schemas/{domain}.py`
- Migration: Run `alembic revision --autogenerate -m "description"`

**New Service/Integration:**
- Implementation: `backend/app/services/{service}_service.py`
- Config: Add settings to `backend/app/core/config.py`
- Environment vars: Document in `.env.example`

**New Admin Feature:**
- Frontend: `frontend/src/app/admin/{feature}/page.tsx`
- API: `backend/app/api/routes/admin.py` (add endpoints)
- Sidebar: Update `frontend/src/components/AdminSidebar.tsx`

**Utilities:**
- Backend: `backend/app/core/` for infrastructure, `backend/app/services/` for business logic
- Frontend: `frontend/src/lib/` for shared helpers

## Special Directories

**backend/uploads/:**
- Purpose: User-uploaded files storage
- Generated: Yes (by file upload service)
- Committed: No (in .gitignore)
- Subdirectories organize by file type (avatars, documents, invoices, etc.)

**backend/migrations/versions/:**
- Purpose: Alembic migration scripts
- Generated: Yes (via `alembic revision --autogenerate`)
- Committed: Yes (version control for schema)

**frontend/.next/:**
- Purpose: Next.js build output and cache
- Generated: Yes (during `npm run build` or dev server)
- Committed: No (in .gitignore)

**frontend/node_modules/:**
- Purpose: npm package dependencies
- Generated: Yes (via `npm install`)
- Committed: No (in .gitignore)

**backend/venv/:**
- Purpose: Python virtual environment
- Generated: Yes (via `python -m venv venv`)
- Committed: No (in .gitignore)

**.planning/codebase/:**
- Purpose: GSD codebase analysis documents
- Generated: Yes (by `/gsd:map-codebase` command)
- Committed: Yes (helps future GSD operations)

**docs/:**
- Purpose: Project documentation
- Generated: Manually created
- Committed: Yes

---

*Structure analysis: 2026-01-18*
