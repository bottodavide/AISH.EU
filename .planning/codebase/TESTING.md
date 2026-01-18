# Testing Patterns

**Analysis Date:** 2026-01-18

## Test Framework

**Frontend:**
- Runner: Jest 29.7.0
- Config: `frontend/package.json` (config not yet created as separate file)
- Assertion Library: `@testing-library/jest-dom` 6.2.0
- React Testing: `@testing-library/react` 14.1.2
- User Events: `@testing-library/user-event` 14.5.2
- Environment: `jest-environment-jsdom` 29.7.0

**Backend:**
- Runner: pytest 7.4.4
- Async support: pytest-asyncio 0.23.3
- Coverage: pytest-cov 4.1.0
- HTTP Testing: httpx 0.26.0 (for FastAPI TestClient)
- Fake Data: faker 22.2.0

**Run Commands:**

Frontend:
```bash
npm run test              # Run all tests
npm run test:watch        # Watch mode
npm run test:coverage     # Coverage report
```

Backend:
```bash
pytest                    # Run all tests
pytest --cov=app          # With coverage
pytest -v                 # Verbose output
pytest -k test_login      # Run specific test
```

## Test File Organization

**Location:**
- Frontend: No formal test files detected yet (testing infrastructure configured but tests not written)
- Backend: Test files in root `backend/` directory alongside code
  - Ad-hoc test scripts: `test_login.py`, `test_email_service.py`, `test_files_api.py`, `test_invoices_api.py`

**Naming:**
- Frontend pattern (expected): `ComponentName.test.tsx` or `ComponentName.spec.tsx`
- Backend pattern (current): `test_*.py` for pytest discovery

**Structure:**

Frontend (expected pattern based on dependencies):
```
frontend/src/
├── components/
│   ├── Hero.tsx
│   └── Hero.test.tsx
├── lib/
│   ├── api-client.ts
│   └── api-client.test.ts
```

Backend (current pattern):
```
backend/
├── app/
│   ├── api/
│   ├── models/
│   └── services/
├── test_login.py
├── test_email_service.py
└── test_files_api.py
```

## Test Structure

**Frontend Suite Organization (expected based on testing-library):**

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComponentName } from './ComponentName';

describe('ComponentName', () => {
  beforeEach(() => {
    // Setup before each test
  });

  afterEach(() => {
    // Cleanup after each test
  });

  it('should render correctly', () => {
    render(<ComponentName />);
    expect(screen.getByText('Expected text')).toBeInTheDocument();
  });

  it('should handle user interaction', async () => {
    const user = userEvent.setup();
    render(<ComponentName />);

    await user.click(screen.getByRole('button'));

    await waitFor(() => {
      expect(screen.getByText('Result')).toBeInTheDocument();
    });
  });
});
```

**Backend Patterns:**

Example from `backend/test_login.py`:
```python
import asyncio
from app.core.security import verify_password
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserProfile

async def test_login():
    email = "admin@aistrategyhub.eu"
    password = "Test123!"

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print("User not found")
            return

        # Verify password
        if not verify_password(password, user.password_hash):
            print("Password incorrect")
            return

        print("Login successful!")
        print(f"\nUser data that should be returned:")
        print(f"  email: {user.email}")
        print(f"  role: {user.role.value}")

asyncio.run(test_login())
```

**Patterns:**
- Backend: Direct async function calls with `asyncio.run()`
- Database: Use `AsyncSessionLocal` for async database access
- Assertions: Manual `print` statements for debugging (not using pytest assertions yet)

## Mocking

**Framework:**
- Frontend: Jest built-in mocking capabilities
- Backend: No mocking framework imported yet (pytest-mock would be standard)

**Patterns (expected based on dependencies):**

Frontend API mocking:
```typescript
import apiClient from '@/lib/api-client';

jest.mock('@/lib/api-client');

describe('Component with API', () => {
  it('should fetch data', async () => {
    (apiClient.get as jest.Mock).mockResolvedValue({ data: 'test' });

    // Test component
  });
});
```

**What to Mock:**
- External API calls (axios/httpx)
- Database queries in unit tests
- Email services (Microsoft Graph API)
- Payment processing (Stripe)
- File system operations

**What NOT to Mock:**
- Pure utility functions
- Internal business logic
- Simple data transformations

## Fixtures and Factories

**Test Data:**

Backend pattern (from `test_login.py`):
```python
# Hardcoded test credentials
email = "admin@aistrategyhub.eu"
password = "Test123!"
```

**Expected patterns with faker:**
```python
from faker import Faker

fake = Faker()

def create_test_user():
    return {
        "email": fake.email(),
        "password": "TestPass123!",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
```

**Location:**
- Backend: Test fixtures would typically go in `backend/tests/conftest.py` (pytest convention)
- Frontend: Test utilities in `__tests__/utils.ts` or similar

## Coverage

**Requirements:**
- No specific coverage target enforced yet
- Coverage tools configured but not actively measured

**View Coverage:**

Frontend:
```bash
npm run test:coverage
# Opens HTML report in browser
```

Backend:
```bash
pytest --cov=app --cov-report=html
# Opens htmlcov/index.html
```

**Current State:**
- Test infrastructure present but comprehensive test suites not yet written
- Focus appears to be on manual/integration testing during development

## Test Types

**Unit Tests:**
- Scope: Individual functions, methods, components
- Current state: Limited unit tests; mostly ad-hoc test scripts
- Approach: Direct function calls with print-based verification

**Integration Tests:**
- Scope: API endpoints, database operations, service interactions
- Current state: Manual integration test scripts (e.g., `test_login.py`, `test_email_service.py`)
- Approach: Full stack testing with real database connections

**E2E Tests:**
- Framework: Not configured
- No Playwright, Cypress, or similar E2E tools detected
- Manual testing via browser likely current approach

## Common Patterns

**Async Testing:**

Backend (current pattern):
```python
async def test_function():
    async with AsyncSessionLocal() as db:
        # Database operations
        result = await db.execute(query)
        # Assertions
        assert result is not None

# Run with asyncio
asyncio.run(test_function())
```

Frontend (expected pattern with testing-library):
```typescript
it('should handle async operation', async () => {
  render(<AsyncComponent />);

  await waitFor(() => {
    expect(screen.getByText('Loaded')).toBeInTheDocument();
  });
});
```

**Error Testing:**

Backend pattern (expected):
```python
def test_invalid_password():
    with pytest.raises(HTTPException) as exc_info:
        # Code that should raise
        authenticate_user(email, wrong_password)

    assert exc_info.value.status_code == 401
```

Frontend pattern (expected):
```typescript
it('should display error message', async () => {
  apiClient.post.mockRejectedValue(new Error('Network error'));

  render(<LoginForm />);

  await userEvent.click(screen.getByRole('button', { name: 'Login' }));

  expect(await screen.findByText(/errore/i)).toBeInTheDocument();
});
```

**Database Testing:**

Current pattern from `test_login.py`:
```python
async with AsyncSessionLocal() as db:
    # Query database
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    # Verify result
    if not user:
        print("User not found")
        return

    # Test security functions
    if not verify_password(password, user.password_hash):
        print("Password incorrect")
        return
```

Expected pattern with pytest fixtures:
```python
@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_user_login(db_session):
    user = await create_test_user(db_session)

    result = await authenticate_user(user.email, "password")

    assert result.email == user.email
    assert result.is_authenticated
```

## Authentication Testing

**Pattern for JWT:**

Backend:
```python
from app.core.security import create_access_token

def test_with_auth():
    token = create_access_token(subject=str(user_id))
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/users/me", headers=headers)
    assert response.status_code == 200
```

Frontend:
```typescript
beforeEach(() => {
  // Mock authenticated state
  localStorage.setItem('access_token', 'fake-token');
});

afterEach(() => {
  localStorage.clear();
});
```

## Test Data Management

**Current Approach:**
- Hardcoded test credentials for manual testing
- Direct database queries without cleanup
- No database reset between tests

**Recommended Approach:**
- Use pytest fixtures for database transactions
- Rollback after each test
- Use Faker for generating realistic test data
- Separate test database from development database

## API Testing

**Backend Pattern (with httpx):**

```python
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_api_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password"
        })

        assert response.status_code == 200
        assert "access_token" in response.json()
```

**Frontend Pattern (mocking axios):**

```typescript
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

it('should login successfully', async () => {
  mockedAxios.post.mockResolvedValue({
    data: {
      access_token: 'token',
      user: { email: 'test@example.com' }
    }
  });

  // Test login flow
});
```

## Current Testing Gaps

**Missing Test Suites:**
- No React component tests written
- No comprehensive API endpoint tests
- No security/authentication flow tests
- No validation schema tests

**Testing Infrastructure Present:**
- Jest configured for frontend
- pytest configured for backend
- Testing libraries installed
- Manual test scripts demonstrate testing approach

**Next Steps:**
- Write unit tests for utility functions (`frontend/src/lib/utils.ts`)
- Write integration tests for API endpoints (`backend/app/api/routes/`)
- Write component tests for critical UI components
- Set up CI/CD pipeline to run tests automatically
- Establish coverage targets (recommend 80%+ for critical paths)

---

*Testing analysis: 2026-01-18*
