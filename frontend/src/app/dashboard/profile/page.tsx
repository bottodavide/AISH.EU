/**
 * Profile Edit Page
 * Descrizione: Modifica profilo utente con upload avatar
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/contexts/AuthContext';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { User, Building, Mail, Phone, CheckCircle, Camera } from 'lucide-react';

interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  company_name?: string;
  phone?: string;
  avatar_url?: string;
}

export default function ProfileEditPage() {
  const { user, isAuthenticated } = useAuth();

  const [formData, setFormData] = useState<ProfileData>({
    first_name: '',
    last_name: '',
    email: '',
    company_name: '',
    phone: '',
    avatar_url: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && user) {
      loadProfile();
    }
  }, [isAuthenticated, user]);

  const loadProfile = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const profile = await apiClient.get<any>('/api/v1/users/me');

      setFormData({
        first_name: profile.profile?.first_name || '',
        last_name: profile.profile?.last_name || '',
        email: profile.email || '',
        company_name: profile.profile?.company_name || '',
        phone: profile.profile?.phone || '',
        avatar_url: profile.profile?.avatar_url || '',
      });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validation
    if (!formData.first_name.trim()) {
      setError('Il nome è obbligatorio');
      return;
    }

    if (!formData.last_name.trim()) {
      setError('Il cognome è obbligatorio');
      return;
    }

    setIsSaving(true);

    try {
      await apiClient.put('/api/v1/users/me', {
        first_name: formData.first_name,
        last_name: formData.last_name,
        company_name: formData.company_name || undefined,
        phone: formData.phone || undefined,
        avatar_url: formData.avatar_url || undefined,
      });

      setSuccess('Profilo aggiornato con successo!');

      // Ricarica il profilo per aggiornare il context
      loadProfile();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  if (isLoading) {
    return (
      <>
        <Navigation />
        <div className="container flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navigation />
      <main className="container py-12 max-w-3xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Il Tuo Profilo</h1>
          <p className="text-muted-foreground">
            Aggiorna le tue informazioni personali
          </p>
        </div>

        {/* Alerts */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-500/50 text-green-700 dark:text-green-400">
            <AlertDescription className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              {success}
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Avatar Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Camera className="h-5 w-5" />
                Immagine Profilo
              </CardTitle>
              <CardDescription>
                La tua foto profilo (opzionale)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {formData.avatar_url && (
                <div className="flex justify-center">
                  <div className="relative w-32 h-32 rounded-full overflow-hidden border-4 border-primary/20">
                    <img
                      src={formData.avatar_url}
                      alt="Avatar"
                      className="w-full h-full object-cover"
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="avatar_url">URL Immagine</Label>
                <Input
                  id="avatar_url"
                  name="avatar_url"
                  type="url"
                  placeholder="https://esempio.com/avatar.jpg"
                  value={formData.avatar_url}
                  onChange={handleChange}
                  disabled={isSaving}
                />
                <p className="text-xs text-muted-foreground">
                  Inserisci l'URL di un'immagine o lascia vuoto per usare l'avatar predefinito
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Personal Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Informazioni Personali
              </CardTitle>
              <CardDescription>
                Nome e cognome
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="first_name">Nome *</Label>
                  <Input
                    id="first_name"
                    name="first_name"
                    type="text"
                    placeholder="Mario"
                    value={formData.first_name}
                    onChange={handleChange}
                    required
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="last_name">Cognome *</Label>
                  <Input
                    id="last_name"
                    name="last_name"
                    type="text"
                    placeholder="Rossi"
                    value={formData.last_name}
                    onChange={handleChange}
                    required
                    disabled={isSaving}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Contact Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Informazioni di Contatto
              </CardTitle>
              <CardDescription>
                Email e telefono
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={formData.email}
                  disabled
                  className="bg-muted cursor-not-allowed"
                />
                <p className="text-xs text-muted-foreground">
                  L'email non può essere modificata. Contatta il supporto per cambiarla.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="phone">Telefono</Label>
                <Input
                  id="phone"
                  name="phone"
                  type="tel"
                  placeholder="+39 123 456 7890"
                  value={formData.phone}
                  onChange={handleChange}
                  disabled={isSaving}
                />
              </div>
            </CardContent>
          </Card>

          {/* Company Info */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Building className="h-5 w-5" />
                Informazioni Azienda
              </CardTitle>
              <CardDescription>
                Ragione sociale e dati aziendali
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="company_name">Nome Azienda</Label>
                <Input
                  id="company_name"
                  name="company_name"
                  type="text"
                  placeholder="Acme S.r.l."
                  value={formData.company_name}
                  onChange={handleChange}
                  disabled={isSaving}
                />
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex gap-4">
            <Button type="submit" size="lg" disabled={isSaving}>
              {isSaving ? 'Salvataggio...' : 'Salva Modifiche'}
            </Button>
            <Link href="/dashboard">
              <Button type="button" variant="outline" size="lg">
                Annulla
              </Button>
            </Link>
          </div>
        </form>
      </main>
    </>
  );
}
