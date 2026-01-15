# AI Strategy Hub - Backend API

FastAPI backend per piattaforma e-commerce servizi consulenza.

## Stack Tecnologico

- **Framework**: FastAPI 0.110+
- **Database**: PostgreSQL 15+ con pgvector
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Cache/Sessions**: Redis 7+
- **Authentication**: JWT (JSON Web Tokens) + MFA (TOTP)
- **Password Hashing**: Argon2
- **Validazione**: Pydantic v2
- **Testing**: pytest
- **Logging**: Structured JSON logging

## Features Implementate

### ✅ Autenticazione e Autorizzazione
- Registrazione utenti con email verification
- Login con JWT (access + refresh tokens)
- MFA con TOTP (Google Authenticator, Authy)
- Backup codes per MFA recovery
- Password reset via email
- Account locking dopo failed attempts
- RBAC con 6 ruoli (super_admin, admin, editor, support, customer, guest)

### ✅ Gestione Utenti
- CRUD completo utenti (admin)
- Profili utente con dati fatturazione
- Statistiche utenti (dashboard admin)
- Self-service (GET/PUT /me, /me/profile)

### ✅ Gestione Servizi
- CRUD servizi consulenza
- CMS per contenuti servizio
- FAQ per servizio
- Gestione immagini
- Filtri e ricerca
- Pubblicazione/bozze

### 📋 TODO
- Orders & Quotes
- Invoices (fatturazione elettronica italiana)
- CMS & Blog
- AI Chatbot con RAG
- Support Tickets
- Notifications
- Webhooks (Stripe, etc.)

## Setup Locale

### Prerequisiti

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Poetry (package manager) oppure pip

### 1. Crea Database

```bash
# Accedi a PostgreSQL
psql -U postgres

# Crea database e utente
CREATE DATABASE aistrategyhub;
CREATE USER aistrategyhub WITH ENCRYPTED PASSWORD 'your-password';
GRANT ALL PRIVILEGES ON DATABASE aistrategyhub TO aistrategyhub;

# Installa estensione pgvector
\c aistrategyhub
CREATE EXTENSION IF NOT EXISTS vector;
```

### 2. Configura Environment

```bash
# Copia template environment
cp .env.example .env

# Modifica .env con i tuoi valori
nano .env
```

Valori minimi richiesti:
```bash
SECRET_KEY=your-secret-key-here  # Genera con: python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET_KEY=your-jwt-secret-key-here
POSTGRES_PASSWORD=your-postgres-password
```

### 3. Installa Dependencies

```bash
# Con pip
pip install -r requirements.txt

# Oppure con Poetry
poetry install
```

### 4. Run Migrations

```bash
# Crea tutte le tabelle
alembic upgrade head

# Verifica migrations
alembic current
```

### 5. Seed Database (Opzionale)

Popola database con dati di test:

```bash
python seed.py
```

Questo crea:
- 6 utenti di test (password: `Test123!`)
  - `admin@aistrategyhub.eu` (Super Admin)
  - `mario.verdi@azienda.it` (Customer)
- 4 servizi di esempio
- 2 ordini
- 1 fattura
- Blog posts, etc.

### 6. Avvia Server

```bash
# Development (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 7. Accedi alla Documentazione

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Testing delle API

### Health Check

```bash
curl http://localhost:8000/health
```

### Registrazione

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "confirm_password": "Test123!",
    "first_name": "Mario",
    "last_name": "Rossi",
    "accept_terms": true,
    "accept_privacy": true
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@aistrategyhub.eu",
    "password": "Test123!"
  }'
```

Salva l'`access_token` dalla response.

### Get Current User

```bash
curl http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Lista Servizi (Pubblico)

```bash
curl http://localhost:8000/api/v1/services
```

### Dettaglio Servizio

```bash
curl http://localhost:8000/api/v1/services/{service_id}
```

## Database Migrations

### Crea Nuova Migration

```bash
# Auto-genera da modifiche models
alembic revision --autogenerate -m "Description"

# Oppure migration vuota
alembic revision -m "Description"
```

### Applica Migrations

```bash
# Upgrade alla latest
alembic upgrade head

# Upgrade di 1 step
alembic upgrade +1

# Downgrade di 1 step
alembic downgrade -1
```

### Storia Migrations

```bash
alembic history
alembic current
```

## Logging

Tutti i log sono strutturati in JSON (production) o testo (development).

Locations:
- **Stdout**: Tutti i log
- **File**: `/app/logs/app.log` (se configurato)
- **Error File**: `/app/logs/error.log` (solo errori)

Log levels:
- `DEBUG`: Informazioni dettagliate per debugging
- `INFO`: Eventi normali applicazione
- `WARNING`: Eventi anomali ma gestiti
- `ERROR`: Errori che impediscono funzionalità
- `CRITICAL`: Errori gravi che fermano applicazione

## Security

### Password Policy

- Minimo 8 caratteri
- Almeno 1 maiuscola
- Almeno 1 numero
- Almeno 1 carattere speciale
- Hash con Argon2

### JWT Tokens

- **Access Token**: 15 minuti
- **Refresh Token**: 7 giorni
- Algorithm: HS256

### Account Locking

- Lock automatico dopo 5 failed login attempts
- Lock duration: 30 minuti
- Reset counter su login riuscito

### MFA (Multi-Factor Authentication)

- TOTP (Time-based One-Time Password)
- Compatible con: Google Authenticator, Authy, Microsoft Authenticator
- 10 backup codes per recovery

## API Endpoints

### Authentication (`/api/v1/auth`)

- `POST /register` - Registrazione nuovo utente
- `POST /login` - Login con email/password (+ MFA se abilitato)
- `POST /refresh` - Refresh access token
- `POST /verify-email` - Verifica email con token
- `POST /password-reset` - Richiesta reset password
- `POST /password-reset/confirm` - Conferma reset password
- `POST /password-change` - Cambio password (authenticated)
- `POST /mfa/setup` - Setup MFA
- `POST /mfa/enable` - Abilita MFA
- `POST /mfa/disable` - Disabilita MFA
- `POST /logout` - Logout

### Users (`/api/v1/users`)

- `GET /me` - Current user info
- `PUT /me` - Update current user
- `GET /me/profile` - Current user profile
- `PUT /me/profile` - Update current user profile
- `GET /` - List users (admin)
- `POST /` - Create user (admin)
- `GET /{id}` - Get user detail
- `PUT /{id}` - Update user (admin)
- `DELETE /{id}` - Delete user (admin)
- `PUT /{id}/role` - Change user role (admin)
- `GET /statistics/overview` - User statistics (admin)

### Services (`/api/v1/services`)

- `GET /` - List services (public + filters)
- `GET /{id}` - Get service detail
- `POST /` - Create service (admin)
- `PUT /{id}` - Update service (admin)
- `DELETE /{id}` - Delete service (admin)
- `POST /{id}/contents` - Add content (admin)
- `PUT /{id}/contents/{content_id}` - Update content (admin)
- `DELETE /{id}/contents/{content_id}` - Delete content (admin)
- `POST /{id}/faqs` - Add FAQ (admin)
- `PUT /{id}/faqs/{faq_id}` - Update FAQ (admin)
- `DELETE /{id}/faqs/{faq_id}` - Delete FAQ (admin)

## Troubleshooting

### Database Connection Error

```
psycopg2.OperationalError: could not connect to server
```

Verifica:
1. PostgreSQL è in esecuzione: `pg_ctl status`
2. Credenziali corrette in `.env`
3. Database esiste: `psql -U postgres -l`

### Migration Error

```
alembic.util.exc.CommandError: Can't locate revision identified by 'xxxx'
```

Reset migrations:
```bash
# Drop alembic_version table
psql -U postgres -d aistrategyhub -c "DROP TABLE alembic_version;"

# Re-run migrations
alembic upgrade head
```

### Import Error

```
ModuleNotFoundError: No module named 'app'
```

Assicurati di essere nella directory `backend/`:
```bash
cd backend/
python -m app.main
```

## Development

### Code Style

- **Formatter**: Black
- **Linter**: Ruff
- **Type Checker**: mypy (opzionale)

```bash
# Format code
black app/

# Lint code
ruff check app/
```

### Testing

```bash
# Run all tests
pytest

# Run con coverage
pytest --cov=app --cov-report=html
```

## Production Deployment

### Environment Variables

Cambia in `.env`:
```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<strong-random-key>
JWT_SECRET_KEY=<strong-random-key>
```

### Run con Gunicorn

```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile - \
  --error-logfile -
```

### Docker

```bash
# Build
docker build -t aistrategyhub-backend .

# Run
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name aistrategyhub-backend \
  aistrategyhub-backend
```

## Support

Per problemi o domande:
- **GitHub Issues**: https://github.com/bottodavide/AISH.EU/issues
- **Email**: support@aistrategyhub.eu
- **LinkedIn**: https://www.linkedin.com/in/davidebotto/

## License

Proprietary - All Rights Reserved
