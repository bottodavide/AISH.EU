# AI Strategy Hub - Production Deployment Guide

Guida completa per il deployment su Linode VPS con Docker Compose.

## Table of Contents
- [Prerequisiti](#prerequisiti)
- [Setup Iniziale](#setup-iniziale)
- [Configurazione SSL](#configurazione-ssl)
- [Deployment](#deployment)
- [Manutenzione](#manutenzione)
- [Troubleshooting](#troubleshooting)

---

## Prerequisiti

### Server Requirements
- **VPS**: Linode o equivalente
- **OS**: Ubuntu 22.04 LTS o superiore
- **RAM**: Minimo 4GB (raccomandato 8GB)
- **Storage**: Minimo 40GB SSD
- **CPU**: 2+ cores

### Software Requirements
- Docker Engine 24.0+
- Docker Compose v2
- Git
- Nginx (opzionale, se non usi il container nginx)

### Domain & DNS
- Dominio: `aistrategyhub.eu`
- DNS A record puntato all'IP del VPS
- DNS A record per `www.aistrategyhub.eu` (opzionale)

---

## Setup Iniziale

### 1. Preparazione Server

```bash
# Update sistema
sudo apt update && sudo apt upgrade -y

# Installa Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Installa Docker Compose v2
sudo apt install docker-compose-plugin

# Verifica installazione
docker --version
docker compose version

# Aggiungi user al gruppo docker (opzionale)
sudo usermod -aG docker $USER
```

### 2. Setup Directory Structure

```bash
# Crea directory progetto
sudo mkdir -p /srv/aish.eu
sudo chown -R deploy:deploy /srv/aish.eu

# Naviga alla directory
cd /srv/aish.eu

# Clone repository
git clone https://github.com/davidebotto/aistrategyhub.git .

# Crea directory per dati persistenti
mkdir -p data/{postgres,redis,uploads}
mkdir -p logs/{backend,nginx}
mkdir -p ssl/{letsencrypt,www}
mkdir -p backups

# Setta permessi
chmod 700 data/postgres
chmod 755 data/redis data/uploads logs/backend logs/nginx backups
```

### 3. Configurazione Environment Variables

```bash
# Copia template .env
cp .env.prod.example .env

# Modifica con editor
vim .env

# IMPORTANTE: Genera chiavi sicure con:
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_urlsafe(32))"
python3 -c "import secrets; print('POSTGRES_PASSWORD=' + secrets.token_urlsafe(24))"
python3 -c "import secrets; print('REDIS_PASSWORD=' + secrets.token_urlsafe(24))"
```

**Checklist variabili obbligatorie da compilare:**
- [ ] `SECRET_KEY` - Chiave segreta applicazione
- [ ] `JWT_SECRET_KEY` - Chiave JWT per autenticazione
- [ ] `POSTGRES_PASSWORD` - Password database PostgreSQL
- [ ] `REDIS_PASSWORD` - Password Redis
- [ ] `MS_GRAPH_*` - Credenziali Microsoft Graph API
- [ ] `STRIPE_*` - Chiavi Stripe (LIVE, non test!)
- [ ] `ANTHROPIC_API_KEY` - Chiave Claude API
- [ ] `SELLER_*` - Dati azienda per fatturazione

---

## Configurazione SSL

### Opzione 1: Let's Encrypt (Raccomandato)

```bash
# 1. Prima avvia solo nginx per ottenere certificati
cd /srv/aish.eu

# 2. Modifica temporaneamente nginx.prod.conf per HTTP only
# Commenta blocco HTTPS (server listen 443) nel file nginx/nginx.prod.conf

# 3. Avvia nginx
docker compose -f docker-compose.prod.yml up -d nginx

# 4. Genera certificati SSL
docker compose -f docker-compose.prod.yml run --rm certbot certonly \
  --webroot -w /var/www/certbot \
  -d aistrategyhub.eu \
  -d www.aistrategyhub.eu \
  --email davide@aistrategyhub.eu \
  --agree-tos \
  --no-eff-email

# 5. Verifica certificati creati
sudo ls -la /srv/aish.eu/ssl/letsencrypt/live/aistrategyhub.eu/

# 6. Ripristina configurazione nginx completa (rimuovi commenti blocco HTTPS)
vim nginx/nginx.prod.conf

# 7. Riavvia nginx
docker compose -f docker-compose.prod.yml restart nginx
```

### Opzione 2: Certificato Esistente

Se hai già certificati SSL:

```bash
# Copia certificati nella directory
sudo cp /path/to/fullchain.pem /srv/aish.eu/ssl/letsencrypt/live/aistrategyhub.eu/
sudo cp /path/to/privkey.pem /srv/aish.eu/ssl/letsencrypt/live/aistrategyhub.eu/
sudo cp /path/to/chain.pem /srv/aish.eu/ssl/letsencrypt/live/aistrategyhub.eu/

# Setta permessi
sudo chmod 600 /srv/aish.eu/ssl/letsencrypt/live/aistrategyhub.eu/*.pem
```

### Auto-renewal SSL

Aggiungi cronjob per rinnovo automatico:

```bash
# Apri crontab
crontab -e

# Aggiungi questa riga (rinnova ogni giorno alle 3 AM)
0 3 * * * cd /srv/aish.eu && docker compose -f docker-compose.prod.yml exec certbot certbot renew --quiet && docker compose -f docker-compose.prod.yml exec nginx nginx -s reload >> /srv/aish.eu/logs/ssl-renewal.log 2>&1
```

---

## Deployment

### First Deployment

```bash
cd /srv/aish.eu

# 1. Build immagini Docker
docker compose -f docker-compose.prod.yml build

# 2. Avvia database e redis prima (per inizializzazione)
docker compose -f docker-compose.prod.yml up -d postgres redis

# 3. Aspetta che siano healthy
docker compose -f docker-compose.prod.yml ps

# 4. Inizializza database con Alembic
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 5. (Opzionale) Seed dati iniziali
# docker compose -f docker-compose.prod.yml run --rm backend python -m app.scripts.seed_data

# 6. Avvia tutti i servizi
docker compose -f docker-compose.prod.yml up -d

# 7. Verifica che tutti i servizi siano healthy
docker compose -f docker-compose.prod.yml ps

# 8. Test health check
curl http://localhost/health
curl https://aistrategyhub.eu/health

# 9. Controlla logs
docker compose -f docker-compose.prod.yml logs -f
```

### Updates / Redeploy

Per aggiornamenti successivi:

```bash
cd /srv/aish.eu

# Pull latest code
git pull origin main

# Backup database PRIMA di ogni update
docker exec aistrategyhub-postgres pg_dump -U aistrategyhub aistrategyhub > backups/db_$(date +%Y%m%d_%H%M%S).sql

# Pull/rebuild immagini
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml build

# Run migrations
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Riavvia servizi (zero-downtime con rolling restart)
docker compose -f docker-compose.prod.yml up -d --no-deps --build backend
docker compose -f docker-compose.prod.yml up -d --no-deps --build frontend

# Verify
curl https://aistrategyhub.eu/health
```

### CI/CD Deployment (GitHub Actions)

Il workflow `.github/workflows/deploy.yml` automatizza il deployment:

1. Push su branch `main` triggera il workflow
2. Workflow esegue:
   - Backup database
   - Git pull
   - Docker compose pull & build
   - Database migrations
   - Container restart
   - Health checks

**Required GitHub Secrets:**
- `SSH_PRIVATE_KEY` - Chiave SSH per accesso VPS
- `SSH_HOST` - IP del Linode VPS
- `SSH_USER` - Username SSH (es. `deploy`)
- `WORK_DIR` - Directory progetto (`/srv/aish.eu`)

---

## Manutenzione

### Monitoring

```bash
# Verifica status containers
docker compose -f docker-compose.prod.yml ps

# Logs in tempo reale
docker compose -f docker-compose.prod.yml logs -f

# Logs specifico servizio
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx

# Resource usage
docker stats

# Disk usage
docker system df
```

### Database Backup

#### Backup Manuale

```bash
# Backup completo
docker exec aistrategyhub-postgres pg_dump -U aistrategyhub aistrategyhub > /srv/aish.eu/backups/db_$(date +%Y%m%d_%H%M%S).sql

# Backup compresso
docker exec aistrategyhub-postgres pg_dump -U aistrategyhub aistrategyhub | gzip > /srv/aish.eu/backups/db_$(date +%Y%m%d_%H%M%S).sql.gz
```

#### Backup Automatico

Aggiungi a crontab:

```bash
# Backup giornaliero alle 2 AM
0 2 * * * docker exec aistrategyhub-postgres pg_dump -U aistrategyhub aistrategyhub | gzip > /srv/aish.eu/backups/db_$(date +\%Y\%m\%d_\%H\%M\%S).sql.gz

# Cleanup backups vecchi (mantieni ultimi 30 giorni)
0 4 * * * find /srv/aish.eu/backups -name "db_*.sql.gz" -mtime +30 -delete
```

#### Restore Database

```bash
# Stop backend per evitare connessioni attive
docker compose -f docker-compose.prod.yml stop backend

# Restore da backup
cat /srv/aish.eu/backups/db_20260118_020000.sql | docker exec -i aistrategyhub-postgres psql -U aistrategyhub aistrategyhub

# Oppure da backup compresso
gunzip -c /srv/aish.eu/backups/db_20260118_020000.sql.gz | docker exec -i aistrategyhub-postgres psql -U aistrategyhub aistrategyhub

# Restart backend
docker compose -f docker-compose.prod.yml start backend
```

### Log Rotation

Configura logrotate per gestire logs:

```bash
# Crea file /etc/logrotate.d/aistrategyhub
sudo vim /etc/logrotate.d/aistrategyhub

# Contenuto:
/srv/aish.eu/logs/*/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    missingok
    create 0644 deploy deploy
    sharedscripts
    postrotate
        docker compose -f /srv/aish.eu/docker-compose.prod.yml exec nginx nginx -s reopen
    endscript
}
```

### Cleanup Docker

```bash
# Rimuovi immagini non utilizzate
docker image prune -a -f

# Rimuovi volumi non utilizzati
docker volume prune -f

# Pulizia completa sistema
docker system prune -a -f --volumes
```

---

## Troubleshooting

### Container non si avvia

```bash
# Verifica logs
docker compose -f docker-compose.prod.yml logs backend

# Verifica configurazione
docker compose -f docker-compose.prod.yml config

# Verifica .env
cat /srv/aish.eu/.env

# Riavvia container specifico
docker compose -f docker-compose.prod.yml restart backend
```

### Database Connection Errors

```bash
# Verifica che postgres sia healthy
docker compose -f docker-compose.prod.yml ps postgres

# Test connessione da backend
docker compose -f docker-compose.prod.yml exec backend python -c "from app.core.database import engine; print('OK')"

# Verifica password in .env
grep POSTGRES /srv/aish.eu/.env

# Logs postgres
docker compose -f docker-compose.prod.yml logs postgres
```

### SSL Certificate Issues

```bash
# Verifica certificati esistono
ls -la /srv/aish.eu/ssl/letsencrypt/live/aistrategyhub.eu/

# Test rinnovo manuale
docker compose -f docker-compose.prod.yml run --rm certbot renew --dry-run

# Rigenera certificati
docker compose -f docker-compose.prod.yml run --rm certbot certonly --force-renewal \
  --webroot -w /var/www/certbot \
  -d aistrategyhub.eu -d www.aistrategyhub.eu

# Reload nginx
docker compose -f docker-compose.prod.yml exec nginx nginx -s reload
```

### Health Check Fails

```bash
# Test health endpoint direttamente
curl -v http://localhost/health
curl -v https://aistrategyhub.eu/health

# Test backend diretto
docker compose -f docker-compose.prod.yml exec backend curl http://localhost:8000/health

# Test frontend diretto
docker compose -f docker-compose.prod.yml exec frontend wget -O- http://localhost:3000/health
```

### Out of Disk Space

```bash
# Verifica spazio
df -h

# Trova directory grandi
du -sh /srv/aish.eu/* | sort -h

# Cleanup logs vecchi
find /srv/aish.eu/logs -name "*.log" -mtime +7 -delete

# Cleanup backups vecchi
find /srv/aish.eu/backups -name "*.sql.gz" -mtime +30 -delete

# Cleanup Docker
docker system prune -a -f --volumes
```

### Performance Issues

```bash
# Verifica resource usage
docker stats

# Verifica PostgreSQL slow queries
docker compose -f docker-compose.prod.yml exec postgres psql -U aistrategyhub -c "SELECT * FROM pg_stat_activity WHERE state = 'active';"

# Ottimizza database
docker compose -f docker-compose.prod.yml exec postgres psql -U aistrategyhub -c "VACUUM ANALYZE;"

# Svuota cache Redis (attenzione!)
docker compose -f docker-compose.prod.yml exec redis redis-cli -a ${REDIS_PASSWORD} FLUSHDB
```

---

## Security Checklist

- [ ] Cambiato tutte le password di default in .env
- [ ] Generato SECRET_KEY e JWT_SECRET_KEY casuali e sicure
- [ ] Configurato firewall (UFW): solo porte 22, 80, 443 aperte
- [ ] Disabilitato root SSH login
- [ ] Configurato fail2ban per SSH
- [ ] SSL/TLS attivo con certificati validi
- [ ] Security headers configurati in Nginx
- [ ] Rate limiting attivo su API
- [ ] Backup automatici configurati
- [ ] Log rotation configurato
- [ ] Monitoring attivo (opzionale: Sentry, Datadog, etc.)
- [ ] 2FA abilitato per account critici

---

## Support

Per supporto o problemi:
- Email: davide@aistrategyhub.eu
- GitHub Issues: https://github.com/davidebotto/aistrategyhub/issues
- Documentazione: https://docs.aistrategyhub.eu (TODO)

---

**Last Updated**: 2026-01-18
**Version**: 0.1.0
