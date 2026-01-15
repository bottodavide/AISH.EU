# GUIDA: MEMORIA PERSISTENTE DEL PROGETTO

**Data**: 2026-01-15  
**Autore**: Claude (per Davide)

---

## PERCHÃ‰ QUESTA DOCUMENTAZIONE?

Claude (come altri LLM) non mantiene memoria tra sessioni o durante conversazioni molto lunghe. 
Per evitare di "perdere il filo" durante lo sviluppo, abbiamo creato un **sistema di memoria esterna** 
basato su file Markdown che documentano:

1. **Cosa** stiamo costruendo (requisiti)
2. **Come** lo stiamo costruendo (architettura)
3. **Dove siamo** nel processo (log sviluppo)
4. **Cosa manca** da fare (TODO)

---

## I 4 FILE CORE

### 1. `PROJECT_REQUIREMENTS.md`
**Scopo**: Single source of truth per requisiti di progetto

**Quando aggiornarlo**:
- âœ… Nuovo requisito identificato
- âœ… Modifica a requisito esistente
- âœ… Decisione tecnologica presa
- âœ… Nuova integrazione richiesta

**Cosa contiene**:
- Stack tecnologico
- FunzionalitÃ  richieste
- Security requirements
- Deployment specs
- Coding standards
- Performance targets

**Esempio aggiornamento**:
```markdown
## 12.2 Decisioni da Finalizzare
- [x] Backend: FastAPI (decisione presa 2026-01-16)
- [ ] CMS: Custom vs Payload CMS
```

---

### 2. `ARCHITECTURE.md`
**Scopo**: Documentare scelte architetturali e design del sistema

**Quando aggiornarlo**:
- âœ… Nuovo componente aggiunto
- âœ… Schema database modificato
- âœ… Nuovo endpoint API creato
- âœ… Integration pattern definito
- âœ… Cambio architetturale

**Cosa contiene**:
- Diagrammi architettura
- Database schema
- API design
- Security architecture
- Integration patterns
- Deployment architecture

**Esempio aggiornamento**:
```markdown
## 2.1 Entities Principali

Table: loyalty_points  <-- NUOVA TABELLA AGGIUNTA
- id (UUID, PK)
- user_id (UUID, FK â†’ users)
- points (INTEGER)
- earned_at (TIMESTAMP)
```

---

### 3. `DEVELOPMENT_LOG.md`
**Scopo**: Tracciare cronologicamente progresso e decisioni

**Quando aggiornarlo**:
- âœ… **OGNI GIORNO** di lavoro (anche breve update)
- âœ… Feature completata
- âœ… Bug risolto
- âœ… Decisione tecnica presa
- âœ… Issue incontrato

**Cosa contiene**:
- Log cronologico (diario di bordo)
- Decisioni tecniche e rationale
- Issues & risoluzioni
- Code snippets importanti
- Meeting notes
- Lessons learned

**Esempio aggiornamento**:
```markdown
### 2026-01-16 - Implementazione Auth Backend

#### Completato Oggi
- âœ… User model e migrations
- âœ… JWT token generation
- âœ… POST /auth/login endpoint
- âœ… Password hashing con bcrypt

#### Issues Risolti
**Issue #1: Token expiry validation failing**
- Descrizione: JWT verify sempre falliva anche con token valido
- Root Cause: Timezone mismatch (UTC vs local)
- Soluzione: Forzato UTC in tutte le date
- Commit: abc123

#### Prossimi Step Domani
- [ ] Implementare refresh token logic
- [ ] Email verification flow
- [ ] Rate limiting su /auth/login
```

---

### 4. `TODO.md`
**Scopo**: Task tracking e pianificazione lavoro

**Quando aggiornarlo**:
- âœ… **FINE DI OGNI SESSIONE** di lavoro
- âœ… Task completato (check âœ…)
- âœ… Nuovo task identificato
- âœ… PrioritÃ  cambiate
- âœ… Bug scoperto

**Cosa contiene**:
- Task organizzati per fase
- Checkbox per completamento
- PrioritÃ 
- Backlog funzionalitÃ 
- Bug tracker

**Esempio aggiornamento**:
```markdown
### Autenticazione & Users (Giorni 1-3)
- [x] User model e database schema
- [x] Password hashing (bcrypt)
- [x] JWT token generation/validation
- [ ] Redis session storage  <-- IN PROGRESS
- [ ] API Endpoints:
  - [x] POST /auth/register
  - [x] POST /auth/login
  - [ ] POST /auth/refresh
```

---

## WORKFLOW CONSIGLIATO

### All'inizio di ogni sessione con Claude:

1. **Carica i file rilevanti**:
   ```
   "Leggi PROJECT_REQUIREMENTS.md e DEVELOPMENT_LOG.md 
    per riprendere il contesto del progetto"
   ```

2. **Claude consulterÃ **:
   - Requisiti attuali
   - Stato attuale sviluppo
   - Decisioni giÃ  prese
   - TODO in sospeso

3. **Claude puÃ² partire informato** senza ripetere spiegazioni

---

### Durante lo sviluppo:

1. **Claude genera codice/soluzioni**

2. **Dopo ogni feature significativa**, chiedi:
   ```
   "Aggiorna DEVELOPMENT_LOG.md con quello che abbiamo fatto oggi"
   ```

3. **Se emerge nuovo requisito**:
   ```
   "Aggiungi questo requisito a PROJECT_REQUIREMENTS.md"
   ```

4. **Se cambia architettura**:
   ```
   "Aggiorna ARCHITECTURE.md con il nuovo endpoint/tabella/integrazione"
   ```

---

### Fine sessione:

1. **Aggiorna TODO.md**:
   ```
   "Segna come completati i task fatti oggi e aggiungi eventuali 
    nuovi task emersi in TODO.md"
   ```

2. **Sintesi nel DEVELOPMENT_LOG**:
   ```
   "Aggiungi entry in DEVELOPMENT_LOG con summary della sessione odierna"
   ```

---

## BEST PRACTICES

### âœ… DO

1. **Aggiorna incrementalmente**: Piccoli update frequenti > Grande update finale
2. **Sii specifico**: "Implementato JWT con bcrypt" > "Fatto auth"
3. **Traccia decisioni**: Spiega PERCHÃ‰ una scelta, non solo COSA
4. **Documenta workaround**: Se risolvi un bug strano, documentalo
5. **Link tra file**: Riferimenti incrociati ("Vedi ARCHITECTURE.md sezione 3.2")

### âŒ DON'T

1. **Non dimenticare di aggiornare**: File obsoleti = memoria falsa
2. **Non duplicare info**: Un posto per ogni informazione
3. **Non essere vago**: "Fatto roba API" non aiuta
4. **Non solo TODO**: Il log cronologico Ã¨ altrettanto importante

---

## COMANDI UTILI PER CLAUDE

### Riprendere contesto:
```
"Carica PROJECT_REQUIREMENTS.md, ARCHITECTURE.md, e DEVELOPMENT_LOG.md 
 per riprendere il progetto da dove ci eravamo fermati"
```

### Update dopo lavoro:
```
"Aggiorna DEVELOPMENT_LOG.md con:
 - Completato: [elenco feature]
 - Issue risolti: [elenco problemi]
 - TODO domani: [prossimi step]
 
 Poi aggiorna TODO.md checkando i task completati"
```

### Revisione architettura:
```
"In base al codice che abbiamo scritto oggi, aggiorna 
 ARCHITECTURE.md con i nuovi endpoint API e modifiche database schema"
```

### Planning prossima sessione:
```
"Leggi TODO.md e suggerisci quale fase/task affrontare nella 
 prossima sessione, considerando dipendenze e prioritÃ "
```

---

## ESEMPIO CONVERSAZIONE TIPO

**Tu**: "Ciao Claude, riprendi il progetto sito e-commerce"

**Claude**: 
```
[Carica PROJECT_REQUIREMENTS.md, DEVELOPMENT_LOG.md, TODO.md]

Perfetto Davide! Vedo che:

- Ultimo lavoro: 2026-01-15, creazione documentazione
- Decisione pending: Backend framework (raccomandato FastAPI)
- Prossimo step: Iniziare Fase 1 setup progetto
- TODO prioritÃ  alta: Decisione finale backend + struttura Docker

Vuoi procedere con:
1. Confermare scelta FastAPI e iniziare setup backend?
2. Oppure preferisci iniziare dal frontend con Next.js?
3. O setup Docker completo prima?
```

**Tu**: "Andiamo con FastAPI. Setup backend e database."

**Claude**:
```
[Genera struttura progetto backend FastAPI]
[Crea Dockerfile, requirements.txt, database schema, ecc.]

Ok! Ho creato:
- /backend con struttura FastAPI
- Database schema in models/
- Docker setup completo
- Primi endpoint auth

Ora aggiorno la documentazione...
[Aggiorna DEVELOPMENT_LOG.md, TODO.md, ARCHITECTURE.md]

Fatto! Prossimi step suggeriti:
- Test locale con docker-compose up
- Implementare logica JWT completa
```

---

## MANUTENZIONE DOCUMENTAZIONE

### Settimanale
- [ ] Review TODO.md (riprioritizzare se necessario)
- [ ] Cleanup task completati da >1 settimana
- [ ] Verifica coerenza tra i 4 file

### Al completamento milestone
- [ ] Update versione in tutti i file
- [ ] Summary milestone in DEVELOPMENT_LOG
- [ ] Planning prossima milestone in TODO

### Pre-deploy
- [ ] Verifica tutti i requisiti in PROJECT_REQUIREMENTS
- [ ] Check ARCHITECTURE.md riflette implementazione reale
- [ ] Security checklist in TODO completata

---

## TROUBLESHOOTING

**Problema**: "Claude si dimentica di cose dette 10 messaggi fa"
- âœ… Soluzione: Chiedi a Claude di rileggere il file rilevante

**Problema**: "I file sono troppo lunghi da caricare ogni volta"
- âœ… Soluzione: Carica solo file pertinenti alla sessione corrente
- ðŸ’¡ Esempio: Solo TODO.md + DEVELOPMENT_LOG.md per quick check

**Problema**: "Claude dÃ  info contrastante con la documentazione"
- âœ… Soluzione: Ricorda a Claude: "Verifica con PROJECT_REQUIREMENTS.md"
- ðŸ’¡ I file sono source of truth, non la memoria di Claude

**Problema**: "Non so quale file aggiornare"
- âœ… Regola generale:
  - Nuovo requisito â†’ PROJECT_REQUIREMENTS.md
  - Come funziona â†’ ARCHITECTURE.md
  - Cosa abbiamo fatto â†’ DEVELOPMENT_LOG.md
  - Cosa fare â†’ TODO.md

---

## TEMPLATE VELOCI

### Daily Log Entry
```markdown
### YYYY-MM-DD - [Titolo sessione]

#### Completato Oggi
- âœ… Task 1
- âœ… Task 2

#### Issues
**Issue #N**: [Descrizione]
- Root Cause: 
- Soluzione: 

#### Prossimi Step
- [ ] Task A
- [ ] Task B
```

### Nuova Decisione Tecnica
```markdown
### [Nome Decisione]: [DA DECIDERE / DECISO]
**Opzioni**:
- **Opzione A**
  - âœ… Pro: 
  - âŒ Con: 

- **Opzione B**
  - âœ… Pro: 
  - âŒ Con: 

**Decisione**: [Scelta] - Motivo: [Rationale]
**Data**: YYYY-MM-DD
```

---

## CONCLUSIONE

Questa documentazione Ã¨ il "cervello esterno" del progetto. 

**Investimento tempo**:
- 5-10 min fine ogni sessione per update
- Previene ore perse a ricostruire contesto

**Benefici**:
- âœ… ContinuitÃ  tra sessioni
- âœ… Onboarding rapido (anche per te dopo pause)
- âœ… Base per documentazione finale
- âœ… Audit trail decisioni tecniche

**Ricorda**: File aggiornati = Claude informato = Sviluppo efficiente

---

**Versione**: 1.0  
**Ultimo Update**: 2026-01-15
