/**
 * Edit Page
 * Descrizione: Form per modificare pagina CMS esistente
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';

interface ContentSection {
  section_type: string;
  content: any;
  order: number;
}

interface Page {
  id: string;
  slug: string;
  title: string;
  page_type: string;
  meta_title?: string;
  meta_description?: string;
  meta_keywords?: string;
  og_image_url?: string;
  is_published: boolean;
  content_sections: any[];
  status: string;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

interface EditPageProps {
  params: {
    id: string;
  };
}

export default function EditPagePage({ params }: EditPageProps) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState<Page | null>(null);

  const [formData, setFormData] = useState({
    slug: '',
    title: '',
    page_type: 'custom' as string,
    meta_title: '',
    meta_description: '',
    meta_keywords: '',
    og_image_url: '',
    is_published: false,
  });

  const [contentSections, setContentSections] = useState<ContentSection[]>([]);

  useEffect(() => {
    loadPage();
  }, [params.id]);

  const loadPage = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<Page>(`/cms/pages/${params.id}`);
      setPage(response);

      // Populate form
      setFormData({
        slug: response.slug,
        title: response.title,
        page_type: response.page_type,
        meta_title: response.meta_title || '',
        meta_description: response.meta_description || '',
        meta_keywords: response.meta_keywords || '',
        og_image_url: response.og_image_url || '',
        is_published: response.is_published,
      });

      // Load content sections
      if (response.content_sections && response.content_sections.length > 0) {
        setContentSections(response.content_sections as ContentSection[]);
      } else {
        setContentSections([
          {
            section_type: 'text',
            content: { text: '' },
            order: 0,
          },
        ]);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Validate required fields
      if (!formData.slug || !formData.title) {
        throw new Error('Slug e titolo sono obbligatori');
      }

      const payload = {
        ...formData,
        og_image_url: formData.og_image_url || undefined,
        content_sections: contentSections,
      };

      await apiClient.put(`/cms/pages/${params.id}`, payload);

      // Reload page to show updates
      await loadPage();

      // Show success message
      alert('Pagina aggiornata con successo!');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!confirm('Sei sicuro di voler eliminare questa pagina?')) {
      return;
    }

    try {
      await apiClient.delete(`/cms/pages/${params.id}`);
      router.push('/admin/pages');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handlePublish = async () => {
    try {
      await apiClient.post(`/cms/pages/${params.id}/publish`, {});
      await loadPage();
      alert('Pagina pubblicata con successo!');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleUnpublish = async () => {
    try {
      await apiClient.put(`/cms/pages/${params.id}`, {
        is_published: false,
      });
      await loadPage();
      alert('Pagina impostata come bozza!');
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const addSection = () => {
    setContentSections([
      ...contentSections,
      {
        section_type: 'text',
        content: { text: '' },
        order: contentSections.length,
      },
    ]);
  };

  const removeSection = (index: number) => {
    const newSections = contentSections.filter((_, i) => i !== index);
    newSections.forEach((section, i) => {
      section.order = i;
    });
    setContentSections(newSections);
  };

  const updateSection = (index: number, field: string, value: any) => {
    const newSections = [...contentSections];
    if (field === 'section_type') {
      newSections[index].section_type = value;
    } else {
      newSections[index].content[field] = value;
    }
    setContentSections(newSections);
  };

  if (isLoading) {
    return (
      <div className="container py-8">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Caricamento pagina...</p>
        </div>
      </div>
    );
  }

  if (!page) {
    return (
      <div className="container py-8">
        <Alert variant="destructive">
          <AlertDescription>Pagina non trovata</AlertDescription>
        </Alert>
        <div className="mt-4">
          <Link href="/admin/pages">
            <Button>Torna alle Pagine</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8 max-w-4xl">
      {/* Header */}
      <div className="mb-8">
        <Link href="/admin/pages">
          <Button variant="ghost" size="sm" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Torna alle Pagine
          </Button>
        </Link>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Modifica Pagina</h1>
            <p className="text-muted-foreground mt-2">
              {page.is_published ? (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  Pubblicata
                </span>
              ) : (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                  Bozza
                </span>
              )}
            </p>
          </div>
          <div className="flex gap-2">
            {page.is_published ? (
              <Button variant="outline" onClick={handleUnpublish}>
                Imposta come Bozza
              </Button>
            ) : (
              <Button onClick={handlePublish}>Pubblica</Button>
            )}
            <Button variant="destructive" onClick={handleDelete}>
              <Trash2 className="h-4 w-4 mr-2" />
              Elimina
            </Button>
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>Informazioni Base</CardTitle>
            <CardDescription>
              Modifica le informazioni principali della pagina
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="title">Titolo *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) =>
                  setFormData({ ...formData, title: e.target.value })
                }
                placeholder="Titolo della pagina"
                required
              />
            </div>

            <div>
              <Label htmlFor="slug">Slug (URL) *</Label>
              <Input
                id="slug"
                value={formData.slug}
                onChange={(e) =>
                  setFormData({ ...formData, slug: e.target.value })
                }
                placeholder="slug-pagina"
                required
              />
              <p className="text-sm text-muted-foreground mt-1">
                URL della pagina: /{formData.slug}
              </p>
            </div>

            <div>
              <Label htmlFor="page_type">Tipo Pagina</Label>
              <select
                id="page_type"
                value={formData.page_type}
                onChange={(e) =>
                  setFormData({ ...formData, page_type: e.target.value })
                }
                className="w-full rounded-md border border-input bg-background px-3 py-2"
              >
                <option value="custom">Personalizzata</option>
                <option value="homepage">Homepage</option>
                <option value="about">Chi Siamo</option>
                <option value="contact">Contatti</option>
                <option value="service">Servizio</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* SEO Meta */}
        <Card>
          <CardHeader>
            <CardTitle>SEO & Meta</CardTitle>
            <CardDescription>
              Ottimizza la pagina per i motori di ricerca
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="meta_title">Meta Title</Label>
              <Input
                id="meta_title"
                value={formData.meta_title}
                onChange={(e) =>
                  setFormData({ ...formData, meta_title: e.target.value })
                }
                placeholder="Titolo per SEO"
                maxLength={60}
              />
              <p className="text-sm text-muted-foreground mt-1">
                {formData.meta_title.length}/60 caratteri
              </p>
            </div>

            <div>
              <Label htmlFor="meta_description">Meta Description</Label>
              <textarea
                id="meta_description"
                value={formData.meta_description}
                onChange={(e) =>
                  setFormData({ ...formData, meta_description: e.target.value })
                }
                placeholder="Descrizione per motori di ricerca"
                maxLength={160}
                rows={3}
                className="w-full rounded-md border border-input bg-background px-3 py-2"
              />
              <p className="text-sm text-muted-foreground mt-1">
                {formData.meta_description.length}/160 caratteri
              </p>
            </div>

            <div>
              <Label htmlFor="meta_keywords">Meta Keywords</Label>
              <Input
                id="meta_keywords"
                value={formData.meta_keywords}
                onChange={(e) =>
                  setFormData({ ...formData, meta_keywords: e.target.value })
                }
                placeholder="parola1, parola2, parola3"
              />
            </div>

            <div>
              <Label htmlFor="og_image_url">Open Graph Image URL</Label>
              <Input
                id="og_image_url"
                type="url"
                value={formData.og_image_url}
                onChange={(e) =>
                  setFormData({ ...formData, og_image_url: e.target.value })
                }
                placeholder="https://example.com/image.jpg"
              />
            </div>
          </CardContent>
        </Card>

        {/* Content Sections */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Sezioni Contenuto</CardTitle>
                <CardDescription>
                  Modifica le sezioni della pagina
                </CardDescription>
              </div>
              <Button type="button" variant="outline" onClick={addSection}>
                Aggiungi Sezione
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {contentSections.map((section, index) => (
              <div key={index} className="border rounded-lg p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <Label>Sezione {index + 1}</Label>
                  {contentSections.length > 1 && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => removeSection(index)}
                      className="text-destructive"
                    >
                      Rimuovi
                    </Button>
                  )}
                </div>

                <div>
                  <Label>Tipo Sezione</Label>
                  <select
                    value={section.section_type}
                    onChange={(e) =>
                      updateSection(index, 'section_type', e.target.value)
                    }
                    className="w-full rounded-md border border-input bg-background px-3 py-2"
                  >
                    <option value="text">Testo</option>
                    <option value="hero">Hero</option>
                    <option value="cta">Call to Action</option>
                    <option value="features">Features</option>
                    <option value="gallery">Galleria</option>
                  </select>
                </div>

                <div>
                  <Label>Contenuto</Label>
                  <textarea
                    value={section.content.text || ''}
                    onChange={(e) =>
                      updateSection(index, 'text', e.target.value)
                    }
                    rows={4}
                    className="w-full rounded-md border border-input bg-background px-3 py-2"
                    placeholder="Inserisci il contenuto della sezione..."
                  />
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Submit Buttons */}
        <div className="flex gap-4">
          <Button type="submit" disabled={isSubmitting} size="lg">
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Salvataggio...' : 'Salva Modifiche'}
          </Button>
          <Link href="/admin/pages">
            <Button type="button" variant="outline" size="lg">
              Annulla
            </Button>
          </Link>
        </div>
      </form>

      {/* Page Info */}
      <Card className="mt-8">
        <CardHeader>
          <CardTitle>Informazioni Pagina</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">ID:</span>
            <span className="font-mono">{page.id}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Creata il:</span>
            <span>
              {new Date(page.created_at).toLocaleDateString('it-IT', {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Ultimo aggiornamento:</span>
            <span>
              {new Date(page.updated_at).toLocaleDateString('it-IT', {
                day: '2-digit',
                month: 'long',
                year: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
              })}
            </span>
          </div>
          {page.published_at && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">Pubblicata il:</span>
              <span>
                {new Date(page.published_at).toLocaleDateString('it-IT', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
