/**
 * Newsletter Form Component
 * Descrizione: Form iscrizione/disiscrizione newsletter
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Mail, CheckCircle } from 'lucide-react';
import apiClient from '@/lib/api-client';
import { getErrorMessage } from '@/lib/api-client';

interface NewsletterFormProps {
  variant?: 'default' | 'compact';
  showUnsubscribe?: boolean;
}

export function NewsletterForm({
  variant = 'default',
  showUnsubscribe = true
}: NewsletterFormProps) {
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [mode, setMode] = useState<'subscribe' | 'unsubscribe'>('subscribe');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (mode === 'subscribe') {
        // Validate terms acceptance
        if (!acceptTerms) {
          setError('Devi accettare i Termini di Servizio e la Privacy Policy');
          setIsLoading(false);
          return;
        }

        // Subscribe
        const response = await apiClient.post<{ message: string }>(
          '/newsletter/subscribe',
          {
            email,
            first_name: firstName || undefined,
            last_name: lastName || undefined,
            accept_terms: acceptTerms,
            source: 'web_form',
          }
        );

        setSuccess(response.message);
        setEmail('');
        setFirstName('');
        setLastName('');
        setAcceptTerms(false);
      } else {
        // Unsubscribe
        const response = await apiClient.post<{ message: string }>(
          '/newsletter/unsubscribe',
          { email }
        );

        setSuccess(response.message);
        setEmail('');
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  if (variant === 'compact') {
    return (
      <div className="w-full max-w-md">
        {success && (
          <Alert className="mb-4 border-green-500/50 text-green-700 dark:text-green-400">
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>{success}</AlertDescription>
          </Alert>
        )}

        {error && (
          <Alert variant="destructive" className="mb-4">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="flex gap-2">
            <Input
              type="email"
              placeholder="La tua email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
              className="flex-1"
            />
            <Button type="submit" disabled={isLoading}>
              {isLoading ? 'Invio...' : mode === 'subscribe' ? 'Iscriviti' : 'Annulla'}
            </Button>
          </div>

          {mode === 'subscribe' && (
            <div className="flex items-start space-x-2">
              <input
                type="checkbox"
                id="acceptTermsCompact"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                disabled={isLoading}
                className="mt-0.5 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                required
              />
              <label htmlFor="acceptTermsCompact" className="text-xs text-muted-foreground">
                Accetto i{' '}
                <Link href="/termini" target="_blank" className="text-primary hover:underline">
                  Termini di Servizio
                </Link>{' '}
                e la{' '}
                <Link href="/privacy" target="_blank" className="text-primary hover:underline">
                  Privacy Policy
                </Link>
              </label>
            </div>
          )}

          {showUnsubscribe && (
            <div className="text-center">
              <button
                type="button"
                onClick={() => {
                  setMode(mode === 'subscribe' ? 'unsubscribe' : 'subscribe');
                  setError(null);
                  setSuccess(null);
                }}
                className="text-xs text-muted-foreground hover:text-foreground underline"
              >
                {mode === 'subscribe' ? 'Vuoi disiscriverti?' : 'Torna all\'iscrizione'}
              </button>
            </div>
          )}
        </form>
      </div>
    );
  }

  // Default variant - full form
  return (
    <div className="w-full max-w-lg">
      {success && (
        <Alert className="mb-6 border-green-500/50 text-green-700 dark:text-green-400">
          <CheckCircle className="h-4 w-4" />
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Mode Toggle */}
        <div className="flex gap-2 justify-center mb-4">
          <Button
            type="button"
            variant={mode === 'subscribe' ? 'default' : 'outline'}
            onClick={() => {
              setMode('subscribe');
              setError(null);
              setSuccess(null);
            }}
            size="sm"
          >
            Iscriviti
          </Button>
          {showUnsubscribe && (
            <Button
              type="button"
              variant={mode === 'unsubscribe' ? 'default' : 'outline'}
              onClick={() => {
                setMode('unsubscribe');
                setError(null);
                setSuccess(null);
              }}
              size="sm"
            >
              Disiscrizione
            </Button>
          )}
        </div>

        {mode === 'subscribe' ? (
          <>
            {/* Name Fields */}
            <div className="grid md:grid-cols-2 gap-4">
              <Input
                type="text"
                placeholder="Nome (opzionale)"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                disabled={isLoading}
              />
              <Input
                type="text"
                placeholder="Cognome (opzionale)"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                disabled={isLoading}
              />
            </div>

            {/* Email */}
            <Input
              type="email"
              placeholder="Email *"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />

            {/* Terms Acceptance */}
            <div className="flex items-start space-x-2">
              <input
                type="checkbox"
                id="acceptTerms"
                checked={acceptTerms}
                onChange={(e) => setAcceptTerms(e.target.checked)}
                disabled={isLoading}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                required
              />
              <label htmlFor="acceptTerms" className="text-sm text-muted-foreground">
                Accetto i{' '}
                <Link href="/termini" target="_blank" className="text-primary hover:underline font-medium">
                  Termini di Servizio
                </Link>{' '}
                e la{' '}
                <Link href="/privacy" target="_blank" className="text-primary hover:underline font-medium">
                  Privacy Policy
                </Link>
                {' '}<span className="text-destructive">*</span>
              </label>
            </div>

            <Button type="submit" className="w-full" disabled={isLoading}>
              <Mail className="mr-2 h-4 w-4" />
              {isLoading ? 'Iscrizione in corso...' : 'Iscriviti alla Newsletter'}
            </Button>
          </>
        ) : (
          <>
            {/* Unsubscribe Mode */}
            <p className="text-sm text-muted-foreground text-center">
              Inserisci l'email con cui ti sei iscritto per cancellarti dalla newsletter
            </p>

            <Input
              type="email"
              placeholder="Email *"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={isLoading}
            />

            <Button
              type="submit"
              className="w-full"
              variant="destructive"
              disabled={isLoading}
            >
              {isLoading ? 'Elaborazione...' : 'Conferma Disiscrizione'}
            </Button>
          </>
        )}
      </form>
    </div>
  );
}
