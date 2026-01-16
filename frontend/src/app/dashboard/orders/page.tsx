/**
 * User Orders Page
 * Descrizione: Visualizzazione ordini utente
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, ShoppingCart, FileText, Download } from 'lucide-react';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { formatDate } from '@/lib/utils';

interface Order {
  id: string;
  order_number: string;
  status: string;
  total: number;
  currency: string;
  created_at: string;
  service_name: string;
}

export default function OrdersPage() {
  const { user } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadOrders();
    }
  }, [user]);

  const loadOrders = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await apiClient.get<{ orders: Order[] }>('/orders/my-orders');
      setOrders(response.orders || []);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { label: 'In attesa', variant: 'secondary' as const },
      confirmed: { label: 'Confermato', variant: 'default' as const },
      completed: { label: 'Completato', variant: 'default' as const },
      cancelled: { label: 'Annullato', variant: 'destructive' as const },
    };

    const config = statusConfig[status as keyof typeof statusConfig] || { label: status, variant: 'secondary' as const };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">I Miei Ordini</h1>
        <p className="text-muted-foreground mt-2">
          Visualizza e gestisci i tuoi ordini
        </p>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {orders.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <ShoppingCart className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">Nessun ordine</h3>
            <p className="text-muted-foreground text-center mb-6">
              Non hai ancora effettuato ordini
            </p>
            <Button asChild>
              <a href="/servizi">Scopri i Servizi</a>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => (
            <Card key={order.id}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg">
                      Ordine #{order.order_number}
                    </CardTitle>
                    <CardDescription>
                      {formatDate(order.created_at)}
                    </CardDescription>
                  </div>
                  <div className="text-right">
                    {getStatusBadge(order.status)}
                    <div className="text-lg font-bold mt-2">
                      €{order.total.toFixed(2)}
                    </div>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{order.service_name}</p>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm">
                      <FileText className="h-4 w-4 mr-2" />
                      Dettagli
                    </Button>
                    {order.status === 'completed' && (
                      <Button variant="outline" size="sm">
                        <Download className="h-4 w-4 mr-2" />
                        Fattura
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
