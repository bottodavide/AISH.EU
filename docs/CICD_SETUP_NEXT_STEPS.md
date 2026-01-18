# CI/CD Setup - Next Steps

## ✅ Completato

- [x] GitHub Actions workflows creati e pushati
- [x] Test Suite workflow attivo
- [x] Code Quality workflow attivo
- [x] README con status badges
- [x] GitHub templates (PR, issues)
- [x] Documentazione completa CI/CD

**Status**: https://github.com/bottodavide/AISH.EU/actions

---

## 🎯 Prossimi Step

### 1. Codecov Setup (Raccomandato) ⭐

Codecov fornisce visualizzazione grafica del coverage e commenti automatici sulle PR.

**Setup (5 minuti)**:

1. **Registrati su Codecov**
   - Vai su: https://codecov.io
   - Click "Sign up with GitHub"
   - Autorizza con il tuo account GitHub

2. **Aggiungi Repository**
   - Una volta loggato, click su "+ Add new repository"
   - Cerca "AISH.EU" nella lista
   - Click "Setup repo"

3. **Copia Token**
   - Codecov mostrerà un token tipo: `a1b2c3d4-e5f6-7890-abcd-ef1234567890`
   - Copia questo token

4. **Aggiungi Secret su GitHub**
   ```bash
   # Via browser
   1. Vai su: https://github.com/bottodavide/AISH.EU/settings/secrets/actions
   2. Click "New repository secret"
   3. Name: CODECOV_TOKEN
   4. Value: [incolla il token copiato]
   5. Click "Add secret"

   # Oppure via CLI
   gh secret set CODECOV_TOKEN --repo bottodavide/AISH.EU
   # Incolla il token quando richiesto
   ```

5. **Verifica**
   - Fai un nuovo push o trigger manualmente il workflow
   - Dopo i test, vai su: https://codecov.io/gh/bottodavide/AISH.EU
   - Dovresti vedere il coverage report

**Benefici**:
- ✅ Coverage badge funzionante nel README
- ✅ Grafici coverage per file/modulo
- ✅ Commenti automatici sulle PR con coverage diff
- ✅ Tracking coverage nel tempo

---

### 2. Deploy Automation Setup (Opzionale - solo quando pronto per prod)

Setup per deploy automatico su Linode VPS quando fai push su `main`.

**Prerequisiti**:
- VPS Linode configurato
- Docker e docker-compose installati sul VPS
- Repository clonato su VPS: `/opt/aistrategyhub`

**Setup (15 minuti)**:

#### A. Genera SSH Key per Deploy

```bash
# Sul tuo Mac
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/aish_deploy

# Non impostare passphrase (premi Enter quando richiesta)
```

#### B. Aggiungi Chiave Pubblica al VPS

```bash
# Copia chiave pubblica sul VPS
ssh-copy-id -i ~/.ssh/aish_deploy.pub user@your-vps-ip

# Oppure manualmente:
cat ~/.ssh/aish_deploy.pub
# Copia l'output

# SSH nel VPS
ssh user@your-vps-ip

# Aggiungi chiave a authorized_keys
echo "ssh-ed25519 AAAA... github-actions-deploy" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

#### C. Test Connessione SSH

```bash
# Dal tuo Mac
ssh -i ~/.ssh/aish_deploy user@your-vps-ip

# Se funziona, esci
exit
```

#### D. Aggiungi Secrets su GitHub

```bash
# 1. DEPLOY_SSH_KEY (chiave privata)
cat ~/.ssh/aish_deploy
# Copia TUTTO l'output (incluso -----BEGIN... e -----END...)

# Vai su: https://github.com/bottodavide/AISH.EU/settings/secrets/actions
# New secret:
# Name: DEPLOY_SSH_KEY
# Value: [incolla la chiave privata]

# 2. VPS_HOST (IP del VPS)
# New secret:
# Name: VPS_HOST
# Value: 123.45.67.89  (il tuo IP Linode)

# 3. VPS_USER (username SSH)
# New secret:
# Name: VPS_USER
# Value: root  (o il tuo username)
```

#### E. Prepara VPS per Deploy

```bash
# SSH nel VPS
ssh user@your-vps-ip

# Crea directory progetto
sudo mkdir -p /opt/aistrategyhub
sudo chown $USER:$USER /opt/aistrategyhub

# Clone repository
cd /opt
git clone https://github.com/bottodavide/AISH.EU.git aistrategyhub
cd aistrategyhub

# Crea directory backup
sudo mkdir -p /backup
sudo chown $USER:$USER /backup

# Crea .env production (se non esiste)
cp .env.example .env
nano .env  # Configura variabili production

# Setup docker-compose (se non esiste)
# ... configurazione docker-compose.yml ...
```

#### F. Test Deploy Manuale

```bash
# Dal tuo Mac, trigger manual deploy
gh workflow run deploy.yml --repo bottodavide/AISH.EU

# Oppure via browser:
# https://github.com/bottodavide/AISH.EU/actions/workflows/deploy.yml
# Click "Run workflow"
```

**Benefici**:
- ✅ Deploy automatico su push a `main`
- ✅ Backup database automatico prima di ogni deploy
- ✅ Migrations automatiche
- ✅ Health check post-deploy
- ✅ Rollback automatico in caso di errore

---

### 3. Branch Protection Rules (Raccomandato)

Proteggi il branch `main` per evitare push diretti senza review.

**Setup (2 minuti)**:

1. Vai su: https://github.com/bottodavide/AISH.EU/settings/branches
2. Click "Add branch protection rule"
3. Branch name pattern: `main`
4. Seleziona:
   - [x] Require a pull request before merging
   - [x] Require status checks to pass before merging
     - Cerca e seleziona: "Backend Tests"
     - Cerca e seleziona: "Backend Linting"
   - [x] Require branches to be up to date before merging
   - [x] Include administrators (opzionale)
5. Click "Create"

**Benefici**:
- ✅ Tutti i cambi passano per PR
- ✅ Review obbligatoria prima del merge
- ✅ Test devono passare prima del merge
- ✅ Previene errori accidentali

---

### 4. Dependabot Setup (Opzionale ma raccomandato)

Aggiorna automaticamente dipendenze con PR automatiche.

**Setup (1 minuto)**:

Crea file `.github/dependabot.yml`:

```yaml
version: 2
updates:
  # Backend Python dependencies
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "backend"

  # Frontend npm dependencies
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "dependencies"
      - "frontend"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    labels:
      - "dependencies"
      - "ci-cd"
```

Commit e push:
```bash
git add .github/dependabot.yml
git commit -m "ci: Add Dependabot configuration"
git push origin main
```

**Benefici**:
- ✅ Dipendenze sempre aggiornate
- ✅ Security updates automatici
- ✅ PR automatiche con changelog
- ✅ Test automatici sulle PR di update

---

### 5. Notifiche Slack/Discord (Opzionale)

Ricevi notifiche quando workflow falliscono.

**Setup Slack**:

1. Crea Slack Incoming Webhook:
   - Vai su: https://api.slack.com/messaging/webhooks
   - Crea webhook per il tuo workspace
   - Copia webhook URL

2. Aggiungi secret su GitHub:
   ```bash
   gh secret set SLACK_WEBHOOK_URL --repo bottodavide/AISH.EU
   # Incolla webhook URL
   ```

3. Aggiungi step ai workflow (esempio per `test.yml`):
   ```yaml
   - name: Notify Slack on failure
     if: failure()
     uses: slackapi/slack-github-action@v1.24.0
     with:
       payload: |
         {
           "text": "❌ Test Suite failed on main branch",
           "blocks": [
             {
               "type": "section",
               "text": {
                 "type": "mrkdwn",
                 "text": "*Test Suite Failed*\nCommit: ${{ github.sha }}\nAuthor: ${{ github.actor }}\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"
               }
             }
           ]
         }
     env:
       SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
   ```

---

## 🎯 Priorità Raccomandata

### Immediate (oggi):
1. ✅ **Codecov Setup** (5 min) - Coverage visualization
2. ✅ **Branch Protection** (2 min) - Previeni errori

### Short-term (questa settimana):
3. ⏳ **Dependabot** (1 min) - Security updates
4. ⏳ **Review workflow runs** - Verifica tutto green

### Medium-term (quando pronto per prod):
5. 📅 **Deploy Automation** (15 min) - Solo quando hai VPS pronto
6. 📅 **Notifiche** (opzionale) - Se vuoi alerts

---

## 📊 Verifica Status

```bash
# Check workflow runs
gh run list --repo bottodavide/AISH.EU

# Watch specific run
gh run watch <run-id> --repo bottodavide/AISH.EU

# View README badges
open https://github.com/bottodavide/AISH.EU

# Check coverage (dopo Codecov setup)
open https://codecov.io/gh/bottodavide/AISH.EU
```

---

## 🆘 Troubleshooting

### Workflow Failed - Come Debuggare

```bash
# 1. Vedi lista runs
gh run list --repo bottodavide/AISH.EU

# 2. Vedi dettagli run fallito
gh run view <run-id> --repo bottodavide/AISH.EU --log-failed

# 3. Re-run workflow
gh run rerun <run-id> --repo bottodavide/AISH.EU

# 4. Run localmente i test
cd backend
pytest -v
```

### Test Falliscono su CI ma non in locale

Possibili cause:
- Environment variables diverse
- PostgreSQL version diversa
- Timezone differences
- Dependency versions

Soluzione:
```bash
# Controlla file .env.test nel workflow
# Verifica PostgreSQL service version
# Run tests con --tb=short per vedere stack trace
```

### Deploy Failed

```bash
# 1. Verifica secrets configurati
gh secret list --repo bottodavide/AISH.EU

# 2. Test SSH connection dal tuo Mac
ssh -i ~/.ssh/aish_deploy user@vps-ip

# 3. Check VPS /opt/aistrategyhub directory exists
ssh user@vps-ip "ls -la /opt/aistrategyhub"
```

---

## 📝 Checklist Completa

- [x] GitHub Actions workflows pushati
- [x] Test Suite workflow attivo
- [x] Code Quality workflow attivo
- [ ] Codecov setup (raccomandato)
- [ ] Branch protection configurato (raccomandato)
- [ ] Dependabot configurato (opzionale)
- [ ] Deploy secrets configurati (solo per prod)
- [ ] VPS preparato per deploy (solo per prod)
- [ ] Notifiche configurate (opzionale)

---

**Next Step Immediato**: Setup Codecov per avere coverage badge funzionante! 🎯

https://codecov.io
