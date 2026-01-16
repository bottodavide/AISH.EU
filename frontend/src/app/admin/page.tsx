/**
 * Admin Dashboard Page
 * Descrizione: Dashboard amministratore con gestione completa
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface AdminStats {
  total_users: number;
  total_orders: number;
  total_revenue: number;
  total_services: number;
  total_blog_posts: number;
  pending_orders: number;
  unpaid_invoices: number;
}

interface RecentUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
  is_verified: boolean;
}

interface RecentOrder {
  id: string;
  order_number: string;
  customer_email: string;
  status: string;
  total_amount: number;
  created_at: string;
}

export default function AdminDashboardPage() {
  const { isAuthenticated } = useAuth();

  const [stats, setStats] = useState<AdminStats | null>(null);
  const [recentUsers, setRecentUsers] = useState<RecentUser[]>([]);
  const [recentOrders, setRecentOrders] = useState<RecentOrder[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load admin data
  useEffect(() => {
    if (isAuthenticated) {
      loadAdminData();
    }
  }, [isAuthenticated]);

  const loadAdminData = async () => {
    setIsLoading(true);
    setError(null);

    try {
      // Load stats
      const statsResponse = await apiClient.get<AdminStats>(
        '/admin/stats'
      );
      setStats(statsResponse);

      // Load recent users
      const usersResponse = await apiClient.get<{ users: RecentUser[]; total: number }>(
        '/admin/users?page=1&page_size=5&sort_by=created_at&sort_order=desc'
      );
      setRecentUsers(usersResponse.users || []);

      // TODO: Load recent orders quando endpoint sarà implementato
      // Per ora lasciamo lista vuota
      setRecentOrders([]);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
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

  const formatCurrency = (amount: number): string => {
    return new Intl.NumberFormat('it-IT', {
      style: 'currency',
      currency: 'EUR',
    }).format(amount);
  };

  return (
    <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Admin Dashboard</h1>
          <p className="text-muted-foreground">
            Gestione completa della piattaforma
          </p>
        </div>

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
        {!isLoading && stats && (
          <div className="space-y-8">
            {/* Stats Grid */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Utenti Totali
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{stats.total_users}</div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Ordini Totali
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">{stats.total_orders}</div>
                  {stats.pending_orders > 0 && (
                    <p className="text-sm text-yellow-600 mt-1">
                      {stats.pending_orders} in attesa
                    </p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Fatturato Totale
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-bold">
                    {formatCurrency(stats.total_revenue)}
                  </div>
                  {stats.unpaid_invoices > 0 && (
                    <p className="text-sm text-yellow-600 mt-1">
                      {stats.unpaid_invoices} fatture non pagate
                    </p>
                  )}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    Contenuti
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-1">
                    <p className="text-lg font-semibold">
                      {stats.total_services} Servizi
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {stats.total_blog_posts} Articoli Blog
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Gestione Contenuti</CardTitle>
                <CardDescription>
                  Accesso rapido alle funzioni di gestione
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  {/* Services Management */}
                  <Card className="border-2">
                    <CardHeader>
                      <CardTitle className="text-lg">Servizi</CardTitle>
                      <CardDescription>
                        Gestisci i servizi di consulenza
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <Link href="/admin/services">
                        <Button variant="outline" className="w-full">
                          Visualizza Servizi
                        </Button>
                      </Link>
                      <Link href="/admin/services/new">
                        <Button className="w-full">Nuovo Servizio</Button>
                      </Link>
                    </CardContent>
                  </Card>

                  {/* Blog Management */}
                  <Card className="border-2">
                    <CardHeader>
                      <CardTitle className="text-lg">Blog</CardTitle>
                      <CardDescription>
                        Gestisci articoli e categorie
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <Link href="/admin/blog">
                        <Button variant="outline" className="w-full">
                          Visualizza Articoli
                        </Button>
                      </Link>
                      <Link href="/admin/blog/new">
                        <Button className="w-full">Nuovo Articolo</Button>
                      </Link>
                    </CardContent>
                  </Card>

                  {/* Pages Management */}
                  <Card className="border-2">
                    <CardHeader>
                      <CardTitle className="text-lg">Pagine</CardTitle>
                      <CardDescription>
                        Gestisci le pagine del sito
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      <Link href="/admin/pages">
                        <Button variant="outline" className="w-full">
                          Visualizza Pagine
                        </Button>
                      </Link>
                      <Link href="/admin/pages/new">
                        <Button className="w-full">Nuova Pagina</Button>
                      </Link>
                    </CardContent>
                  </Card>
                </div>
              </CardContent>
            </Card>

            {/* Management Sections */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Orders Management */}
              <Card>
                <CardHeader>
                  <CardTitle>Gestione Ordini</CardTitle>
                  <CardDescription>
                    Gestisci ordini e fatture
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Link href="/admin/orders">
                    <Button variant="outline" className="w-full">
                      Visualizza Tutti gli Ordini
                    </Button>
                  </Link>
                  <Link href="/admin/invoices">
                    <Button variant="outline" className="w-full">
                      Gestione Fatture
                    </Button>
                  </Link>
                  <Link href="/admin/payments">
                    <Button variant="outline" className="w-full">
                      Storico Pagamenti
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              {/* Users Management */}
              <Card>
                <CardHeader>
                  <CardTitle>Gestione Utenti</CardTitle>
                  <CardDescription>
                    Gestisci utenti e permessi
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Link href="/admin/users">
                    <Button variant="outline" className="w-full">
                      Visualizza Tutti gli Utenti
                    </Button>
                  </Link>
                  <Link href="/admin/users/new">
                    <Button className="w-full">Crea Nuovo Utente</Button>
                  </Link>
                </CardContent>
              </Card>
            </div>

            {/* Recent Activity */}
            <div className="grid lg:grid-cols-2 gap-6">
              {/* Recent Users */}
              <Card>
                <CardHeader>
                  <CardTitle>Utenti Recenti</CardTitle>
                  <CardDescription>
                    Ultimi 5 utenti registrati
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {recentUsers.length === 0 ? (
                    <p className="text-muted-foreground text-center py-4">
                      Nessun utente registrato
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {recentUsers.map((user) => (
                        <div
                          key={user.id}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div>
                            <div className="font-medium">
                              {user.first_name} {user.last_name}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {user.email}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {formatDate(user.created_at)}
                            </div>
                          </div>
                          {user.is_verified && (
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded-full">
                              Verificato
                            </span>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Recent Orders */}
              <Card>
                <CardHeader>
                  <CardTitle>Ordini Recenti</CardTitle>
                  <CardDescription>
                    Ultimi 5 ordini ricevuti
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {recentOrders.length === 0 ? (
                    <p className="text-muted-foreground text-center py-4">
                      Nessun ordine ricevuto
                    </p>
                  ) : (
                    <div className="space-y-3">
                      {recentOrders.map((order) => (
                        <div
                          key={order.id}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div>
                            <div className="font-medium">
                              #{order.order_number}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {order.customer_email}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {formatDate(order.created_at)}
                            </div>
                          </div>
                          <div className="text-right">
                            <div className="font-semibold mb-1">
                              {formatCurrency(order.total_amount)}
                            </div>
                            <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">
                              {order.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* System Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Impostazioni Sistema</CardTitle>
                <CardDescription>
                  Configurazione e strumenti avanzati
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-3 gap-4">
                  <Link href="/admin/settings">
                    <Button variant="outline" className="w-full">
                      Impostazioni Generali
                    </Button>
                  </Link>
                  <Link href="/admin/analytics">
                    <Button variant="outline" className="w-full">
                      Analytics
                    </Button>
                  </Link>
                  <Link href="/admin/logs">
                    <Button variant="outline" className="w-full">
                      Log Sistema
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
    </div>
  );
}
