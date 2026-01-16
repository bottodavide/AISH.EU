/**
 * Admin Services Management Page
 * Descrizione: Gestione completa servizi (lista, create, edit, delete)
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface Service {
  id: string;
  slug: string;
  name: string;
  category: 'ai_compliance' | 'cybersecurity_nis2' | 'toolkit_formazione';
  type: 'PACCHETTO_FISSO' | 'CUSTOM_QUOTE' | 'ABBONAMENTO';
  short_description: string;
  pricing_type: 'FIXED' | 'RANGE' | 'CUSTOM';
  price_min?: number;
  price_max?: number;
  is_featured: boolean;
  is_published: boolean;
  created_at: string;
  updated_at: string;
}

interface ServicesResponse {
  services: Service[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function AdminServicesPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();

  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load services
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadServices();
    }
  }, [isAuthenticated, isAdmin, currentPage, filterCategory]);

  const loadServices = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', '20');

      if (filterCategory) {
        params.append('category', filterCategory);
      }

      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const response = await apiClient.get<ServicesResponse>(
        `/api/v1/services?${params.toString()}`
      );

      setServices(response.services);
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
    loadServices();
  };

  const handleDelete = async (serviceId: string, serviceName: string) => {
    if (!confirm(`Sei sicuro di voler eliminare "${serviceName}"?`)) {
      return;
    }

    try {
      await apiClient.delete(`/api/v1/services/${serviceId}`);
      await loadServices();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const togglePublish = async (serviceId: string, currentStatus: boolean) => {
    try {
      await apiClient.patch(`/api/v1/services/${serviceId}`, {
        is_published: !currentStatus,
      });
      await loadServices();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const getCategoryLabel = (category: string): string => {
    const labels: Record<string, string> = {
      ai_compliance: 'AI & Compliance',
      cybersecurity_nis2: 'Cybersecurity & NIS2',
      toolkit_formazione: 'Toolkit & Formazione',
    };
    return labels[category] || category;
  };

  const getTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      PACCHETTO_FISSO: 'Pacchetto Fisso',
      CUSTOM_QUOTE: 'Su Misura',
      ABBONAMENTO: 'Abbonamento',
    };
    return labels[type] || type;
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
            <h1 className="text-4xl font-bold mb-2">Gestione Servizi</h1>
            <p className="text-muted-foreground">
              Crea, modifica ed elimina i servizi di consulenza
            </p>
          </div>
          <Link href="/admin/services/new">
            <Button size="lg">+ Nuovo Servizio</Button>
          </Link>
        </div>

        {/* Filters & Search */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <form onSubmit={handleSearch} className="flex-1 flex gap-2">
                <Input
                  type="search"
                  placeholder="Cerca servizi..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1"
                />
                <Button type="submit">Cerca</Button>
              </form>

              {/* Category Filter */}
              <div className="flex gap-2">
                <Button
                  variant={filterCategory === null ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterCategory(null);
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Tutti
                </Button>
                <Button
                  variant={filterCategory === 'ai_compliance' ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterCategory('ai_compliance');
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  AI
                </Button>
                <Button
                  variant={filterCategory === 'cybersecurity_nis2' ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterCategory('cybersecurity_nis2');
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Cyber
                </Button>
                <Button
                  variant={filterCategory === 'toolkit_formazione' ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterCategory('toolkit_formazione');
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Toolkit
                </Button>
              </div>
            </div>
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
            <p className="text-muted-foreground">Caricamento servizi...</p>
          </div>
        )}

        {/* Services Table */}
        {!isLoading && services.length > 0 && (
          <>
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted">
                      <tr>
                        <th className="text-left p-4 font-semibold">Nome</th>
                        <th className="text-left p-4 font-semibold">Categoria</th>
                        <th className="text-left p-4 font-semibold">Tipo</th>
                        <th className="text-left p-4 font-semibold">Prezzo</th>
                        <th className="text-center p-4 font-semibold">Status</th>
                        <th className="text-center p-4 font-semibold">Data</th>
                        <th className="text-right p-4 font-semibold">Azioni</th>
                      </tr>
                    </thead>
                    <tbody>
                      {services.map((service) => (
                        <tr key={service.id} className="border-t hover:bg-muted/50">
                          <td className="p-4">
                            <div>
                              <div className="font-semibold">{service.name}</div>
                              <div className="text-sm text-muted-foreground line-clamp-1">
                                {service.short_description}
                              </div>
                              {service.is_featured && (
                                <span className="inline-block mt-1 text-xs px-2 py-0.5 bg-primary/10 text-primary rounded-full">
                                  In Evidenza
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="p-4">
                            <span className="text-sm">
                              {getCategoryLabel(service.category)}
                            </span>
                          </td>
                          <td className="p-4">
                            <span className="text-sm">
                              {getTypeLabel(service.type)}
                            </span>
                          </td>
                          <td className="p-4">
                            <span className="text-sm">
                              {service.pricing_type === 'CUSTOM' && 'Su preventivo'}
                              {service.pricing_type === 'FIXED' && service.price_min && `€${service.price_min}`}
                              {service.pricing_type === 'RANGE' && service.price_min && service.price_max &&
                                `€${service.price_min}-€${service.price_max}`}
                            </span>
                          </td>
                          <td className="p-4 text-center">
                            <span
                              className={`text-xs px-2 py-1 rounded-full ${
                                service.is_published
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {service.is_published ? 'Pubblicato' : 'Bozza'}
                            </span>
                          </td>
                          <td className="p-4 text-center text-sm text-muted-foreground">
                            {formatDate(service.updated_at)}
                          </td>
                          <td className="p-4">
                            <div className="flex justify-end gap-2">
                              <Link href={`/servizi/${service.slug}`} target="_blank">
                                <Button variant="ghost" size="sm">
                                  Vedi
                                </Button>
                              </Link>
                              <Link href={`/admin/services/${service.id}/edit`}>
                                <Button variant="outline" size="sm">
                                  Modifica
                                </Button>
                              </Link>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => togglePublish(service.id, service.is_published)}
                              >
                                {service.is_published ? 'Nascondi' : 'Pubblica'}
                              </Button>
                              <Button
                                variant="destructive"
                                size="sm"
                                onClick={() => handleDelete(service.id, service.name)}
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
        {!isLoading && services.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <p className="text-muted-foreground text-lg mb-4">
                {searchQuery || filterCategory
                  ? 'Nessun servizio trovato con questi filtri'
                  : 'Nessun servizio creato ancora'}
              </p>
              <Link href="/admin/services/new">
                <Button>Crea il Primo Servizio</Button>
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
