/**
 * Admin Create Blog Post Page
 * Descrizione: Form per creare nuovo articolo blog con TipTap editor
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { RichTextEditor } from '@/components/RichTextEditor';
import { ImageUpload } from '@/components/ImageUpload';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface BlogCategory {
  id: string;
  name: string;
  slug: string;
}

interface BlogTag {
  id: string;
  name: string;
  slug: string;
}

export default function AdminCreateBlogPostPage() {
  const router = useRouter();
  const { user, isAuthenticated, isAdmin } = useAuth();

  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [tags, setTags] = useState<BlogTag[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(true);

  const [formData, setFormData] = useState({
    title: '',
    slug: '',
    excerpt: '',
    content_html: '',
    featured_image_url: '',
    category_id: '',
    tag_ids: [] as string[],
    author_name: user?.first_name && user?.last_name
      ? `${user.first_name} ${user.last_name}`
      : user?.email || '',
    meta_description: '',
    meta_keywords: '',
    is_featured: false,
    is_published: false,
  });

  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Load categories and tags
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadData();
    }
  }, [isAuthenticated, isAdmin]);

  const loadData = async () => {
    setIsLoadingData(true);
    try {
      const [categoriesRes, tagsRes] = await Promise.all([
        apiClient.get<{ categories: BlogCategory[] }>('/cms/blog/categories'),
        apiClient.get<{ tags: BlogTag[] }>('/cms/blog/tags'),
      ]);

      setCategories(categoriesRes.categories);
      setTags(tagsRes.tags);

      // Auto-select first category if available
      if (categoriesRes.categories.length > 0 && !formData.category_id) {
        setFormData((prev) => ({ ...prev, category_id: categoriesRes.categories[0].id }));
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoadingData(false);
    }
  };

  // Auto-generate slug from title
  const handleTitleChange = (title: string) => {
    setFormData((prev) => ({
      ...prev,
      title,
      slug: title
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, ''),
    }));
  };

  // Toggle tag selection
  const toggleTag = (tagId: string) => {
    setFormData((prev) => ({
      ...prev,
      tag_ids: prev.tag_ids.includes(tagId)
        ? prev.tag_ids.filter((id) => id !== tagId)
        : [...prev.tag_ids, tagId],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Validate
      if (!formData.category_id) {
        setError('Seleziona una categoria');
        setIsSubmitting(false);
        return;
      }

      if (!formData.content_html.trim()) {
        setError('Il contenuto è obbligatorio');
        setIsSubmitting(false);
        return;
      }

      // Prepare data
      const payload = {
        title: formData.title,
        slug: formData.slug,
        excerpt: formData.excerpt,
        content_html: formData.content_html,
        featured_image_url: formData.featured_image_url || undefined,
        category_id: formData.category_id,
        tag_ids: formData.tag_ids,
        author_name: formData.author_name,
        meta_description: formData.meta_description || undefined,
        meta_keywords: formData.meta_keywords ? formData.meta_keywords.split(',').map((k) => k.trim()) : undefined,
        is_featured: formData.is_featured,
        is_published: formData.is_published,
      };

      await apiClient.post('/cms/blog/posts', payload);

      // Redirect to blog list
      router.push('/admin/blog');
    } catch (err) {
      setError(getErrorMessage(err));
      setIsSubmitting(false);
    }
  };

  if (!isAuthenticated || !isAdmin) {
    return null;
  }

  if (isLoadingData) {
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

      <main className="container py-12 max-w-5xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Crea Nuovo Articolo</h1>
          <p className="text-muted-foreground">
            Scrivi un nuovo articolo per il blog
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Categories Warning */}
        {categories.length === 0 && (
          <Alert className="mb-6">
            <AlertDescription>
              Non hai ancora creato categorie.{' '}
              <Link href="/admin/blog/categories" className="underline font-semibold">
                Crea una categoria
              </Link>{' '}
              prima di creare articoli.
            </AlertDescription>
          </Alert>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Info */}
          <Card>
            <CardHeader>
              <CardTitle>Informazioni Base</CardTitle>
              <CardDescription>Titolo, slug e categoria</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="title">Titolo *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => handleTitleChange(e.target.value)}
                  required
                  placeholder="es. Come prepararsi al AI Act 2024"
                />
              </div>

              <div>
                <Label htmlFor="slug">Slug URL *</Label>
                <Input
                  id="slug"
                  value={formData.slug}
                  onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
                  required
                  placeholder="es. come-prepararsi-ai-act-2024"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Generato automaticamente dal titolo
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="category">Categoria *</Label>
                  <select
                    id="category"
                    value={formData.category_id}
                    onChange={(e) => setFormData({ ...formData, category_id: e.target.value })}
                    className="w-full px-3 py-2 border rounded-md"
                    required
                    disabled={categories.length === 0}
                  >
                    {categories.length === 0 ? (
                      <option value="">Nessuna categoria disponibile</option>
                    ) : (
                      <>
                        <option value="">Seleziona una categoria</option>
                        {categories.map((cat) => (
                          <option key={cat.id} value={cat.id}>
                            {cat.name}
                          </option>
                        ))}
                      </>
                    )}
                  </select>
                </div>

                <div>
                  <Label htmlFor="author_name">Nome Autore *</Label>
                  <Input
                    id="author_name"
                    value={formData.author_name}
                    onChange={(e) => setFormData({ ...formData, author_name: e.target.value })}
                    required
                  />
                </div>
              </div>

              <div>
                <Label htmlFor="excerpt">Estratto *</Label>
                <textarea
                  id="excerpt"
                  value={formData.excerpt}
                  onChange={(e) => setFormData({ ...formData, excerpt: e.target.value })}
                  required
                  rows={3}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="Breve estratto per anteprima (2-3 righe)"
                />
              </div>

              <div>
                <Label>Immagine in Evidenza</Label>
                <ImageUpload
                  value={formData.featured_image_url}
                  onUploadSuccess={(url) => {
                    setFormData({ ...formData, featured_image_url: url });
                  }}
                  onError={(err) => {
                    setError(err);
                  }}
                  maxWidth={1200}
                  maxHeight={630}
                  maxSizeKB={500}
                  acceptedFormats={['image/jpeg', 'image/png', 'image/webp']}
                  label="Carica Immagine Featured (1200x630px)"
                  showSpecs={true}
                  category="image"
                  isPublic={true}
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Oppure inserisci l'URL manualmente:
                </p>
                <Input
                  type="url"
                  value={formData.featured_image_url}
                  onChange={(e) => setFormData({ ...formData, featured_image_url: e.target.value })}
                  placeholder="https://esempio.com/immagine.jpg"
                  className="mt-1"
                />
              </div>
            </CardContent>
          </Card>

          {/* Content */}
          <Card>
            <CardHeader>
              <CardTitle>Contenuto</CardTitle>
              <CardDescription>
                Scrivi il contenuto dell'articolo con l'editor rich text
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div>
                <Label htmlFor="content_html">Contenuto Articolo *</Label>
                <div className="mt-2">
                  <RichTextEditor
                    content={formData.content_html}
                    onChange={(html) => setFormData({ ...formData, content_html: html })}
                    placeholder="Inizia a scrivere il tuo articolo..."
                  />
                </div>
                <div className="text-sm text-muted-foreground mt-2 space-y-1">
                  <p>Usa la toolbar per formattare il testo: grassetto, corsivo, titoli, liste, link e immagini</p>
                  <div className="mt-2 p-3 bg-muted/50 rounded-md">
                    <p className="font-medium mb-1">Specifiche immagini inline:</p>
                    <ul className="list-disc list-inside ml-2 space-y-0.5 text-xs">
                      <li><strong>Dimensioni:</strong> Max 1200px larghezza, altezza proporzionale</li>
                      <li><strong>Formati ammessi:</strong> JPG, PNG, WebP, GIF</li>
                      <li><strong>Peso massimo:</strong> 300 KB per immagine</li>
                      <li><strong>Note:</strong> Comprimi le immagini per velocizzare il caricamento della pagina</li>
                    </ul>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Tags */}
          <Card>
            <CardHeader>
              <CardTitle>Tag</CardTitle>
              <CardDescription>Seleziona i tag pertinenti</CardDescription>
            </CardHeader>
            <CardContent>
              {tags.length === 0 ? (
                <p className="text-muted-foreground text-sm">
                  Nessun tag disponibile.{' '}
                  <Link href="/admin/blog/categories" className="underline">
                    Crea tag
                  </Link>
                </p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <button
                      key={tag.id}
                      type="button"
                      onClick={() => toggleTag(tag.id)}
                      className={`px-3 py-1 rounded-full text-sm border transition-colors ${
                        formData.tag_ids.includes(tag.id)
                          ? 'bg-primary text-primary-foreground border-primary'
                          : 'bg-background border-muted-foreground hover:border-primary'
                      }`}
                    >
                      {tag.name}
                    </button>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* SEO */}
          <Card>
            <CardHeader>
              <CardTitle>SEO & Meta Tags</CardTitle>
              <CardDescription>Ottimizzazione per motori di ricerca</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="meta_description">Meta Description</Label>
                <textarea
                  id="meta_description"
                  value={formData.meta_description}
                  onChange={(e) => setFormData({ ...formData, meta_description: e.target.value })}
                  rows={2}
                  maxLength={160}
                  className="w-full px-3 py-2 border rounded-md"
                  placeholder="Descrizione per Google (max 160 caratteri)"
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
                  onChange={(e) => setFormData({ ...formData, meta_keywords: e.target.value })}
                  placeholder="keyword1, keyword2, keyword3"
                />
                <p className="text-sm text-muted-foreground mt-1">
                  Separare con virgole
                </p>
              </div>
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
                <Label htmlFor="is_featured">Articolo in Evidenza</Label>
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
            <Button type="submit" size="lg" disabled={isSubmitting || categories.length === 0}>
              {isSubmitting ? 'Salvataggio...' : 'Crea Articolo'}
            </Button>
            <Link href="/admin/blog">
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
