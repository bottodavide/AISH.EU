/**
 * Email Verification Page
 * Descrizione: Verifica email utente tramite token ricevuto via email
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { CheckCircle, XCircle, Loader2, Mail } from 'lucide-react';
import apiClient, { getErrorMessage } from '@/lib/api-client';

type VerificationStatus = 'loading' | 'success' | 'error' | 'missing-token';

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  const [status, setStatus] = useState<VerificationStatus>('loading');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [countdown, setCountdown] = useState(5);
  const hasVerifiedRef = useRef(false);

  useEffect(() => {
    // Se non c'è token, errore immediato
    if (!token) {
      setStatus('missing-token');
      return;
    }

    // Previeni chiamate duplicate (React Strict Mode fa doppio mount in dev)
    if (hasVerifiedRef.current) {
      return;
    }

    // Verifica email
    hasVerifiedRef.current = true;
    verifyEmail(token);
  }, [token]);

  // Countdown per redirect automatico dopo successo
  useEffect(() => {
    if (status === 'success' && countdown > 0) {
      const timer = setTimeout(() => {
        setCountdown(countdown - 1);
      }, 1000);

      return () => clearTimeout(timer);
    }

    if (status === 'success' && countdown === 0) {
      router.push('/login');
    }
  }, [status, countdown, router]);

  const verifyEmail = async (verificationToken: string) => {
    try {
      await apiClient.post('/auth/verify-email', {
        token: verificationToken,
      });

      setStatus('success');
    } catch (err: any) {
      setStatus('error');
      setErrorMessage(getErrorMessage(err));
    }
  };

  const handleRetry = () => {
    if (token) {
      setStatus('loading');
      setErrorMessage('');
      hasVerifiedRef.current = false; // Reset flag for retry
      verifyEmail(token);
    }
  };

  return (
    <>
      <Navigation />
      <main className="container flex items-center justify-center min-h-screen py-12">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle className="text-center">Verifica Email</CardTitle>
            <CardDescription className="text-center">
              Conferma del tuo indirizzo email
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Loading State */}
            {status === 'loading' && (
              <div className="flex flex-col items-center gap-4 py-8">
                <Loader2 className="h-16 w-16 text-primary animate-spin" />
                <p className="text-muted-foreground text-center">
                  Verifica in corso...
                </p>
              </div>
            )}

            {/* Success State */}
            {status === 'success' && (
              <div className="flex flex-col items-center gap-4 py-8">
                <CheckCircle className="h-16 w-16 text-green-600" />
                <div className="text-center space-y-2">
                  <h3 className="text-xl font-semibold text-green-700 dark:text-green-400">
                    Email Verificata!
                  </h3>
                  <p className="text-muted-foreground">
                    Il tuo account è stato verificato con successo.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Verrai reindirizzato alla pagina di login tra {countdown} secondi...
                  </p>
                </div>
                <Link href="/login" className="w-full">
                  <Button className="w-full" size="lg">
                    Vai al Login
                  </Button>
                </Link>
              </div>
            )}

            {/* Error State */}
            {status === 'error' && (
              <div className="flex flex-col items-center gap-4 py-8">
                <XCircle className="h-16 w-16 text-destructive" />
                <div className="text-center space-y-2">
                  <h3 className="text-xl font-semibold text-destructive">
                    Verifica Fallita
                  </h3>
                  <p className="text-muted-foreground">
                    {errorMessage || 'Si è verificato un errore durante la verifica.'}
                  </p>
                </div>

                <Alert variant="destructive" className="mt-4">
                  <AlertDescription className="space-y-3">
                    <p>Possibili cause:</p>
                    <ul className="list-disc list-inside text-sm ml-2">
                      <li>Token di verifica non valido o scaduto</li>
                      <li>Email già verificata in precedenza</li>
                      <li>Link di verifica utilizzato più volte</li>
                    </ul>
                  </AlertDescription>
                </Alert>

                <div className="flex flex-col gap-2 w-full mt-4">
                  <Button onClick={handleRetry} variant="outline" className="w-full">
                    Riprova
                  </Button>
                  <Link href="/login" className="w-full">
                    <Button variant="secondary" className="w-full">
                      Vai al Login
                    </Button>
                  </Link>
                </div>
              </div>
            )}

            {/* Missing Token State */}
            {status === 'missing-token' && (
              <div className="flex flex-col items-center gap-4 py-8">
                <Mail className="h-16 w-16 text-muted-foreground" />
                <div className="text-center space-y-2">
                  <h3 className="text-xl font-semibold">Token Mancante</h3>
                  <p className="text-muted-foreground">
                    Il link di verifica non è valido. Controlla di aver copiato correttamente
                    il link dalla email di conferma.
                  </p>
                </div>

                <Alert className="mt-4">
                  <AlertDescription>
                    <p className="mb-2">
                      Se non hai ricevuto l'email di verifica o il link è scaduto:
                    </p>
                    <ul className="list-disc list-inside text-sm ml-2">
                      <li>Controlla la cartella spam/posta indesiderata</li>
                      <li>Richiedi un nuovo link dalla pagina di login</li>
                    </ul>
                  </AlertDescription>
                </Alert>

                <Link href="/login" className="w-full mt-4">
                  <Button className="w-full">Vai al Login</Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </>
  );
}
