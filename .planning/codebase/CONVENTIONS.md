# Coding Conventions

**Analysis Date:** 2026-01-18

## Naming Patterns

**Files:**
- TypeScript/React: `PascalCase.tsx` for components (e.g., `AuthContext.tsx`, `RichTextEditor.tsx`)
- TypeScript utilities: `kebab-case.ts` for non-component files (e.g., `api-client.ts`, `error-handler.ts`)
- Python modules: `snake_case.py` (e.g., `security.py`, `logging_config.py`)
- Next.js pages: `page.tsx` in directory structure (e.g., `app/admin/settings/page.tsx`)

**Functions:**
- TypeScript: `camelCase` (e.g., `getErrorMessage`, `formatCurrency`, `isAuthenticated`)
- Python: `snake_case` (e.g., `hash_password`, `verify_mfa_token`, `generate_api_key`)

**Variables:**
- TypeScript: `camelCase` (e.g., `isLoading`, `accessToken`, `userId`)
- Python: `snake_case` (e.g., `password_hash`, `mfa_enabled`, `refresh_token`)

**Types/Interfaces:**
- TypeScript: `PascalCase` (e.g., `User`, `LoginCredentials`, `ApiError`, `UserRole`)
- Python classes: `PascalCase` (e.g., `User`, `UserProfile`, `Session`)
- Python enums: `PascalCase` class with `SCREAMING_SNAKE_CASE` values (e.g., `UserRole.SUPER_ADMIN`)

**Constants:**
- TypeScript: `SCREAMING_SNAKE_CASE` for true constants (rarely used)
- Python: `SCREAMING_SNAKE_CASE` at module level (not prevalent in this codebase)

## Code Style

**Formatting:**
- Frontend: Prettier with config at `frontend/.prettierrc`
  - Semi-colons: required (`;`)
  - Quotes: single quotes (`'`)
  - Trailing commas: `es5`
  - Print width: 100 characters
  - Tab width: 2 spaces
  - Plugin: `prettier-plugin-tailwindcss` for class ordering
- Backend: Black (specified in `backend/requirements.txt`)
  - Line length: 88 characters (Black default)
  - Python version target: 3.11+

**Linting:**
- Frontend: ESLint with config at `frontend/.eslintrc.json`
  - Extends: `next/core-web-vitals`, `prettier`
  - Disabled rules: `@next/next/no-html-link-for-pages`, `react/no-unescaped-entities`
- Backend: Flake8, mypy, isort (specified in requirements.txt)
  - Type checking with mypy enabled
  - Import sorting with isort

## Import Organization

**TypeScript Order:**
1. External libraries (React, Next.js, third-party packages)
2. Internal components from `@/components`
3. Internal utilities from `@/lib`
4. Internal contexts from `@/contexts`
5. Relative imports

**Example from `frontend/src/app/admin/settings/page.tsx`:**
```typescript
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/contexts/AuthContext';
```

**Python Order (PEP 8):**
1. Standard library imports
2. Third-party library imports
3. Local application imports (grouped by: core, models, schemas, services, api)

**Example from `backend/app/api/routes/auth.py`:**
```python
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_async_db
from app.core.dependencies import get_current_user
```

**Path Aliases:**
- TypeScript: `@/*` maps to `src/*` (configured in `frontend/tsconfig.json`)
  - `@/components/*` for components
  - `@/lib/*` for utilities
  - `@/app/*` for pages
  - `@/styles/*` for styles

## Error Handling

**TypeScript Patterns:**
- Use try-catch blocks for async operations
- Translate technical errors to user-friendly Italian messages
- Log errors to console in development mode only
- Use axios interceptors for global HTTP error handling

**Example from `frontend/src/lib/api-client.ts`:**
```typescript
try {
  const response = await apiClient.post<LoginResponse>('/auth/login', credentials);
  apiClient.setTokens(response.access_token, response.refresh_token);
  setUser(response.user);
  return response;
} catch (error: any) {
  if (error?.response?.status === 403 && error?.response?.data?.details?.mfa_required) {
    // Handle MFA required case
    return mfaResponse;
  }
  throw new Error(getErrorMessage(error));
}
```

**Python Patterns:**
- Use try-except blocks with specific exception types
- Log all errors with appropriate level (debug, info, warning, error, critical)
- Include `exc_info=True` for stack traces on errors
- Return appropriate HTTP status codes via FastAPI HTTPException

**Example from `backend/app/core/security.py`:**
```python
try:
    is_valid = pwd_context.verify(plain_password, hashed_password)
    if is_valid:
        logger.debug("Password verification: SUCCESS")
    else:
        logger.debug("Password verification: FAILED")
    return is_valid
except Exception as e:
    logger.error(f"Password verification error: {str(e)}", exc_info=True)
    return False
```

## Logging

**Frontend:**
- Use `console.log`, `console.error`, `console.warn`
- Wrap in `if (process.env.NODE_ENV === 'development')` checks for verbose logs
- Always log API errors in api-client interceptors

**Example from `frontend/src/lib/api-client.ts`:**
```typescript
if (process.env.NODE_ENV === 'development') {
  console.error('API Error:', {
    url: error.config?.url,
    method: error.config?.method,
    status: error.response?.status,
    data: error.response?.data,
  });
}
```

**Backend:**
- Use Python logging module with logger per module
- Initialize logger: `logger = logging.getLogger(__name__)`
- Log levels: debug for detailed info, info for operations, warning for unexpected behavior, error for failures
- Include context in log messages (user IDs, operation details)

**Example from `backend/app/core/security.py`:**
```python
logger = logging.getLogger(__name__)

logger.debug("Hashing password")
hashed = pwd_context.hash(password)
logger.debug("Password hashed successfully")

logger.info(f"Access token created for {subject}, expires at {expire}")

logger.warning(f"JWT decode error: {str(e)}")

logger.error(f"Unexpected error decoding token: {str(e)}", exc_info=True)
```

## Comments

**When to Comment:**
- File headers: ALWAYS include module description, author, date
- Complex business logic: explain the "why", not the "what"
- Security-sensitive code: document security considerations
- Public APIs: document parameters, returns, examples

**TypeScript Example from `frontend/src/lib/api-client.ts`:**
```typescript
/**
 * API Client
 * Descrizione: Client HTTP per comunicare con backend FastAPI
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

/**
 * Imposta access e refresh tokens
 */
setTokens(accessToken: string, refreshToken: string): void {
  this.accessToken = accessToken;
  this.refreshToken = refreshToken;

  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  }
}
```

**Python Example from `backend/app/models/user.py`:**
```python
"""
Modulo: user.py
Descrizione: Modelli SQLAlchemy per utenti, autenticazione e sessioni
Autore: Claude per Davide
Data: 2026-01-15

Modelli inclusi:
- User: Utente principale con credenziali e MFA
- UserProfile: Dati anagrafici e fatturazione
- Session: Sessioni JWT (access + refresh tokens)
- LoginAttempt: Log tentativi login per security

Note sulla sicurezza:
- Password hashate con Argon2 (mai in chiaro)
- MFA (TOTP) con backup codes
- Email verification obbligatoria
- Tracking login attempts per prevenire brute force
"""

def hash_password(password: str) -> str:
    """
    Crea hash di una password usando Argon2.

    Args:
        password: Password in chiaro

    Returns:
        str: Hash della password

    Example:
        >>> hashed = hash_password("MySecurePass123!")
        >>> print(hashed)
        $argon2id$v=19$m=65536,t=3,p=4$...
    """
    logger.debug("Hashing password")
    hashed = pwd_context.hash(password)
    logger.debug("Password hashed successfully")
    return hashed
```

**JSDoc/TSDoc:**
- Use for exported functions and public APIs
- Include `@param`, `@returns`, `@example` tags
- Not heavily used in this codebase; inline comments preferred

## Function Design

**Size:**
- Keep functions focused on single responsibility
- Extract complex logic into helper functions
- Functions typically 20-50 lines; split if longer

**Parameters:**
- TypeScript: Use destructuring for objects with multiple properties
- Python: Use type hints for all parameters
- Default values specified in function signature

**TypeScript Example:**
```typescript
async uploadFile<T>(
  url: string,
  file: File,
  additionalData?: Record<string, any>,
  onProgress?: (progress: number) => void
): Promise<T>
```

**Python Example:**
```python
def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict[str, Any]] = None,
) -> str:
```

**Return Values:**
- Always specify return types
- TypeScript: Use `Promise<T>` for async functions
- Python: Use `->` syntax with type hints
- Return early for error cases (guard clauses)

## Module Design

**Exports:**
- TypeScript: Use named exports for utilities, default export for React components
- Python: All public functions/classes at module level

**TypeScript Example from `frontend/src/lib/api-client.ts`:**
```typescript
// Singleton instance
const apiClient = new ApiClient();

export default apiClient;
export { apiClient }; // Named export for convenience

// Helper functions
export function getErrorMessage(error: unknown): string { ... }
export function isNotFoundError(error: unknown): boolean { ... }
```

**Barrel Files:**
- Not heavily used; prefer direct imports
- Python uses `__init__.py` for package initialization

## TypeScript Configuration

**Strict Mode:**
- Enabled in `frontend/tsconfig.json`
- `strict: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`
- `noFallthroughCasesInSwitch: true`
- `noImplicitReturns: true`
- `noUncheckedIndexedAccess: true`

**Target:**
- ES2022
- JSX: preserve (for Next.js)
- Module: ESNext with bundler resolution

## Python Configuration

**Version:**
- Python 3.11+ required
- Uses modern type hints (`dict[str, Any]` instead of `Dict[str, Any]`)

**Type Hints:**
- ALWAYS use type hints for function signatures
- Use `Optional[T]` for nullable values
- Use `Union` or `|` for multiple types
- SQLAlchemy models use Column types

**Example from `backend/app/models/user.py`:**
```python
email = Column(
    String(255),
    unique=True,
    nullable=False,
    index=True,
    comment="Email univoca per login",
)
```

---

*Convention analysis: 2026-01-18*
