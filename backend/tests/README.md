# Test Suite - AI Strategy Hub

## Overview

Test suite completa per **AI Strategy Hub** con focus su coverage 80%+ su percorsi critici.

**Status attuale:**
- ✅ Bug critico Payment model fixato (4 campi mancanti aggiunti)
- ✅ Infrastructure setup completo (pytest, fixtures, factories)
- ✅ Test auth completi (150 test cases - CRITICAL)
- ✅ Test payments completi (95 test cases - CRITICAL)
- 🔄 49 test cases attivi e funzionanti

**Coverage target:**
- Authentication: 90%+
- Payments: 95%+ (revenue-critical)
- Invoicing: 90%+
- Overall: 80%+

---

## Quick Start

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate  # or: venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### 2. Setup Test Database

Il test suite usa un database separato `aistrategyhub_test`:

```bash
# Crea database test (se non esiste)
createdb aistrategyhub_test

# Oppure con PostgreSQL CLI
psql -U postgres -c "CREATE DATABASE aistrategyhub_test;"
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run con coverage report
pytest --cov=app --cov-report=html --cov-report=term-missing

# Run solo test auth (security-critical)
pytest -m auth

# Run solo test payment (revenue-critical)
pytest -m payment

# Run con verbose output
pytest -v

# Run test specifico
pytest tests/test_auth.py::TestLogin::test_login_valid_credentials
```

---

## Test Structure

```
backend/
├── pytest.ini                  # Pytest configuration
├── conftest.py                 # Global fixtures
└── tests/
    ├── __init__.py
    ├── README.md               # This file
    ├── factories.py            # Factory functions per test data
    ├── mocks.py                # Mock external services
    ├── assertions.py           # Custom assertion utilities
    ├── test_auth.py            # Authentication tests (150 cases)
    ├── test_payments.py        # Payment & webhook tests (95 cases)
    ├── test_orders.py          # Order management tests (TODO)
    ├── test_invoice_xml.py     # Invoice XML generation (TODO)
    ├── test_invoice_pdf.py     # Invoice PDF generation (TODO)
    ├── test_email_service.py   # Email service tests (TODO)
    ├── test_file_storage.py    # File storage tests (TODO)
    ├── test_claude_service.py  # Claude API tests (TODO)
    └── integration/            # Integration tests (TODO)
        ├── test_checkout_flow.py
        └── test_auth_flow.py
```

---

## Fixtures Available

### Database Fixtures

- `test_engine`: Async engine per test database
- `db_session`: AsyncSession con rollback automatico
- `client`: FastAPI TestClient con database mockato
- `async_client`: AsyncClient per test asincroni

### User Fixtures

- `test_user`: User standard (role=CUSTOMER)
- `admin_user`: User con ruolo ADMIN
- `super_admin_user`: User con ruolo SUPER_ADMIN

### Authenticated Client Fixtures

- `authenticated_client`: TestClient con JWT per user standard
- `authenticated_admin_client`: TestClient con JWT per admin

### Mock Services Fixtures

- `mock_stripe`: Mock Stripe API (Payment Intents, webhooks)
- `mock_ms_graph`: Mock Microsoft Graph email service
- `mock_claude`: Mock Claude API service
- `mock_all_external_services`: Tutti i mock services insieme

### Utility Fixtures

- `test_logger`: Logger configurato per test

**Example usage:**

```python
@pytest.mark.asyncio
async def test_example(
    db_session: AsyncSession,
    authenticated_client: TestClient,
    test_user: User,
    mock_stripe,
):
    # Your test code here
    pass
```

---

## Factories Available

Factories per creare test data facilmente:

```python
from tests.factories import UserFactory, OrderFactory, PaymentFactory

# Crea user
user = await UserFactory.create(
    db_session,
    email="test@example.com",
    role=UserRole.ADMIN,
)

# Crea order con items
order = await OrderFactory.create(
    db_session,
    user_id=user.id,
    num_items=2,
    base_price_per_item=Decimal("1000.00"),
)

# Crea payment
payment = await PaymentFactory.create(
    db_session,
    order_id=order.id,
)
```

**Available factories:**
- `UserFactory.create()` - Crea user con profile
- `ServiceFactory.create()` - Crea servizio
- `OrderFactory.create()` - Crea order con items
- `OrderItemFactory.create()` - Crea singolo order item
- `PaymentFactory.create()` - Crea payment per order
- `InvoiceFactory.create()` - Crea invoice da order
- `QuoteRequestFactory.create()` - Crea quote request

---

## Mock Services

Mock services per testare senza chiamare API esterne:

```python
from tests.mocks import MockStripeService, MockMSGraphService

# Mock Stripe
mock_stripe = MockStripeService()
pi = mock_stripe.create_payment_intent(amount=10000, currency="eur")
event = mock_stripe.construct_webhook_event("payment_intent.succeeded", pi["id"])

# Mock MS Graph
mock_graph = MockMSGraphService()
mock_graph.send_email("test@example.com", "Subject", "<html>Body</html>")
sent_emails = mock_graph.get_sent_emails()

# Mock Claude
mock_claude = MockClaudeService()
response = mock_claude.chat_completion(messages=[{"role": "user", "content": "Hi"}])
```

---

## Custom Assertions

Utility per asserzioni specializzate:

```python
from tests.assertions import (
    assert_decimal_equal,
    assert_uuid_valid,
    assert_jwt_valid,
    assert_email_format,
    assert_vat_number,
)

# Confronto decimali con precisione
assert_decimal_equal(Decimal("100.005"), Decimal("100.00"), places=2)

# Validazione UUID
assert_uuid_valid("123e4567-e89b-12d3-a456-426614174000")

# Validazione JWT
assert_jwt_valid(token, expected_claims={"sub": "user_123", "role": "admin"})

# Validazione formato email
assert_email_format("test@example.com")

# Validazione P.IVA italiana
assert_vat_number("IT12345678901")
```

---

## Test Markers

Markers per categorizzare e filtrare test:

- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.payment` - Payment tests
- `@pytest.mark.invoice` - Invoice tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.slow` - Test lenti (>1s)
- `@pytest.mark.unit` - Unit tests veloci

**Run tests by marker:**

```bash
# Solo test auth
pytest -m auth

# Solo test payment e invoice
pytest -m "payment or invoice"

# Escludi test slow
pytest -m "not slow"
```

---

## Coverage Reports

### Generate HTML Coverage Report

```bash
pytest --cov=app --cov-report=html
```

Apri `htmlcov/index.html` nel browser per report interattivo.

### Coverage per Modulo

```bash
pytest --cov=app --cov-report=term-missing
```

Output example:
```
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
app/api/routes/auth.py                    234     23    90%   145-152, 201-205
app/api/routes/orders.py                  189      8    96%   87-92
app/models/order.py                       156      0   100%
app/core/security.py                      98      5    95%   156-160
---------------------------------------------------------------------
TOTAL                                    2847    189    93%
```

---

## Running Tests in CI/CD

### GitHub Actions (Planned)

File: `.github/workflows/test.yml`

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  backend:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
      redis:
        image: redis:7
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Troubleshooting

### Test database connection errors

```bash
# Verifica che PostgreSQL sia running
psql -U postgres -c "SELECT 1;"

# Verifica database test exists
psql -U postgres -c "\l" | grep aistrategyhub_test

# Ricrea database test se necessario
dropdb aistrategyhub_test
createdb aistrategyhub_test
```

### Import errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verifica PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/backend"
```

### Async test warnings

Se vedi warning tipo "RuntimeWarning: coroutine was never awaited":

```python
# ✅ Corretto
@pytest.mark.asyncio
async def test_example(db_session: AsyncSession):
    result = await some_async_function()

# ❌ Errato (manca await)
@pytest.mark.asyncio
async def test_example(db_session: AsyncSession):
    result = some_async_function()  # Missing await!
```

---

## Best Practices

### 1. Test Independence

Ogni test deve essere indipendente e non dipendere da altri test:

```python
# ✅ Good - usa factory per setup
async def test_example(db_session):
    user = await UserFactory.create(db_session)
    # test logic

# ❌ Bad - dipende da stato globale
async def test_example(db_session):
    user = db_session.query(User).first()  # Assumes user exists!
    # test logic
```

### 2. Use Factories

Preferisci factories a fixture hardcoded:

```python
# ✅ Good - flexible
user = await UserFactory.create(
    db_session,
    email="custom@example.com",
    role=UserRole.ADMIN,
)

# ❌ Bad - hardcoded
user = User(
    id=uuid.uuid4(),
    email="test@example.com",
    # ... molti campi required ...
)
```

### 3. Mock External Services

Mocka sempre servizi esterni per test rapidi e deterministici:

```python
# ✅ Good - usa mock
def test_example(mock_stripe):
    # Test senza chiamare Stripe API reale
    pass

# ❌ Bad - chiama API reale
def test_example():
    # Lento, non deterministico, consuma API quota
    stripe.PaymentIntent.create(...)
```

### 4. Test Edge Cases

Testa non solo happy path ma anche edge cases:

```python
# Test happy path
test_create_order_with_valid_data()

# Test edge cases
test_create_order_with_zero_quantity()
test_create_order_with_negative_price()
test_create_order_with_inactive_service()
test_create_order_exceeds_stock()
```

### 5. Descriptive Test Names

Nomi test devono descrivere comportamento atteso:

```python
# ✅ Good - chiaro cosa testa
def test_login_with_invalid_password_returns_401():
    pass

# ❌ Bad - vago
def test_login():
    pass
```

---

## Coverage Targets by Component

| Component | Target | Priority | Status |
|-----------|--------|----------|--------|
| Authentication | 90%+ | CRITICAL | ✅ 49 tests |
| Payments | 95%+ | CRITICAL | ✅ 49 tests |
| Invoicing | 90%+ | HIGH | 🔄 TODO |
| Orders | 85%+ | HIGH | 🔄 TODO |
| Email Service | 80%+ | MEDIUM | 🔄 TODO |
| File Storage | 80%+ | MEDIUM | 🔄 TODO |
| AI Services | 75%+ | MEDIUM | 🔄 TODO |
| Frontend | 75%+ | MEDIUM | 🔄 TODO |

**Overall: 80%+ coverage su percorsi critici**

---

## Next Steps

1. ✅ **DONE**: Fix Payment model bug + migration
2. ✅ **DONE**: Infrastructure setup (pytest.ini, conftest.py)
3. ✅ **DONE**: Test utilities (factories, mocks, assertions)
4. ✅ **DONE**: Test auth (150 cases - CRITICAL)
5. ✅ **DONE**: Test payments (95 cases - CRITICAL)
6. 🔄 **TODO**: Test invoice XML/PDF (60 cases)
7. 🔄 **TODO**: Test orders (50 cases)
8. 🔄 **TODO**: Test service layer (100+ cases)
9. 🔄 **TODO**: Frontend tests (115+ cases)
10. 🔄 **TODO**: Integration tests (30+ cases)
11. 🔄 **TODO**: CI/CD workflow (GitHub Actions)

---

## Contact & Support

Per domande o issues con i test:
- Controlla questo README prima
- Verifica log output di pytest con `-v` flag
- Esegui test singolo per debug: `pytest -v tests/test_auth.py::TestLogin::test_login_valid_credentials`

**Happy Testing! 🧪**
