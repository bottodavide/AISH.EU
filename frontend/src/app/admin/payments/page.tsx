/**
 * Admin Payments History
 * Descrizione: Storico pagamenti e transazioni
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import { CreditCard, Search, Download } from 'lucide-react';
import { Input } from '@/components/ui/input';

interface Payment {
  id: string;
  order_id: string;
  user_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'succeeded' | 'failed' | 'cancelled' | 'refunded';
  payment_method: string;
  payment_intent_id?: string;
  stripe_charge_id?: string;
  transaction_date: string;
  refunded_at?: string;
  refund_reason?: string;
  metadata?: any;
  created_at: string;
  updated_at: string;
}

interface PaymentStats {
  total_payments: number;
  total_amount: number;
  successful_payments: number;
  successful_amount: number;
  failed_payments: number;
  refunded_amount: number;
}

export default function AdminPaymentsPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();
  const [payments, setPayments] = useState<Payment[]>([]);
  const [stats, setStats] = useState<PaymentStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadData();
    }
  }, [isAuthenticated, isAdmin, filterStatus]);

  const loadData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      await Promise.all([loadPayments(), loadStats()]);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const loadPayments = async () => {
    try {
      const params = new URLSearchParams();
      params.append('page', '1');
      params.append('page_size', '100');

      if (filterStatus) {
        params.append('status', filterStatus);
      }

      // Try to load payments from orders
      const response = await apiClient.get<Payment[]>(
        `/orders/payments?${params.toString()}`
      );
      setPayments(response);
    } catch (err) {
      // If endpoint doesn't exist, show empty state
      console.error('Failed to load payments:', err);
      setPayments([]);
    }
  };

  const loadStats = async () => {
    try {
      const response = await apiClient.get<PaymentStats>('/orders/payments/stats');
      setStats(response);
    } catch (err) {
      // Stats might not be available
      console.error('Failed to load payment stats:', err);
      // Create mock stats from payments data
      if (payments.length > 0) {
        const mockStats: PaymentStats = {
          total_payments: payments.length,
          total_amount: payments.reduce((sum, p) => sum + p.amount, 0),
          successful_payments: payments.filter((p) => p.status === 'succeeded')
            .length,
          successful_amount: payments
            .filter((p) => p.status === 'succeeded')
            .reduce((sum, p) => sum + p.amount, 0),
          failed_payments: payments.filter((p) => p.status === 'failed').length,
          refunded_amount: payments
            .filter((p) => p.status === 'refunded')
            .reduce((sum, p) => sum + p.amount, 0),
        };
        setStats(mockStats);
      }
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { bg: string; text: string; label: string }> = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'In Attesa' },
      succeeded: {
        bg: 'bg-green-100',
        text: 'text-green-800',
        label: 'Completato',
      },
      failed: { bg: 'bg-red-100', text: 'text-red-800', label: 'Fallito' },
      cancelled: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Annullato' },
      refunded: {
        bg: 'bg-orange-100',
        text: 'text-orange-800',
        label: 'Rimborsato',
      },
    };

    const badge = badges[status] || badges.pending;

    return (
      <span
        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${badge.bg} ${badge.text}`}
      >
        {badge.label}
      </span>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  const filteredPayments = payments.filter((payment) => {
    if (!searchQuery) return true;
    const search = searchQuery.toLowerCase();
    return (
      payment.id.toLowerCase().includes(search) ||
      payment.order_id.toLowerCase().includes(search) ||
      payment.payment_intent_id?.toLowerCase().includes(search) ||
      payment.stripe_charge_id?.toLowerCase().includes(search)
    );
  });

  if (authLoading || !isAuthenticated || !isAdmin) {
    return (
      <div className="container py-12">
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
          <p className="text-muted-foreground">Caricamento...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Storico Pagamenti</h1>
          <p className="text-muted-foreground mt-2">
            Visualizza tutte le transazioni e pagamenti
          </p>
        </div>
        <Link href="/admin">
          <Button variant="outline">← Dashboard</Button>
        </Link>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Stats Cards */}
      {stats && (
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Totale Pagamenti
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_payments}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Completati
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {stats.successful_payments}
              </div>
              <div className="text-sm text-muted-foreground mt-1">
                {formatCurrency(stats.successful_amount)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Falliti
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {stats.failed_payments}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Rimborsati
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {formatCurrency(stats.refunded_amount)}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters & Search */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Filtri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            {/* Search */}
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Cerca per ID, ordine, Payment Intent..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>

            {/* Status Filters */}
            <div className="flex gap-2">
              <Button
                variant={filterStatus === null ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus(null)}
              >
                Tutti
              </Button>
              <Button
                variant={filterStatus === 'succeeded' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('succeeded')}
              >
                Completati
              </Button>
              <Button
                variant={filterStatus === 'pending' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('pending')}
              >
                In Attesa
              </Button>
              <Button
                variant={filterStatus === 'failed' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('failed')}
              >
                Falliti
              </Button>
              <Button
                variant={filterStatus === 'refunded' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('refunded')}
              >
                Rimborsati
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Caricamento pagamenti...</p>
        </div>
      )}

      {/* Payments Table */}
      {!isLoading && filteredPayments.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Pagamenti ({filteredPayments.length})</CardTitle>
            <CardDescription>
              Storico completo delle transazioni
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-semibold">ID Transazione</th>
                    <th className="text-left p-4 font-semibold">Ordine</th>
                    <th className="text-left p-4 font-semibold">Data</th>
                    <th className="text-left p-4 font-semibold">Metodo</th>
                    <th className="text-left p-4 font-semibold">Importo</th>
                    <th className="text-left p-4 font-semibold">Stato</th>
                    <th className="text-right p-4 font-semibold">Azioni</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredPayments.map((payment) => (
                    <tr key={payment.id} className="border-b hover:bg-muted/50">
                      <td className="p-4">
                        <code className="text-xs font-mono bg-muted px-2 py-1 rounded block max-w-[150px] truncate">
                          {payment.id}
                        </code>
                        {payment.payment_intent_id && (
                          <code className="text-xs text-muted-foreground mt-1 block">
                            PI: {payment.payment_intent_id.slice(0, 20)}...
                          </code>
                        )}
                      </td>
                      <td className="p-4">
                        <Link
                          href={`/admin/orders?order_id=${payment.order_id}`}
                          className="text-primary hover:underline"
                        >
                          <code className="text-sm">
                            {payment.order_id.slice(0, 8)}...
                          </code>
                        </Link>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">
                          {new Date(payment.transaction_date).toLocaleDateString(
                            'it-IT',
                            {
                              day: '2-digit',
                              month: 'short',
                              year: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            }
                          )}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="text-sm capitalize">
                          {payment.payment_method}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="font-semibold">
                          {formatCurrency(payment.amount)}
                        </span>
                      </td>
                      <td className="p-4">{getStatusBadge(payment.status)}</td>
                      <td className="p-4">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Dettagli Stripe"
                            onClick={() =>
                              alert(
                                `Dettagli Stripe per ${payment.id} - Funzionalità in sviluppo`
                              )
                            }
                          >
                            <CreditCard className="h-4 w-4" />
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
      {!isLoading && filteredPayments.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <CreditCard className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              Nessun pagamento trovato
            </h3>
            <p className="text-muted-foreground">
              {searchQuery || filterStatus
                ? 'Nessun pagamento corrisponde ai criteri di ricerca'
                : 'I pagamenti verranno registrati automaticamente quando i clienti completano gli acquisti'}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
