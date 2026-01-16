/**
 * Global Error Boundary
 * Descrizione: Gestione errori globale del sito
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Navigation } from '@/components/Navigation';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to console
    console.error('[Global Error]', error);
  }, [error]);

  return (
    <>
      <Navigation />
      <main className="container py-24">
        <div className="max-w-2xl mx-auto text-center space-y-6">
          <div className="space-y-3">
            <h1 className="text-4xl font-bold text-destructive">Si è verificato un errore</h1>
            <p className="text-muted-foreground text-lg">
              Qualcosa è andato storto durante il caricamento della pagina.
            </p>
          </div>

          {error.message && (
            <div className="p-4 bg-muted rounded-lg text-left">
              <p className="text-sm font-mono text-destructive">{error.message}</p>
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3 justify-center pt-6">
            <Button onClick={reset} size="lg">
              Riprova
            </Button>
            <Link href="/">
              <Button variant="outline" size="lg">Torna alla Home</Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="ghost" size="lg">Vai alla Dashboard</Button>
            </Link>
          </div>

          {error.digest && (
            <div className="text-xs text-muted-foreground pt-8">
              <p>Error ID: {error.digest}</p>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
