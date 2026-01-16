/**
 * Admin Invoices Management
 * Descrizione: Gestione fatture e fatturazione
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
import { Download, Eye, FileText, Search } from 'lucide-react';
import { Input } from '@/components/ui/input';

interface Invoice {
  id: string;
  invoice_number: string;
  order_id: string;
  user_id: string;
  status: 'draft' | 'issued' | 'paid' | 'cancelled' | 'overdue';
  issue_date: string;
  due_date: string;
  paid_date?: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  currency: string;
  customer_name?: string;
  customer_email?: string;
  created_at: string;
  updated_at: string;
}

interface InvoiceStats {
  total_invoices: number;
  total_amount: number;
  paid_amount: number;
  pending_amount: number;
  overdue_amount: number;
}

export default function AdminInvoicesPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [stats, setStats] = useState<InvoiceStats | null>(null);
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
      // Load invoices and stats in parallel
      const [invoicesData, statsData] = await Promise.all([
        loadInvoices(),
        loadStats(),
      ]);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const loadInvoices = async () => {
    const params = new URLSearchParams();
    params.append('page', '1');
    params.append('page_size', '50');

    if (filterStatus) {
      params.append('status', filterStatus);
    }

    const response = await apiClient.get<Invoice[]>(
      `/invoices?${params.toString()}`
    );
    setInvoices(response);
    return response;
  };

  const loadStats = async () => {
    try {
      const response = await apiClient.get<InvoiceStats>('/invoices/stats');
      setStats(response);
      return response;
    } catch (err) {
      // Stats might not be available, continue without them
      console.error('Failed to load invoice stats:', err);
      return null;
    }
  };

  const getStatusBadge = (status: string) => {
    const badges: Record<string, { bg: string; text: string; label: string }> = {
      draft: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Bozza' },
      issued: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Emessa' },
      paid: { bg: 'bg-green-100', text: 'text-green-800', label: 'Pagata' },
      cancelled: { bg: 'bg-red-100', text: 'text-red-800', label: 'Annullata' },
      overdue: { bg: 'bg-orange-100', text: 'text-orange-800', label: 'Scaduta' },
    };

    const badge = badges[status] || badges.draft;

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

  const filteredInvoices = invoices.filter((invoice) => {
    if (!searchQuery) return true;
    const search = searchQuery.toLowerCase();
    return (
      invoice.invoice_number.toLowerCase().includes(search) ||
      invoice.customer_name?.toLowerCase().includes(search) ||
      invoice.customer_email?.toLowerCase().includes(search)
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
          <h1 className="text-3xl font-bold">Gestione Fatture</h1>
          <p className="text-muted-foreground mt-2">
            Visualizza e gestisci tutte le fatture
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
                Totale Fatture
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_invoices}</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Importo Totale
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(stats.total_amount)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Incassato
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(stats.paid_amount)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Da Incassare
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-600">
                {formatCurrency(stats.pending_amount + stats.overdue_amount)}
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
                  placeholder="Cerca per numero, cliente, email..."
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
                Tutte
              </Button>
              <Button
                variant={filterStatus === 'paid' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('paid')}
              >
                Pagate
              </Button>
              <Button
                variant={filterStatus === 'issued' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('issued')}
              >
                Emesse
              </Button>
              <Button
                variant={filterStatus === 'overdue' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFilterStatus('overdue')}
              >
                Scadute
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Caricamento fatture...</p>
        </div>
      )}

      {/* Invoices Table */}
      {!isLoading && filteredInvoices.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Fatture ({filteredInvoices.length})</CardTitle>
            <CardDescription>
              Elenco completo delle fatture emesse
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-4 font-semibold">Numero</th>
                    <th className="text-left p-4 font-semibold">Cliente</th>
                    <th className="text-left p-4 font-semibold">Data Emissione</th>
                    <th className="text-left p-4 font-semibold">Scadenza</th>
                    <th className="text-left p-4 font-semibold">Importo</th>
                    <th className="text-left p-4 font-semibold">Stato</th>
                    <th className="text-right p-4 font-semibold">Azioni</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredInvoices.map((invoice) => (
                    <tr key={invoice.id} className="border-b hover:bg-muted/50">
                      <td className="p-4">
                        <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                          {invoice.invoice_number}
                        </code>
                      </td>
                      <td className="p-4">
                        <div className="font-medium">
                          {invoice.customer_name || 'N/A'}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {invoice.customer_email}
                        </div>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">
                          {new Date(invoice.issue_date).toLocaleDateString('it-IT')}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="text-sm">
                          {new Date(invoice.due_date).toLocaleDateString('it-IT')}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="font-semibold">
                          {formatCurrency(invoice.total_amount)}
                        </span>
                      </td>
                      <td className="p-4">{getStatusBadge(invoice.status)}</td>
                      <td className="p-4">
                        <div className="flex items-center justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Visualizza"
                            onClick={() =>
                              alert(
                                `Dettaglio fattura ${invoice.invoice_number} - Funzionalità in sviluppo`
                              )
                            }
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            title="Scarica PDF"
                            onClick={() =>
                              alert(
                                `Download fattura ${invoice.invoice_number} - Funzionalità in sviluppo`
                              )
                            }
                          >
                            <Download className="h-4 w-4" />
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
      {!isLoading && filteredInvoices.length === 0 && (
        <Card>
          <CardContent className="text-center py-12">
            <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">Nessuna fattura trovata</h3>
            <p className="text-muted-foreground">
              {searchQuery || filterStatus
                ? 'Nessuna fattura corrisponde ai criteri di ricerca'
                : 'Le fatture verranno generate automaticamente dagli ordini'}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
