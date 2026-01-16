/**
 * Profile Edit Page
 * Descrizione: Modifica profilo utente con upload avatar
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/contexts/AuthContext';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { User, Building, Mail, Phone, CheckCircle, Camera, MapPin } from 'lucide-react';

interface ProfileData {
  first_name: string;
  last_name: string;
  email: string;
  company_name?: string;
  phone_mobile?: string;
  phone_landline?: string;
  vat_number?: string;
  tax_code?: string;
  rea_number?: string;
  sdi_code?: string;
  pec_email?: string;
  legal_address_street?: string;
  legal_address_city?: string;
  legal_address_zip?: string;
  legal_address_province?: string;
  legal_address_country?: string;
  operational_address_street?: string;
  operational_address_city?: string;
  operational_address_zip?: string;
  operational_address_province?: string;
  operational_address_country?: string;
  avatar_url?: string;
}

export default function ProfileEditPage() {
  const { user, isAuthenticated } = useAuth();

  const [formData, setFormData] = useState<ProfileData>({
    first_name: '',
    last_name: '',
    email: '',
    company_name: '',
    phone_mobile: '',
    phone_landline: '',
    vat_number: '',
    tax_code: '',
    rea_number: '',
    sdi_code: '',
    pec_email: '',
    legal_address_street: '',
    legal_address_city: '',
    legal_address_zip: '',
    legal_address_province: '',
    legal_address_country: 'IT',
    operational_address_street: '',
    operational_address_city: '',
    operational_address_zip: '',
    operational_address_province: '',
    operational_address_country: 'IT',
    avatar_url: '',
  });

  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
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
      const profile = await apiClient.get<any>('/users/me');

      setFormData({
        first_name: profile.profile?.first_name || '',
        last_name: profile.profile?.last_name || '',
        email: profile.email || '',
        company_name: profile.profile?.company_name || '',
        phone_mobile: profile.profile?.phone_mobile || '',
        phone_landline: profile.profile?.phone_landline || '',
        vat_number: profile.profile?.vat_number || '',
        tax_code: profile.profile?.tax_code || '',
        rea_number: profile.profile?.rea_number || '',
        sdi_code: profile.profile?.sdi_code || '',
        pec_email: profile.profile?.pec_email || '',
        legal_address_street: profile.profile?.legal_address?.street || '',
        legal_address_city: profile.profile?.legal_address?.city || '',
        legal_address_zip: profile.profile?.legal_address?.zip || '',
        legal_address_province: profile.profile?.legal_address?.province || '',
        legal_address_country: profile.profile?.legal_address?.country || 'IT',
        operational_address_street: profile.profile?.operational_address?.street || '',
        operational_address_city: profile.profile?.operational_address?.city || '',
        operational_address_zip: profile.profile?.operational_address?.zip || '',
        operational_address_province: profile.profile?.operational_address?.province || '',
        operational_address_country: profile.profile?.operational_address?.country || 'IT',
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

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Formato file non valido. Usa JPG, PNG o WEBP.');
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File troppo grande. Dimensione massima: 5MB.');
      return;
    }

    setIsUploadingAvatar(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', 'avatar');
      formData.append('is_public', 'true');

      const response = await apiClient.postFormData('/files/upload', formData);

      // Update avatar URL with the file download URL
      setFormData((prev) => ({
        ...prev,
        avatar_url: response.url,
      }));

      // Save avatar URL to profile immediately
      await apiClient.put('/users/me', {
        avatar_url: response.url,
      });

      setSuccess('Avatar caricato e salvato con successo!');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsUploadingAvatar(false);
    }
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
      // Prepare legal address JSON
      const legal_address = formData.legal_address_street ? {
        street: formData.legal_address_street,
        city: formData.legal_address_city || '',
        zip: formData.legal_address_zip || '',
        province: formData.legal_address_province || '',
        country: formData.legal_address_country || 'IT',
      } : undefined;

      // Prepare operational address JSON
      const operational_address = formData.operational_address_street ? {
        street: formData.operational_address_street,
        city: formData.operational_address_city || '',
        zip: formData.operational_address_zip || '',
        province: formData.operational_address_province || '',
        country: formData.operational_address_country || 'IT',
      } : undefined;

      await apiClient.put('/users/me', {
        first_name: formData.first_name,
        last_name: formData.last_name,
        company_name: formData.company_name || undefined,
        phone_mobile: formData.phone_mobile || undefined,
        phone_landline: formData.phone_landline || undefined,
        vat_number: formData.vat_number || undefined,
        tax_code: formData.tax_code || undefined,
        rea_number: formData.rea_number || undefined,
        sdi_code: formData.sdi_code || undefined,
        pec_email: formData.pec_email || undefined,
        legal_address: legal_address,
        operational_address: operational_address,
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
      <div className="container mx-auto flex items-center justify-center min-h-screen px-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <main className="container mx-auto py-8 px-4 max-w-3xl">
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
                      src={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${formData.avatar_url}`}
                      alt="Avatar"
                      className="w-full h-full object-cover"
                      onError={(e) => {
                        // Fallback to placeholder if image fails to load
                        e.currentTarget.src = 'https://via.placeholder.com/400x400?text=Avatar';
                      }}
                    />
                  </div>
                </div>
              )}

              <div className="space-y-2">
                <Label htmlFor="avatar_file">Carica Immagine</Label>
                <Input
                  id="avatar_file"
                  type="file"
                  accept=".jpg,.jpeg,.png,.webp"
                  onChange={handleAvatarUpload}
                  disabled={isSaving || isUploadingAvatar}
                  className="cursor-pointer"
                />
                <div className="text-xs text-muted-foreground space-y-1">
                  <p><strong>Formati supportati:</strong> JPG, PNG, WEBP</p>
                  <p><strong>Dimensione massima:</strong> 5 MB</p>
                  <p><strong>Dimensioni consigliate:</strong> 400x400 px (verrà ridimensionata automaticamente)</p>
                </div>
                {isUploadingAvatar && (
                  <div className="flex items-center gap-2 text-sm text-primary">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                    Caricamento in corso...
                  </div>
                )}
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
                <Phone className="h-5 w-5" />
                Informazioni di Contatto
              </CardTitle>
              <CardDescription>
                Email e recapiti telefonici
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

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="phone_mobile">Telefono Mobile</Label>
                  <Input
                    id="phone_mobile"
                    name="phone_mobile"
                    type="tel"
                    placeholder="+39 333 123 4567"
                    value={formData.phone_mobile}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone_landline">Telefono Fisso</Label>
                  <Input
                    id="phone_landline"
                    name="phone_landline"
                    type="tel"
                    placeholder="+39 02 1234567"
                    value={formData.phone_landline}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>
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
                <Label htmlFor="company_name">Ragione Sociale</Label>
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

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="vat_number">Partita IVA</Label>
                  <Input
                    id="vat_number"
                    name="vat_number"
                    type="text"
                    placeholder="IT12345678901"
                    value={formData.vat_number}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="tax_code">Codice Fiscale</Label>
                  <Input
                    id="tax_code"
                    name="tax_code"
                    type="text"
                    placeholder="RSSMRA80A01H501U"
                    value={formData.tax_code}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="rea_number">Numero REA</Label>
                <Input
                  id="rea_number"
                  name="rea_number"
                  type="text"
                  placeholder="MI-1234567"
                  value={formData.rea_number}
                  onChange={handleChange}
                  disabled={isSaving}
                />
                <p className="text-xs text-muted-foreground">
                  Repertorio Economico Amministrativo (es: MI-1234567)
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="sdi_code">Codice SDI</Label>
                  <Input
                    id="sdi_code"
                    name="sdi_code"
                    type="text"
                    placeholder="ABCDEFG"
                    maxLength={7}
                    value={formData.sdi_code}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                  <p className="text-xs text-muted-foreground">
                    Codice destinatario fatturazione elettronica (7 caratteri)
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="pec_email">Email PEC</Label>
                  <Input
                    id="pec_email"
                    name="pec_email"
                    type="email"
                    placeholder="azienda@pec.it"
                    value={formData.pec_email}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                  <p className="text-xs text-muted-foreground">
                    Posta Elettronica Certificata per fatture
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Legal Address */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Sede Legale
              </CardTitle>
              <CardDescription>
                Indirizzo della sede legale dell'azienda
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="legal_address_street">Indirizzo</Label>
                <Input
                  id="legal_address_street"
                  name="legal_address_street"
                  type="text"
                  placeholder="Via Roma 123"
                  value={formData.legal_address_street}
                  onChange={handleChange}
                  disabled={isSaving}
                />
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="legal_address_city">Città</Label>
                  <Input
                    id="legal_address_city"
                    name="legal_address_city"
                    type="text"
                    placeholder="Milano"
                    value={formData.legal_address_city}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="legal_address_province">Provincia</Label>
                  <Input
                    id="legal_address_province"
                    name="legal_address_province"
                    type="text"
                    placeholder="MI"
                    maxLength={2}
                    value={formData.legal_address_province}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="legal_address_zip">CAP</Label>
                  <Input
                    id="legal_address_zip"
                    name="legal_address_zip"
                    type="text"
                    placeholder="20100"
                    maxLength={5}
                    value={formData.legal_address_zip}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="legal_address_country">Paese</Label>
                <Input
                  id="legal_address_country"
                  name="legal_address_country"
                  type="text"
                  placeholder="IT"
                  maxLength={2}
                  value={formData.legal_address_country}
                  onChange={handleChange}
                  disabled={isSaving}
                />
              </div>
            </CardContent>
          </Card>

          {/* Operational Address */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MapPin className="h-5 w-5" />
                Sede Operativa
              </CardTitle>
              <CardDescription>
                Indirizzo della sede operativa (se diverso dalla sede legale)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="operational_address_street">Indirizzo</Label>
                <Input
                  id="operational_address_street"
                  name="operational_address_street"
                  type="text"
                  placeholder="Via Roma 123"
                  value={formData.operational_address_street}
                  onChange={handleChange}
                  disabled={isSaving}
                />
              </div>

              <div className="grid md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="operational_address_city">Città</Label>
                  <Input
                    id="operational_address_city"
                    name="operational_address_city"
                    type="text"
                    placeholder="Milano"
                    value={formData.operational_address_city}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="operational_address_province">Provincia</Label>
                  <Input
                    id="operational_address_province"
                    name="operational_address_province"
                    type="text"
                    placeholder="MI"
                    maxLength={2}
                    value={formData.operational_address_province}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="operational_address_zip">CAP</Label>
                  <Input
                    id="operational_address_zip"
                    name="operational_address_zip"
                    type="text"
                    placeholder="20100"
                    maxLength={5}
                    value={formData.operational_address_zip}
                    onChange={handleChange}
                    disabled={isSaving}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="operational_address_country">Paese</Label>
                <Input
                  id="operational_address_country"
                  name="operational_address_country"
                  type="text"
                  placeholder="IT"
                  maxLength={2}
                  value={formData.operational_address_country}
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
  );
}
