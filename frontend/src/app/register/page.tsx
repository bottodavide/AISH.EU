/**
 * Register Page
 * Descrizione: Pagina registrazione con email verification
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/contexts/AuthContext';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';

export default function RegisterPage() {
  const router = useRouter();
  const { register } = useAuth();
  const [isMounted, setIsMounted] = useState(false);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    firstName: '',
    lastName: '',
    companyName: '',
    vatNumber: '',
  });
  const [acceptTerms, setAcceptTerms] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Fix hydration mismatch
  useEffect(() => {
    setIsMounted(true);
  }, []);

  // Prevent hydration mismatch by not rendering until mounted
  if (!isMounted) {
    return (
      <>
        <Navigation />
        <div className="container flex items-center justify-center min-h-screen py-12">
          <Card className="w-full max-w-md">
            <CardContent className="py-12">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              </div>
            </CardContent>
          </Card>
        </div>
      </>
    );
  }

  /**
   * Handle form input changes
   */
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  /**
   * Handle registration
   */
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate terms acceptance
    if (!acceptTerms) {
      setError('Devi accettare i Termini di Servizio e la Privacy Policy per registrarti');
      return;
    }

    // Validate business email (no generic providers)
    const genericProviders = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com', 'icloud.com', 'libero.it', 'virgilio.it'];
    const emailDomain = formData.email.split('@')[1]?.toLowerCase();
    if (genericProviders.includes(emailDomain)) {
      setError('Devi utilizzare un indirizzo email aziendale, non un provider generico (es. Gmail, Yahoo, Hotmail)');
      return;
    }

    // Validate company name
    if (!formData.companyName.trim()) {
      setError('Il nome dell\'azienda è obbligatorio');
      return;
    }

    // Validate passwords match
    if (formData.password !== formData.confirmPassword) {
      setError('Le password non corrispondono');
      return;
    }

    // Validate password strength (min 8 chars)
    if (formData.password.length < 8) {
      setError('La password deve essere di almeno 8 caratteri');
      return;
    }

    setIsLoading(true);

    try {
      await register({
        email: formData.email,
        password: formData.password,
        confirm_password: formData.confirmPassword,
        first_name: formData.firstName,
        last_name: formData.lastName,
        company_name: formData.companyName,
        accept_terms: acceptTerms,
        accept_privacy: acceptTerms, // Usando lo stesso checkbox per entrambi
      });

      // Show success message
      setSuccess(true);
    } catch (err: any) {
      // Mostra sempre errore inline
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  // Success state - show email verification message
  if (success) {
    return (
      <>
        <Navigation />
        <div className="container flex items-center justify-center min-h-screen py-12">
          <Card className="w-full max-w-md">
            <CardHeader>
              <CardTitle className="text-2xl font-bold text-center">
                Registrazione Completata!
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <Alert variant="success">
                <AlertTitle>Email di Verifica Inviata</AlertTitle>
                <AlertDescription>
                  Ti abbiamo inviato un'email all'indirizzo <strong>{formData.email}</strong>.
                  <br />
                  <br />
                  Clicca sul link nell'email per verificare il tuo account e completare la registrazione.
                </AlertDescription>
              </Alert>

              <div className="text-sm text-muted-foreground space-y-2">
                <p>Non hai ricevuto l'email?</p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Controlla la cartella spam</li>
                  <li>Verifica che l'indirizzo email sia corretto</li>
                  <li>Richiedi un nuovo link di verifica dalla pagina di login</li>
                </ul>
              </div>
            </CardContent>
            <CardFooter>
              <Link href="/login" className="w-full">
                <Button className="w-full">Vai al Login</Button>
              </Link>
            </CardFooter>
          </Card>
        </div>
      </>
    );
  }

  // Registration form
  return (
    <>
      <Navigation />
      <div className="container flex items-center justify-center min-h-screen py-12">
        <Card className="w-full max-w-lg">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold">Registrazione Business</CardTitle>
            <CardDescription>
              Crea un account aziendale per accedere ai nostri servizi di consulenza
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleRegister}>
            <CardContent className="space-y-4">
              {/* Error Alert */}
              {error && (
                <Alert variant="destructive">
                  <AlertTitle>Errore nella registrazione</AlertTitle>
                  <AlertDescription>
                    {error.includes('.') || error.includes(',') ? (
                      // Multiple errors - show as list
                      <ul className="list-disc list-inside space-y-1 mt-2">
                        {error.split(/[.,]/).filter(e => e.trim()).map((err, idx) => (
                          <li key={idx}>{err.trim()}</li>
                        ))}
                      </ul>
                    ) : (
                      // Single error - show as text
                      error
                    )}
                  </AlertDescription>
                </Alert>
              )}

              {/* Company Information */}
              <div className="space-y-4 p-4 bg-muted/50 rounded-lg">
                <h3 className="font-semibold text-sm">Informazioni Azienda</h3>

                {/* Company Name */}
                <div className="space-y-2">
                  <Label htmlFor="companyName">Nome Azienda *</Label>
                  <Input
                    id="companyName"
                    name="companyName"
                    type="text"
                    placeholder="Es. Acme S.r.l."
                    value={formData.companyName}
                    onChange={handleChange}
                    required
                    disabled={isLoading}
                  />
                </div>

                {/* VAT Number */}
                <div className="space-y-2">
                  <Label htmlFor="vatNumber">Partita IVA (opzionale)</Label>
                  <Input
                    id="vatNumber"
                    name="vatNumber"
                    type="text"
                    placeholder="IT12345678901"
                    value={formData.vatNumber}
                    onChange={handleChange}
                    disabled={isLoading}
                  />
                </div>
              </div>

              {/* Personal Information */}
              <div className="space-y-4">
                <h3 className="font-semibold text-sm">Dati Personali</h3>

                {/* First Name & Last Name */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="firstName">Nome</Label>
                    <Input
                      id="firstName"
                      name="firstName"
                      type="text"
                      placeholder="Mario"
                      value={formData.firstName}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="lastName">Cognome</Label>
                    <Input
                      id="lastName"
                      name="lastName"
                      type="text"
                      placeholder="Rossi"
                      value={formData.lastName}
                      onChange={handleChange}
                      disabled={isLoading}
                    />
                  </div>
                </div>

                {/* Business Email */}
                <div className="space-y-2">
                  <Label htmlFor="email">Email Aziendale *</Label>
                  <Input
                    id="email"
                    name="email"
                    type="email"
                    placeholder="nome@tuaazienda.it"
                    value={formData.email}
                    onChange={handleChange}
                    required
                    autoComplete="email"
                    disabled={isLoading}
                  />
                  <p className="text-xs text-muted-foreground">
                    Utilizza un indirizzo email aziendale (non Gmail, Yahoo, Hotmail, etc.)
                  </p>
                </div>
              </div>

            {/* Password */}
            <div className="space-y-2">
              <Label htmlFor="password">Password *</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
                autoComplete="new-password"
                disabled={isLoading}
              />
              <div className="text-xs text-muted-foreground space-y-1">
                <p>La password deve contenere:</p>
                <ul className="list-disc list-inside ml-2">
                  <li>Almeno 8 caratteri</li>
                  <li>Almeno 1 lettera maiuscola</li>
                  <li>Almeno 1 numero</li>
                  <li>Almeno 1 carattere speciale (!@#$%^&*...)</li>
                </ul>
              </div>
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Conferma Password *</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                minLength={8}
                autoComplete="new-password"
                disabled={isLoading}
              />
            </div>

            {/* Terms & Privacy Acceptance - REQUIRED */}
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
                <Link
                  href="/termini"
                  target="_blank"
                  className="text-primary hover:underline font-medium"
                >
                  Termini di Servizio
                </Link>{' '}
                e la{' '}
                <Link
                  href="/privacy"
                  target="_blank"
                  className="text-primary hover:underline font-medium"
                >
                  Privacy Policy
                </Link>
                {' '}<span className="text-destructive">*</span>
              </label>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? 'Registrazione...' : 'Registrati'}
            </Button>

            <div className="text-sm text-center text-muted-foreground">
              Hai già un account?{' '}
              <Link href="/login" className="text-primary hover:underline">
                Accedi
              </Link>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
    </>
  );
}
