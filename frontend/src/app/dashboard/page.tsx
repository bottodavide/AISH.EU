/**
 * Customer Dashboard Page
 * Descrizione: Dashboard cliente con ordini, fatture e profilo
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import { ShieldAlert } from 'lucide-react';

// Types
interface Order {
  id: string;
  order_number: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'CANCELLED';
  total_amount: number;
  currency: string;
  created_at: string;
  service_name: string;
}

interface Invoice {
  id: string;
  invoice_number: string;
  status: 'DRAFT' | 'SENT' | 'PAID' | 'OVERDUE' | 'CANCELLED';
  total_amount: number;
  currency: string;
  issue_date: string;
  due_date: string;
  paid_at?: string;
}

interface UserProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name?: string;
  phone?: string;
  is_verified: boolean;
}

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading } = useAuth();

  const [activeTab, setActiveTab] = useState<'overview' | 'orders' | 'invoices' | 'profile'>('overview');
  const [orders, setOrders] = useState<Order[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login?redirect=/dashboard');
    }
  }, [authLoading, isAuthenticated, router]);

  // Redirect admin users to admin dashboard
  useEffect(() => {
    if (user && ['admin', 'super_admin', 'editor'].includes(user.role)) {
      router.push('/admin');
    }
  }, [user, router]);

  // Load dashboard data
  useEffect(() => {
    if (isAuthenticated) {
      loadDashboardData();
    }
  }, [isAuthenticated]);

  const loadDashboardData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Load orders (with fallback)
      try {
        const ordersResponse = await apiClient.get<{ orders: Order[] }>(
          '/orders'
        );
        setOrders(ordersResponse.orders || []);
      } catch {
        setOrders([]);
      }

      // Load invoices (with fallback)
      try {
        const invoicesResponse = await apiClient.get<{ invoices: Invoice[] }>(
          '/invoices'
        );
        setInvoices(invoicesResponse.invoices || []);
      } catch {
        setInvoices([]);
      }

      // Load profile (with fallback)
      try {
        const profileResponse = await apiClient.get<UserProfile>(
          '/users/me'
        );
        setProfile(profileResponse);
      } catch {
        // Profile loading can fail, that's ok
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const getOrderStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      PENDING: 'bg-yellow-100 text-yellow-800',
      PROCESSING: 'bg-blue-100 text-blue-800',
      COMPLETED: 'bg-green-100 text-green-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const getInvoiceStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      DRAFT: 'bg-gray-100 text-gray-800',
      SENT: 'bg-blue-100 text-blue-800',
      PAID: 'bg-green-100 text-green-800',
      OVERDUE: 'bg-red-100 text-red-800',
      CANCELLED: 'bg-red-100 text-red-800',
    };
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-800'}`}>
        {status}
      </span>
    );
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const formatCurrency = (amount: number, currency: string): string => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: currency,
    }).format(amount);
  };

  if (authLoading || !isAuthenticated) {
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
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">
            Benvenuto, {user?.first_name || user?.email}
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-8 border-b">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'overview'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Panoramica
          </button>
          <button
            onClick={() => setActiveTab('orders')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'orders'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Ordini ({orders?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('invoices')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'invoices'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Fatture ({invoices?.length || 0})
          </button>
          <button
            onClick={() => setActiveTab('profile')}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === 'profile'
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Profilo
          </button>
        </div>

        {/* MFA Banner for non-admin users */}
        {user && !user.mfa_enabled && !['admin', 'super_admin', 'editor'].includes(user.role) && (
          <Alert className="mb-8 border-blue-500 bg-blue-50">
            <ShieldAlert className="h-4 w-4 text-blue-600" />
            <AlertDescription className="text-blue-900">
              <strong>Migliora la sicurezza del tuo account:</strong> Abilita l'autenticazione a due fattori (MFA) per proteggere meglio il tuo account.
              {' '}
              <Link href="/dashboard/security" className="font-medium underline">
                Abilita MFA →
              </Link>
            </AlertDescription>
          </Alert>
        )}

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-8">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento...</p>
          </div>
        )}

        {/* Content */}
        {!isLoading && (
          <>
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Stats Cards */}
                <div className="grid md:grid-cols-3 gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Ordini Totali
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold">{orders?.length || 0}</div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Fatture In Sospeso
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold">
                        {invoices?.filter((inv) => inv.status === 'SENT').length || 0}
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-sm font-medium text-muted-foreground">
                        Ordini Attivi
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="text-3xl font-bold">
                        {orders?.filter((ord) => ord.status === 'PROCESSING').length || 0}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Quick Actions */}
                <Card>
                  <CardHeader>
                    <CardTitle>Azioni Rapide</CardTitle>
                  </CardHeader>
                  <CardContent className="flex flex-wrap gap-3">
                    <Link href="/servizi">
                      <Button>Esplora Servizi</Button>
                    </Link>
                    <Link href="/dashboard/security">
                      <Button variant="outline">Impostazioni Sicurezza</Button>
                    </Link>
                    <Link href="/contatti">
                      <Button variant="outline">Contatta il Supporto</Button>
                    </Link>
                    <Link href="/blog">
                      <Button variant="outline">Leggi il Blog</Button>
                    </Link>
                  </CardContent>
                </Card>

                {/* Recent Orders */}
                <Card>
                  <CardHeader>
                    <CardTitle>Ordini Recenti</CardTitle>
                    <CardDescription>I tuoi ultimi 5 ordini</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {!orders || orders.length === 0 ? (
                      <p className="text-muted-foreground text-center py-4">
                        Nessun ordine ancora
                      </p>
                    ) : (
                      <div className="space-y-3">
                        {orders?.slice(0, 5).map((order) => (
                          <div
                            key={order.id}
                            className="flex items-center justify-between p-3 border rounded-lg"
                          >
                            <div>
                              <div className="font-medium">{order.service_name}</div>
                              <div className="text-sm text-muted-foreground">
                                {order.order_number} • {formatDate(order.created_at)}
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="text-right">
                                <div className="font-semibold">
                                  {formatCurrency(order.total_amount, order.currency)}
                                </div>
                                {getOrderStatusBadge(order.status)}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Orders Tab */}
            {activeTab === 'orders' && (
              <Card>
                <CardHeader>
                  <CardTitle>I Tuoi Ordini</CardTitle>
                  <CardDescription>
                    Visualizza e gestisci tutti i tuoi ordini
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {!orders || orders.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground mb-4">
                        Non hai ancora effettuato ordini
                      </p>
                      <Link href="/servizi">
                        <Button>Esplora Servizi</Button>
                      </Link>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {orders?.map((order) => (
                        <div
                          key={order.id}
                          className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="font-semibold mb-1">{order.service_name}</div>
                            <div className="text-sm text-muted-foreground">
                              Ordine #{order.order_number}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Data: {formatDate(order.created_at)}
                            </div>
                          </div>
                          <div className="text-right space-y-2">
                            <div className="font-bold">
                              {formatCurrency(order.total_amount, order.currency)}
                            </div>
                            {getOrderStatusBadge(order.status)}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Invoices Tab */}
            {activeTab === 'invoices' && (
              <Card>
                <CardHeader>
                  <CardTitle>Le Tue Fatture</CardTitle>
                  <CardDescription>
                    Visualizza e scarica le tue fatture
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {!invoices || invoices.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-muted-foreground">
                        Non hai ancora fatture
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {invoices?.map((invoice) => (
                        <div
                          key={invoice.id}
                          className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="font-semibold mb-1">
                              Fattura #{invoice.invoice_number}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Emessa: {formatDate(invoice.issue_date)}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              Scadenza: {formatDate(invoice.due_date)}
                            </div>
                            {invoice.paid_at && (
                              <div className="text-sm text-green-600">
                                Pagata: {formatDate(invoice.paid_at)}
                              </div>
                            )}
                          </div>
                          <div className="text-right space-y-2">
                            <div className="font-bold">
                              {formatCurrency(invoice.total_amount, invoice.currency)}
                            </div>
                            {getInvoiceStatusBadge(invoice.status)}
                            <div>
                              <Button variant="outline" size="sm">
                                Scarica PDF
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Profile Tab */}
            {activeTab === 'profile' && profile && (
              <Card>
                <CardHeader>
                  <CardTitle>Il Tuo Profilo</CardTitle>
                  <CardDescription>
                    Gestisci le tue informazioni personali
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium text-muted-foreground">
                        Email
                      </label>
                      <div className="flex items-center gap-2 mt-1">
                        <p className="text-lg">{profile.email}</p>
                        {profile.is_verified && (
                          <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                            Verificata
                          </span>
                        )}
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium text-muted-foreground">
                        Nome
                      </label>
                      <p className="text-lg mt-1">
                        {profile.first_name} {profile.last_name}
                      </p>
                    </div>

                    {profile.company_name && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">
                          Azienda
                        </label>
                        <p className="text-lg mt-1">{profile.company_name}</p>
                      </div>
                    )}

                    {profile.phone && (
                      <div>
                        <label className="text-sm font-medium text-muted-foreground">
                          Telefono
                        </label>
                        <p className="text-lg mt-1">{profile.phone}</p>
                      </div>
                    )}
                  </div>

                  <div className="pt-4 border-t space-y-3">
                    <Link href="/dashboard/profile" className="block">
                      <Button variant="outline" className="w-full">
                        Modifica Profilo
                      </Button>
                    </Link>
                    <Link href="/dashboard/security" className="block">
                      <Button variant="outline" className="w-full">
                        Sicurezza & Password
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            )}
          </>
        )}
      </main>
    </>
  );
}
