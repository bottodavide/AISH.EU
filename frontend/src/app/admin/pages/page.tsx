/**
 * Admin Pages Management
 * Descrizione: Gestione pagine CMS del sito
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { Plus, Edit, Trash2, Eye, EyeOff, FileText } from 'lucide-react';

interface Page {
  id: string;
  slug: string;
  title: string;
  page_type: 'homepage' | 'service' | 'about' | 'contact' | 'custom';
  status: 'draft' | 'published';
  is_published: boolean;
  meta_title?: string;
  meta_description?: string;
  published_at?: string;
  created_at: string;
  updated_at: string;
}

interface PagesResponse {
  pages: Page[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function AdminPagesPage() {
  const router = useRouter();
  const [pages, setPages] = useState<Page[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<string | null>(null);
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  useEffect(() => {
    loadPages();
  }, [filterType, filterStatus]);

  const loadPages = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('page', '1');
      params.append('page_size', '50');

      if (filterType) {
        params.append('page_type', filterType);
      }

      if (filterStatus) {
        params.append('status', filterStatus);
      }

      const response = await apiClient.get<PagesResponse>(
        `/cms/pages?${params.toString()}`
      );

      setPages(response.pages || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (page: Page) => {
    if (!confirm(`Sei sicuro di voler eliminare la pagina "${page.title}"?`)) {
      return;
    }

    try {
      await apiClient.delete(`/cms/pages/${page.id}`);
      await loadPages();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleTogglePublish = async (page: Page) => {
    try {
      if (page.is_published) {
        // Unpublish (set to draft)
        await apiClient.put(`/cms/pages/${page.id}`, {
          is_published: false,
        });
      } else {
        // Publish
        await apiClient.post(`/cms/pages/${page.id}/publish`, {});
      }
      await loadPages();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const getPageTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      homepage: 'Homepage',
      service: 'Servizio',
      about: 'Chi Siamo',
      contact: 'Contatti',
      custom: 'Personalizzata',
    };
    return labels[type] || type;
  };

  const getStatusBadge = (page: Page) => {
    if (page.is_published) {
      return (
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Pubblicata
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
        Bozza
      </span>
    );
  };

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Gestione Pagine</h1>
          <p className="text-muted-foreground mt-2">
            Gestisci le pagine del sito web
          </p>
        </div>
        <Link href="/admin/pages/new">
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Nuova Pagina
          </Button>
        </Link>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filtri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {/* Type Filter */}
            <div className="flex gap-2">
              <Button
                variant={filterType === null ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterType(null)}
              >
                Tutti i Tipi
              </Button>
              <Button
                variant={filterType === 'homepage' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterType('homepage')}
              >
                Homepage
              </Button>
              <Button
                variant={filterType === 'about' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterType('about')}
              >
                Chi Siamo
              </Button>
              <Button
                variant={filterType === 'contact' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterType('contact')}
              >
                Contatti
              </Button>
              <Button
                variant={filterType === 'custom' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterType('custom')}
              >
                Personalizzate
              </Button>
            </div>

            {/* Status Filter */}
            <div className="flex gap-2 border-l pl-4">
              <Button
                variant={filterStatus === null ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus(null)}
              >
                Tutti gli Stati
              </Button>
              <Button
                variant={filterStatus === 'published' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('published')}
              >
                Pubblicate
              </Button>
              <Button
                variant={filterStatus === 'draft' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('draft')}
              >
                Bozze
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Caricamento pagine...</p>
        </div>
      )}

      {/* Pages Table */}
      {!isLoading && pages.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Pagine ({pages.length})</CardTitle>
            <CardDescription>
              Lista di tutte le pagine gestite tramite CMS
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-semibold">Titolo</th>
                    <th className="text-left p-4 font-semibold">Tipo</th>
                    <th className="text-left p-4 font-semibold">Slug</th>
                    <th className="text-left p-4 font-semibold">Stato</th>
                    <th className="text-left p-4 font-semibold">Ultima Modifica</th>
                    <th className="text-right p-4 font-semibold">Azioni</th>
                  </tr>
                </thead>
                <tbody>
                  {pages.map((page) => (
                    <tr key={page.id} className="border-b hover:bg-muted/50">
                      <td className="p-4">
                        <div className="font-medium">{page.title}</div>
                        {page.meta_description && (
                          <div className="text-sm text-muted-foreground mt-1 line-clamp-1">
                            {page.meta_description}
                          </div>
                        )}
                      </td>
                      <td className="p-4">
                        <span className="text-sm">{getPageTypeLabel(page.page_type)}</span>
                      </td>
                      <td className="p-4">
                        <code className="text-sm bg-muted px-2 py-1 rounded">
                          /{page.slug}
                        </code>
                      </td>
                      <td className="p-4">{getStatusBadge(page)}</td>
                      <td className="p-4">
                        <span className="text-sm text-muted-foreground">
                          {new Date(page.updated_at).toLocaleDateString('it-IT', {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric',
                          })}
                        </span>
                      </td>
                      <td className="p-4">
                        <div className="flex items-center justify-end gap-2">
                          {/* Toggle Publish */}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleTogglePublish(page)}
                            title={page.is_published ? 'Nascondi' : 'Pubblica'}
                          >
                            {page.is_published ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>

                          {/* Edit */}
                          <Link href={`/admin/pages/${page.id}/edit`}>
                            <Button variant="ghost" size="sm" title="Modifica">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>

                          {/* Delete */}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(page)}
                            className="text-destructive hover:text-destructive"
                            title="Elimina"
                          >
                            <Trash2 className="h-4 w-4" />
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
      )}

      {/* Empty State */}
      {!isLoading && pages.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nessuna pagina trovata</h3>
            <p className="text-muted-foreground mb-4">
              {filterType || filterStatus
                ? 'Nessuna pagina corrisponde ai filtri selezionati'
                : 'Inizia creando la tua prima pagina'}
            </p>
            <Link href="/admin/pages/new">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Crea Prima Pagina
              </Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Back to Admin */}
      <div className="mt-8">
        <Link href="/admin">
          <Button variant="outline">← Torna alla Dashboard</Button>
        </Link>
      </div>
    </div>
  );
}
