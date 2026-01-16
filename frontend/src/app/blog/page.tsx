/**
 * Blog Listing Page
 * Descrizione: Lista articoli blog con filtri e paginazione
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { NewsletterForm } from '@/components/NewsletterForm';

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

interface BlogPost {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  featured_image_url?: string;
  category: BlogCategory;
  tags: BlogTag[];
  author_name: string;
  published_at: string;
  reading_time_minutes?: number;
  is_featured: boolean;
}

interface BlogPostsResponse {
  posts: BlogPost[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function BlogPage() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [categories, setCategories] = useState<BlogCategory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Load categories on mount
  useEffect(() => {
    loadCategories();
  }, []);

  // Load posts when filters change
  useEffect(() => {
    loadPosts();
  }, [selectedCategory, currentPage]);

  const loadCategories = async () => {
    try {
      const response = await apiClient.get<BlogCategory[]>(
        '/api/v1/cms/blog/categories'
      );
      setCategories(Array.isArray(response) ? response : []);
    } catch (err) {
      console.error('Failed to load categories:', err);
      // Non mostrare errore per categories - non è critico
      setCategories([]);
    }
  };

  const loadPosts = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', '12');

      if (selectedCategory) {
        params.append('category_slug', selectedCategory);
      }

      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const response = await apiClient.get<BlogPostsResponse>(
        `/api/v1/cms/blog/posts?${params.toString()}`
      );

      setPosts(response.posts || []);
      setTotalPages(response.total_pages || 0);
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      // Solo mostra errore se non è semplicemente "nessun dato"
      if (errorMsg && !errorMsg.includes('404')) {
        setError(errorMsg);
      }
      setPosts([]);
      setTotalPages(0);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    loadPosts();
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  return (
    <>
      <Navigation />

      <main className="container py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Blog</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Approfondimenti su AI, Compliance, GDPR, Cybersecurity e innovazione digitale
          </p>
        </div>

        {/* Search Bar */}
        <div className="max-w-2xl mx-auto mb-8">
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
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <Button
            variant={selectedCategory === null ? 'default' : 'outline'}
            onClick={() => {
              setSelectedCategory(null);
              setCurrentPage(1);
            }}
          >
            Tutti gli Articoli
          </Button>
          {categories.map((category) => (
            <Button
              key={category.id}
              variant={selectedCategory === category.slug ? 'default' : 'outline'}
              onClick={() => {
                setSelectedCategory(category.slug);
                setCurrentPage(1);
              }}
            >
              {category.name}
            </Button>
          ))}
        </div>

        {/* Error Alert with Retry */}
        {error && (
          <Alert variant="destructive" className="mb-8">
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={loadPosts}
                className="ml-4 bg-white hover:bg-gray-100"
              >
                Riprova
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento articoli...</p>
          </div>
        )}

        {/* Blog Posts Grid */}
        {!isLoading && posts.length > 0 && (
          <>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {posts.map((post) => (
                <Card key={post.id} className="flex flex-col overflow-hidden">
                  {/* Featured Image */}
                  {post.featured_image_url && (
                    <div className="aspect-video bg-muted overflow-hidden">
                      <img
                        src={post.featured_image_url}
                        alt={post.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}

                  <CardHeader>
                    {post.is_featured && (
                      <div className="mb-2">
                        <span className="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-primary/10 text-primary">
                          In Evidenza
                        </span>
                      </div>
                    )}
                    <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
                      <span className="font-medium text-primary">
                        {post.category.name}
                      </span>
                      <span>•</span>
                      <time dateTime={post.published_at}>
                        {formatDate(post.published_at)}
                      </time>
                      {post.reading_time_minutes && (
                        <>
                          <span>•</span>
                          <span>{post.reading_time_minutes} min</span>
                        </>
                      )}
                    </div>
                    <CardTitle className="text-xl line-clamp-2">{post.title}</CardTitle>
                    <CardDescription className="line-clamp-3">
                      {post.excerpt}
                    </CardDescription>
                  </CardHeader>

                  <CardContent className="flex-grow">
                    {post.tags.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {post.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag.id}
                            className="text-xs px-2 py-1 rounded-md bg-muted text-muted-foreground"
                          >
                            #{tag.name}
                          </span>
                        ))}
                      </div>
                    )}
                  </CardContent>

                  <CardFooter className="pt-0">
                    <Link href={`/blog/${post.slug}`} className="w-full">
                      <Button className="w-full" variant="outline">
                        Leggi Articolo
                      </Button>
                    </Link>
                  </CardFooter>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2">
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
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">
              {searchQuery
                ? `Nessun articolo trovato per "${searchQuery}"`
                : 'Nessun articolo trovato'}
              {selectedCategory && ' in questa categoria'}.
            </p>
            {(selectedCategory || searchQuery) && (
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => {
                  setSelectedCategory(null);
                  setSearchQuery('');
                  setCurrentPage(1);
                }}
              >
                Mostra Tutti gli Articoli
              </Button>
            )}
          </div>
        )}

        {/* Newsletter CTA */}
        <div className="mt-16 text-center bg-muted rounded-lg p-8">
          <h2 className="text-2xl font-bold mb-4">Resta Aggiornato</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Iscriviti alla nostra newsletter per ricevere gli ultimi articoli su AI, compliance e cybersecurity
          </p>
          <div className="flex justify-center">
            <NewsletterForm variant="compact" showUnsubscribe={true} />
          </div>
        </div>
      </main>
    </>
  );
}
