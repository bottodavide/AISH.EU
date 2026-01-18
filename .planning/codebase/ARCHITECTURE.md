# Architecture

**Analysis Date:** 2026-01-18

## Pattern Overview

**Overall:** Monolithic full-stack application with RESTful API backend and server-side rendered frontend

**Key Characteristics:**
- Backend-driven architecture with FastAPI providing API endpoints
- Next.js App Router frontend consuming REST APIs
- Clear separation between presentation (frontend) and business logic (backend)
- Service layer pattern isolating external integrations
- Async-first design with async/await throughout

## Layers

**Presentation Layer:**
- Purpose: User interface and client-side interactions
- Location: `frontend/src/app` and `frontend/src/components`
- Contains: Next.js pages, React components, forms, UI elements
- Depends on: API Client (`frontend/src/lib/api-client.ts`), shadcn/ui components
- Used by: End users via web browser

**API Layer:**
- Purpose: HTTP endpoints exposing business functionality
- Location: `backend/app/api/routes`
- Contains: FastAPI routers for auth, services, orders, CMS, chat, admin
- Depends on: Core dependencies, services, schemas, models
- Used by: Frontend API client, external webhooks (Stripe)

**Service Layer:**
- Purpose: Business logic and external integrations
- Location: `backend/app/services`
- Contains: Email service (MS Graph), Stripe integration, Claude AI, RAG, file storage, invoice generation
- Depends on: Core config, database, external APIs
- Used by: API route handlers

**Data Access Layer:**
- Purpose: Database operations and ORM models
- Location: `backend/app/models`
- Contains: SQLAlchemy models for users, orders, services, invoices, CMS, knowledge base
- Depends on: SQLAlchemy, PostgreSQL with pgvector extension
- Used by: API routes (via async sessions), services

**Infrastructure Layer:**
- Purpose: Cross-cutting concerns and configuration
- Location: `backend/app/core`
- Contains: Config, database connections, security (JWT/MFA), logging, exception handling, dependencies
- Depends on: Environment variables, external services configuration
- Used by: All other layers

## Data Flow

**Public Request Flow (Unauthenticated):**

1. User visits public page → Next.js renders SSR page (`frontend/src/app/page.tsx`)
2. Client-side hydration loads React components (`frontend/src/components`)
3. Component fetches data via API client (`frontend/src/lib/api-client.ts`)
4. API client sends HTTP request to FastAPI endpoint (`backend/app/api/routes/*.py`)
5. Route handler queries database via async session (`backend/app/core/database.py`)
6. Response serialized via Pydantic schema (`backend/app/schemas/*.py`)
7. Frontend receives JSON, updates UI

**Authenticated Request Flow:**

1. User logs in → JWT tokens stored in localStorage
2. API client intercepts requests → adds Bearer token to Authorization header
3. FastAPI security middleware validates JWT (`backend/app/core/dependencies.py:get_current_user`)
4. Token decoded → user loaded from database
5. Route handler checks role-based permissions via `RoleChecker` dependency
6. If authorized → business logic executes
7. If MFA required → returns 403, frontend redirects to MFA setup

**AI Chat Flow:**

1. User sends message via ChatWidget (`frontend/src/components/ChatWidget.tsx`)
2. POST /api/v1/chat/message endpoint receives request (`backend/app/api/routes/chat.py`)
3. Guardrails service validates topic and content (`backend/app/services/guardrails_service.py`)
4. RAG service retrieves context: query → embedding → pgvector similarity search (`backend/app/services/rag_service.py`)
5. Claude service constructs prompt with context → calls Anthropic API (`backend/app/services/claude_service.py`)
6. Streaming response sent back to frontend
7. Conversation saved to database (`backend/app/models/chat.py`)

**Order & Payment Flow:**

1. User selects service/package → adds to cart
2. Checkout component collects billing info → creates order
3. POST /api/v1/orders → Order created in database (`backend/app/api/routes/orders.py`)
4. POST /api/v1/checkout/payment → Stripe Payment Intent created (`backend/app/services/stripe_service.py`)
5. Frontend loads Stripe Elements → user completes payment
6. Stripe webhook confirms payment → POST /api/v1/webhooks/stripe
7. Order status updated → Invoice generated (XML + PDF) (`backend/app/services/invoice_xml.py`, `invoice_pdf.py`)
8. Invoice sent via email (MS Graph API) (`backend/app/services/email_service.py`)

**State Management:**
- Frontend: React Context for auth (`frontend/src/contexts/AuthContext.tsx`), Zustand for global state
- Backend: PostgreSQL for persistent state, Redis for sessions/cache (configured but not fully implemented)
- Client-side: localStorage for JWT tokens, session storage for temporary data

## Key Abstractions

**User & Authentication:**
- Purpose: Represents system users with role-based access control
- Examples: `backend/app/models/user.py` (User, UserProfile, UserRole enum, Session, LoginAttempt)
- Pattern: JWT tokens (access + refresh), TOTP-based MFA, email verification flow

**Service & Offerings:**
- Purpose: Consultancy services offered to customers
- Examples: `backend/app/models/service.py` (Service, ServiceCategory, ServiceType, PricingType)
- Pattern: CMS-like content management with rich text, pricing tiers, active/inactive flags

**Order & Commerce:**
- Purpose: E-commerce order management
- Examples: `backend/app/models/order.py` (Order, OrderItem, OrderStatus, PaymentStatus)
- Pattern: Order aggregates line items, links to payments and invoices

**Invoice & Billing:**
- Purpose: Italian electronic invoicing (Sistema di Interscambio)
- Examples: `backend/app/models/invoice.py` (Invoice, InvoiceLine, InvoiceStatus)
- Pattern: Generates XML (PA format) and PDF, tracks SDI submission status

**Knowledge Base & RAG:**
- Purpose: Document storage with vector embeddings for similarity search
- Examples: `backend/app/models/knowledge_base.py` (KnowledgeBaseDocument, KnowledgeBaseChunk)
- Pattern: Documents chunked → OpenAI embeddings → stored in pgvector → retrieved via cosine similarity

**CMS Content:**
- Purpose: Headless CMS for pages, blog posts, banners
- Examples: `backend/app/models/cms.py` (Page, BlogPost, BlogCategory)
- Pattern: Slug-based routing, rich text content (TipTap), publish/draft states

## Entry Points

**Frontend Entry Point:**
- Location: `frontend/src/app/layout.tsx`
- Triggers: Browser navigation to any route
- Responsibilities: Root layout, metadata, providers (AuthProvider, ErrorBoundary), global components (ChatWidget, CookieBanner, MFAEnforcer)

**Frontend Homepage:**
- Location: `frontend/src/app/page.tsx`
- Triggers: User visits root URL
- Responsibilities: Landing page rendering, hero banner, service overview sections

**Backend Entry Point:**
- Location: `backend/app/main.py`
- Triggers: Uvicorn starts application
- Responsibilities: FastAPI app initialization, middleware setup (CORS, Gzip), router registration, exception handlers, lifespan management

**Admin Panel Entry:**
- Location: `frontend/src/app/admin/page.tsx` with layout `frontend/src/app/admin/layout.tsx`
- Triggers: Authenticated admin user navigates to /admin
- Responsibilities: Admin dashboard, sidebar navigation, RBAC enforcement

**User Dashboard Entry:**
- Location: `frontend/src/app/dashboard/page.tsx`
- Triggers: Authenticated customer navigates to /dashboard
- Responsibilities: Customer dashboard showing orders, services, profile

## Error Handling

**Strategy:** Centralized exception handling with custom exception classes and HTTP exception handlers

**Patterns:**
- Backend exceptions: Custom `AIStrategyHubException` base class (`backend/app/core/exceptions.py`)
- FastAPI exception handlers: `aistrategyhub_exception_handler`, `http_exception_handler`, `generic_exception_handler` registered in `backend/app/main.py`
- Frontend error handling: `getErrorMessage()` utility translates Axios errors to user-friendly Italian messages (`frontend/src/lib/api-client.ts`)
- ErrorBoundary component catches React errors (`frontend/src/components/ErrorBoundary.tsx`)
- Email notifications for critical errors via `email_service.send_error_notification()` (`backend/app/services/email_service.py`)
- Structured logging with context: `logger.error(message, exc_info=True)` throughout codebase
- Validation errors: Pydantic validation at API boundary returns 422 with detailed field errors
- 401/403 handling: API client intercepts, attempts token refresh, redirects to login if refresh fails

## Cross-Cutting Concerns

**Logging:**
- Centralized configuration in `backend/app/core/logging_config.py`
- JSON structured logging with `python-json-logger`
- Per-module loggers: `logger = logging.getLogger(__name__)`
- System-wide logger utilities: `backend/app/core/system_logger.py` (log_info, log_warning, log_error)
- Log levels: DEBUG for development, INFO for operations, WARNING for handled issues, ERROR for failures
- Frontend: Console logging in development mode only

**Validation:**
- Backend: Pydantic v2 schemas for request/response validation (`backend/app/schemas/`)
- Type hints throughout: all functions have type annotations
- Frontend: Zod schemas with React Hook Form (`@hookform/resolvers/zod`)
- File validation: MIME type checking, size limits in `backend/app/services/file_storage.py`
- Email validation: `email-validator` library
- SQL injection prevention: SQLAlchemy parameterized queries only

**Authentication:**
- JWT-based with access (15min) and refresh (7 days) tokens
- Token generation/validation: `backend/app/core/security.py`
- Password hashing: Argon2 via passlib
- MFA: TOTP (Time-based One-Time Password) with pyotp, QR code generation
- Email verification: Token-based email confirmation flow
- Dependency injection: `get_current_user` dependency validates token and loads user
- Role-based access control: `RoleChecker` class validates user roles
- Session tracking: `Session` model records login/logout events
- Login attempt tracking: `LoginAttempt` model for rate limiting/security monitoring
- Frontend: AuthContext provides authentication state across app

---

*Architecture analysis: 2026-01-18*
