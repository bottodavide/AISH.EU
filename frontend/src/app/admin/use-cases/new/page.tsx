/**
 * Admin Create Use Case Page
 * Descrizione: Form per creare nuovo caso d'uso
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { ArrowLeft, Save } from 'lucide-react';

interface UseCaseFormData {
  title: string;
  slug: string;
  industry: string;
  icon: string;
  challenge_title: string;
  challenge_description: string;
  solution_title: string;
  solution_description: string;
  result_title: string;
  result_description: string;
  display_order: number;
  is_active: boolean;
}

export default function AdminNewUseCasePage() {
  const router = useRouter();
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [formData, setFormData] = useState<UseCaseFormData>({
    title: '',
    slug: '',
    industry: 'Finance',
    icon: '',
    challenge_title: 'LA SFIDA',
    challenge_description: '',
    solution_title: 'LA SOLUZIONE',
    solution_description: '',
    result_title: 'IL RISULTATO',
    result_description: '',
    display_order: 0,
    is_active: true,
  });

  const handleChange = (field: keyof UseCaseFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));

    // Auto-generate slug from title
    if (field === 'title' && value) {
      const slug = value
        .toLowerCase()
        .replace(/[àáâãäå]/g, 'a')
        .replace(/[èéêë]/g, 'e')
        .replace(/[ìíîï]/g, 'i')
        .replace(/[òóôõö]/g, 'o')
        .replace(/[ùúûü]/g, 'u')
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
      setFormData((prev) => ({ ...prev, slug }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validation
    if (!formData.title.trim()) {
      setError('Il titolo è obbligatorio');
      return;
    }
    if (!formData.slug.trim()) {
      setError('Lo slug è obbligatorio');
      return;
    }
    if (!formData.challenge_description.trim()) {
      setError('La descrizione della sfida è obbligatoria');
      return;
    }
    if (!formData.solution_description.trim()) {
      setError('La descrizione della soluzione è obbligatoria');
      return;
    }
    if (!formData.result_description.trim()) {
      setError('La descrizione del risultato è obbligatoria');
      return;
    }

    setIsSaving(true);

    try {
      await apiClient.post('/use-cases/admin', formData);
      setSuccess('Caso d\'uso creato con successo!');
      setTimeout(() => {
        router.push('/admin/use-cases');
      }, 1000);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <Navigation />

      <main className="container py-12">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex items-center gap-4">
            <Link href="/admin/use-cases">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <h1 className="text-4xl font-bold mb-2">Nuovo Caso d'Uso</h1>
              <p className="text-muted-foreground">
                Crea un nuovo success story
              </p>
            </div>
          </div>

          {/* Alerts */}
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mb-6 border-green-500/50 text-green-700 dark:text-green-400">
              <AlertDescription>{success}</AlertDescription>
            </Alert>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Informazioni Principali */}
            <Card>
              <CardHeader>
                <CardTitle>Informazioni Principali</CardTitle>
                <CardDescription>Titolo, categoria e identificativo</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Titolo *</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => handleChange('title', e.target.value)}
                    placeholder="es: Fintech: AI Credit Scoring Compliance"
                    required
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="slug">Slug URL *</Label>
                  <Input
                    id="slug"
                    value={formData.slug}
                    onChange={(e) => handleChange('slug', e.target.value)}
                    placeholder="fintech-ai-credit-scoring"
                    required
                    disabled={isSaving}
                  />
                  <p className="text-xs text-muted-foreground">
                    URL: /casi-uso/{formData.slug || 'slug'}
                  </p>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="industry">Settore *</Label>
                    <Select
                      value={formData.industry}
                      onValueChange={(value) => handleChange('industry', value)}
                      disabled={isSaving}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Finance">Finance</SelectItem>
                        <SelectItem value="Sanità">Sanità</SelectItem>
                        <SelectItem value="Retail">Retail</SelectItem>
                        <SelectItem value="E-commerce">E-commerce</SelectItem>
                        <SelectItem value="Manufacturing">Manufacturing</SelectItem>
                        <SelectItem value="Industria 4.0">Industria 4.0</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="icon">Icona (nome Lucide)</Label>
                    <Input
                      id="icon"
                      value={formData.icon}
                      onChange={(e) => handleChange('icon', e.target.value)}
                      placeholder="Building2, Heart, ShoppingCart..."
                      disabled={isSaving}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* LA SFIDA */}
            <Card>
              <CardHeader>
                <CardTitle>La Sfida</CardTitle>
                <CardDescription>Descrivi il problema del cliente</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="challenge_title">Titolo Sezione</Label>
                  <Input
                    id="challenge_title"
                    value={formData.challenge_title}
                    onChange={(e) => handleChange('challenge_title', e.target.value)}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="challenge_description">Descrizione *</Label>
                  <Textarea
                    id="challenge_description"
                    value={formData.challenge_description}
                    onChange={(e) => handleChange('challenge_description', e.target.value)}
                    placeholder="Descrivi la sfida o il problema che il cliente doveva affrontare..."
                    rows={4}
                    required
                    disabled={isSaving}
                  />
                </div>
              </CardContent>
            </Card>

            {/* LA SOLUZIONE */}
            <Card>
              <CardHeader>
                <CardTitle>La Soluzione</CardTitle>
                <CardDescription>Come è stato risolto il problema</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="solution_title">Titolo Sezione</Label>
                  <Input
                    id="solution_title"
                    value={formData.solution_title}
                    onChange={(e) => handleChange('solution_title', e.target.value)}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="solution_description">Descrizione *</Label>
                  <Textarea
                    id="solution_description"
                    value={formData.solution_description}
                    onChange={(e) => handleChange('solution_description', e.target.value)}
                    placeholder="Descrivi la soluzione implementata..."
                    rows={4}
                    required
                    disabled={isSaving}
                  />
                </div>
              </CardContent>
            </Card>

            {/* IL RISULTATO */}
            <Card>
              <CardHeader>
                <CardTitle>Il Risultato</CardTitle>
                <CardDescription>L'outcome ottenuto</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="result_title">Titolo Sezione</Label>
                  <Input
                    id="result_title"
                    value={formData.result_title}
                    onChange={(e) => handleChange('result_title', e.target.value)}
                    disabled={isSaving}
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="result_description">Descrizione *</Label>
                  <Textarea
                    id="result_description"
                    value={formData.result_description}
                    onChange={(e) => handleChange('result_description', e.target.value)}
                    placeholder="Descrivi i risultati ottenuti..."
                    rows={4}
                    required
                    disabled={isSaving}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Pubblicazione */}
            <Card>
              <CardHeader>
                <CardTitle>Pubblicazione</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="display_order">Ordine Visualizzazione</Label>
                    <Input
                      id="display_order"
                      type="number"
                      min="0"
                      value={formData.display_order}
                      onChange={(e) => handleChange('display_order', parseInt(e.target.value) || 0)}
                      disabled={isSaving}
                    />
                  </div>

                  <div className="space-y-2 flex items-end">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="is_active"
                        checked={formData.is_active}
                        onCheckedChange={(checked) => handleChange('is_active', checked)}
                        disabled={isSaving}
                      />
                      <Label htmlFor="is_active">Pubblica (visibile sul sito)</Label>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex gap-4">
              <Button type="submit" size="lg" disabled={isSaving}>
                <Save className="h-5 w-5 mr-2" />
                {isSaving ? 'Salvataggio...' : 'Crea Caso d\'Uso'}
              </Button>
              <Link href="/admin/use-cases">
                <Button type="button" variant="outline" size="lg" disabled={isSaving}>
                  Annulla
                </Button>
              </Link>
            </div>
          </form>
        </div>
      </main>
    </>
  );
}
