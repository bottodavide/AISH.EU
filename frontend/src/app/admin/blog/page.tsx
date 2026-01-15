/**
 * Admin Blog Management Page
 * Descrizione: Gestione completa articoli blog (lista, create, edit, delete)
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
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface BlogCategory {
  id: string;
  name: string;
  slug: string;
}

interface BlogPost {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  category: BlogCategory;
  author_name: string;
  published_at?: string;
  is_featured: boolean;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

interface BlogPostsResponse {
  posts: BlogPost[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function AdminBlogPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();

  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load posts
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadPosts();
    }
  }, [isAuthenticated, isAdmin, currentPage]);

  const loadPosts = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', '20');

      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const response = await apiClient.get<BlogPostsResponse>(
        `/api/v1/cms/blog/posts?${params.toString()}`
      );

      setPosts(response.posts);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    loadPosts();
  };

  const handleDelete = async (postId: string, postTitle: string) => {
    if (!confirm(`Sei sicuro di voler eliminare "${postTitle}"?`)) {
      return;
    }

    try {
      await apiClient.delete(`/api/v1/cms/blog/posts/${postId}`);
      await loadPosts();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const togglePublish = async (postId: string) => {
    try {
      await apiClient.post(`/api/v1/cms/blog/posts/${postId}/publish`);
      await loadPosts();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
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

      <main className="container py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Gestione Blog</h1>
            <p className="text-muted-foreground">
              Crea, modifica ed elimina articoli del blog
            </p>
          </div>
          <div className="flex gap-2">
            <Link href="/admin/blog/categories">
              <Button variant="outline">Gestisci Categorie</Button>
            </Link>
            <Link href="/admin/blog/new">
              <Button size="lg">+ Nuovo Articolo</Button>
            </Link>
          </div>
        </div>

        {/* Search */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <form onSubmit={handleSearch} className="flex gap-2">
              <Input
                type="search"
                placeholder="Cerca articoli..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1"
              />
              <Button type="submit">Cerca</Button>
            </form>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento articoli...</p>
          </div>
        )}

        {/* Posts Table */}
        {!isLoading && posts.length > 0 && (
          <>
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted">
                      <tr>
                        <th className="text-left p-4 font-semibold">Titolo</th>
                        <th className="text-left p-4 font-semibold">Categoria</th>
                        <th className="text-left p-4 font-semibold">Autore</th>
                        <th className="text-center p-4 font-semibold">Status</th>
                        <th className="text-center p-4 font-semibold">Data Pubblicazione</th>
                        <th className="text-right p-4 font-semibold">Azioni</th>
                      </tr>
                    </thead>
                    <tbody>
                      {posts.map((post) => (
                        <tr key={post.id} className="border-t hover:bg-muted/50">
                          <td className="p-4">
                            <div>
                              <div className="font-semibold">{post.title}</div>
                              <div className="text-sm text-muted-foreground line-clamp-1">
                                {post.excerpt}
                              </div>
                              {post.is_featured && (
                                <span className="inline-block mt-1 text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full">
                                  In Evidenza
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="p-4">
                            <span className="text-sm">{post.category.name}</span>
                          </td>
                          <td className="p-4">
                            <span className="text-sm">{post.author_name}</span>
                          </td>
                          <td className="p-4 text-center">
                            <span
                              className={`text-xs px-2 py-1 rounded-full ${
                                post.is_published
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {post.is_published ? 'Pubblicato' : 'Bozza'}
                            </span>
                          </td>
                          <td className="p-4 text-center text-sm text-muted-foreground">
                            {post.published_at ? formatDate(post.published_at) : '-'}
                          </td>
                          <td className="p-4">
                            <div className="flex justify-end gap-2">
                              {post.is_published && (
                                <Link href={`/blog/${post.slug}`} target="_blank">
                                  <Button variant="ghost" size="sm">
                                    Vedi
                                  </Button>
                                </Link>
                              )}
                              <Link href={`/admin/blog/${post.id}/edit`}>
                                <Button variant="outline" size="sm">
                                  Modifica
                                </Button>
                              </Link>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => togglePublish(post.id)}
                              >
                                {post.is_published ? 'Nascondi' : 'Pubblica'}
                              </Button>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => handleDelete(post.id, post.title)}
                              >
                                Elimina
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  Precedente
                </Button>
                <span className="text-sm text-muted-foreground px-4">
                  Pagina {currentPage} di {totalPages}
                </span>
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  Successiva
                </Button>
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!isLoading && posts.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <p className="text-muted-foreground text-lg mb-4">
                {searchQuery
                  ? 'Nessun articolo trovato con questi filtri'
                  : 'Nessun articolo creato ancora'}
              </p>
              <Link href="/admin/blog/new">
                <Button>Crea il Primo Articolo</Button>
              </Link>
            </CardContent>
          </Card>
        )}

        {/* Back to Admin */}
        <div className="mt-8">
          <Link href="/admin">
            <Button variant="ghost">← Torna alla Dashboard Admin</Button>
          </Link>
        </div>
      </main>
    </>
  );
}
