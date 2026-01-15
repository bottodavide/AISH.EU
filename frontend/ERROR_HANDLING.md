# Sistema di Gestione Errori - AI Strategy Hub

Sistema centralizzato per la gestione degli errori con pagina dedicata e codici tracciamento.

## 📋 Componenti

### 1. Pagina Errore (`/error`)
Pagina dedicata che mostra:
- **Titolo e descrizione** user-friendly
- **Codice errore** univoco per tracking
- **Timestamp** e percorso dove è avvenuto l'errore
- **ID tracciamento** formato: `ERR-[CODE]-[DATE]-[TIME]`
- **Azioni suggerite** basate sul tipo di errore
- **Dettagli tecnici** (collassabili per sviluppatori)
- **Pulsante copia** per condividere info errore

### 2. Error Handler Utility (`lib/error-handler.ts`)
Funzioni per gestire errori in modo uniforme:

```typescript
// Redirect a pagina errore
handleApiError(error);

// Handler specifici
handleChatError(error);
handleUploadError(error);
handleAuthError(error);

// Ottieni messaggio errore senza redirect
const message = getErrorMessage(error);

// Wrapper async con error handling
const result = await withErrorHandler(() => apiCall());
```

### 3. Error Boundary (`components/ErrorBoundary.tsx`)
Cattura errori React non gestiti e reindirizza automaticamente.

### 4. API Client Interceptor
Logging automatico errori API in development.

## 🏷️ Codici Errore

| Codice | Descrizione | Uso |
|--------|-------------|-----|
| `UNKNOWN_ERROR` | Errore sconosciuto | Fallback generico |
| `NETWORK_ERROR` | Errore connessione | No response dal server |
| `AUTH_ERROR` | Autenticazione | 401 Unauthorized |
| `PERMISSION_ERROR` | Permessi | 403 Forbidden |
| `NOT_FOUND` | Risorsa non trovata | 404 Not Found |
| `VALIDATION_ERROR` | Dati non validi | 400 Bad Request |
| `SERVER_ERROR` | Errore server | 500, 502, 503, 504 |
| `RATE_LIMIT` | Troppi tentativi | 429 Too Many Requests |
| `CHAT_ERROR` | Errore chatbot AI | Specifico per chat |
| `UPLOAD_ERROR` | Errore caricamento | Specifico per upload |

## 🚀 Utilizzo

### In un Component

```typescript
import { handleApiError, getErrorMessage } from '@/lib/error-handler';

// Opzione 1: Redirect a pagina errore per errori gravi
try {
  await apiClient.post('/endpoint', data);
} catch (error) {
  handleApiError(error); // Redirect automatico
}

// Opzione 2: Mostra errore inline per validazione
try {
  await apiClient.post('/endpoint', data);
} catch (error) {
  setError(getErrorMessage(error)); // Solo messaggio
}

// Opzione 3: Mix (usato in ChatWidget)
try {
  await apiClient.post('/endpoint', data);
} catch (error) {
  // Errori gravi → redirect
  if (!error.response || error.response.status >= 500) {
    handleChatError(error);
    return;
  }

  // Errori minori → inline
  setError(getErrorMessage(error));
}
```

### Error Boundary

Già configurato nel layout principale. Cattura automaticamente:
- Errori di rendering
- Errori lifecycle
- Errori in event handlers

## 🎨 Personalizzazione

### Aggiungere Nuovo Codice Errore

1. Aggiungi a `ErrorCode` type in `error-handler.ts`:
```typescript
export type ErrorCode =
  | 'EXISTING_CODES'
  | 'NEW_ERROR_CODE'; // ← Nuovo
```

2. Aggiungi mapping in `error/page.tsx`:
```typescript
const titles: Record<string, string> = {
  // ...existing
  NEW_ERROR_CODE: 'Titolo Errore',
};

const descriptions: Record<string, string> = {
  // ...existing
  NEW_ERROR_CODE: 'Descrizione dettagliata',
};

const actions: Record<string, string[]> = {
  // ...existing
  NEW_ERROR_CODE: [
    'Azione suggerita 1',
    'Azione suggerita 2',
  ],
};
```

### Cambiare Stile Pagina Errore

Modifica `/app/error/page.tsx`. Utilizza:
- Tailwind CSS classes
- Componenti UI da `components/ui/`
- Design consistente con resto del sito

## 🔍 Debugging

### ID Tracciamento
Formato: `ERR-[CODE]-[YYYYMMDD]-[HHMMSS]`

Esempio: `ERR-CHAT_ERROR-20260115-143052`

### Dettagli Tecnici
Nella pagina errore, clicca su "Dettagli Tecnici" per vedere:
- Stack trace
- Component stack (per errori React)
- Response body completo

### Copia Info Errore
Pulsante "Copia Info" genera testo formattato:
```
Error ID: ERR-CHAT_ERROR-20260115-143052
Codice: CHAT_ERROR
Messaggio: Errore durante invio messaggio
Timestamp: 2026-01-15T14:30:52.000Z
Path: /dashboard
Dettagli: [stack trace]
```

## 📝 Best Practices

### DO ✅
- Usa `handleApiError()` per errori critici (500, network)
- Usa `getErrorMessage()` per validazione form inline
- Fornisci ID tracciamento al supporto
- Log dettagli in console (solo development)

### DON'T ❌
- Non esporre stack trace all'utente finale
- Non usare `alert()` o `console.log()` per errori
- Non fare catch silenti senza logging
- Non mostrare codice SQL o dettagli interni

## 🛠️ Manutenzione

### Monitoraggio
In produzione, considera integrare:
- **Sentry** per error tracking
- **LogRocket** per session replay
- **Datadog** per monitoring

### Analytics
Traccia errori frequenti per identificare:
- Pattern ricorrenti
- Problemi UX
- Bug da fixare

## 📞 Supporto

Per assistenza:
- Email: support@aistrategyhub.eu
- Fornire sempre ID tracciamento errore
- Allegare screenshot se possibile
