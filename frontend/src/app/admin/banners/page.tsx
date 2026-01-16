/**
 * Admin Banners Management Page
 * Descrizione: Gestione banner homepage
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import { Plus, Edit, Trash2, Eye, EyeOff, ArrowUp, ArrowDown, Image as ImageIcon } from 'lucide-react';

interface Banner {
  id: string;
  title: string;
  subtitle?: string;
  description?: string;
  image_url?: string;
  video_url?: string;
  cta_text?: string;
  cta_link?: string;
  cta_variant: string;
  position: string;
  display_order: number;
  background_color?: string;
  text_color?: string;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

interface BannersResponse {
  banners: Banner[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function AdminBannersPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();
  const [banners, setBanners] = useState<Banner[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterPosition, setFilterPosition] = useState<string | null>(null);
  const [filterActive, setFilterActive] = useState<boolean | null>(null);

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadBanners();
    }
  }, [isAuthenticated, isAdmin, filterPosition, filterActive]);

  const loadBanners = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('page', '1');
      params.append('page_size', '50');
      params.append('active_only', 'false'); // Mostra tutti per admin

      if (filterPosition) {
        params.append('position', filterPosition);
      }

      const response = await apiClient.get<BannersResponse>(
        `/homepage/banners?${params.toString()}`
      );

      let filteredBanners = response.banners || [];

      // Filtro client-side per is_active se necessario
      if (filterActive !== null) {
        filteredBanners = filteredBanners.filter(b => b.is_active === filterActive);
      }

      setBanners(filteredBanners);
    } catch (err) {
      const errorMsg = getErrorMessage(err);
      // Solo mostra errore se non è 404 (nessun banner)
      if (!errorMsg?.includes('404')) {
        setError(errorMsg);
      }
      setBanners([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleActive = async (banner: Banner) => {
    try {
      await apiClient.put(`/homepage/banners/${banner.id}`, {
        is_active: !banner.is_active,
      });
      await loadBanners();
    } catch (err) {
      alert(getErrorMessage(err));
    }
  };

  const handleDelete = async (banner: Banner) => {
    if (!confirm(`Sei sicuro di voler eliminare il banner "${banner.title}"?`)) {
      return;
    }

    try {
      await apiClient.delete(`/homepage/banners/${banner.id}`);
      await loadBanners();
    } catch (err) {
      alert(getErrorMessage(err));
    }
  };

  const handleReorder = async (banner: Banner, direction: 'up' | 'down') => {
    const newOrder = direction === 'up' ? banner.display_order - 1 : banner.display_order + 1;
    if (newOrder < 0) return;

    try {
      await apiClient.patch(`/homepage/banners/${banner.id}/reorder?new_order=${newOrder}`);
      await loadBanners();
    } catch (err) {
      alert(getErrorMessage(err));
    }
  };

  const formatDate = (dateString?: string): string => {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const positionLabels: Record<string, string> = {
    hero: 'Hero Principal',
    slider: 'Slider',
    section: 'Sezione',
    footer: 'Footer',
  };

  if (authLoading || !isAuthenticated || !isAdmin) {
    return (
      <>
        <Navigation />
        <main className="container py-12">
          <div className="flex flex-col items-center justify-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
            <p className="text-muted-foreground">Caricamento...</p>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navigation />

      <main className="container py-12">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Banner Homepage</h1>
              <p className="text-muted-foreground">
                Gestisci i banner e le sezioni della homepage
              </p>
            </div>
        <Link href="/admin/banners/new">
          <Button size="lg">
            <Plus className="h-5 w-5 mr-2" />
            Nuovo Banner
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filtri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Posizione</label>
              <div className="flex gap-2">
                <Button
                  variant={filterPosition === null ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterPosition(null)}
                >
                  Tutti
                </Button>
                <Button
                  variant={filterPosition === 'hero' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterPosition('hero')}
                >
                  Hero
                </Button>
                <Button
                  variant={filterPosition === 'slider' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterPosition('slider')}
                >
                  Slider
                </Button>
                <Button
                  variant={filterPosition === 'section' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterPosition('section')}
                >
                  Sezione
                </Button>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium">Stato</label>
              <div className="flex gap-2">
                <Button
                  variant={filterActive === null ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterActive(null)}
                >
                  Tutti
                </Button>
                <Button
                  variant={filterActive === true ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterActive(true)}
                >
                  Attivi
                </Button>
                <Button
                  variant={filterActive === false ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setFilterActive(false)}
                >
                  Inattivi
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription className="flex items-center justify-between">
            <span>{error}</span>
            <Button
              variant="outline"
              size="sm"
              onClick={loadBanners}
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
          <p className="text-muted-foreground">Caricamento banner...</p>
        </div>
      )}

      {/* Banners List */}
      {!isLoading && (
        <>
          {banners.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <ImageIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground mb-4">
                  Nessun banner trovato. Crea il primo banner per la homepage!
                </p>
                <Link href="/admin/banners/new">
                  <Button>
                    <Plus className="h-4 w-4 mr-2" />
                    Crea Primo Banner
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {banners.map((banner) => (
                <Card key={banner.id}>
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <CardTitle className="text-xl">{banner.title}</CardTitle>
                          <Badge variant={banner.is_active ? 'default' : 'secondary'}>
                            {banner.is_active ? 'Attivo' : 'Inattivo'}
                          </Badge>
                          <Badge variant="outline">{positionLabels[banner.position] || banner.position}</Badge>
                          <Badge variant="outline">Ordine: {banner.display_order}</Badge>
                        </div>
                        {banner.subtitle && (
                          <CardDescription>{banner.subtitle}</CardDescription>
                        )}
                      </div>
                      <div className="flex gap-2">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleReorder(banner, 'up')}
                          title="Sposta su"
                          disabled={banner.display_order === 0}
                        >
                          <ArrowUp className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleReorder(banner, 'down')}
                          title="Sposta giù"
                        >
                          <ArrowDown className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleToggleActive(banner)}
                          title={banner.is_active ? 'Disattiva' : 'Attiva'}
                        >
                          {banner.is_active ? (
                            <EyeOff className="h-4 w-4" />
                          ) : (
                            <Eye className="h-4 w-4" />
                          )}
                        </Button>
                        <Link href={`/admin/banners/${banner.id}/edit`}>
                          <Button variant="ghost" size="icon" title="Modifica">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </Link>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDelete(banner)}
                          title="Elimina"
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid md:grid-cols-4 gap-4">
                      {/* Preview immagine */}
                      {banner.image_url && (
                        <div className="md:col-span-1">
                          <img
                            src={banner.image_url}
                            alt={banner.title}
                            className="w-full h-24 object-cover rounded-md"
                          />
                        </div>
                      )}

                      {/* Info */}
                      <div className={banner.image_url ? 'md:col-span-3' : 'md:col-span-4'}>
                        {banner.description && (
                          <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                            {banner.description}
                          </p>
                        )}
                        <div className="flex flex-wrap gap-4 text-xs text-muted-foreground">
                          {banner.cta_text && (
                            <div>
                              <span className="font-semibold">CTA:</span> {banner.cta_text}
                            </div>
                          )}
                          {banner.start_date && (
                            <div>
                              <span className="font-semibold">Inizio:</span> {formatDate(banner.start_date)}
                            </div>
                          )}
                          {banner.end_date && (
                            <div>
                              <span className="font-semibold">Fine:</span> {formatDate(banner.end_date)}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </>
      )}
        </div>
      </main>
    </>
  );
}
