/**
 * Admin Newsletter Management Page
 * Descrizione: Gestione iscritti newsletter con export CSV
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Download, Search, Users, UserCheck, UserX, Mail, TrendingUp } from 'lucide-react';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import { handleApiError } from '@/lib/error-handler';

// Types
interface NewsletterSubscriber {
  id: string;
  email: string;
  first_name: string | null;
  last_name: string | null;
  status: 'PENDING' | 'ACTIVE' | 'UNSUBSCRIBED' | 'BOUNCED';
  subscribed_at: string;
  confirmed_at: string | null;
  unsubscribed_at: string | null;
  source: string | null;
  created_at: string;
  updated_at: string;
}

interface NewsletterStats {
  total_subscribers: number;
  active_subscribers: number;
  pending_subscribers: number;
  unsubscribed_subscribers: number;
  subscribed_today: number;
  subscribed_this_week: number;
  subscribed_this_month: number;
}

interface SubscriberListResponse {
  subscribers: NewsletterSubscriber[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function AdminNewsletterPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();
  const [subscribers, setSubscribers] = useState<NewsletterSubscriber[]>([]);
  const [stats, setStats] = useState<NewsletterStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [total, setTotal] = useState(0);

  const pageSize = 20;

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load stats only if authenticated and admin
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadStats();
    }
  }, [isAuthenticated, isAdmin]);

  // Load subscribers only if authenticated and admin
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadSubscribers();
    }
  }, [isAuthenticated, isAdmin, currentPage, statusFilter, searchQuery]);

  const loadStats = async () => {
    try {
      const data = await apiClient.get<NewsletterStats>('/newsletter/stats');
      setStats(data);
    } catch (err: any) {
      console.error('Failed to load newsletter stats:', err);
    }
  };

  const loadSubscribers = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        page: currentPage.toString(),
        page_size: pageSize.toString(),
      });

      if (statusFilter) {
        params.append('status', statusFilter);
      }

      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const data = await apiClient.get<SubscriberListResponse>(
        `/newsletter/subscribers?${params.toString()}`
      );

      setSubscribers(data.subscribers);
      setTotal(data.total);
      setTotalPages(data.total_pages);
    } catch (err: any) {
      if (!err.response || err.response?.status >= 500 || err.code === 'ERR_NETWORK') {
        handleApiError(err);
        return;
      }
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportCSV = async () => {
    try {
      const params = new URLSearchParams();
      if (statusFilter) {
        params.append('status_filter', statusFilter);
      }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/newsletter/subscribers/export?${params.toString()}`,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      if (!response.ok) {
        throw new Error('Export failed');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `newsletter_subscribers_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      setError('Errore durante l\'export CSV');
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, { variant: any; label: string }> = {
      ACTIVE: { variant: 'default', label: 'Attivo' },
      PENDING: { variant: 'secondary', label: 'In Attesa' },
      UNSUBSCRIBED: { variant: 'outline', label: 'Disiscritto' },
      BOUNCED: { variant: 'destructive', label: 'Bounce' },
    };

    const config = variants[status] || { variant: 'secondary', label: status };
    return <Badge variant={config.variant as any}>{config.label}</Badge>;
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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
      <main className="container py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Gestione Newsletter</h1>
          <p className="text-muted-foreground">
            Visualizza e gestisci gli iscritti alla newsletter
          </p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Totale Iscritti</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.total_subscribers}</div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Attivi</CardTitle>
                <UserCheck className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {stats.active_subscribers}
                </div>
                <p className="text-xs text-muted-foreground">
                  {stats.total_subscribers > 0
                    ? Math.round((stats.active_subscribers / stats.total_subscribers) * 100)
                    : 0}
                  % del totale
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Questo Mese</CardTitle>
                <TrendingUp className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  +{stats.subscribed_this_month}
                </div>
                <p className="text-xs text-muted-foreground">
                  Questa settimana: {stats.subscribed_this_week}
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Disiscritti</CardTitle>
                <UserX className="h-4 w-4 text-destructive" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-destructive">
                  {stats.unsubscribed_subscribers}
                </div>
                <p className="text-xs text-muted-foreground">
                  In attesa: {stats.pending_subscribers}
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filters & Actions */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
              <div>
                <CardTitle>Iscritti Newsletter</CardTitle>
                <CardDescription>
                  {total} iscritti totali
                </CardDescription>
              </div>
              <Button onClick={handleExportCSV} className="gap-2">
                <Download className="h-4 w-4" />
                Esporta CSV
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col md:flex-row gap-4 mb-6">
              {/* Search */}
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Cerca per email o nome..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setCurrentPage(1);
                  }}
                  className="pl-9"
                />
              </div>

              {/* Status Filter */}
              <select
                value={statusFilter}
                onChange={(e) => {
                  setStatusFilter(e.target.value);
                  setCurrentPage(1);
                }}
                className="px-3 py-2 border rounded-md bg-background"
              >
                <option value="">Tutti gli stati</option>
                <option value="ACTIVE">Attivi</option>
                <option value="PENDING">In Attesa</option>
                <option value="UNSUBSCRIBED">Disiscritti</option>
                <option value="BOUNCED">Bounce</option>
              </select>
            </div>

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive" className="mb-4">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-muted-foreground">Caricamento...</p>
              </div>
            )}

            {/* Table */}
            {!isLoading && subscribers.length > 0 && (
              <>
                <div className="rounded-md border">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Email</TableHead>
                        <TableHead>Nome</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead>Iscritto</TableHead>
                        <TableHead>Confermato</TableHead>
                        <TableHead>Fonte</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {subscribers.map((subscriber) => (
                        <TableRow key={subscriber.id}>
                          <TableCell className="font-medium">
                            <div className="flex items-center gap-2">
                              <Mail className="h-4 w-4 text-muted-foreground" />
                              {subscriber.email}
                            </div>
                          </TableCell>
                          <TableCell>
                            {subscriber.first_name || subscriber.last_name
                              ? `${subscriber.first_name || ''} ${subscriber.last_name || ''}`.trim()
                              : '-'}
                          </TableCell>
                          <TableCell>{getStatusBadge(subscriber.status)}</TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {formatDate(subscriber.subscribed_at)}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {formatDate(subscriber.confirmed_at)}
                          </TableCell>
                          <TableCell className="text-sm text-muted-foreground">
                            {subscriber.source || '-'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-between mt-4">
                    <p className="text-sm text-muted-foreground">
                      Pagina {currentPage} di {totalPages} ({total} totali)
                    </p>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                        disabled={currentPage === 1}
                      >
                        Precedente
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                        disabled={currentPage === totalPages}
                      >
                        Successiva
                      </Button>
                    </div>
                  </div>
                )}
              </>
            )}

            {/* Empty State */}
            {!isLoading && subscribers.length === 0 && (
              <div className="text-center py-12">
                <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <p className="text-muted-foreground text-lg">
                  {searchQuery || statusFilter
                    ? 'Nessun iscritto trovato con i filtri selezionati'
                    : 'Nessun iscritto alla newsletter'}
                </p>
                {(searchQuery || statusFilter) && (
                  <Button
                    variant="outline"
                    className="mt-4"
                    onClick={() => {
                      setSearchQuery('');
                      setStatusFilter('');
                      setCurrentPage(1);
                    }}
                  >
                    Rimuovi Filtri
                  </Button>
                )}
              </div>
            )}
          </CardContent>
        </Card>
      </main>
    </>
  );
}
