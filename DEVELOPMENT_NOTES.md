# AI Strategy Hub - Development Notes

## Last Session: 2026-01-16

### Completed Tasks

#### Authentication & Security
- ✅ Autenticazione aggiunta a tutte le pagine admin (10 pagine)
  - `/admin/about`, `/admin/use-cases`, `/admin/newsletter`, `/admin/banners`
  - `/admin/pages`, `/admin/settings`, `/admin/analytics`, `/admin/invoices`
  - `/admin/knowledge-base`, `/admin/payments`
- ✅ Pattern: Defense-in-depth (AdminLayout + page-level useAuth checks)
- ✅ Redirect automatico a `/` se non autenticato o non admin
- ✅ Loading state durante verifica autenticazione

#### Legal Pages (Cookie, Privacy, Termini)
- ✅ Create 3 pagine nel database CMS:
  - `slug: cookie` - Cookie Policy
  - `slug: privacy` - Privacy Policy
  - `slug: termini` - Termini di Servizio
- ✅ Gestione 404 graceful nel frontend:
  - Se page non esiste in CMS → mostra contenuto fallback statico
  - Se errore server (500) → mostra errore con bottone "Riprova"
- ✅ API endpoint funzionanti:
  - GET `/api/v1/cms/pages/slug/cookie`
  - GET `/api/v1/cms/pages/slug/privacy`
  - GET `/api/v1/cms/pages/slug/termini`
- ✅ Computed properties aggiunte a Page model:
  - `is_published`: Boolean (True se status == PUBLISHED)
  - `content_sections`: Alias per content_blocks

#### ChatWidget
- ✅ Messaggio di benvenuto aggiornato:
  - "Ciao! Sono il tuo assistente AI. Posso aiutarti a ricevere informazioni sui servizi erogati in ambito Cybersecurity, Compliance, AI e GDPR"

#### Bug Fixes
- ✅ Pydantic UUID validation fix in `/api/v1/about`
  - Changed schemas from `id: str` to `id: UUID`
  - Updated to Pydantic v2 syntax: `ConfigDict(from_attributes=True)`

---

## Architecture Decisions

### Authentication Pattern
- **Defense-in-depth**: Doppio controllo auth
  1. `AdminLayout` verifica ruolo utente
  2. Ogni pagina admin verifica con `useAuth()` hook
- **AuthContext**: Propaga `user`, `role`, `isAuthenticated`, `isAdmin`
- **Ruoli**: `super_admin` | `admin` | `editor` | `user`

### Error Handling
- **404 su legal pages**: Comportamento atteso, mostra fallback
- **500 errors**: Redirect a pagina errore o alert inline
- **Chat errors**: Gestione differenziata per errori gravi vs validazione

### CMS Strategy
- Legal pages hanno `content_sections: []` vuoti
- Frontend usa contenuto statico fallback finché non popolato da admin
- Questo permette deploy immediato con contenuto già pronto

---

## Known Issues & Workarounds

### SQLAlchemy Relationship Error
**Problema**: User model ha relationship a SystemLog non definito correttamente
```
InvalidRequestError: expression 'SystemLog' failed to locate a name
```

**Workaround**:
- Non usare ORM per query su User in script di seed
- Usare raw SQL con asyncpg: `conn.execute(text(...))`
- Oppure importare tutti i models necessari prima di query

### PostgreSQL Enums
**Problema**: Enum values devono essere UPPERCASE
```python
# ❌ WRONG
page_type='custom', status='published'

# ✅ CORRECT
page_type='CUSTOM', status='PUBLISHED'
```

**Enum values nel DB**:
- `PageType`: HOMEPAGE, SERVICE, ABOUT, CONTACT, CUSTOM
- `ContentStatus`: DRAFT, PUBLISHED, ARCHIVED

---

## Project Structure

```
aistrategyhub/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # FastAPI endpoints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── core/           # Config, database, security
│   │   └── main.py         # FastAPI app
│   ├── scripts/            # Seed scripts
│   ├── venv/               # Virtual environment
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js pages
│   │   ├── components/     # React components
│   │   ├── contexts/       # React contexts (AuthContext)
│   │   └── lib/            # Utilities, API client
│   └── package.json
└── docs/                   # Documentation
```

---

## Database

### Connection Info
- **Host**: localhost:5432
- **Database**: aistrategyhub
- **User**: aistrategyhub
- **Password**: aistrategyhub_dev_password (in .env)

### Key Tables
- `users` - Utenti con ruoli (super_admin, admin, editor, user)
- `pages` - CMS pages (homepage, about, cookie, privacy, termini, ecc.)
- `blog_posts` - Articoli blog
- `services` - Servizi offerti
- `use_cases` - Casi d'uso
- `orders` - Ordini clienti
- `files` - File uploads
- `chat_conversations` - Conversazioni chatbot
- `newsletter_subscriptions` - Iscritti newsletter

---

## Tech Stack

### Backend
- **Framework**: FastAPI
- **ORM**: SQLAlchemy (async)
- **Validation**: Pydantic v2
- **Database**: PostgreSQL 14+
- **Auth**: JWT tokens
- **AI**: OpenAI GPT-4 (chatbot + RAG)
- **Vector DB**: pgvector (embeddings)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui
- **State**: React Context API
- **HTTP Client**: Axios
- **Markdown**: react-markdown + remark-gfm

---

## Environment Setup

### Backend

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000

# Run migrations (if needed)
alembic upgrade head

# Seed legal pages
python scripts/seed_legal_pages.py
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

---

## Useful Commands

### Git
```bash
# Commit con messaggio dettagliato
git add . && git commit -m "Descrizione" && git push

# Vedere ultimi commit
git log --oneline -10

# Vedere cosa è cambiato oggi
git log --since="1 day ago" --oneline
```

### Database
```bash
# Connetti a PostgreSQL
psql -h localhost -U aistrategyhub -d aistrategyhub

# Backup database
pg_dump -h localhost -U aistrategyhub aistrategyhub > backup.sql

# Liste pagine CMS
psql -h localhost -U aistrategyhub -d aistrategyhub -c "SELECT slug, title, status FROM pages;"
```

### Development
```bash
# Check Python version
python --version  # Should be 3.12+

# Check Node version
node --version    # Should be 18+

# Tail backend logs
tail -f /tmp/claude/-System-Volumes-Data-home/tasks/*.output

# Test API endpoint
curl http://localhost:8000/api/v1/cms/pages/slug/cookie | python -m json.tool
```

---

## API Endpoints (Key)

### Authentication
- POST `/api/v1/auth/register` - Registrazione
- POST `/api/v1/auth/login` - Login
- GET `/api/v1/auth/me` - Current user info

### CMS
- GET `/api/v1/cms/pages` - Lista pagine
- GET `/api/v1/cms/pages/slug/{slug}` - Get page by slug
- POST `/api/v1/cms/pages` - Create page (admin only)
- PUT `/api/v1/cms/pages/{id}` - Update page (admin only)

### Blog
- GET `/api/v1/blog/posts` - Lista articoli
- GET `/api/v1/blog/posts/{slug}` - Get article by slug
- POST `/api/v1/blog/posts` - Create post (admin only)

### Chat
- POST `/api/v1/chat/message` - Send message to chatbot
- GET `/api/v1/chat/conversations` - Get user conversations
- POST `/api/v1/chat/feedback` - Submit feedback

### About Page
- GET `/api/v1/about` - Get about page content
- PUT `/api/v1/about` - Update about page (admin only)

---

## Frontend Routes

### Public Pages
- `/` - Homepage
- `/servizi` - Lista servizi
- `/servizi/[slug]` - Dettaglio servizio
- `/blog` - Lista articoli blog
- `/blog/[slug]` - Articolo blog
- `/cookie` - Cookie Policy
- `/privacy` - Privacy Policy
- `/termini` - Termini di Servizio
- `/contatti` - Pagina contatti

### Admin Pages (Auth Required)
- `/admin/dashboard` - Dashboard admin
- `/admin/about` - Editor pagina about
- `/admin/services` - Gestione servizi
- `/admin/blog` - Gestione blog
- `/admin/pages` - Gestione pagine CMS
- `/admin/use-cases` - Gestione casi d'uso
- `/admin/banners` - Gestione banner
- `/admin/newsletter` - Newsletter management
- `/admin/settings` - Impostazioni sito
- `/admin/analytics` - Analytics
- `/admin/invoices` - Fatture
- `/admin/knowledge-base` - Knowledge base per RAG
- `/admin/payments` - Gestione pagamenti

---

## Next Steps & TODO

### High Priority
- [ ] Popolare content_sections delle legal pages tramite admin panel
- [ ] Test completo funzionalità admin (tutti gli endpoint)
- [ ] Verificare permessi granulari (super_admin vs admin vs editor)

### Medium Priority
- [ ] Aggiungere paginazione alle liste admin
- [ ] Implementare search/filter nelle liste
- [ ] Aggiungere preview pagine prima della pubblicazione
- [ ] Sistema di notifiche in-app

### Low Priority
- [ ] Dark mode support
- [ ] Internazionalizzazione (i18n)
- [ ] Analytics dashboard con grafici
- [ ] Export dati in CSV/Excel

### Documentation
- [ ] API documentation con Swagger/OpenAPI
- [ ] Component storybook per frontend
- [ ] Deployment guide (production)
- [ ] Security best practices document

---

## Troubleshooting

### Backend non parte
```bash
# Check PostgreSQL
pg_isready -h localhost -p 5432

# Check .env file exists
cat backend/.env

# Recreate venv se necessario
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend non parte
```bash
# Clear node_modules
cd frontend
rm -rf node_modules package-lock.json
npm install

# Check Next.js version
npm list next

# Clear .next cache
rm -rf .next
```

### Database Issues
```bash
# Reset database (ATTENZIONE: cancella tutti i dati!)
psql -h localhost -U postgres -c "DROP DATABASE IF EXISTS aistrategyhub;"
psql -h localhost -U postgres -c "CREATE DATABASE aistrategyhub OWNER aistrategyhub;"

# Run migrations
cd backend
alembic upgrade head

# Re-seed data
python scripts/seed_legal_pages.py
```

---

## Important Files

### Configuration
- `backend/.env` - Environment variables (secrets, DB connection)
- `backend/app/core/config.py` - App configuration
- `frontend/.env.local` - Frontend environment variables

### Authentication
- `backend/app/core/security.py` - JWT token handling
- `frontend/src/contexts/AuthContext.tsx` - Auth state management
- `frontend/src/lib/api-client.ts` - Axios client with auth headers

### Database
- `backend/app/models/` - SQLAlchemy models
- `backend/app/schemas/` - Pydantic schemas
- `backend/alembic/versions/` - Database migrations

---

## Contact & Resources

### Project Info
- **Repository**: https://github.com/bottodavide/AISH.EU.git
- **Production URL**: https://aistrategyhub.eu (quando deployato)
- **Local Backend**: http://localhost:8000
- **Local Frontend**: http://localhost:3000

### Documentation Links
- FastAPI Docs: http://localhost:8000/docs
- FastAPI ReDoc: http://localhost:8000/redoc
- Next.js Docs: https://nextjs.org/docs
- Tailwind CSS: https://tailwindcss.com/docs

---

## Notes

### Pydantic v2 Migration
Quando si usano Pydantic schemas:
```python
# OLD (Pydantic v1)
class MySchema(BaseModel):
    class Config:
        orm_mode = True

# NEW (Pydantic v2)
from pydantic import ConfigDict

class MySchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
```

### UUID Handling
```python
# In schemas
from uuid import UUID
id: UUID  # Not id: str

# In database
from sqlalchemy.dialects.postgresql import UUID
id = Column(UUID(as_uuid=True), primary_key=True)
```

---

**Last Updated**: 2026-01-16 21:35
**Last Commit**: a2da22e - "Fix legal pages: create database records and add computed properties"
**Claude Version**: Sonnet 4.5
