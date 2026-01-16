/**
 * Admin Edit Use Case Page
 * Descrizione: Form per modificare caso d'uso esistente
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState, useEffect } from 'react';
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
import { ArrowLeft, Save, Loader2 } from 'lucide-react';

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

export default function AdminEditUseCasePage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
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

  // Load use case data
  useEffect(() => {
    const loadUseCase = async () => {
      try {
        setIsLoading(true);
        setError(null);

        // Fetch from admin endpoint to get all data including inactive
        const response = await apiClient.get(`/use-cases/admin/all?page=1&page_size=100`);
        const useCase = response.use_cases.find((uc: any) => uc.id === params.id);

        if (!useCase) {
          setError('Caso d\'uso non trovato');
          return;
        }

        setFormData({
          title: useCase.title || '',
          slug: useCase.slug || '',
          industry: useCase.industry || 'Finance',
          icon: useCase.icon || '',
          challenge_title: useCase.challenge_title || 'LA SFIDA',
          challenge_description: useCase.challenge_description || '',
          solution_title: useCase.solution_title || 'LA SOLUZIONE',
          solution_description: useCase.solution_description || '',
          result_title: useCase.result_title || 'IL RISULTATO',
          result_description: useCase.result_description || '',
          display_order: useCase.display_order || 0,
          is_active: useCase.is_active !== false,
        });
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setIsLoading(false);
      }
    };

    loadUseCase();
  }, [params.id]);

  const handleChange = (field: keyof UseCaseFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
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

    setIsSaving(true);

    try {
      await apiClient.put(`/use-cases/admin/${params.id}`, formData);
      setSuccess('Caso d\'uso aggiornato con successo!');
      setTimeout(() => {
        router.push('/admin/use-cases');
      }, 1000);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <>
        <Navigation />
        <main className="container py-12">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-muted-foreground">Caricamento caso d'uso...</p>
              </div>
            </div>
          </div>
        </main>
      </>
    );
  }

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
              <h1 className="text-4xl font-bold mb-2">Modifica Caso d'Uso</h1>
              <p className="text-muted-foreground">
                Aggiorna le informazioni del caso d'uso
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
                {isSaving ? 'Salvataggio...' : 'Salva Modifiche'}
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
