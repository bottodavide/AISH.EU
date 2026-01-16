/**
 * Contact Page (Contatti)
 * Descrizione: Pagina contatti con form di richiesta informazioni
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Mail, Phone, MapPin } from 'lucide-react';
import apiClient, { getErrorMessage } from '@/lib/api-client';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    company: '',
    role: '',
    subject: '',
    message: '',
  });
  const [acceptPrivacy, setAcceptPrivacy] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // Validate privacy acceptance
    if (!acceptPrivacy) {
      setError('Devi accettare la Privacy Policy per inviare il messaggio');
      setIsLoading(false);
      return;
    }

    // Validate business email (no generic providers)
    const genericProviders = [
      'gmail.com', 'yahoo.com', 'yahoo.it', 'hotmail.com', 'hotmail.it',
      'outlook.com', 'outlook.it', 'live.com', 'live.it', 'icloud.com',
      'me.com', 'libero.it', 'virgilio.it', 'tiscali.it', 'alice.it',
      'tin.it', 'fastwebnet.it', 'protonmail.com', 'aol.com'
    ];
    const emailDomain = formData.email.split('@')[1]?.toLowerCase();
    if (genericProviders.includes(emailDomain)) {
      setError(
        `Per favore utilizza un'email aziendale. Provider consumer come ${emailDomain} non sono ammessi per richieste commerciali.`
      );
      setIsLoading(false);
      return;
    }

    try {
      await apiClient.post('/api/v1/contact', formData);
      setSuccess(true);
      setFormData({ name: '', email: '', company: '', role: '', subject: '', message: '' });
      setAcceptPrivacy(false);
    } catch (err: any) {
      // Mostra sempre errore inline
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Navigation />
      <main className="container py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Contattaci</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Hai domande sui nostri servizi? Compila il form o contattaci direttamente
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Contact Info */}
          <div className="lg:col-span-1 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Mail className="h-5 w-5" />
                  Email
                </CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href="mailto:info@aistrategyhub.eu"
                  className="text-primary hover:underline"
                >
                  info@aistrategyhub.eu
                </a>
                <p className="text-sm text-muted-foreground mt-2">
                  Risposta entro 24 ore lavorative
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Phone className="h-5 w-5" />
                  Telefono
                </CardTitle>
              </CardHeader>
              <CardContent>
                <a
                  href="tel:+39xxxxxxxxxx"
                  className="text-primary hover:underline"
                >
                  +39 XXX XXX XXXX
                </a>
                <p className="text-sm text-muted-foreground mt-2">
                  Lun-Ven, 9:00-18:00
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MapPin className="h-5 w-5" />
                  Sede
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p>Italia</p>
                <p className="text-sm text-muted-foreground mt-2">
                  Consulenze in tutta Europa
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Contact Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Richiedi Informazioni</CardTitle>
                <CardDescription>
                  Compila il form e ti ricontatteremo al più presto
                </CardDescription>
              </CardHeader>
              <CardContent>
                {success && (
                  <Alert className="mb-6 border-green-500/50 text-green-700 dark:text-green-400">
                    <AlertDescription>
                      Grazie per averci contattato! Riceverai una risposta entro 24 ore lavorative.
                    </AlertDescription>
                  </Alert>
                )}

                {error && (
                  <Alert variant="destructive" className="mb-6">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <form onSubmit={handleSubmit} className="space-y-4">
                  {/* Name */}
                  <div className="space-y-2">
                    <Label htmlFor="name">Nome e Cognome *</Label>
                    <Input
                      id="name"
                      name="name"
                      type="text"
                      placeholder="Mario Rossi"
                      value={formData.name}
                      onChange={handleChange}
                      required
                      disabled={isLoading}
                    />
                  </div>

                  {/* Email */}
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Aziendale *</Label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      placeholder="nome@tuaazienda.com"
                      value={formData.email}
                      onChange={handleChange}
                      required
                      disabled={isLoading}
                    />
                    <p className="text-xs text-muted-foreground">
                      Utilizza un'email aziendale (non Gmail, Yahoo, Hotmail, etc.)
                    </p>
                  </div>

                  {/* Company and Role */}
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="company">Azienda</Label>
                      <Input
                        id="company"
                        name="company"
                        type="text"
                        placeholder="Acme S.r.l."
                        value={formData.company}
                        onChange={handleChange}
                        disabled={isLoading}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="role">Ruolo</Label>
                      <Input
                        id="role"
                        name="role"
                        type="text"
                        placeholder="CEO, CTO, Manager..."
                        value={formData.role}
                        onChange={handleChange}
                        disabled={isLoading}
                      />
                    </div>
                  </div>

                  {/* Subject */}
                  <div className="space-y-2">
                    <Label htmlFor="subject">Oggetto *</Label>
                    <Input
                      id="subject"
                      name="subject"
                      type="text"
                      placeholder="Richiesta informazioni su..."
                      value={formData.subject}
                      onChange={handleChange}
                      required
                      disabled={isLoading}
                    />
                  </div>

                  {/* Message */}
                  <div className="space-y-2">
                    <Label htmlFor="message">Messaggio *</Label>
                    <Textarea
                      id="message"
                      name="message"
                      placeholder="Descrivi la tua richiesta..."
                      value={formData.message}
                      onChange={handleChange}
                      required
                      disabled={isLoading}
                      rows={6}
                    />
                  </div>

                  {/* Privacy Acceptance */}
                  <div className="flex items-start space-x-2">
                    <input
                      type="checkbox"
                      id="acceptPrivacy"
                      checked={acceptPrivacy}
                      onChange={(e) => setAcceptPrivacy(e.target.checked)}
                      disabled={isLoading}
                      className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                      required
                    />
                    <label htmlFor="acceptPrivacy" className="text-sm text-muted-foreground">
                      Accetto la{' '}
                      <Link href="/privacy" target="_blank" className="text-primary hover:underline font-medium">
                        Privacy Policy
                      </Link>{' '}
                      e acconsento al trattamento dei miei dati personali per ricevere risposta alla mia richiesta
                      {' '}<span className="text-destructive">*</span>
                    </label>
                  </div>

                  {/* Submit */}
                  <Button type="submit" className="w-full" disabled={isLoading}>
                    {isLoading ? 'Invio in corso...' : 'Invia Richiesta'}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </>
  );
}
