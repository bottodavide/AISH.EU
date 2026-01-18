# Deployment Action Plan - Linode VPS

**Data:** 2026-01-18
**Server:** 172.235.235.144 (Linode ArchLinux)
**Dominio:** aistrategyhub.eu

---

## 📊 Situazione Attuale

### ✅ Locale (Mac) - TUTTO OK

**Frontend Build Status:**
```bash
✓ Compiled successfully
✓ Build completes (47/47 pages)
⚠ 4 warnings su useSearchParams (non bloccanti)
```

**Dipendenze installate:**
- ✅ autoprefixer 10.4.17
- ✅ postcss 8.4.33
- ✅ tailwindcss 3.4.1
- ✅ clsx, tailwind-merge, js-cookie
- ✅ class-variance-authority

**File creati:**
- ✅ src/lib/utils.ts
- ✅ src/lib/cookies.ts
- ✅ src/components/Navigation.tsx
- ✅ src/components/Footer.tsx
- ✅ src/components/ui/card.tsx
- ✅ src/components/ui/badge.tsx

**Git Status:**
- ✅ Ultimo commit: 2abbaa5 (pushed to main)
- ✅ Precedente commit con frontend fixes: 1c93d8e

### ⚠️ Linode VPS - DA AGGIORNARE

**Problema:** Il server Linode probabilmente ha ancora la versione vecchia del codice.

**Azioni richieste:**
1. Pull del codice aggiornato da GitHub
2. Rebuild del container Docker
3. Restart dei servizi

---

## 🎯 Action Plan per Linode

### Step 1: SSH al Server

```bash
ssh deploy@172.235.235.144
```

### Step 2: Verifica Stato Repository

```bash
cd /srv/aish.eu

# Check current commit
git log --oneline -5

# Check if updates available
git fetch origin main
git status
```

**Expected Output:**
```
On branch main
Your branch is behind 'origin/main' by X commits
```

### Step 3: Pull Latest Code

```bash
# Pull latest changes (includes frontend fixes + test reports)
git pull origin main
```

**Questo porta:**
- Frontend fixes (commit 1c93d8e)
- Test coverage reports (commit 2abbaa5)
- Security fixes (console.log rimossi)
- Codebase documentation

### Step 4: Rebuild Frontend Container

**Option A: Full Rebuild (Raccomandato)**
```bash
# Stop container
docker compose -f docker-compose.prod.yml down

# Rebuild frontend stage (force no cache)
docker compose -f docker-compose.prod.yml build --no-cache frontend

# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check logs
docker compose -f docker-compose.prod.yml logs -f frontend
```

**Option B: Quick Rebuild (Se Option A fallisce)**
```bash
# Rebuild solo frontend senza cache
docker compose -f docker-compose.prod.yml build --no-cache

# Restart
docker compose -f docker-compose.prod.yml up -d --force-recreate
```

### Step 5: Verify Deployment

```bash
# Check container status
docker compose -f docker-compose.prod.yml ps

# Check frontend is running
curl -I http://localhost:3000

# Check via public domain
curl -I https://aistrategyhub.eu

# View frontend logs
docker compose -f docker-compose.prod.yml logs frontend --tail=50

# View all logs
docker compose -f docker-compose.prod.yml logs --tail=100
```

**Expected:**
- ✅ Container status: Up
- ✅ HTTP 200 response
- ✅ No module errors in logs

---

## 🔧 Troubleshooting

### Problema: "Cannot find module 'autoprefixer'"

**Causa:** node_modules non installati o vecchi nel container

**Fix:**
```bash
# Rebuild con --no-cache per forzare npm install
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d
```

### Problema: "Module not found: @/components/Navigation"

**Causa:** File non copiati nel container durante build

**Verifica file esistono:**
```bash
ls -la frontend/src/components/Navigation.tsx
ls -la frontend/src/components/Footer.tsx
ls -la frontend/src/lib/utils.ts
ls -la frontend/src/lib/cookies.ts
```

**Fix:** Rebuild con --no-cache

### Problema: Build molto lento

**Causa:** Linode VPS con risorse limitate

**Soluzione:**
```bash
# Check available resources
free -h
df -h

# If low memory, temporarily stop other services
docker compose -f docker-compose.prod.yml stop backend
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d
```

### Problema: Errori di permessi

```bash
# Fix ownership
sudo chown -R deploy:deploy /srv/aish.eu

# Rebuild
docker compose -f docker-compose.prod.yml build --no-cache frontend
docker compose -f docker-compose.prod.yml up -d
```

---

## 📋 Checklist Deployment

### Pre-Deployment
- [ ] Git pull completato
- [ ] Verificato commit 1c93d8e presente
- [ ] Verificato commit 2abbaa5 presente

### Build
- [ ] Docker build --no-cache eseguito
- [ ] Build completato senza errori
- [ ] Container started successfully

### Post-Deployment
- [ ] Container in stato "Up"
- [ ] HTTP 200 su http://localhost:3000
- [ ] HTTPS 200 su https://aistrategyhub.eu
- [ ] No errors in `docker logs`
- [ ] Homepage carica correttamente
- [ ] Navigation e Footer visibili

### Verification Tests
- [ ] Homepage: https://aistrategyhub.eu
- [ ] Admin login: https://aistrategyhub.eu/login
- [ ] Services page: https://aistrategyhub.eu/servizi
- [ ] Blog page: https://aistrategyhub.eu/blog
- [ ] Contact: https://aistrategyhub.eu/contatti

---

## 🚨 Fallback Plan

Se il deployment fallisce:

### Plan A: Rollback
```bash
# Rollback to previous commit
git log --oneline -10  # Find last working commit
git reset --hard <commit-hash>

# Rebuild
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

### Plan B: Manual Fix in Container
```bash
# Access container
docker compose -f docker-compose.prod.yml exec frontend sh

# Check if files exist
ls /app/frontend/src/components/
ls /app/frontend/src/lib/

# Check node_modules
ls /app/frontend/node_modules/ | grep -E "autoprefixer|postcss|tailwind"

# Exit container
exit
```

### Plan C: Fresh Build
```bash
# Remove all containers and volumes
docker compose -f docker-compose.prod.yml down -v

# Remove old images
docker images | grep aistrategyhub | awk '{print $3}' | xargs docker rmi -f

# Fresh build
docker compose -f docker-compose.prod.yml build --no-cache
docker compose -f docker-compose.prod.yml up -d
```

---

## 📊 Expected Timeline

| Step | Time | Total |
|------|------|-------|
| SSH + Git Pull | 1 min | 1 min |
| Docker Build (no cache) | 10-15 min | 16 min |
| Container Start | 1 min | 17 min |
| Verification | 2 min | 19 min |
| **TOTAL** | | **~20 minuti** |

---

## 💡 Optimization Tips

### Speed Up Future Deployments

1. **Use Build Cache** (se no dependency changes):
   ```bash
   # No --no-cache flag
   docker compose -f docker-compose.prod.yml build frontend
   ```

2. **Multi-stage Build** (già implementato):
   - Stage 1: Dependencies (cached)
   - Stage 2: Build (quando cambia code)
   - Stage 3: Runtime (minimal)

3. **Parallel Builds** (se rebuild tutto):
   ```bash
   docker compose -f docker-compose.prod.yml build --parallel
   ```

---

## 🔍 Monitoring Post-Deployment

### Check Logs Continuously
```bash
# Follow all logs
docker compose -f docker-compose.prod.yml logs -f

# Follow frontend only
docker compose -f docker-compose.prod.yml logs -f frontend

# Last 100 lines
docker compose -f docker-compose.prod.yml logs --tail=100
```

### Check Resource Usage
```bash
# Container stats
docker stats

# Disk usage
df -h

# Memory usage
free -h
```

### Check Nginx
```bash
# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Or from container
docker compose -f docker-compose.prod.yml logs nginx
```

---

## 📝 Post-Deployment Actions

### 1. Verify All Features Work
- [ ] User registration
- [ ] User login
- [ ] Admin panel access
- [ ] Service pages load
- [ ] Blog posts display
- [ ] Contact form works

### 2. Check Performance
```bash
# Response time test
time curl -I https://aistrategyhub.eu

# Expected: < 500ms
```

### 3. Test Critical Paths
- [ ] Checkout flow (if payments enabled)
- [ ] File uploads
- [ ] Email sending
- [ ] AI Chatbot (if enabled)

### 4. Update Documentation
- [ ] Update CHANGELOG.md with deployment
- [ ] Mark deployment in project tracker
- [ ] Notify team if applicable

---

## 🎯 Success Criteria

✅ **Deployment Successful When:**
1. ✅ All containers running (docker ps shows "Up")
2. ✅ Frontend accessible via HTTPS
3. ✅ No errors in docker logs
4. ✅ Homepage loads in <2 seconds
5. ✅ Navigation and Footer visible
6. ✅ Admin login works
7. ✅ No console errors in browser
8. ✅ Mobile responsive works

---

## 📞 Support

**Se problemi persistono:**

1. **Check Logs:**
   ```bash
   docker compose -f docker-compose.prod.yml logs frontend > frontend-logs.txt
   ```

2. **Check Environment:**
   ```bash
   cat .env | grep -v PASSWORD
   ```

3. **Restart Services:**
   ```bash
   docker compose -f docker-compose.prod.yml restart
   ```

4. **Full Restart:**
   ```bash
   docker compose -f docker-compose.prod.yml down
   docker compose -f docker-compose.prod.yml up -d
   ```

---

## 🚀 Quick Start (TL;DR)

```bash
# SSH
ssh deploy@172.235.235.144

# Update code
cd /srv/aish.eu && git pull origin main

# Rebuild
docker compose -f docker-compose.prod.yml build --no-cache frontend

# Restart
docker compose -f docker-compose.prod.yml up -d

# Verify
curl -I https://aistrategyhub.eu
docker compose -f docker-compose.prod.yml logs frontend --tail=50
```

**Expected Time:** 20 minuti

---

**Documento creato:** 2026-01-18 21:45
**Next Action:** SSH to Linode and execute deployment steps
