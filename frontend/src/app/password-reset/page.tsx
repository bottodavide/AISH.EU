/**
 * Password Reset Page
 * Descrizione: Reset password tramite email
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { handleApiError, getErrorMessage } from '@/lib/error-handler';
import apiClient from '@/lib/api-client';

export default function PasswordResetPage() {
  const searchParams = useSearchParams();
  const token = searchParams?.get('token');

  const [isMounted, setIsMounted] = useState(false);
  const [step, setStep] = useState<'request' | 'reset'>('request');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  // Fix hydration mismatch
  useEffect(() => {
    setIsMounted(true);
    if (token) {
      setStep('reset');
    }
  }, [token]);

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await apiClient.post('/api/v1/auth/request-password-reset', { email });
      setSuccess(true);
    } catch (err: any) {
      if (!err.response || err.response?.status >= 500 || err.code === 'ERR_NETWORK') {
        handleApiError(err);
        return;
      }
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError('Le password non corrispondono');
      return;
    }

    if (password.length < 8) {
      setError('La password deve essere di almeno 8 caratteri');
      return;
    }

    setIsLoading(true);

    try {
      await apiClient.post('/api/v1/auth/reset-password', {
        token,
        new_password: password,
      });
      setSuccess(true);
    } catch (err: any) {
      if (!err.response || err.response?.status >= 500 || err.code === 'ERR_NETWORK') {
        handleApiError(err);
        return;
      }
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  // Prevent hydration mismatch
  if (!isMounted) {
    return (
      <div className="container flex items-center justify-center min-h-screen py-12">
        <Card className="w-full max-w-md">
          <CardContent className="py-12">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Success state
  if (success) {
    return (
      <div className="container flex items-center justify-center min-h-screen py-12">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle className="text-center">
              {step === 'request' ? 'Email Inviata!' : 'Password Reimpostata!'}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Alert className="border-green-500/50 text-green-700 dark:text-green-400">
              <AlertTitle>Successo</AlertTitle>
              <AlertDescription>
                {step === 'request' ? (
                  <>
                    Ti abbiamo inviato un'email all'indirizzo <strong>{email}</strong> con
                    le istruzioni per reimpostare la password.
                    <br /><br />
                    Controlla la tua casella di posta (anche spam) e clicca sul link entro 1 ora.
                  </>
                ) : (
                  <>
                    La tua password è stata reimpostata con successo.
                    Ora puoi accedere con la nuova password.
                  </>
                )}
              </AlertDescription>
            </Alert>
          </CardContent>
          <CardFooter>
            <Link href="/login" className="w-full">
              <Button className="w-full">Vai al Login</Button>
            </Link>
          </CardFooter>
        </Card>
      </div>
    );
  }

  // Request reset form
  if (step === 'request') {
    return (
      <div className="container flex items-center justify-center min-h-screen py-12">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Reimposta Password</CardTitle>
            <CardDescription>
              Inserisci la tua email per ricevere il link di reset
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleRequestReset}>
            <CardContent className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}

              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="nome@esempio.it"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  autoFocus
                  disabled={isLoading}
                />
              </div>

              <p className="text-sm text-muted-foreground">
                Riceverai un'email con un link per reimpostare la password.
                Il link sarà valido per 1 ora.
              </p>
            </CardContent>

            <CardFooter className="flex flex-col space-y-4">
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? 'Invio in corso...' : 'Invia Link di Reset'}
              </Button>

              <div className="text-sm text-center text-muted-foreground">
                Ricordi la password?{' '}
                <Link href="/login" className="text-primary hover:underline">
                  Accedi
                </Link>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    );
  }

  // Reset password form (with token)
  return (
    <div className="container flex items-center justify-center min-h-screen py-12">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Nuova Password</CardTitle>
          <CardDescription>
            Scegli una nuova password per il tuo account
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleResetPassword}>
          <CardContent className="space-y-4">
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Label htmlFor="password">Nuova Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
                autoComplete="new-password"
                disabled={isLoading}
              />
              <p className="text-xs text-muted-foreground">
                Minimo 8 caratteri
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Conferma Password</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                autoComplete="new-password"
                disabled={isLoading}
              />
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Salvataggio...' : 'Reimposta Password'}
            </Button>

            <div className="text-sm text-center text-muted-foreground">
              <Link href="/login" className="text-primary hover:underline">
                Torna al Login
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
}
