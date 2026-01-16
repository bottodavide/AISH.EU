# Configurazione Stripe per AI Strategy Hub

## Overview

L'applicazione utilizza Stripe per gestire i pagamenti dei servizi di consulenza.

## Setup Stripe

### 1. Crea un Account Stripe

1. Vai su [https://stripe.com](https://stripe.com)
2. Crea un account (puoi usare la modalità Test senza carta di credito)
3. Accedi alla Dashboard: [https://dashboard.stripe.com](https://dashboard.stripe.com)

### 2. Ottieni le API Keys

#### Modalità Test (per sviluppo)

1. Vai su: [https://dashboard.stripe.com/test/apikeys](https://dashboard.stripe.com/test/apikeys)
2. Copia le seguenti chiavi:
   - **Publishable key** (inizia con `pk_test_`)
   - **Secret key** (inizia con `sk_test_`) - **NON CONDIVIDERE MAI QUESTA CHIAVE**

#### Modalità Live (per produzione)

1. Vai su: [https://dashboard.stripe.com/apikeys](https://dashboard.stripe.com/apikeys)
2. Copia le seguenti chiavi:
   - **Publishable key** (inizia con `pk_live_`)
   - **Secret key** (inizia con `sk_live_`)

### 3. Configura il Backend

Modifica `/backend/.env`:

```env
# Stripe Configuration
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_WEBHOOK_SECRET=  # Configurato dopo (step 4)
```

### 4. Configura il Frontend

Modifica `/frontend/.env.local`:

```env
# Stripe Configuration
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
```

**NOTA:** La publishable key è sicura da esporre nel frontend (è pubblica per design).

### 5. Configura Webhook (Opzionale ma Raccomandato)

I webhook permettono a Stripe di notificare il backend quando un pagamento ha successo.

#### Sviluppo Locale (con Stripe CLI)

1. Installa Stripe CLI: [https://stripe.com/docs/stripe-cli](https://stripe.com/docs/stripe-cli)

2. Effettua login:
   ```bash
   stripe login
   ```

3. Forward webhook a localhost:
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/payments/webhook
   ```

4. Copia il webhook secret mostrato (inizia con `whsec_`) e aggiungilo al backend `.env`:
   ```env
   STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET
   ```

#### Produzione

1. Vai su: [https://dashboard.stripe.com/webhooks](https://dashboard.stripe.com/webhooks)
2. Clicca "Add endpoint"
3. URL endpoint: `https://tuodominio.com/api/v1/payments/webhook`
4. Seleziona eventi da ascoltare:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `payment_intent.canceled`
   - `charge.refunded`
5. Copia il webhook secret e aggiungilo al backend `.env`

### 6. Testa il Pagamento

#### Test Cards Stripe

Stripe fornisce carte di test per simulare pagamenti:

- **Successo:** `4242 4242 4242 4242`
- **Richiede autenticazione:** `4000 0025 0000 3155`
- **Carta declinata:** `4000 0000 0000 9995`

**Dettagli carte test:**
- Data scadenza: Qualsiasi data futura (es: 12/34)
- CVV: Qualsiasi 3 cifre (es: 123)
- ZIP: Qualsiasi 5 cifre (es: 12345)

#### Flow di Test

1. Vai su: `http://localhost:3000/servizi`
2. Seleziona un servizio
3. Clicca "Acquista Ora"
4. Compila il form di checkout
5. Inserisci i dati della carta test
6. Completa il pagamento
7. Verifica che l'ordine sia marcato come "Pagato"

### 7. Verifica Pagamenti nella Dashboard

1. Vai su: [https://dashboard.stripe.com/test/payments](https://dashboard.stripe.com/test/payments)
2. Dovresti vedere i pagamenti test effettuati

## Eventi Webhook Gestiti

Il backend gestisce automaticamente i seguenti eventi Stripe:

| Evento | Azione |
|--------|--------|
| `payment_intent.succeeded` | Order status → PAID |
| `payment_intent.payment_failed` | Payment status → FAILED (logged) |
| `payment_intent.canceled` | Order status → CANCELLED |
| `charge.refunded` | Order status → REFUNDED |

## Sicurezza

### ✅ Best Practices

- ✅ **Secret key** salvata solo nel backend (mai nel frontend)
- ✅ **Webhook signature** verificata per ogni richiesta
- ✅ Importi gestiti lato backend (frontend non può manipolare prezzi)
- ✅ Stripe Elements per input sicuro carte (PCI compliant)
- ✅ HTTPS obbligatorio in produzione

### ⚠️ Importante

- **NON** committare mai le chiavi Stripe in Git
- **NON** esporre mai la Secret Key nel frontend
- **NON** permettere al frontend di decidere gli importi

## Troubleshooting

### Webhook non ricevuto

1. Verifica che `STRIPE_WEBHOOK_SECRET` sia configurato
2. Controlla i log del backend per errori di signature
3. Usa `stripe listen` per debuggare in locale

### Pagamento fallisce senza motivo

1. Controlla la console browser per errori JavaScript
2. Verifica che `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` sia configurato
3. Controlla che le chiavi siano della stessa modalità (test/live)

### "Stripe not configured" error

1. Verifica che `STRIPE_SECRET_KEY` sia presente nel backend `.env`
2. Riavvia il backend dopo aver modificato `.env`

## Link Utili

- **Dashboard Stripe:** [https://dashboard.stripe.com](https://dashboard.stripe.com)
- **Documentazione:** [https://stripe.com/docs](https://stripe.com/docs)
- **Test Cards:** [https://stripe.com/docs/testing](https://stripe.com/docs/testing)
- **Webhook Testing:** [https://stripe.com/docs/webhooks/test](https://stripe.com/docs/webhooks/test)

## Supporto

Per domande o problemi con l'integrazione Stripe:
1. Consulta la documentazione ufficiale Stripe
2. Verifica i log del backend (`tail -f backend/logs/*.log`)
3. Usa `stripe listen` per debuggare webhook in locale
