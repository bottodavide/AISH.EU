# Technology Stack

**Analysis Date:** 2026-01-18

## Languages

**Primary:**
- Python 3.11+ - Backend API (FastAPI)
- TypeScript 5.3.3 - Frontend (strict mode enabled)
- JavaScript ES2022 - Next.js runtime

**Secondary:**
- SQL - PostgreSQL database queries
- Bash - Deployment and utility scripts

## Runtime

**Environment:**
- Node.js 20 (LTS) - Frontend development and production
- Python 3.11 - Backend runtime
- Docker - Monolithic containerized deployment

**Package Manager:**
- npm 9.0.0+ - Frontend dependencies
- pip - Backend Python dependencies
- Lockfile: `package-lock.json` present in `/Users/davidebotto/aistrategyhub/frontend/`
- Lockfile: `requirements.txt` in `/Users/davidebotto/aistrategyhub/backend/`

## Frameworks

**Core:**
- FastAPI 0.109.0 - Backend REST API framework with OpenAPI
- Next.js 14.1.0 - React framework with App Router
- React 18.2.0 - UI library
- SQLAlchemy 2.0.25 - Python ORM with async support

**Testing:**
- Jest 29.7.0 - JavaScript testing framework
- pytest 7.4.4 - Python testing framework
- React Testing Library 14.1.2 - Component testing
- pytest-asyncio 0.23.3 - Async Python testing

**Build/Dev:**
- Uvicorn 0.27.0 - ASGI server for FastAPI
- PostCSS 8.4.33 - CSS transformations
- Autoprefixer 10.4.17 - CSS vendor prefixes
- TailwindCSS 3.4.1 - Utility-first CSS framework
- ESLint 8.56.0 - JavaScript/TypeScript linting
- Prettier 3.2.4 - Code formatting

## Key Dependencies

**Critical:**
- Pydantic 2.5.3 - Data validation and settings management
- Zod 3.22.4 - TypeScript schema validation
- Axios 1.6.5 - HTTP client for API calls
- React Hook Form 7.49.3 - Form state management

**Infrastructure:**
- psycopg2-binary 2.9.9 - PostgreSQL adapter (sync)
- asyncpg 0.29.0 - Async PostgreSQL driver
- redis 5.0.1 - Redis client with hiredis 2.3.2 performance boost
- pgvector 0.2.4 - Vector database extension for embeddings

**AI/ML:**
- anthropic 0.12.0 - Claude API client
- openai 1.12.0 - OpenAI API (for embeddings)

**Authentication:**
- python-jose 3.3.0 - JWT token handling
- passlib 1.7.4 - Password hashing with Argon2
- pyotp 2.9.0 - TOTP for MFA
- qrcode 7.4.2 - QR code generation for MFA setup

**Payments:**
- stripe 7.11.0 - Stripe payment processing (Python)
- @stripe/stripe-js 2.4.0 - Stripe SDK (JavaScript)
- @stripe/react-stripe-js 2.4.0 - React Stripe components

**Email:**
- msal 1.26.0 - Microsoft Authentication Library for Graph API
- aiohttp 3.9.1 - Async HTTP client for MS Graph
- Jinja2 3.1.3 - Email template rendering
- premailer 3.10.0 - Inline CSS for HTML emails

**UI Components:**
- @radix-ui/* (multiple packages) - Headless accessible UI primitives
- lucide-react 0.312.0 - Icon library
- TipTap 2.27.2 - Rich text editor
- sonner 1.3.1 - Toast notifications
- next-themes 0.2.1 - Dark mode support

**State Management:**
- Zustand 4.4.7 - Lightweight state management
- @tanstack/react-query 5.17.19 - Server state management

**Data Processing:**
- date-fns 3.2.0 - Date manipulation
- lxml 5.1.0 - XML processing for Italian e-invoicing
- xmlschema 3.0.2 - XML schema validation
- reportlab 4.0.9 - PDF generation
- weasyprint 60.2 - HTML to PDF conversion

## Configuration

**Environment:**
- `.env` files for all environments (development/staging/production)
- Pydantic Settings for Python config validation
- Environment variables loaded via `python-dotenv 1.0.1`
- Frontend: `NEXT_PUBLIC_*` prefix for client-side vars
- Backend: Centralized config in `/Users/davidebotto/aistrategyhub/backend/app/core/config.py`

**Build:**
- Next.js config: `/Users/davidebotto/aistrategyhub/frontend/next.config.js`
- TypeScript config: `/Users/davidebotto/aistrategyhub/frontend/tsconfig.json`
- TailwindCSS config: `/Users/davidebotto/aistrategyhub/frontend/tailwind.config.js`
- PostCSS config: `/Users/davidebotto/aistrategyhub/frontend/postcss.config.js`
- Docker multi-stage build: `/Users/davidebotto/aistrategyhub/Dockerfile`
- Supervisord config: `/Users/davidebotto/aistrategyhub/supervisord.conf`

## Platform Requirements

**Development:**
- Node.js >= 18.17.0
- npm >= 9.0.0
- Python 3.11+
- PostgreSQL 15+ with pgvector extension
- Redis 7+
- Docker (optional for local development)

**Production:**
- Linode VPS running ArchLinux
- Docker single monolithic container containing:
  - PostgreSQL 15
  - Redis 7
  - FastAPI backend (4 uvicorn workers)
  - Next.js frontend
  - Nginx reverse proxy
  - Supervisord process manager
- Nginx with SSL/TLS (Let's Encrypt)
- 80/443 ports exposed externally

---

*Stack analysis: 2026-01-18*
