/**
 * New Page Creation
 * Descrizione: Form per creare nuova pagina CMS
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

interface ContentSection {
  section_type: string;
  content: any;
  order: number;
}

export default function NewPagePage() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    slug: '',
    title: '',
    page_type: 'custom' as 'homepage' | 'service' | 'about' | 'contact' | 'custom',
    meta_title: '',
    meta_description: '',
    meta_keywords: '',
    og_image_url: '',
    is_published: false,
  });

  const [contentSections, setContentSections] = useState<ContentSection[]>([
    {
      section_type: 'text',
      content: { text: '' },
      order: 0,
    },
  ]);

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

      const response = await apiClient.post('/cms/pages', payload);

      // Redirect to edit page or pages list
      router.push(`/admin/pages/${response.id}/edit`);
    } catch (err) {
      setError(getErrorMessage(err));
      setIsSubmitting(false);
    }
  };

  const generateSlug = (title: string) => {
    return title
      .toLowerCase()
      .replace(/[àáâãäå]/g, 'a')
      .replace(/[èéêë]/g, 'e')
      .replace(/[ìíîï]/g, 'i')
      .replace(/[òóôõö]/g, 'o')
      .replace(/[ùúûü]/g, 'u')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
  };

  const handleTitleChange = (title: string) => {
    setFormData({ ...formData, title });
    // Auto-generate slug if it's empty
    if (!formData.slug) {
      setFormData({ ...formData, title, slug: generateSlug(title) });
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
    // Reorder
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
        <h1 className="text-3xl font-bold">Nuova Pagina</h1>
        <p className="text-muted-foreground mt-2">
          Crea una nuova pagina per il sito
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
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>Informazioni Base</CardTitle>
            <CardDescription>
              Inserisci le informazioni principali della pagina
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="title">Titolo *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => handleTitleChange(e.target.value)}
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
                  setFormData({
                    ...formData,
                    page_type: e.target.value as any,
                  })
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
                placeholder="Titolo per SEO (se vuoto usa il titolo della pagina)"
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
                  Aggiungi e organizza le sezioni della pagina
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

        {/* Publish Options */}
        <Card>
          <CardHeader>
            <CardTitle>Pubblicazione</CardTitle>
          </CardHeader>
          <CardContent>
            <label className="flex items-center space-x-2 cursor-pointer">
              <input
                type="checkbox"
                checked={formData.is_published}
                onChange={(e) =>
                  setFormData({ ...formData, is_published: e.target.checked })
                }
                className="rounded border-gray-300"
              />
              <span>Pubblica immediatamente</span>
            </label>
            <p className="text-sm text-muted-foreground mt-2">
              Se non selezionato, la pagina sarà salvata come bozza
            </p>
          </CardContent>
        </Card>

        {/* Submit Buttons */}
        <div className="flex gap-4">
          <Button type="submit" disabled={isSubmitting} size="lg">
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Creazione...' : 'Crea Pagina'}
          </Button>
          <Link href="/admin/pages">
            <Button type="button" variant="outline" size="lg">
              Annulla
            </Button>
          </Link>
        </div>
      </form>
    </div>
  );
}
