/**
 * Order Detail Page
 * Descrizione: Pagina dettaglio ordine e stato
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
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface OrderItem {
  id: string;
  service_id: string;
  service_name: string;
  quantity: number;
  unit_price: number;
  total_price: number;
}

interface Order {
  id: string;
  order_number: string;
  status: 'pending' | 'awaiting_payment' | 'paid' | 'processing' | 'completed' | 'cancelled' | 'refunded';
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  currency: string;
  items: OrderItem[];
  billing_data: {
    company_name?: string;
    vat_number?: string;
    address?: string;
    city?: string;
    postal_code?: string;
    country?: string;
    email?: string;
    phone?: string;
  };
  notes?: string;
  created_at: string;
  updated_at: string;
}

interface OrderDetailPageProps {
  params: {
    id: string;
  };
}

export default function OrderDetailPage({ params }: OrderDetailPageProps) {
  const router = useRouter();
  const { isAuthenticated, isLoading: authLoading } = useAuth();

  const [order, setOrder] = useState<Order | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push(`/login?redirect=/ordini/${params.id}`);
    }
  }, [authLoading, isAuthenticated, params.id, router]);

  // Load order
  useEffect(() => {
    if (isAuthenticated) {
      loadOrder();
    }
  }, [isAuthenticated, params.id]);

  const loadOrder = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<Order>(`/orders/${params.id}`);
      setOrder(response);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusLabel = (status: string): string => {
    const labels: Record<string, string> = {
      pending: 'In attesa',
      awaiting_payment: 'In attesa di pagamento',
      paid: 'Pagato',
      processing: 'In lavorazione',
      completed: 'Completato',
      cancelled: 'Annullato',
      refunded: 'Rimborsato',
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      awaiting_payment: 'bg-orange-100 text-orange-800',
      paid: 'bg-green-100 text-green-800',
      processing: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-gray-100 text-gray-800',
      refunded: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  const formatPrice = (amount: number): string => {
    return amount.toLocaleString('it-IT', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
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

      <main className="container py-12 max-w-4xl">
        {/* Back Button */}
        <div className="mb-6">
          <Link href="/profilo?tab=ordini">
            <Button variant="ghost" size="sm">
              ← Torna ai Miei Ordini
            </Button>
          </Link>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento ordine...</p>
          </div>
        )}

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-8">
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={loadOrder}
                className="ml-4 bg-white hover:bg-gray-100"
              >
                Riprova
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Order Content */}
        {!isLoading && order && (
          <div className="space-y-6">
            {/* Header */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h1 className="text-4xl font-bold">Ordine #{order.order_number}</h1>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(
                    order.status
                  )}`}
                >
                  {getStatusLabel(order.status)}
                </span>
              </div>
              <p className="text-muted-foreground">
                Creato il {formatDate(order.created_at)}
              </p>
            </div>

            {/* Success Message for New Orders */}
            {order.status === 'pending' || order.status === 'awaiting_payment' ? (
              <Alert className="bg-green-50 border-green-200">
                <AlertDescription>
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">✓</span>
                    <div>
                      <div className="font-semibold text-green-800 mb-1">
                        Ordine ricevuto con successo!
                      </div>
                      <p className="text-sm text-green-700">
                        Ti abbiamo inviato una email di conferma con tutti i dettagli.
                        Procederemo con il pagamento e l'attivazione del servizio.
                      </p>
                    </div>
                  </div>
                </AlertDescription>
              </Alert>
            ) : null}

            {/* Order Items */}
            <Card>
              <CardHeader>
                <CardTitle>Servizi Ordinati</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {order.items.map((item) => (
                    <div
                      key={item.id}
                      className="flex justify-between items-start pb-4 border-b last:border-0 last:pb-0"
                    >
                      <div className="flex-1">
                        <div className="font-semibold">{item.service_name}</div>
                        <div className="text-sm text-muted-foreground mt-1">
                          Quantità: {item.quantity}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">
                          €{formatPrice(item.total_price)}
                        </div>
                        {item.quantity > 1 && (
                          <div className="text-sm text-muted-foreground">
                            €{formatPrice(item.unit_price)} cad.
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Price Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Riepilogo Importi</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Subtotale</span>
                  <span>€{formatPrice(order.subtotal)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">IVA (22%)</span>
                  <span>€{formatPrice(order.tax_amount)}</span>
                </div>
                <div className="flex justify-between text-lg font-bold pt-2 border-t">
                  <span>Totale</span>
                  <span className="text-primary">€{formatPrice(order.total_amount)}</span>
                </div>
              </CardContent>
            </Card>

            {/* Billing Information */}
            {order.billing_data && (
              <Card>
                <CardHeader>
                  <CardTitle>Dati di Fatturazione</CardTitle>
                </CardHeader>
                <CardContent className="space-y-2 text-sm">
                  {order.billing_data.company_name && (
                    <div>
                      <span className="font-semibold">Ragione Sociale:</span>{' '}
                      {order.billing_data.company_name}
                    </div>
                  )}
                  {order.billing_data.vat_number && (
                    <div>
                      <span className="font-semibold">Partita IVA:</span>{' '}
                      {order.billing_data.vat_number}
                    </div>
                  )}
                  {order.billing_data.address && (
                    <div>
                      <span className="font-semibold">Indirizzo:</span>{' '}
                      {order.billing_data.address}
                    </div>
                  )}
                  {order.billing_data.city && order.billing_data.postal_code && (
                    <div>
                      <span className="font-semibold">Città:</span>{' '}
                      {order.billing_data.postal_code} {order.billing_data.city} (
                      {order.billing_data.country})
                    </div>
                  )}
                  {order.billing_data.email && (
                    <div>
                      <span className="font-semibold">Email:</span> {order.billing_data.email}
                    </div>
                  )}
                  {order.billing_data.phone && (
                    <div>
                      <span className="font-semibold">Telefono:</span> {order.billing_data.phone}
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* Notes */}
            {order.notes && (
              <Card>
                <CardHeader>
                  <CardTitle>Note</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{order.notes}</p>
                </CardContent>
              </Card>
            )}

            {/* Actions */}
            <Card className="bg-muted">
              <CardContent className="pt-6">
                <div className="text-center space-y-3">
                  <div className="text-2xl mb-2">💬</div>
                  <h3 className="font-semibold">Hai bisogno di assistenza?</h3>
                  <p className="text-sm text-muted-foreground">
                    Per domande su questo ordine, contatta il nostro supporto clienti
                  </p>
                  <Link href="/contatti">
                    <Button variant="outline" size="sm">
                      Contatta il Supporto
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Not Found State */}
        {!isLoading && !error && !order && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg mb-4">Ordine non trovato</p>
            <Link href="/profilo?tab=ordini">
              <Button>Torna ai Miei Ordini</Button>
            </Link>
          </div>
        )}
      </main>
    </>
  );
}
