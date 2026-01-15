/**
 * Admin Create Service Page
 * Descrizione: Form per creare nuovo servizio
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

export default function AdminCreateServicePage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin } = useAuth();

  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    category: 'AI_COMPLIANCE' as 'AI_COMPLIANCE' | 'CYBERSECURITY_NIS2' | 'TOOLKIT_FORMAZIONE',
    type: 'PACCHETTO_FISSO' as 'PACCHETTO_FISSO' | 'CUSTOM_QUOTE' | 'ABBONAMENTO',
    short_description: '',
    long_description: '',
    pricing_type: 'FIXED' as 'FIXED' | 'RANGE' | 'CUSTOM',
    price_min: '',
    price_max: '',
    currency: 'EUR',
    duration_weeks: '',
    is_featured: false,
    is_published: false,
    features: [''],
    deliverables: [''],
    target_audience: [''],
  });

  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Auto-generate slug from name
  const handleNameChange = (name: string) => {
    setFormData((prev) => ({
      ...prev,
      name,
      slug: name
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, ''),
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Prepare data
      const payload = {
        name: formData.name,
        slug: formData.slug,
        category: formData.category,
        type: formData.type,
        short_description: formData.short_description,
        long_description: formData.long_description,
        pricing_type: formData.pricing_type,
        price_min: formData.price_min ? parseFloat(formData.price_min) : undefined,
        price_max: formData.price_max ? parseFloat(formData.price_max) : undefined,
        currency: formData.currency,
        duration_weeks: formData.duration_weeks ? parseInt(formData.duration_weeks) : undefined,
        is_featured: formData.is_featured,
        is_published: formData.is_published,
        features: formData.features.filter((f) => f.trim() !== ''),
        deliverables: formData.deliverables.filter((d) => d.trim() !== ''),
        target_audience: formData.target_audience.filter((t) => t.trim() !== ''),
      };

      await apiClient.post('/api/v1/services', payload);

      // Redirect to services list
      router.push('/admin/services');
    } catch (err) {
      setError(getErrorMessage(err));
      setIsSubmitting(false);
    }
  };

  const addArrayItem = (field: 'features' | 'deliverables' | 'target_audience') => {
    setFormData((prev) => ({
      ...prev,
      [field]: [...prev[field], ''],
    }));
  };

  const updateArrayItem = (
    field: 'features' | 'deliverables' | 'target_audience',
    index: number,
    value: string
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: prev[field].map((item, i) => (i === index ? value : item)),
    }));
  };

  const removeArrayItem = (field: 'features' | 'deliverables' | 'target_audience', index: number) => {
    setFormData((prev) => ({
      ...prev,
      [field]: prev[field].filter((_, i) => i !== index),
    }));
  };

  if (!isAuthenticated || !isAdmin) {
    return null;
  }

  return (
    <>
      <Navigation />

      <main className="container py-12 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Crea Nuovo Servizio</h1>
          <p className="text-muted-foreground">
            Compila il form per creare un nuovo servizio di consulenza
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <Card>
            <CardHeader>
              <CardTitle>Informazioni Base</CardTitle>
              <CardDescription>Dettagli principali del servizio</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="name">Nome Servizio *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => handleNameChange(e.target.value)}
                  required
                  placeholder="es. Audit AI Compliance"
                />
              </div>

              <div>
                <Label htmlFor="slug">Slug URL *</Label>
                <Input
                  id="slug"
                  value={formData.slug}
                  onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                  required
                  placeholder="es. audit-ai-compliance"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Generato automaticamente dal nome
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="category">Categoria *</Label>
                  <select
                    id="category"
                    value={formData.category}
                    onChange={(e) => setFormData({ ...formData, category: e.target.value as any })}
                    className="w-full px-3 py-2 border rounded-md"
                    required
                  >
                    <option value="AI_COMPLIANCE">AI & Compliance</option>
                    <option value="CYBERSECURITY_NIS2">Cybersecurity & NIS2</option>
                    <option value="TOOLKIT_FORMAZIONE">Toolkit & Formazione</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="type">Tipo *</Label>
                  <select
                    id="type"
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as any })}
                    className="w-full px-3 py-2 border rounded-md"
                    required
                  >
                    <option value="PACCHETTO_FISSO">Pacchetto Fisso</option>
                    <option value="CUSTOM_QUOTE">Su Misura</option>
                    <option value="ABBONAMENTO">Abbonamento</option>
                  </select>
                </div>
              </div>

              <div>
                <Label htmlFor="short_description">Descrizione Breve *</Label>
                <textarea
                  id="short_description"
                  value={formData.short_description}
                  onChange={(e) => setFormData({ ...formData, short_description: e.target.value })}
                  required
                  rows={2}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="Breve descrizione (1-2 righe)"
                />
              </div>

              <div>
                <Label htmlFor="long_description">Descrizione Completa *</Label>
                <textarea
                  id="long_description"
                  value={formData.long_description}
                  onChange={(e) => setFormData({ ...formData, long_description: e.target.value })}
                  required
                  rows={6}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="Descrizione dettagliata del servizio"
                />
              </div>
            </CardContent>
          </Card>

          {/* Pricing */}
          <Card>
            <CardHeader>
              <CardTitle>Pricing</CardTitle>
              <CardDescription>Impostazioni di prezzo</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="pricing_type">Tipo Pricing *</Label>
                <select
                  id="pricing_type"
                  value={formData.pricing_type}
                  onChange={(e) => setFormData({ ...formData, pricing_type: e.target.value as any })}
                  className="w-full px-3 py-2 border rounded-md"
                  required
                >
                  <option value="FIXED">Prezzo Fisso</option>
                  <option value="RANGE">Range di Prezzo</option>
                  <option value="CUSTOM">Su Preventivo</option>
                </select>
              </div>

              {formData.pricing_type !== 'CUSTOM' && (
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="price_min">
                      {formData.pricing_type === 'FIXED' ? 'Prezzo (€)' : 'Prezzo Minimo (€)'}
                    </Label>
                    <Input
                      id="price_min"
                      type="number"
                      step="0.01"
                      value={formData.price_min}
                      onChange={(e) => setFormData({ ...formData, price_min: e.target.value })}
                      placeholder="es. 2500"
                    />
                  </div>

                  {formData.pricing_type === 'RANGE' && (
                    <div>
                      <Label htmlFor="price_max">Prezzo Massimo (€)</Label>
                      <Input
                        id="price_max"
                        type="number"
                        step="0.01"
                        value={formData.price_max}
                        onChange={(e) => setFormData({ ...formData, price_max: e.target.value })}
                        placeholder="es. 5000"
                      />
                    </div>
                  )}
                </div>
              )}

              <div>
                <Label htmlFor="duration_weeks">Durata Stimata (settimane)</Label>
                <Input
                  id="duration_weeks"
                  type="number"
                  value={formData.duration_weeks}
                  onChange={(e) => setFormData({ ...formData, duration_weeks: e.target.value })}
                  placeholder="es. 4"
                />
              </div>
            </CardContent>
          </Card>

          {/* Features */}
          <Card>
            <CardHeader>
              <CardTitle>Cosa Include</CardTitle>
              <CardDescription>Lista delle feature incluse</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {formData.features.map((feature, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    value={feature}
                    onChange={(e) => updateArrayItem('features', index, e.target.value)}
                    placeholder="es. Analisi documentale completa"
                  />
                  {formData.features.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => removeArrayItem('features', index)}
                    >
                      Rimuovi
                    </Button>
                  )}
                </div>
              ))}
              <Button type="button" variant="outline" onClick={() => addArrayItem('features')}>
                + Aggiungi Feature
              </Button>
            </CardContent>
          </Card>

          {/* Deliverables */}
          <Card>
            <CardHeader>
              <CardTitle>Cosa Riceverai</CardTitle>
              <CardDescription>Lista dei deliverables</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {formData.deliverables.map((deliverable, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    value={deliverable}
                    onChange={(e) => updateArrayItem('deliverables', index, e.target.value)}
                    placeholder="es. Report PDF completo"
                  />
                  {formData.deliverables.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => removeArrayItem('deliverables', index)}
                    >
                      Rimuovi
                    </Button>
                  )}
                </div>
              ))}
              <Button type="button" variant="outline" onClick={() => addArrayItem('deliverables')}>
                + Aggiungi Deliverable
              </Button>
            </CardContent>
          </Card>

          {/* Target Audience */}
          <Card>
            <CardHeader>
              <CardTitle>Per Chi È Questo Servizio</CardTitle>
              <CardDescription>Target audience</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {formData.target_audience.map((audience, index) => (
                <div key={index} className="flex gap-2">
                  <Input
                    value={audience}
                    onChange={(e) => updateArrayItem('target_audience', index, e.target.value)}
                    placeholder="es. PMI che implementano sistemi AI"
                  />
                  {formData.target_audience.length > 1 && (
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => removeArrayItem('target_audience', index)}
                    >
                      Rimuovi
                    </Button>
                  )}
                </div>
              ))}
              <Button type="button" variant="outline" onClick={() => addArrayItem('target_audience')}>
                + Aggiungi Target
              </Button>
            </CardContent>
          </Card>

          {/* Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Impostazioni</CardTitle>
              <CardDescription>Status e visibilità</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_featured"
                  checked={formData.is_featured}
                  onChange={(e) => setFormData({ ...formData, is_featured: e.target.checked })}
                  className="w-4 h-4"
                />
                <Label htmlFor="is_featured">In Evidenza</Label>
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="is_published"
                  checked={formData.is_published}
                  onChange={(e) => setFormData({ ...formData, is_published: e.target.checked })}
                  className="w-4 h-4"
                />
                <Label htmlFor="is_published">Pubblica subito</Label>
              </div>
            </CardContent>
          </Card>

          {/* Actions */}
          <div className="flex gap-4">
            <Button type="submit" size="lg" disabled={isSubmitting}>
              {isSubmitting ? 'Salvataggio...' : 'Crea Servizio'}
            </Button>
            <Link href="/admin/services">
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
