# Linode Verification Checklist

Comandi da eseguire sul Linode VPS dopo il deployment per verificare che tutto funzioni correttamente.

**Server IP**: 172.235.235.144
**Deploy Directory**: /srv/aish.eu
**Domain**: aistrategyhub.eu

---

## Pre-Deployment Setup (Solo Prima Volta)

Se è la prima volta che fai il deployment con docker-compose.prod.yml, esegui questi comandi:

```bash
# 1. SSH nel server
ssh deploy@172.235.235.144

# 2. Naviga alla directory
cd /srv/aish.eu

# 3. Pull del codice aggiornato
git pull origin main

# 4. Crea le directory necessarie (se non esistono già)
mkdir -p data/{postgres,redis,uploads}
mkdir -p logs/{backend,nginx}
mkdir -p ssl/{letsencrypt,www}
mkdir -p backups

# 5. Crea/aggiorna file .env
cp .env.prod.example .env
vim .env  # Compila con valori reali

# 6. Genera chiavi sicure (copia output nel .env)
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(24))"
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(24))"
```

---

## Step 1: Verifica File e Configurazione

```bash
# Verifica che docker-compose.prod.yml esista
ls -la docker-compose.prod.yml

# Verifica struttura directory
tree -L 2 -d .

# Verifica che .env sia configurato
cat .env | grep -E "(SECRET_KEY|POSTGRES|REDIS)" | head -5

# Verifica configurazione docker-compose
docker compose -f docker-compose.prod.yml config
```

**Expected Output**: Dovrebbe mostrare la configurazione completa senza errori.

---

## Step 2: Stop Vecchi Container (se esistono)

```bash
# Stop e rimuovi vecchi container
docker compose down

# Oppure se usi ancora il vecchio docker-compose.yml
docker stop $(docker ps -q) 2>/dev/null || echo "No containers running"

# Verifica nessun container attivo
docker ps -a
```

---

## Step 3: Build e Avvio Servizi

### Opzione A: Avvio Completo (con SSL - richiede dominio configurato)

Se hai già certificati SSL e il dominio punta al VPS:

```bash
# Build immagini
docker compose -f docker-compose.prod.yml build

# Avvia tutti i servizi
docker compose -f docker-compose.prod.yml up -d

# Verifica che si avviino
docker compose -f docker-compose.prod.yml ps
```

### Opzione B: Avvio Temporaneo Solo HTTP (per test via IP)

Se vuoi testare subito via IP senza SSL:

```bash
# 1. Modifica nginx.prod.conf temporaneamente
cp nginx/nginx.prod.conf nginx/nginx.prod.conf.backup

# 2. Commenta blocco HTTPS nel file nginx.prod.conf
# (linee 96-213 - server block listen 443)
vim nginx/nginx.prod.conf

# 3. Build e avvia
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

# 4. Verifica
docker compose -f docker-compose.prod.yml ps
```

---

## Step 4: Verifica Container Status

```bash
# Verifica che tutti i container siano UP e HEALTHY
docker compose -f docker-compose.prod.yml ps

# Output atteso:
# NAME                        STATUS                   PORTS
# aistrategyhub-postgres      Up (healthy)            127.0.0.1:5432->5432/tcp
# aistrategyhub-redis         Up (healthy)            127.0.0.1:6379->6379/tcp
# aistrategyhub-backend       Up (healthy)            8000/tcp
# aistrategyhub-frontend      Up (healthy)            3000/tcp
# aistrategyhub-nginx         Up (healthy)            0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp

# Verifica anche con docker ps
docker ps

# Verifica resource usage
docker stats --no-stream
```

**Expected**: Tutti i container devono avere status "Up" e health "healthy".

---

## Step 5: Verifica Logs

```bash
# Logs di tutti i servizi
docker compose -f docker-compose.prod.yml logs --tail=50

# Logs per singolo servizio
docker compose -f docker-compose.prod.yml logs -f postgres
docker compose -f docker-compose.prod.yml logs -f redis
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f frontend
docker compose -f docker-compose.prod.yml logs -f nginx

# Cerca errori
docker compose -f docker-compose.prod.yml logs | grep -i error
docker compose -f docker-compose.prod.yml logs | grep -i fail
```

**Expected**: Nessun errore critico. Alcuni warning sono normali durante l'avvio.

---

## Step 6: Health Check Endpoints

### Test Locale (dal server Linode)

```bash
# Test health check nginx (HTTP)
curl -v http://localhost/health

# Expected output:
# HTTP/1.1 200 OK
# {"status":"healthy","timestamp":"2026-01-18T..."}

# Test health check nginx (HTTPS) - se SSL configurato
curl -v https://localhost/health

# Test backend diretto
docker compose -f docker-compose.prod.yml exec backend curl -f http://localhost:8000/health

# Expected output:
# HTTP/1.1 200 OK
# {"status":"ok","database":"connected","redis":"connected"}

# Test frontend diretto
docker compose -f docker-compose.prod.yml exec frontend wget -O- http://localhost:3000/health

# Expected output:
# HTTP/1.1 200 OK
```

### Test Esterno (dal tuo PC o altro server)

```bash
# Test via IP (HTTP) - se hai avviato senza SSL
curl -v http://172.235.235.144/health

# Expected:
# HTTP/1.1 200 OK
# {"status":"healthy","timestamp":"..."}

# Test via dominio (HTTP)
curl -v http://aistrategyhub.eu/health

# Test via dominio (HTTPS) - se SSL configurato
curl -v https://aistrategyhub.eu/health
```

---

## Step 7: Verifica Database

```bash
# Connetti a PostgreSQL
docker compose -f docker-compose.prod.yml exec postgres psql -U aistrategyhub aistrategyhub

# Una volta dentro psql, esegui:
\dt          # Lista tabelle
\q           # Esci

# Oppure comando diretto
docker compose -f docker-compose.prod.yml exec postgres psql -U aistrategyhub aistrategyhub -c "\dt"

# Expected: Dovrebbe mostrare le tabelle create da Alembic
```

---

## Step 8: Verifica Redis

```bash
# Connetti a Redis (usa password da .env)
docker compose -f docker-compose.prod.yml exec redis redis-cli

# Una volta dentro redis-cli:
AUTH your_redis_password_here
PING                           # Expected: PONG
DBSIZE                         # Expected: numero di chiavi
INFO server                    # Info server Redis
QUIT

# Oppure comando diretto
docker compose -f docker-compose.prod.yml exec redis redis-cli -a "$(grep REDIS_PASSWORD .env | cut -d= -f2)" PING
```

---

## Step 9: Test API Endpoints

```bash
# Test registrazione utente (dall'interno del server)
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "confirm_password": "TestPassword123!",
    "first_name": "Test",
    "last_name": "User",
    "accept_terms": true,
    "accept_privacy": true
  }'

# Expected: 201 Created con user object JSON

# Test login
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Expected: 200 OK con access_token

# Test lista servizi
curl http://localhost/api/v1/services

# Expected: 200 OK con array servizi (potrebbe essere vuoto)
```

---

## Step 10: Test dal Browser

### Via IP (HTTP)

Apri nel browser: **http://172.235.235.144/**

**Expected**:
- La homepage di Next.js deve caricare
- Nessun errore 502 Bad Gateway
- Nessun errore 404 Not Found

### Via Dominio (se configurato)

Apri nel browser:
- **http://aistrategyhub.eu/** (HTTP)
- **https://aistrategyhub.eu/** (HTTPS - se SSL configurato)

**Expected**:
- Homepage carica correttamente
- Se HTTPS: certificato SSL valido
- Se HTTP-only: redirect a HTTPS (se configurato in nginx)

---

## Step 11: Verifica Network e Connettività

```bash
# Verifica porte aperte
sudo netstat -tulpn | grep -E ':(80|443|5432|6379)'

# Expected:
# tcp  0.0.0.0:80    LISTEN    (nginx)
# tcp  0.0.0.0:443   LISTEN    (nginx)
# tcp  127.0.0.1:5432  LISTEN  (postgres)
# tcp  127.0.0.1:6379  LISTEN  (redis)

# Verifica firewall (UFW)
sudo ufw status

# Expected:
# Status: active
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       Anywhere
# 80/tcp                     ALLOW       Anywhere
# 443/tcp                    ALLOW       Anywhere

# Test DNS resolution (dal server)
nslookup aistrategyhub.eu
dig aistrategyhub.eu

# Expected: Deve risolvere a 172.235.235.144
```

---

## Step 12: Verifica Resource Usage

```bash
# CPU, RAM, Disk usage
docker stats --no-stream

# Expected:
# - PostgreSQL: ~100-500MB RAM
# - Redis: ~50-200MB RAM
# - Backend: ~200-500MB RAM
# - Frontend: ~100-300MB RAM
# - Nginx: ~10-50MB RAM

# Disk usage
df -h
docker system df

# Verifica spazio disponibile
du -sh /srv/aish.eu/*
```

---

## Step 13: Test Complete User Flow

```bash
# 1. Registrazione → 2. Login → 3. Accesso area privata
# (Esegui questi test dal browser o con curl)

# Da browser:
# 1. Vai su http://172.235.235.144/auth/register
# 2. Compila form registrazione
# 3. Verifica email ricevuta (se MS Graph configurato)
# 4. Vai su /auth/login
# 5. Login
# 6. Verifica redirect a dashboard/home
```

---

## Troubleshooting Commands

### Container non healthy

```bash
# Verifica perché un container non è healthy
docker inspect aistrategyhub-backend | grep -A 10 Health

# Restart container specifico
docker compose -f docker-compose.prod.yml restart backend

# Recreate container
docker compose -f docker-compose.prod.yml up -d --force-recreate backend
```

### Errori di connessione backend → database

```bash
# Verifica che backend possa raggiungere postgres
docker compose -f docker-compose.prod.yml exec backend ping -c 3 postgres

# Test connessione database da backend
docker compose -f docker-compose.prod.yml exec backend python -c "
from app.core.database import engine
print('Database connection OK')
"
```

### 502 Bad Gateway

```bash
# Verifica che nginx possa raggiungere backend/frontend
docker compose -f docker-compose.prod.yml exec nginx ping -c 3 backend
docker compose -f docker-compose.prod.yml exec nginx ping -c 3 frontend

# Verifica configurazione nginx
docker compose -f docker-compose.prod.yml exec nginx nginx -t

# Reload nginx
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

---

## Success Criteria Checklist

Verifica che TUTTI questi punti siano OK:

- [ ] `docker compose ps` mostra tutti container UP e healthy
- [ ] `curl http://localhost/health` ritorna 200 OK
- [ ] `curl http://172.235.235.144/health` ritorna 200 OK (da esterno)
- [ ] PostgreSQL accetta connessioni: `psql` funziona
- [ ] Redis risponde: `PING` → `PONG`
- [ ] Backend health check: `http://localhost:8000/health` → 200 OK
- [ ] Frontend health check: `http://localhost:3000/health` → 200 OK
- [ ] API registrazione funziona: `POST /api/v1/auth/register` → 201
- [ ] Browser carica homepage: `http://172.235.235.144/` senza errori
- [ ] Logs non mostrano errori critici
- [ ] Resource usage sotto controllo (<80% RAM)
- [ ] Firewall configurato: porte 80, 443 aperte
- [ ] DNS risolve dominio a IP corretto (se dominio configurato)

---

## Note Importanti

### Accesso via IP vs Dominio

**Via IP (http://172.235.235.144/)**:
- Funziona solo se nginx accetta connessioni da qualsiasi host
- Nginx attuale è configurato per `aistrategyhub.eu`
- Soluzione temporanea: modifica `server_name` in nginx.prod.conf a `server_name _;`

**Via Dominio (https://aistrategyhub.eu/)**:
- Richiede DNS configurato (A record → 172.235.235.144)
- Richiede certificato SSL configurato
- Nginx redirect HTTP → HTTPS automaticamente

### Per testare subito via IP senza SSL:

1. Modifica `nginx/nginx.prod.conf`:
   ```nginx
   # Cambia da:
   server_name aistrategyhub.eu www.aistrategyhub.eu;

   # A:
   server_name _;
   ```

2. Commenta blocco HTTPS (server listen 443) temporaneamente

3. Rebuild nginx:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --force-recreate nginx
   ```

4. Test: `curl http://172.235.235.144/health`

---

## Quick Commands Reference

```bash
# Status
docker compose -f docker-compose.prod.yml ps

# Logs
docker compose -f docker-compose.prod.yml logs -f

# Restart
docker compose -f docker-compose.prod.yml restart

# Stop
docker compose -f docker-compose.prod.yml stop

# Start
docker compose -f docker-compose.prod.yml start

# Rebuild
docker compose -f docker-compose.prod.yml up -d --build

# Health check
curl http://localhost/health

# Resource usage
docker stats --no-stream
```

---

**Happy Deploying! 🚀**
