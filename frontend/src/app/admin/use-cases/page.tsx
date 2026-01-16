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
import { Plus, Edit, Trash2, Eye, EyeOff, ArrowUp, ArrowDown } from 'lucide-react';

interface UseCase {
  id: string;
  title: string;
  slug: string;
  industry: string;
  icon: string | null;
  challenge_title: string;
  challenge_description: string;
  solution_title: string;
  solution_description: string;
  result_title: string;
  result_description: string;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface UseCasesResponse {
  use_cases: UseCase[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function AdminUseCasesPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();
  const [useCases, setUseCases] = useState<UseCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterIndustry, setFilterIndustry] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load data only if authenticated and admin
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadUseCases();
    }
  }, [isAuthenticated, isAdmin, currentPage, filterIndustry]);

  const loadUseCases = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', '20');

      if (filterIndustry) {
        params.append('industry', filterIndustry);
      }

      const response = await apiClient.get<UseCasesResponse>(
        '/use-cases/admin/all?' + params.toString()
      );

      setUseCases(response.use_cases);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleToggleActive = async (useCase: UseCase) => {
    const message = 'Sei sicuro di voler ' + (useCase.is_active ? 'disattivare' : 'attivare') + ' questo caso d\'uso?';
    if (!confirm(message)) {
      return;
    }

    try {
      await apiClient.put('/use-cases/admin/' + useCase.id, {
        is_active: !useCase.is_active,
      });
      await loadUseCases();
    } catch (err) {
      alert(getErrorMessage(err));
    }
  };

  const handleDelete = async (useCase: UseCase) => {
    const message = 'Sei sicuro di voler eliminare "' + useCase.title + '"? Questa azione non può essere annullata.';
    if (!confirm(message)) {
      return;
    }

    try {
      await apiClient.delete('/use-cases/admin/' + useCase.id);
      await loadUseCases();
    } catch (err) {
      alert(getErrorMessage(err));
    }
  };

  const handleReorder = async (useCase: UseCase, newOrder: number) => {
    if (newOrder < 0) return;

    try {
      await apiClient.patch('/use-cases/admin/' + useCase.id + '/reorder?new_order=' + newOrder);
      await loadUseCases();
    } catch (err) {
      alert(getErrorMessage(err));
    }
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
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h1 className="text-4xl font-bold mb-2">Casi d'Uso</h1>
              <p className="text-muted-foreground">
                Gestisci i success stories e i casi d'uso della piattaforma
              </p>
            </div>
            <Link href="/admin/use-cases/new">
              <Button size="lg">
                <Plus className="h-5 w-5 mr-2" />
                Nuovo Caso d'Uso
              </Button>
            </Link>
          </div>

          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Filtri</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={filterIndustry === null ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterIndustry(null);
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Tutti
                </Button>
                {['Finance', 'Sanità', 'Retail', 'Industria 4.0', 'E-commerce', 'Manufacturing'].map((industry) => (
                  <Button
                    key={industry}
                    variant={filterIndustry === industry ? 'default' : 'outline'}
                    onClick={() => {
                      setFilterIndustry(industry);
                      setCurrentPage(1);
                    }}
                    size="sm"
                  >
                    {industry}
                  </Button>
                ))}
              </div>
            </CardContent>
          </Card>

          {isLoading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Caricamento casi d'uso...</p>
            </div>
          )}

          {!isLoading && useCases.length > 0 && (
            <>
              <div className="space-y-4">
                {useCases.map((useCase) => (
                  <Card key={useCase.id} className={!useCase.is_active ? 'opacity-60' : ''}>
                    <CardHeader>
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-3 mb-2">
                            <CardTitle className="text-xl">{useCase.title}</CardTitle>
                            <Badge variant="outline">{useCase.industry}</Badge>
                            {useCase.is_active ? (
                              <Badge className="bg-green-100 text-green-800">Attivo</Badge>
                            ) : (
                              <Badge variant="secondary">Bozza</Badge>
                            )}
                          </div>
                          <CardDescription className="flex items-center gap-4">
                            <span>Slug: {useCase.slug}</span>
                            <span>Ordine: {useCase.display_order}</span>
                          </CardDescription>
                        </div>

                        <div className="flex gap-2">
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleReorder(useCase, useCase.display_order - 1)}
                            title="Sposta su"
                          >
                            <ArrowUp className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleReorder(useCase, useCase.display_order + 1)}
                            title="Sposta giù"
                          >
                            <ArrowDown className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleToggleActive(useCase)}
                            title={useCase.is_active ? 'Disattiva' : 'Attiva'}
                          >
                            {useCase.is_active ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </Button>
                          <Link href={'/admin/use-cases/' + useCase.id + '/edit'}>
                            <Button variant="ghost" size="icon" title="Modifica">
                              <Edit className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDelete(useCase)}
                            title="Elimina"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </CardHeader>

                    <CardContent>
                      <div className="grid md:grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="font-semibold text-xs text-muted-foreground mb-1">
                            {useCase.challenge_title}
                          </p>
                          <p className="line-clamp-2">{useCase.challenge_description}</p>
                        </div>
                        <div>
                          <p className="font-semibold text-xs text-muted-foreground mb-1">
                            {useCase.solution_title}
                          </p>
                          <p className="line-clamp-2">{useCase.solution_description}</p>
                        </div>
                        <div>
                          <p className="font-semibold text-xs text-muted-foreground mb-1">
                            {useCase.result_title}
                          </p>
                          <p className="line-clamp-2">{useCase.result_description}</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>

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

          {!isLoading && useCases.length === 0 && (
            <Card>
              <CardContent className="text-center py-12">
                <p className="text-muted-foreground text-lg mb-4">
                  {filterIndustry
                    ? 'Nessun caso d\'uso trovato per ' + filterIndustry
                    : 'Nessun caso d\'uso creato'}
                </p>
                {!filterIndustry && (
                  <Link href="/admin/use-cases/new">
                    <Button>
                      <Plus className="h-5 w-5 mr-2" />
                      Crea il primo caso d'uso
                    </Button>
                  </Link>
                )}
              </CardContent>
            </Card>
          )}

          <div className="mt-8">
            <Link href="/admin">
              <Button variant="ghost">← Torna alla Dashboard Admin</Button>
            </Link>
          </div>
        </div>
      </main>
    </>
  );
}
