/**
 * Admin Error Boundary
 * Descrizione: Gestione errori per l'area admin
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle } from 'lucide-react';

export default function AdminError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to console in development
    console.error('[Admin Error]', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="max-w-2xl w-full">
        <CardHeader>
          <div className="flex items-center gap-3 mb-2">
            <AlertTriangle className="h-8 w-8 text-destructive" />
            <CardTitle className="text-2xl">Errore nell'Area Admin</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <Alert variant="destructive">
            <AlertDescription>
              Si è verificato un errore durante il caricamento della pagina amministrativa.
            </AlertDescription>
          </Alert>

          {error.message && (
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm font-mono text-destructive">{error.message}</p>
            </div>
          )}

          {error.digest && (
            <div className="text-xs text-muted-foreground">
              <p>Error ID: {error.digest}</p>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-2 pt-4">
            <Button onClick={reset} className="flex-1">
              Riprova
            </Button>
            <Link href="/admin" className="flex-1">
              <Button variant="outline" className="w-full">
                Torna alla Dashboard
              </Button>
            </Link>
            <Link href="/dashboard" className="flex-1">
              <Button variant="ghost" className="w-full">
                Vai al Sito
              </Button>
            </Link>
          </div>

          <div className="text-xs text-muted-foreground pt-4 border-t">
            <p className="font-semibold mb-1">Informazioni per il debug:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Controlla la console del browser per maggiori dettagli</li>
              <li>Verifica che il backend sia attivo</li>
              <li>Se l'errore persiste, contatta il supporto tecnico</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
