/**
 * Login Page
 * Descrizione: Pagina login con email/password e MFA support
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { Suspense, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { login } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [mfaCode, setMfaCode] = useState('');
  const [mfaRequired, setMfaRequired] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Check for redirect param or session expired
  const redirect = searchParams?.get('redirect') || '/dashboard';
  const sessionExpired = searchParams?.get('session_expired') === 'true';

  /**
   * Handle initial login (email + password)
   */
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await login({ email, password });

      // Check if MFA required
      if (response.mfa_required) {
        setMfaRequired(true);
        setIsLoading(false);
        return;
      }

      // Login successful, redirect based on role
      const userRole = response.user?.role;
      if (userRole === 'admin' || userRole === 'super_admin') {
        router.push('/admin');
      } else {
        router.push(redirect);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      setIsLoading(false);
    }
  };

  /**
   * Handle MFA verification
   */
  const handleMfaVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      // Call login again with MFA token
      const response = await login({
        email,
        password,
        mfa_token: mfaCode,
      });

      // If still MFA required, something went wrong
      if (response.mfa_required) {
        throw new Error('MFA verification failed');
      }

      // Login successful, redirect based on role
      const userRole = response.user?.role;
      if (userRole === 'admin' || userRole === 'super_admin') {
        router.push('/admin');
      } else {
        router.push(redirect);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'MFA verification failed');
      setIsLoading(false);
    }
  };

  return (
    <>
      <Navigation />
      <div className="container flex items-center justify-center min-h-screen py-12">
        <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">
            {mfaRequired ? 'Verifica MFA' : 'Accedi'}
          </CardTitle>
          <CardDescription>
            {mfaRequired
              ? 'Inserisci il codice dal tuo authenticator'
              : 'Inserisci le tue credenziali per accedere'}
          </CardDescription>
        </CardHeader>

        <form onSubmit={mfaRequired ? handleMfaVerify : handleLogin}>
          <CardContent className="space-y-4">
            {/* Session Expired Alert */}
            {sessionExpired && (
              <Alert variant="destructive">
                <AlertDescription>
                  La tua sessione è scaduta. Effettua nuovamente il login.
                </AlertDescription>
              </Alert>
            )}

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Login Form */}
            {!mfaRequired ? (
              <>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input
                    id="email"
                    type="email"
                    placeholder="nome@esempio.it"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    autoComplete="email"
                    disabled={isLoading}
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="password">Password</Label>
                    <Link
                      href="/password-reset"
                      className="text-sm text-primary hover:underline"
                    >
                      Password dimenticata?
                    </Link>
                  </div>
                  <Input
                    id="password"
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    autoComplete="current-password"
                    disabled={isLoading}
                  />
                </div>
              </>
            ) : (
              /* MFA Form */
              <div className="space-y-2">
                <Label htmlFor="mfa_code">Codice MFA</Label>
                <Input
                  id="mfa_code"
                  type="text"
                  placeholder="123456"
                  value={mfaCode}
                  onChange={(e) => setMfaCode(e.target.value)}
                  required
                  maxLength={6}
                  pattern="\d{6}"
                  disabled={isLoading}
                  autoFocus
                />
                <p className="text-sm text-muted-foreground">
                  Inserisci il codice a 6 cifre dalla tua app authenticator
                </p>
              </div>
            )}
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Caricamento...' : mfaRequired ? 'Verifica' : 'Accedi'}
            </Button>

            {!mfaRequired && (
              <div className="text-sm text-center text-muted-foreground">
                Non hai un account?{' '}
                <Link href="/register" className="text-primary hover:underline">
                  Registrati
                </Link>
              </div>
            )}

            {mfaRequired && (
              <Button
                type="button"
                variant="ghost"
                className="w-full"
                onClick={() => {
                  setMfaRequired(false);
                  setMfaCode('');
                  setError(null);
                }}
              >
                Torna al login
              </Button>
            )}
          </CardFooter>
        </form>
      </Card>
    </div>
    </>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}
