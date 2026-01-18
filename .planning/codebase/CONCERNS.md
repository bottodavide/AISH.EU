# Codebase Concerns

**Analysis Date:** 2026-01-18

## Tech Debt

**No Test Coverage:**
- Issue: Project has zero test files despite test frameworks configured in package.json (Jest) and requirements.txt (Pytest)
- Files: Entire codebase - no `*.test.ts`, `*.spec.ts`, or `test_*.py` files exist
- Impact: Changes cannot be validated automatically, high risk of regression bugs, difficult to refactor with confidence
- Fix approach: Prioritize critical path testing (auth, payments, invoice generation), add integration tests for API endpoints, implement E2E tests for checkout flow

**Excessive Console Logging in Production Code:**
- Issue: Debug console.log statements scattered throughout codebase, including sensitive data logging
- Files: `frontend/src/contexts/AuthContext.tsx` (lines 110-112, 137-140), `frontend/src/app/admin/layout.tsx` (lines 25-28, 40-41, 67-68, 71, 75), `frontend/src/components/ChatWidget.tsx`, `frontend/src/components/BannerHero.tsx`
- Impact: Performance degradation, potential information leakage in browser console, makes debugging harder with noise
- Fix approach: Replace with proper logging service, use environment-based logging (only in development), implement structured logging with log levels

**Incomplete Payment Integration:**
- Issue: Multiple TODO comments indicate Stripe payment functionality not fully implemented
- Files: `backend/app/api/routes/orders.py` (lines 809-892 - cart management and Payment Intent creation marked TODO), `frontend/src/app/dashboard/my-services/page.tsx` (line 46 - endpoint not implemented)
- Impact: Core e-commerce functionality is incomplete, users cannot complete purchases
- Fix approach: Implement Stripe Payment Intent creation endpoint, webhook handler for payment.succeeded, cart session management

**Hardcoded Placeholder Data:**
- Issue: Placeholder values hardcoded in production code
- Files: `frontend/src/app/contatti/page.tsx` (line 130-133 - phone number "XXX XXX XXXX"), `backend/app/services/invoice_pdf.py` (line 496 - BIC/SWIFT "XXXXXXXXXXX"), `backend/app/models/user.py` (line 357 - VAT format comment)
- Impact: Unprofessional appearance, potential confusion, non-functional contact information
- Fix approach: Replace with actual data from environment variables or CMS-managed content

**Incomplete Email Verification Flow:**
- Issue: Email verification not sending emails despite flow being implemented
- Files: `backend/app/api/routes/auth.py` (line 173 - "TODO: Send verification email"), `backend/app/api/routes/users.py` (line 138 - "TODO: Send email verification")
- Impact: Users cannot complete registration, accounts remain unverified
- Fix approach: Implement MS Graph email sending for verification tokens, ensure email templates exist

**Invoice SDI/PEC Integration Incomplete:**
- Issue: Electronic invoice sending to Italian Tax Authority (Sistema di Interscambio) not fully implemented
- Files: `backend/app/api/routes/invoices.py` (lines 756, 788 - "TODO: Implement real PEC sending"), `backend/app/services/invoice_xml.py` (line 499 - "TODO: Download XSD validation")
- Impact: Cannot legally send invoices to Italian customers, non-compliant with Italian e-invoicing law
- Fix approach: Implement PEC email sending via MS Graph with XML attachment, add XSD validation, implement SDI response tracking

**Admin Settings Page Placeholder:**
- Issue: Settings page marked as unimplemented
- Files: `frontend/src/components/AdminSidebar.tsx` (line 104 - "TODO: Implement settings page"), `frontend/src/app/admin/orders/page.tsx` (line 315 - alert with "TODO")
- Impact: Admin functionality incomplete, configuration management missing
- Fix approach: Create admin settings page for system configuration (company details for invoices, email templates, payment settings)

**Type Safety Violations:**
- Issue: Extensive use of `any` type defeating TypeScript's type safety
- Files: `frontend/src/lib/api-client.ts` (lines 178, 335), `frontend/src/components/RichTextEditor.tsx` (lines 137, 147), `frontend/src/contexts/AuthContext.tsx` (line 160 - `user: {} as any`)
- Impact: Runtime type errors, reduced IDE autocomplete, harder to catch bugs during development
- Fix approach: Define proper TypeScript interfaces, use generic types correctly, enable strict mode

**Missing API Error Context:**
- Issue: Error handling uses generic catch-all (err: any) without proper error type discrimination
- Files: Widespread across frontend components - 189 try/catch blocks with minimal error context
- Impact: Difficult to debug API failures, poor user error messages, no error tracking/monitoring
- Fix approach: Create typed error classes, implement error boundary, add Sentry or similar error tracking

**Duplicate python-multipart Dependency:**
- Issue: Package listed twice in requirements.txt
- Files: `backend/requirements.txt` (lines 39 and 94)
- Impact: Potential version conflict, confusion during dependency resolution
- Fix approach: Remove duplicate entry, ensure single version specification

## Known Bugs

**MFA Token Handling Vulnerability:**
- Symptoms: MFA session token returned in login response could be exploited
- Files: `frontend/src/contexts/AuthContext.tsx` (lines 154-162), `backend/app/api/routes/auth.py`
- Trigger: Login with MFA enabled returns mfa_session_token that might be reused
- Workaround: Implement short-lived session tokens (5 minutes max), one-time use tokens

**LocalStorage Race Condition:**
- Symptoms: User data cached in localStorage may become stale or corrupt
- Files: `frontend/src/contexts/AuthContext.tsx` (lines 225-234 - cached user parse error caught but not handled), `frontend/src/lib/api-client.ts` (lines 54-56, 80-82, 158-161)
- Trigger: Rapid page navigation or concurrent tabs accessing auth state
- Workaround: Use session storage instead, implement proper cache invalidation strategy

**Admin Route Protection Excessive Logging:**
- Symptoms: Every admin page render logs multiple console messages
- Files: `frontend/src/app/admin/layout.tsx` (lines 24-75 - 11 console.log statements in render path)
- Trigger: Any admin page navigation
- Workaround: Remove debug logs or wrap in development-only conditional

**Newsletter Endpoint Direct Token Access:**
- Symptoms: Newsletter page directly accesses localStorage for auth token instead of using apiClient
- Files: `frontend/src/app/admin/newsletter/page.tsx` (line 158)
- Trigger: Newsletter CSV export
- Workaround: Refactor to use apiClient.get() which handles tokens properly

## Security Considerations

**Sensitive Data in Browser Console:**
- Risk: User credentials, roles, and authentication state logged to browser console
- Files: `frontend/src/contexts/AuthContext.tsx` (lines 110-112 log user role), `frontend/src/app/admin/layout.tsx` (logs user object)
- Current mitigation: None - logs always active
- Recommendations: Remove all console.log statements with sensitive data, use proper logging library with environment guards

**JWT Tokens in LocalStorage:**
- Risk: XSS vulnerability - stolen tokens can be used to impersonate users
- Files: `frontend/src/lib/api-client.ts` (lines 136-138, 148-152), `frontend/src/contexts/AuthContext.tsx` (lines 117-119, 147-149)
- Current mitigation: Token refresh mechanism exists (lines 84-106 in api-client.ts)
- Recommendations: Consider httpOnly cookies for tokens, implement CSRF protection, add token binding to browser fingerprint, shorter access token lifetime (currently no expiry visible)

**No Rate Limiting Visible:**
- Risk: API endpoints vulnerable to brute force attacks, DDoS
- Files: No rate limiting implementation found in backend routes or middleware
- Current mitigation: None detected
- Recommendations: Implement rate limiting middleware in FastAPI (slowapi), add IP-based throttling, implement exponential backoff for failed auth attempts

**CORS Configuration Unknown:**
- Risk: Potential CORS misconfiguration allowing unauthorized origins
- Files: `backend/app/main.py` (line 117 - "TODO: Add other middleware")
- Current mitigation: Unknown - CORS config not in reviewed files
- Recommendations: Explicitly configure allowed origins, avoid wildcards in production, enable credentials properly

**Password Storage Security:**
- Risk: Dependency on Argon2 but implementation not verified
- Files: `backend/requirements.txt` (line 38 - passlib[argon2]), `backend/app/core/security.py` (not reviewed but should contain hashing)
- Current mitigation: Using industry-standard Argon2 library
- Recommendations: Verify Argon2 parameters (memory, iterations, parallelism), ensure salt generation is cryptographically secure

**File Upload Validation Gaps:**
- Risk: Potential malicious file uploads
- Files: `backend/app/api/routes/files.py` (625 lines - large file handling), `frontend/src/components/ImageUpload.tsx` (line 176), `frontend/src/components/RichTextEditor.tsx` (line 137)
- Current mitigation: python-magic library for file type detection (requirements.txt line 90)
- Recommendations: Implement file size limits, validate file extensions server-side, scan for malware, store uploads outside web root, generate random filenames

**MFA Setup Password Confirmation:**
- Risk: MFA setup requires password confirmation but doesn't verify password strength
- Files: `frontend/src/app/setup-mfa/page.tsx` (lines 66-86 - password sent in plain text to API)
- Current mitigation: HTTPS transport encryption assumed
- Recommendations: Verify password meets complexity requirements before MFA setup, implement account activity notification when MFA is enabled

## Performance Bottlenecks

**Large Admin Components:**
- Problem: Several admin pages exceed 600+ lines making them hard to maintain and slow to render
- Files: `frontend/src/app/dashboard/profile/page.tsx` (722 lines), `frontend/src/app/admin/banners/[id]/edit/page.tsx` (645 lines), `frontend/src/app/admin/settings/page.tsx` (642 lines)
- Cause: Monolithic components with inline form logic, state management, and API calls
- Improvement path: Split into smaller components, extract custom hooks for form logic, use react-hook-form more effectively, implement lazy loading for admin sections

**Large Backend Route Files:**
- Problem: API route files are becoming unwieldy
- Files: `backend/app/api/routes/cms.py` (1,597 lines), `backend/app/api/routes/orders.py` (1,212 lines), `backend/app/api/routes/auth.py` (1,060 lines)
- Cause: Too much logic in route handlers, business logic not extracted to services
- Improvement path: Extract business logic to service layer, split route files by resource sub-types, implement repository pattern for data access

**No Caching Strategy Visible:**
- Problem: No evidence of caching for frequently accessed data
- Files: No Redis cache usage detected in API routes, static data fetched on every request
- Cause: Missing cache layer implementation
- Improvement path: Implement Redis caching for CMS content, blog posts, service listings; add HTTP cache headers; implement query result caching in SQLAlchemy

**N+1 Query Risk:**
- Problem: SQLAlchemy relationships may cause N+1 queries
- Files: `backend/app/models/order.py` (695 lines with multiple relationships), `backend/app/models/user.py` (683 lines), service loading likely triggers multiple queries
- Cause: Lazy loading relationships by default, no eager loading strategy
- Improvement path: Use joinedload/selectinload for known access patterns, implement query counters in development, add database query monitoring

**Large Dependency Bundle:**
- Problem: Frontend includes many heavy dependencies
- Files: `frontend/package.json` - 44 runtime dependencies including TipTap (4 packages), Radix UI (17 packages), Tanstack Query, multiple form libraries
- Cause: Rich feature set requires many UI components
- Improvement path: Code splitting by route, lazy load admin components, evaluate if all Radix components are used, consider dynamic imports for TipTap editor

## Fragile Areas

**Authentication Context State Management:**
- Files: `frontend/src/contexts/AuthContext.tsx` (328 lines)
- Why fragile: Multiple sources of truth (localStorage, memory state, API), race conditions possible during token refresh, silent error catching on cached user parse
- Safe modification: Always use the provided useAuth hook, never directly access localStorage, test token refresh scenarios, implement proper error boundaries
- Test coverage: None - critical auth logic untested

**File Upload and Storage:**
- Files: `backend/app/services/file_storage.py` (493 lines), `backend/app/api/routes/files.py` (625 lines)
- Why fragile: Complex file handling logic, path traversal risks, large file size, multiple upload vectors (ImageUpload, RichTextEditor)
- Safe modification: Always validate file paths server-side, use whitelist for file extensions, never trust client-provided filenames, implement comprehensive logging
- Test coverage: None - file upload vulnerabilities untested

**Order and Payment Flow:**
- Files: `backend/app/api/routes/orders.py` (1,212 lines), `backend/app/models/order.py` (695 lines)
- Why fragile: State machine for order status not fully implemented, payment webhook handling incomplete, potential race conditions in order creation
- Safe modification: Use database transactions for order creation, implement idempotency keys for payment webhooks, test concurrent order scenarios
- Test coverage: None - critical payment flow untested

**Invoice Generation XML:**
- Files: `backend/app/services/invoice_xml.py` (559 lines), `backend/app/services/invoice_pdf.py` (571 lines)
- Why fragile: Complex Italian e-invoicing XML format, legal compliance requirements, XSD validation pending
- Safe modification: Never modify XML structure without consulting FatturaPA 1.2.1 specs, validate against XSD before deployment, test with real SDI sandbox
- Test coverage: None - legal compliance requirements untested

**Admin Layout Access Control:**
- Files: `frontend/src/app/admin/layout.tsx` (86 lines)
- Why fragile: Multiple render conditions, synchronous role checking, redirect logic in useEffect, excessive logging
- Safe modification: Simplify conditional logic, use route middleware instead of layout checks, implement proper loading states, remove debug logs
- Test coverage: None - access control logic untested

**Database Migrations:**
- Files: `backend/migrations/versions/*.py` - multiple migration files with pgvector commented out
- Why fragile: pgvector extension commented out in migrations (lines marked "TODO: Uncomment when pgvector is installed"), manual intervention required
- Safe modification: Test migrations on staging database first, backup before running, verify pgvector is installed before uncommenting, run migrations in transaction
- Test coverage: Migration rollback scenarios untested

## Scaling Limits

**Single Container Monolith:**
- Current capacity: All services (Frontend, Backend, PostgreSQL, Redis, Nginx) in single Docker container
- Limit: Cannot scale horizontally, single point of failure, resource contention between services
- Scaling path: Separate into microservices (Frontend, Backend, Database separate containers), implement load balancer, use managed database service (e.g., Linode Managed PostgreSQL), add container orchestration (Kubernetes or Docker Swarm)

**File Storage on Local Filesystem:**
- Current capacity: Files stored in local filesystem within container
- Limit: No shared storage for multi-instance deployment, lost on container restart without volume, difficult backup strategy
- Scaling path: Migrate to object storage (S3, Backblaze B2, Linode Object Storage), implement CDN for static assets, use managed service for uploads

**PostgreSQL in Docker Container:**
- Current capacity: Single PostgreSQL instance inside application container
- Limit: Cannot scale read queries, backup complexity, no high availability, limited to single server resources
- Scaling path: Move to managed PostgreSQL service, implement read replicas, add connection pooling (PgBouncer), use pg_stat_statements for query optimization

**Session Storage in Redis:**
- Current capacity: Redis sessions in same container
- Limit: Sessions lost on container restart, no persistence configured, single point of failure
- Scaling path: Use Redis Cluster or managed Redis, enable AOF persistence, implement session store fallback, consider JWT-only approach with shorter lifetimes

**Background Task Processing:**
- Current capacity: No worker implementation detected
- Limit: Long-running tasks (email sending, invoice generation, RAG processing) will block API requests
- Scaling path: Implement Celery workers as per requirements.txt (line 84), use separate worker containers, implement job queue with retries, add task monitoring

## Dependencies at Risk

**TipTap Version Pinning:**
- Risk: Multiple TipTap packages at 2.27.2, not using latest features/fixes
- Impact: Missing security patches, potential compatibility issues
- Migration plan: Upgrade to latest stable TipTap v2.x, test rich text editor thoroughly, update extensions simultaneously

**Next.js 14 App Router:**
- Risk: Using Next.js 14.1.0 while App Router patterns still evolving
- Impact: Breaking changes possible in minor versions, documentation may change
- Migration plan: Stay on 14.x until 15.x stable, monitor Next.js changelog, prepare for React Server Components evolution

**FastAPI 0.109.0:**
- Risk: FastAPI evolving quickly, Pydantic v2 breaking changes
- Impact: Dependency conflicts, migration effort required for major versions
- Migration plan: Pin minor version until testing infrastructure exists, upgrade with comprehensive API testing

**Anthropic Claude API:**
- Risk: Claude API client at 0.12.0, API may deprecate endpoints
- Impact: Chatbot breaks if API changes, token limits may change
- Migration plan: Monitor Anthropic changelog, implement API version pinning, add fallback responses, test with latest SDK regularly

**Stripe SDK 7.11.0:**
- Risk: Payment provider SDK critical for revenue
- Impact: Payment processing breaks if API deprecated
- Migration plan: Subscribe to Stripe API changelog, implement webhook version handling, test in Stripe test mode before upgrading

## Missing Critical Features

**AI Chatbot RAG System:**
- Problem: Core differentiating feature not implemented
- Blocks: Cannot demonstrate AI capabilities, value proposition incomplete
- Priority: High - marked as "CORE FEATURE" and "PRIORITY MASSIMA" in TODO.md
- Files: `backend/app/workers/` (empty), `backend/app/api/routes/knowledge_base.py` (841 lines but RAG pipeline incomplete)

**Stripe Webhook Handler:**
- Problem: Payment completion cannot be verified automatically
- Blocks: Orders stuck in pending, invoices not generated, payment flow incomplete
- Priority: Critical - marked as "CRITICAL" in TODO.md
- Files: `backend/app/api/routes/orders.py` (line 887 - webhook handler marked TODO)

**Background Task Worker:**
- Problem: No async task processing for emails, invoices, long operations
- Blocks: Email sending, invoice generation, RAG processing will block API requests
- Priority: High - required before production deployment
- Files: `backend/app/workers/` directory exists but contains no implementation

**Error Tracking and Monitoring:**
- Problem: No error tracking service integrated (Sentry mentioned but not implemented)
- Blocks: Cannot diagnose production issues, no visibility into user-facing errors
- Priority: Medium - needed before production but workaround possible
- Files: No Sentry configuration found, requirements.txt line 111 has commented Sentry

**CI/CD Pipeline:**
- Problem: No GitHub Actions workflow exists
- Blocks: Manual deployment, no automated testing, no code quality gates
- Priority: Medium - manual deployment possible but error-prone
- Files: No `.github/workflows/` directory found

## Test Coverage Gaps

**Authentication Flow:**
- What's not tested: Registration, email verification, MFA setup/verification, password reset, JWT token refresh
- Files: `frontend/src/contexts/AuthContext.tsx`, `backend/app/api/routes/auth.py` (1,060 lines)
- Risk: Breaking changes go unnoticed, security vulnerabilities, session handling bugs
- Priority: Critical - security-sensitive code

**Payment and Order Processing:**
- What's not tested: Order creation, Stripe payment flow, webhook handling, order state transitions
- Files: `backend/app/api/routes/orders.py` (1,212 lines), payment integration incomplete
- Risk: Revenue loss from broken checkout, incorrect order status, payment fraud
- Priority: Critical - directly affects revenue

**Invoice Generation:**
- What's not tested: XML FatturaPA format, PDF generation, legal compliance, number sequencing
- Files: `backend/app/services/invoice_xml.py` (559 lines), `backend/app/services/invoice_pdf.py` (571 lines)
- Risk: Legal non-compliance, rejected invoices by SDI, tax authority penalties
- Priority: High - regulatory requirement for Italian market

**Admin CRUD Operations:**
- What's not tested: Service creation/editing, blog post management, user management, role assignment
- Files: Multiple admin pages totaling 2,773 lines, `backend/app/api/routes/cms.py` (1,597 lines)
- Risk: Data corruption, unauthorized access, broken admin workflows
- Priority: Medium - admin users can work around issues

**File Upload Security:**
- What's not tested: Malicious file detection, path traversal, file size limits, type validation
- Files: `backend/app/api/routes/files.py` (625 lines), `backend/app/services/file_storage.py` (493 lines)
- Risk: Server compromise, storage exhaustion, malware distribution
- Priority: High - attack vector for malicious actors

**Database Migrations:**
- What's not tested: Migration rollback, data integrity, constraint validation, pgvector setup
- Files: `backend/migrations/versions/*.py` - multiple migrations with commented pgvector code
- Risk: Data loss during migration, broken application after schema change
- Priority: Medium - test on staging first but automated tests missing

---

*Concerns audit: 2026-01-18*
