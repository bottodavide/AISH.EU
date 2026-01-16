/**
 * New User Creation
 * Descrizione: Form per creare nuovo utente (admin)
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { ArrowLeft, Save } from 'lucide-react';

export default function NewUserPage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
    role: 'customer' as 'super_admin' | 'admin' | 'customer',
    is_active: true,
    email_verified: false,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Validate
      if (!formData.email || !formData.password || !formData.full_name) {
        throw new Error('Email, password e nome completo sono obbligatori');
      }

      if (formData.password !== formData.confirmPassword) {
        throw new Error('Le password non corrispondono');
      }

      if (formData.password.length < 8) {
        throw new Error('La password deve essere di almeno 8 caratteri');
      }

      const payload = {
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name,
        role: formData.role,
        is_active: formData.is_active,
        email_verified: formData.email_verified,
      };

      const response = await apiClient.post('/admin/users', payload);

      // Success - redirect to users list
      router.push('/admin/users');
    } catch (err) {
      setError(getErrorMessage(err));
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container py-8 max-w-2xl">
      {/* Header */}
      <div className="mb-8">
        <Link href="/admin/users">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Torna agli Utenti
          </Button>
        </Link>
        <h1 className="text-3xl font-bold">Crea Nuovo Utente</h1>
        <p className="text-muted-foreground mt-2">
          Aggiungi un nuovo utente al sistema
        </p>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Account Info */}
        <Card>
          <CardHeader>
            <CardTitle>Informazioni Account</CardTitle>
            <CardDescription>
              Dati di accesso e informazioni base
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                placeholder="utente@example.com"
                required
              />
            </div>

            <div>
              <Label htmlFor="full_name">Nome Completo *</Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) =>
                  setFormData({ ...formData, full_name: e.target.value })
                }
                placeholder="Mario Rossi"
                required
              />
            </div>

            <div>
              <Label htmlFor="password">Password *</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                placeholder="••••••••"
                minLength={8}
                required
              />
              <p className="text-sm text-muted-foreground mt-1">
                Minimo 8 caratteri
              </p>
            </div>

            <div>
              <Label htmlFor="confirmPassword">Conferma Password *</Label>
              <Input
                id="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={(e) =>
                  setFormData({ ...formData, confirmPassword: e.target.value })
                }
                placeholder="••••••••"
                required
              />
            </div>
          </CardContent>
        </Card>

        {/* Role & Permissions */}
        <Card>
          <CardHeader>
            <CardTitle>Ruolo e Permessi</CardTitle>
            <CardDescription>
              Seleziona il ruolo e i permessi dell'utente
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="role">Ruolo</Label>
              <select
                id="role"
                value={formData.role}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    role: e.target.value as any,
                  })
                }
                className="w-full rounded-md border border-input bg-background px-3 py-2"
              >
                <option value="customer">Cliente</option>
                <option value="admin">Amministratore</option>
                <option value="super_admin">Super Amministratore</option>
              </select>
              <div className="mt-2 text-sm text-muted-foreground space-y-1">
                <p>
                  <strong>Cliente:</strong> Accesso standard, può acquistare
                  servizi
                </p>
                <p>
                  <strong>Amministratore:</strong> Può gestire contenuti, ordini
                  e utenti
                </p>
                <p>
                  <strong>Super Amministratore:</strong> Accesso completo a tutte
                  le funzionalità
                </p>
              </div>
            </div>

            <div className="space-y-3 pt-4 border-t">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.is_active}
                  onChange={(e) =>
                    setFormData({ ...formData, is_active: e.target.checked })
                  }
                  className="rounded border-gray-300"
                />
                <div>
                  <span className="font-medium">Account Attivo</span>
                  <p className="text-sm text-muted-foreground">
                    L'utente può accedere al sistema
                  </p>
                </div>
              </label>

              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={formData.email_verified}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      email_verified: e.target.checked,
                    })
                  }
                  className="rounded border-gray-300"
                />
                <div>
                  <span className="font-medium">Email Verificata</span>
                  <p className="text-sm text-muted-foreground">
                    Segna l'email come già verificata (salta verifica)
                  </p>
                </div>
              </label>
            </div>
          </CardContent>
        </Card>

        {/* Submit Buttons */}
        <div className="flex gap-4">
          <Button type="submit" disabled={isSubmitting} size="lg">
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Creazione...' : 'Crea Utente'}
          </Button>
          <Link href="/admin/users">
            <Button type="button" variant="outline" size="lg">
              Annulla
            </Button>
          </Link>
        </div>
      </form>
    </div>
  );
}
