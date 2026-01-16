'use client';

import React from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { AlertCircle, ArrowLeft, Home, RefreshCw, Copy, Check } from 'lucide-react';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card } from '@/components/ui/card';

export default function ErrorPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [copied, setCopied] = React.useState(false);

  // Estrai parametri errore
  const errorCode = searchParams?.get('code') || 'UNKNOWN_ERROR';
  const errorMessage = searchParams?.get('message') || 'Si è verificato un errore imprevisto';
  const errorTimestamp = searchParams?.get('timestamp') || new Date().toISOString();
  const errorPath = searchParams?.get('path') || '/';
  const errorDetails = searchParams?.get('details');

  // Genera ID tracciamento unico
  const trackingId = React.useMemo(() => {
    const date = new Date(errorTimestamp);
    const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '');
    const timeStr = date.toTimeString().slice(0, 8).replace(/:/g, '');
    return `ERR-${errorCode}-${dateStr}-${timeStr}`;
  }, [errorCode, errorTimestamp]);

  const copyErrorInfo = () => {
    const errorInfo = `
Error ID: ${trackingId}
Codice: ${errorCode}
Messaggio: ${errorMessage}
Timestamp: ${errorTimestamp}
Path: ${errorPath}
${errorDetails ? `Dettagli: ${errorDetails}` : ''}
    `.trim();

    navigator.clipboard.writeText(errorInfo);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getErrorTitle = (code: string): string => {
    const titles: Record<string, string> = {
      UNKNOWN_ERROR: 'Errore Sconosciuto',
      NETWORK_ERROR: 'Errore di Connessione',
      AUTH_ERROR: 'Errore di Autenticazione',
      VALIDATION_ERROR: 'Errore di Validazione',
      PERMISSION_ERROR: 'Permessi Insufficienti',
      NOT_FOUND: 'Risorsa Non Trovata',
      SERVER_ERROR: 'Errore del Server',
      RATE_LIMIT: 'Troppi Tentativi',
      CHAT_ERROR: 'Errore Chat AI',
      UPLOAD_ERROR: 'Errore Caricamento',
    };
    return titles[code] || 'Si è Verificato un Errore';
  };

  const getErrorDescription = (code: string): string => {
    const descriptions: Record<string, string> = {
      UNKNOWN_ERROR: 'Si è verificato un errore imprevisto. Il team è stato notificato.',
      NETWORK_ERROR: 'Impossibile connettersi al server. Verifica la tua connessione internet.',
      AUTH_ERROR: 'La tua sessione è scaduta o non sei autorizzato. Effettua nuovamente il login.',
      VALIDATION_ERROR: 'I dati forniti non sono validi. Controlla i campi e riprova.',
      PERMISSION_ERROR: 'Non hai i permessi necessari per eseguire questa operazione.',
      NOT_FOUND: 'La risorsa che stai cercando non esiste o è stata rimossa.',
      SERVER_ERROR: 'Il server ha riscontrato un problema. Riprova tra qualche minuto.',
      RATE_LIMIT: 'Hai effettuato troppi tentativi. Riprova tra qualche minuto.',
      CHAT_ERROR: 'Si è verificato un errore durante la conversazione con l\'AI.',
      UPLOAD_ERROR: 'Errore durante il caricamento del file. Verifica formato e dimensione.',
    };
    return descriptions[code] || 'Si è verificato un problema durante l\'elaborazione della richiesta.';
  };

  const getSuggestedActions = (code: string): string[] => {
    const actions: Record<string, string[]> = {
      UNKNOWN_ERROR: [
        'Aggiorna la pagina e riprova',
        'Se il problema persiste, contatta il supporto con il codice errore',
      ],
      NETWORK_ERROR: [
        'Verifica la tua connessione internet',
        'Disabilita VPN o proxy se attivi',
        'Riprova tra qualche secondo',
      ],
      AUTH_ERROR: [
        'Effettua nuovamente il login',
        'Verifica le tue credenziali',
        'Controlla che il tuo account sia attivo',
      ],
      VALIDATION_ERROR: [
        'Controlla che tutti i campi obbligatori siano compilati',
        'Verifica il formato dei dati inseriti',
        'Leggi i messaggi di errore specifici',
      ],
      PERMISSION_ERROR: [
        'Contatta l\'amministratore per richiedere i permessi necessari',
        'Verifica di essere loggato con l\'account corretto',
      ],
      NOT_FOUND: [
        'Verifica l\'URL inserito',
        'Torna alla home page',
        'Usa la ricerca per trovare quello che cerchi',
      ],
      SERVER_ERROR: [
        'Riprova tra qualche minuto',
        'Se il problema persiste, contatta il supporto',
      ],
      RATE_LIMIT: [
        'Attendi qualche minuto prima di riprovare',
        'Riduci la frequenza delle richieste',
      ],
      CHAT_ERROR: [
        'Riprova a inviare il messaggio',
        'Avvia una nuova conversazione',
        'Se il problema persiste, ricarica la pagina',
      ],
      UPLOAD_ERROR: [
        'Verifica che il file sia in formato supportato',
        'Controlla che le dimensioni non superino il limite',
        'Riprova il caricamento',
      ],
    };
    return actions[code] || [
      'Aggiorna la pagina',
      'Se il problema persiste, contatta il supporto',
    ];
  };

  return (
    <>
      <Navigation />
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 flex items-center justify-center p-4">
      <Card className="max-w-2xl w-full p-8 space-y-6">
        {/* Header */}
        <div className="flex items-start gap-4">
          <div className="rounded-full bg-destructive/10 p-3">
            <AlertCircle className="h-8 w-8 text-destructive" />
          </div>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-foreground mb-2">
              {getErrorTitle(errorCode)}
            </h1>
            <p className="text-muted-foreground">
              {getErrorDescription(errorCode)}
            </p>
          </div>
        </div>

        {/* Error Message */}
        {errorMessage && errorMessage !== getErrorDescription(errorCode) && (
          <Alert>
            <AlertDescription className="text-sm">
              {errorMessage}
            </AlertDescription>
          </Alert>
        )}

        {/* Error Details (Technical Info) */}
        <div className="bg-muted/50 rounded-lg p-4 space-y-2 font-mono text-sm">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-muted-foreground text-xs mb-1">ID Tracciamento Errore</div>
              <div className="font-semibold text-foreground">{trackingId}</div>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={copyErrorInfo}
              className="gap-2"
            >
              {copied ? (
                <>
                  <Check className="h-4 w-4" />
                  Copiato!
                </>
              ) : (
                <>
                  <Copy className="h-4 w-4" />
                  Copia Info
                </>
              )}
            </Button>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-2 border-t border-border/50">
            <div>
              <div className="text-muted-foreground text-xs">Codice</div>
              <div className="text-foreground">{errorCode}</div>
            </div>
            <div>
              <div className="text-muted-foreground text-xs">Timestamp</div>
              <div className="text-foreground">
                {new Date(errorTimestamp).toLocaleString('it-IT')}
              </div>
            </div>
          </div>

          {errorDetails && (
            <details className="pt-2 border-t border-border/50">
              <summary className="text-muted-foreground text-xs cursor-pointer hover:text-foreground">
                Dettagli Tecnici (per sviluppatori)
              </summary>
              <pre className="mt-2 text-xs text-muted-foreground overflow-auto max-h-32 p-2 bg-background rounded">
                {errorDetails}
              </pre>
            </details>
          )}
        </div>

        {/* Suggested Actions */}
        <div className="space-y-3">
          <h3 className="font-semibold text-sm text-foreground">
            Cosa Puoi Fare:
          </h3>
          <ul className="space-y-2">
            {getSuggestedActions(errorCode).map((action, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm">
                <span className="text-primary mt-1">•</span>
                <span className="text-muted-foreground">{action}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Actions */}
        <div className="flex flex-wrap gap-3 pt-4 border-t">
          <Button
            onClick={() => router.back()}
            variant="outline"
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Torna Indietro
          </Button>

          <Button
            onClick={() => window.location.reload()}
            variant="outline"
            className="gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Ricarica Pagina
          </Button>

          <Button
            onClick={() => router.push('/')}
            className="gap-2"
          >
            <Home className="h-4 w-4" />
            Vai alla Home
          </Button>
        </div>

        {/* Support Link */}
        <div className="pt-4 border-t text-center text-sm text-muted-foreground">
          Hai bisogno di aiuto?{' '}
          <a
            href="mailto:support@aistrategyhub.eu"
            className="text-primary hover:underline"
          >
            Contatta il supporto
          </a>
          {' '}fornendo il codice errore <code className="bg-muted px-1 py-0.5 rounded">{trackingId}</code>
        </div>
      </Card>
    </div>
    </>
  );
}
