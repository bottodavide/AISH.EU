/**
 * Admin Blog Categories Management Page
 * Descrizione: Gestione categorie e tag del blog
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
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface BlogCategory {
  id: string;
  name: string;
  slug: string;
  description?: string;
}

interface BlogTag {
  id: string;
  name: string;
  slug: string;
}

// Utility function to generate slug from name
const generateSlug = (name: string): string => {
  return name
    .toLowerCase()
    .trim()
    .replace(/[àáâãäå]/g, 'a')
    .replace(/[èéêë]/g, 'e')
    .replace(/[ìíîï]/g, 'i')
    .replace(/[òóôõö]/g, 'o')
    .replace(/[ùúûü]/g, 'u')
    .replace(/[ñ]/g, 'n')
    .replace(/[ç]/g, 'c')
    .replace(/[^\w\s-]/g, '') // Remove special characters
    .replace(/\s+/g, '-')      // Replace spaces with hyphens
    .replace(/-+/g, '-')       // Replace multiple hyphens with single hyphen
    .replace(/^-+|-+$/g, '');  // Remove leading/trailing hyphens
};

export default function AdminBlogCategoriesPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();

  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [tags, setTags] = useState<BlogTag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [newCategory, setNewCategory] = useState({ name: '', description: '' });
  const [newTag, setNewTag] = useState('');

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load data
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadData();
    }
  }, [isAuthenticated, isAdmin]);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const [categoriesRes, tagsRes] = await Promise.all([
        apiClient.get<BlogCategory[]>('/api/v1/cms/blog/categories'),
        apiClient.get<BlogTag[]>('/api/v1/cms/blog/tags'),
      ]);

      setCategories(categoriesRes || []);
      setTags(tagsRes || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      await apiClient.post('/api/v1/cms/blog/categories', {
        name: newCategory.name,
        slug: generateSlug(newCategory.name),
        description: newCategory.description || undefined,
      });

      setNewCategory({ name: '', description: '' });
      await loadData();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleDeleteCategory = async (categoryId: string, categoryName: string) => {
    if (!confirm(`Sei sicuro di voler eliminare la categoria "${categoryName}"?`)) {
      return;
    }

    try {
      await apiClient.delete(`/api/v1/cms/blog/categories/${categoryId}`);
      await loadData();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleCreateTag = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      await apiClient.post('/api/v1/cms/blog/tags', {
        name: newTag,
        slug: generateSlug(newTag),
      });

      setNewTag('');
      await loadData();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleDeleteTag = async (tagId: string, tagName: string) => {
    if (!confirm(`Sei sicuro di voler eliminare il tag "${tagName}"?`)) {
      return;
    }

    try {
      await apiClient.delete(`/api/v1/cms/blog/tags/${tagId}`);
      await loadData();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  if (authLoading || !isAuthenticated || !isAdmin) {
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

      <main className="container py-12 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Gestione Categorie & Tag</h1>
          <p className="text-muted-foreground">
            Organizza i contenuti del blog con categorie e tag
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento...</p>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Categories Section */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Create Category */}
              <Card>
                <CardHeader>
                  <CardTitle>Crea Nuova Categoria</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleCreateCategory} className="space-y-4">
                    <div>
                      <Label htmlFor="category_name">Nome Categoria *</Label>
                      <Input
                        id="category_name"
                        value={newCategory.name}
                        onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                        required
                        placeholder="es. AI & Normative"
                      />
                    </div>
                    <div>
                      <Label htmlFor="category_description">Descrizione</Label>
                      <textarea
                        id="category_description"
                        value={newCategory.description}
                        onChange={(e) =>
                          setNewCategory({ ...newCategory, description: e.target.value })
                        }
                        rows={3}
                        className="w-full px-3 py-2 border rounded-md"
                        placeholder="Breve descrizione della categoria"
                      />
                    </div>
                    <Button type="submit">Crea Categoria</Button>
                  </form>
                </CardContent>
              </Card>

              {/* Categories List */}
              <Card>
                <CardHeader>
                  <CardTitle>Categorie Esistenti ({categories.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  {categories.length === 0 ? (
                    <p className="text-muted-foreground text-sm">Nessuna categoria creata</p>
                  ) : (
                    <div className="space-y-2">
                      {categories.map((category) => (
                        <div
                          key={category.id}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div>
                            <div className="font-semibold">{category.name}</div>
                            {category.description && (
                              <div className="text-sm text-muted-foreground">
                                {category.description}
                              </div>
                            )}
                            <div className="text-xs text-muted-foreground mt-1">
                              Slug: {category.slug}
                            </div>
                          </div>
                          <Button
                            variant="destructive"
                            size="sm"
                            onClick={() => handleDeleteCategory(category.id, category.name)}
                          >
                            Elimina
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Tags Section */}
            <div className="grid md:grid-cols-2 gap-6">
              {/* Create Tag */}
              <Card>
                <CardHeader>
                  <CardTitle>Crea Nuovo Tag</CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleCreateTag} className="space-y-4">
                    <div>
                      <Label htmlFor="tag_name">Nome Tag *</Label>
                      <Input
                        id="tag_name"
                        value={newTag}
                        onChange={(e) => setNewTag(e.target.value)}
                        required
                        placeholder="es. GDPR"
                      />
                    </div>
                    <Button type="submit">Crea Tag</Button>
                  </form>
                </CardContent>
              </Card>

              {/* Tags List */}
              <Card>
                <CardHeader>
                  <CardTitle>Tag Esistenti ({tags.length})</CardTitle>
                </CardHeader>
                <CardContent>
                  {tags.length === 0 ? (
                    <p className="text-muted-foreground text-sm">Nessun tag creato</p>
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {tags.map((tag) => (
                        <div
                          key={tag.id}
                          className="flex items-center gap-2 px-3 py-1 border rounded-full"
                        >
                          <span className="text-sm font-medium">{tag.name}</span>
                          <button
                            onClick={() => handleDeleteTag(tag.id, tag.name)}
                            className="text-red-600 hover:text-red-800"
                          >
                            ×
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {/* Back to Blog */}
        <div className="mt-8">
          <Link href="/admin/blog">
            <Button variant="ghost">← Torna alla Gestione Blog</Button>
          </Link>
        </div>
      </main>
    </>
  );
}
