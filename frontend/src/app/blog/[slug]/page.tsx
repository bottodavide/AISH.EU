/**
 * Blog Post Detail Page
 * Descrizione: Pagina dettaglio singolo articolo blog
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';

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
  content_html: string;
  featured_image_url?: string;
  category: BlogCategory;
  tags: BlogTag[];
  author_name: string;
  author_email?: string;
  published_at: string;
  updated_at?: string;
  reading_time_minutes?: number;
  is_featured: boolean;
  meta_description?: string;
  meta_keywords?: string[];
}

interface RelatedPost {
  id: string;
  slug: string;
  title: string;
  excerpt: string;
  featured_image_url?: string;
  category: BlogCategory;
  published_at: string;
}

interface BlogPostDetailPageProps {
  params: {
    slug: string;
  };
}

export default function BlogPostDetailPage({ params }: BlogPostDetailPageProps) {
  const [post, setPost] = useState<BlogPost | null>(null);
  const [relatedPosts, setRelatedPosts] = useState<RelatedPost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load post
  useEffect(() => {
    loadPost();
  }, [params.slug]);

  const loadPost = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<BlogPost>(
        `/api/v1/cms/blog/posts/${params.slug}`
      );

      setPost(response);

      // Load related posts from same category
      if (response.category) {
        loadRelatedPosts(response.category.slug, response.id);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const loadRelatedPosts = async (categorySlug: string, excludePostId: string) => {
    try {
      const params = new URLSearchParams();
      params.append('category_slug', categorySlug);
      params.append('page_size', '3');

      const response = await apiClient.get<{ posts: RelatedPost[] }>(
        `/api/v1/cms/blog/posts?${params.toString()}`
      );

      // Filter out current post
      const filtered = response.posts.filter((p) => p.id !== excludePostId);
      setRelatedPosts(filtered.slice(0, 3));
    } catch (err) {
      console.error('Failed to load related posts:', err);
    }
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const shareOnTwitter = () => {
    if (!post) return;
    const url = encodeURIComponent(window.location.href);
    const text = encodeURIComponent(post.title);
    window.open(
      `https://twitter.com/intent/tweet?url=${url}&text=${text}`,
      '_blank',
      'width=550,height=420'
    );
  };

  const shareOnLinkedIn = () => {
    if (!post) return;
    const url = encodeURIComponent(window.location.href);
    window.open(
      `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
      '_blank',
      'width=550,height=420'
    );
  };

  const copyLink = () => {
    navigator.clipboard.writeText(window.location.href);
    alert('Link copiato negli appunti!');
  };

  return (
    <>
      <Navigation />

      <main className="container py-12">
        {/* Back Button */}
        <div className="mb-6">
          <Link href="/blog">
            <Button variant="ghost" size="sm">
              ← Torna al Blog
            </Button>
          </Link>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento articolo...</p>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-8">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Post Content */}
        {!isLoading && post && (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <article className="lg:col-span-2">
              {/* Featured Image */}
              {post.featured_image_url && (
                <div className="aspect-video bg-muted rounded-lg overflow-hidden mb-6">
                  <img
                    src={post.featured_image_url}
                    alt={post.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              {/* Post Header */}
              <div className="mb-8">
                {post.is_featured && (
                  <div className="mb-4">
                    <span className="inline-block px-3 py-1 text-sm font-semibold rounded-full bg-primary/10 text-primary">
                      In Evidenza
                    </span>
                  </div>
                )}

                {/* Category & Meta */}
                <div className="flex items-center gap-2 text-sm text-muted-foreground mb-4">
                  <Link
                    href={`/blog?category=${post.category.slug}`}
                    className="font-medium text-primary hover:underline"
                  >
                    {post.category.name}
                  </Link>
                  <span>•</span>
                  <time dateTime={post.published_at}>
                    {formatDate(post.published_at)}
                  </time>
                  {post.reading_time_minutes && (
                    <>
                      <span>•</span>
                      <span>{post.reading_time_minutes} min di lettura</span>
                    </>
                  )}
                </div>

                {/* Title */}
                <h1 className="text-4xl font-bold mb-4">{post.title}</h1>

                {/* Excerpt */}
                <p className="text-xl text-muted-foreground mb-6">{post.excerpt}</p>

                {/* Author */}
                <div className="flex items-center gap-3 pb-6 border-b">
                  <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                    <span className="text-xl font-semibold text-primary">
                      {post.author_name.charAt(0)}
                    </span>
                  </div>
                  <div>
                    <div className="font-semibold">{post.author_name}</div>
                    {post.updated_at && post.updated_at !== post.published_at && (
                      <div className="text-sm text-muted-foreground">
                        Aggiornato il {formatDate(post.updated_at)}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Post Content */}
              <div
                className="prose prose-lg max-w-none mb-8"
                dangerouslySetInnerHTML={{ __html: post.content_html }}
              />

              {/* Tags */}
              {post.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-8 pb-8 border-b">
                  {post.tags.map((tag) => (
                    <Link key={tag.id} href={`/blog?tag=${tag.slug}`}>
                      <span className="px-3 py-1 rounded-md bg-muted text-muted-foreground hover:bg-muted/80 transition-colors cursor-pointer">
                        #{tag.name}
                      </span>
                    </Link>
                  ))}
                </div>
              )}

              {/* Share Section */}
              <div className="mb-8">
                <h3 className="text-lg font-semibold mb-4">Condividi questo articolo</h3>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" onClick={shareOnTwitter}>
                    Twitter
                  </Button>
                  <Button variant="outline" size="sm" onClick={shareOnLinkedIn}>
                    LinkedIn
                  </Button>
                  <Button variant="outline" size="sm" onClick={copyLink}>
                    Copia Link
                  </Button>
                </div>
              </div>

              {/* Related Posts */}
              {relatedPosts.length > 0 && (
                <div className="mt-12">
                  <h2 className="text-2xl font-bold mb-6">Articoli Correlati</h2>
                  <div className="grid md:grid-cols-3 gap-4">
                    {relatedPosts.map((relatedPost) => (
                      <Card key={relatedPost.id} className="overflow-hidden">
                        {relatedPost.featured_image_url && (
                          <div className="aspect-video bg-muted">
                            <img
                              src={relatedPost.featured_image_url}
                              alt={relatedPost.title}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}
                        <CardHeader>
                          <div className="text-xs text-muted-foreground mb-2">
                            {relatedPost.category.name}
                          </div>
                          <CardTitle className="text-base line-clamp-2">
                            {relatedPost.title}
                          </CardTitle>
                          <CardDescription className="line-clamp-2">
                            {relatedPost.excerpt}
                          </CardDescription>
                        </CardHeader>
                        <CardContent>
                          <Link href={`/blog/${relatedPost.slug}`}>
                            <Button variant="ghost" size="sm" className="w-full">
                              Leggi
                            </Button>
                          </Link>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </div>
              )}
            </article>

            {/* Sidebar */}
            <aside className="lg:col-span-1">
              <div className="sticky top-24 space-y-6">
                {/* Newsletter Card */}
                <Card>
                  <CardHeader>
                    <CardTitle>Newsletter</CardTitle>
                    <CardDescription>
                      Ricevi i nostri articoli direttamente nella tua inbox
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <input
                      type="email"
                      placeholder="La tua email"
                      className="w-full px-3 py-2 border rounded-md"
                    />
                    <Button className="w-full">Iscriviti</Button>
                  </CardContent>
                </Card>

                {/* CTA Card */}
                <Card className="bg-primary text-primary-foreground">
                  <CardHeader>
                    <CardTitle>Hai bisogno di consulenza?</CardTitle>
                    <CardDescription className="text-primary-foreground/80">
                      Scopri i nostri servizi di AI compliance e cybersecurity
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Link href="/servizi">
                      <Button variant="secondary" className="w-full">
                        Scopri i Servizi
                      </Button>
                    </Link>
                  </CardContent>
                </Card>

                {/* Contact Card */}
                <Card>
                  <CardHeader>
                    <CardTitle>Contattaci</CardTitle>
                    <CardDescription>
                      Hai domande su questo argomento?
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Link href="/contatti">
                      <Button variant="outline" className="w-full">
                        Invia una Richiesta
                      </Button>
                    </Link>
                  </CardContent>
                </Card>
              </div>
            </aside>
          </div>
        )}

        {/* Not Found State */}
        {!isLoading && !error && !post && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg mb-4">
              Articolo non trovato
            </p>
            <Link href="/blog">
              <Button>Torna al Blog</Button>
            </Link>
          </div>
        )}
      </main>
    </>
  );
}
