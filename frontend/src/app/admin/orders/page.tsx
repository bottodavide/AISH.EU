/**
 * Admin Orders Management Page
 * Descrizione: Gestione completa ordini e fatture
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
interface Order {
  id: string;
  order_number: string;
  customer_email: string;
  customer_name: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'CANCELLED';
  total_amount: number;
  currency: string;
  created_at: string;
  updated_at: string;
}

interface OrdersResponse {
  orders: Order[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function AdminOrdersPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();

  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load orders
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadOrders();
    }
  }, [isAuthenticated, isAdmin, currentPage, filterStatus]);

  const loadOrders = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', '20');
      params.append('sort_by', 'created_at');
      params.append('sort_order', 'desc');

      if (filterStatus) {
        params.append('status', filterStatus);
      }

      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const response = await apiClient.get<OrdersResponse>(
        `/api/v1/admin/orders?${params.toString()}`
      );

      setOrders(response.orders);
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
    loadOrders();
  };

  const handleUpdateStatus = async (orderId: string, orderNumber: string) => {
    const newStatus = prompt(
      `Cambia status per ordine ${orderNumber}:\n\nStatus disponibili:\n- PENDING\n- PROCESSING\n- COMPLETED\n- CANCELLED\n\nInserisci il nuovo status:`
    );

    if (!newStatus) return;

    const validStatuses = ['PENDING', 'PROCESSING', 'COMPLETED', 'CANCELLED'];
    const upperStatus = newStatus.toUpperCase();

    if (!validStatuses.includes(upperStatus)) {
      alert('Status non valido');
      return;
    }

    try {
      await apiClient.patch(`/api/v1/admin/orders/${orderId}`, {
        status: upperStatus,
      });
      await loadOrders();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      PROCESSING: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-green-100 text-green-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`text-xs px-2 py-1 rounded-full font-medium ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const formatCurrency = (amount: number, currency: string): string => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
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
            <h1 className="text-4xl font-bold mb-2">Gestione Ordini</h1>
            <p className="text-muted-foreground">
              Visualizza e gestisci tutti gli ordini della piattaforma
            </p>
          </div>
        </div>

        {/* Filters & Search */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <form onSubmit={handleSearch} className="flex-1 flex gap-2">
                <Input
                  type="search"
                  placeholder="Cerca per numero ordine o cliente..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1"
                />
                <Button type="submit">Cerca</Button>
              </form>

              {/* Status Filter */}
              <div className="flex gap-2">
                <Button
                  variant={filterStatus === null ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterStatus(null);
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Tutti
                </Button>
                <Button
                  variant={filterStatus === 'PENDING' ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterStatus('PENDING');
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  In Attesa
                </Button>
                <Button
                  variant={filterStatus === 'PROCESSING' ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterStatus('PROCESSING');
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  In Lavorazione
                </Button>
                <Button
                  variant={filterStatus === 'COMPLETED' ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterStatus('COMPLETED');
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Completati
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
            <p className="text-muted-foreground">Caricamento ordini...</p>
          </div>
        )}

        {/* Orders Table */}
        {!isLoading && orders.length > 0 && (
          <>
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted">
                      <tr>
                        <th className="text-left p-4 font-semibold">Ordine</th>
                        <th className="text-left p-4 font-semibold">Cliente</th>
                        <th className="text-center p-4 font-semibold">Status</th>
                        <th className="text-right p-4 font-semibold">Totale</th>
                        <th className="text-center p-4 font-semibold">Data</th>
                        <th className="text-right p-4 font-semibold">Azioni</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.map((order) => (
                        <tr key={order.id} className="border-t hover:bg-muted/50">
                          <td className="p-4">
                            <div>
                              <div className="font-semibold">#{order.order_number}</div>
                              <div className="text-xs text-muted-foreground">
                                ID: {order.id.slice(0, 8)}...
                              </div>
                            </div>
                          </td>
                          <td className="p-4">
                            <div>
                              <div className="font-medium">{order.customer_name}</div>
                              <div className="text-sm text-muted-foreground">
                                {order.customer_email}
                              </div>
                            </div>
                          </td>
                          <td className="p-4 text-center">{getStatusBadge(order.status)}</td>
                          <td className="p-4 text-right font-semibold">
                            {formatCurrency(order.total_amount, order.currency)}
                          </td>
                          <td className="p-4 text-center text-sm text-muted-foreground">
                            {formatDate(order.created_at)}
                          </td>
                          <td className="p-4">
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => alert('Dettaglio ordine - TODO')}
                              >
                                Dettagli
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleUpdateStatus(order.id, order.order_number)}
                              >
                                Cambia Status
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
        {!isLoading && orders.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <p className="text-muted-foreground text-lg">
                {searchQuery || filterStatus
                  ? 'Nessun ordine trovato con questi filtri'
                  : 'Nessun ordine ancora'}
              </p>
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
