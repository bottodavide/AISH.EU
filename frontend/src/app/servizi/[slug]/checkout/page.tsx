/**
 * Service Checkout Page
 * Descrizione: Pagina checkout per acquisto servizio
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import { loadStripe } from '@stripe/stripe-js';
import { Elements } from '@stripe/react-stripe-js';
import StripeCheckoutForm from '@/components/StripeCheckoutForm';

// Load Stripe
const stripePromise = loadStripe(
  process.env.NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY || ''
);

// Types
interface Service {
  id: string;
  slug: string;
  name: string;
  category: string;
  type: string;
  short_description: string;
  pricing_type: 'fixed' | 'range' | 'custom';
  price_min?: number;
  price_max?: number;
  currency: string;
}

interface BillingInfo {
  company_name: string;
  vat_number: string;
  address: string;
  city: string;
  postal_code: string;
  country: string;
  email: string;
  phone: string;
}

interface CheckoutPageProps {
  params: {
    slug: string;
  };
}

export default function CheckoutPage({ params }: CheckoutPageProps) {
  const router = useRouter();
  const { isAuthenticated, user, isLoading: authLoading } = useAuth();

  const [service, setService] = useState<Service | null>(null);
  const [isLoadingService, setIsLoadingService] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [createdOrderId, setCreatedOrderId] = useState<string | null>(null);

  const [billingInfo, setBillingInfo] = useState<BillingInfo>({
    company_name: '',
    vat_number: '',
    address: '',
    city: '',
    postal_code: '',
    country: 'IT',
    email: user?.email || '',
    phone: '',
  });

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push(`/login?redirect=/servizi/${params.slug}/checkout`);
    }
  }, [authLoading, isAuthenticated, params.slug, router]);

  // Load service
  useEffect(() => {
    if (isAuthenticated) {
      loadService();
    }
  }, [isAuthenticated, params.slug]);

  // Update email when user loads
  useEffect(() => {
    if (user?.email) {
      setBillingInfo((prev) => ({ ...prev, email: user.email }));
    }
  }, [user]);

  const loadService = async () => {
    setIsLoadingService(true);
    setError(null);

    try {
      const response = await apiClient.get<Service>(
        `/services/by-slug/${params.slug}`
      );

      setService(response);

      // Check if service is available for purchase
      if (response.pricing_type === 'custom') {
        setError('Questo servizio richiede un preventivo personalizzato. Sarai reindirizzato.');
        setTimeout(() => {
          router.push(`/contatti?servizio=${params.slug}`);
        }, 3000);
      }
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoadingService(false);
    }
  };

  const calculateSubtotal = (): number => {
    if (!service || !service.price_min) return 0;
    return service.price_min;
  };

  const calculateTax = (subtotal: number): number => {
    return subtotal * 0.22; // IVA 22%
  };

  const calculateTotal = (): number => {
    const subtotal = calculateSubtotal();
    const tax = calculateTax(subtotal);
    return subtotal + tax;
  };

  const formatPrice = (amount: number): string => {
    return amount.toLocaleString('it-IT', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Validate billing info
      if (!billingInfo.company_name || !billingInfo.vat_number || !billingInfo.email) {
        throw new Error('Compilare tutti i campi obbligatori');
      }

      // Create order
      const orderPayload = {
        items: [
          {
            service_id: service!.id,
            quantity: 1,
            unit_price: service!.price_min,
          },
        ],
        notes: `Acquisto servizio: ${service!.name}`,
      };

      const orderResponse = await apiClient.post('/orders', orderPayload);
      const orderId = orderResponse.id;
      setCreatedOrderId(orderId);

      // Create Payment Intent
      const paymentResponse = await apiClient.post(
        `/orders/${orderId}/payment-intent`,
        {}
      );

      setClientSecret(paymentResponse.client_secret);
      setIsSubmitting(false);
    } catch (err) {
      setError(getErrorMessage(err));
      setIsSubmitting(false);
    }
  };

  const handlePaymentSuccess = () => {
    // Redirect to order confirmation
    if (createdOrderId) {
      router.push(`/ordini/${createdOrderId}?payment=success`);
    }
  };

  const handlePaymentError = (error: string) => {
    setError(`Errore pagamento: ${error}`);
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

      <main className="container py-12 max-w-6xl">
        {/* Back Button */}
        <div className="mb-6">
          <Link href={`/servizi/${params.slug}`}>
            <Button variant="ghost" size="sm">
              ← Torna al Servizio
            </Button>
          </Link>
        </div>

        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Checkout</h1>
          <p className="text-muted-foreground">
            Completa il tuo ordine per il servizio selezionato
          </p>
        </div>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isLoadingService && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento...</p>
          </div>
        )}

        {/* Checkout Form */}
        {!isLoadingService && service && (
          <form onSubmit={handleSubmit}>
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Left Column - Billing Info */}
              <div className="lg:col-span-2 space-y-6">
                {/* Billing Information */}
                <Card>
                  <CardHeader>
                    <CardTitle>Informazioni di Fatturazione</CardTitle>
                    <CardDescription>
                      Inserisci i dati per la fatturazione
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="company_name">
                          Ragione Sociale *
                        </Label>
                        <Input
                          id="company_name"
                          value={billingInfo.company_name}
                          onChange={(e) =>
                            setBillingInfo({ ...billingInfo, company_name: e.target.value })
                          }
                          required
                          placeholder="Nome Azienda S.r.l."
                        />
                      </div>

                      <div>
                        <Label htmlFor="vat_number">Partita IVA *</Label>
                        <Input
                          id="vat_number"
                          value={billingInfo.vat_number}
                          onChange={(e) =>
                            setBillingInfo({ ...billingInfo, vat_number: e.target.value })
                          }
                          required
                          placeholder="IT12345678901"
                        />
                      </div>
                    </div>

                    <div>
                      <Label htmlFor="address">Indirizzo *</Label>
                      <Input
                        id="address"
                        value={billingInfo.address}
                        onChange={(e) =>
                          setBillingInfo({ ...billingInfo, address: e.target.value })
                        }
                        required
                        placeholder="Via Roma, 123"
                      />
                    </div>

                    <div className="grid md:grid-cols-3 gap-4">
                      <div>
                        <Label htmlFor="city">Città *</Label>
                        <Input
                          id="city"
                          value={billingInfo.city}
                          onChange={(e) =>
                            setBillingInfo({ ...billingInfo, city: e.target.value })
                          }
                          required
                          placeholder="Milano"
                        />
                      </div>

                      <div>
                        <Label htmlFor="postal_code">CAP *</Label>
                        <Input
                          id="postal_code"
                          value={billingInfo.postal_code}
                          onChange={(e) =>
                            setBillingInfo({ ...billingInfo, postal_code: e.target.value })
                          }
                          required
                          placeholder="20100"
                        />
                      </div>

                      <div>
                        <Label htmlFor="country">Paese *</Label>
                        <Input
                          id="country"
                          value={billingInfo.country}
                          onChange={(e) =>
                            setBillingInfo({ ...billingInfo, country: e.target.value })
                          }
                          required
                          placeholder="IT"
                        />
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="email">Email *</Label>
                        <Input
                          id="email"
                          type="email"
                          value={billingInfo.email}
                          onChange={(e) =>
                            setBillingInfo({ ...billingInfo, email: e.target.value })
                          }
                          required
                          placeholder="contatti@azienda.it"
                        />
                      </div>

                      <div>
                        <Label htmlFor="phone">Telefono *</Label>
                        <Input
                          id="phone"
                          type="tel"
                          value={billingInfo.phone}
                          onChange={(e) =>
                            setBillingInfo({ ...billingInfo, phone: e.target.value })
                          }
                          required
                          placeholder="+39 02 1234567"
                        />
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Payment Method */}
                {!clientSecret ? (
                  <Card>
                    <CardHeader>
                      <CardTitle>Metodo di Pagamento</CardTitle>
                      <CardDescription>
                        Pagamento sicuro con carta di credito tramite Stripe
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center space-x-2 p-4 border rounded-lg bg-primary/5">
                        <span className="text-2xl">💳</span>
                        <div className="flex-1">
                          <div className="font-semibold">Carta di Credito/Debito</div>
                          <div className="text-sm text-muted-foreground">
                            Visa, Mastercard, American Express
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ) : (
                  <Card>
                    <CardHeader>
                      <CardTitle>Pagamento</CardTitle>
                      <CardDescription>
                        Inserisci i dati della tua carta per completare l'acquisto
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {clientSecret && (
                        <Elements
                          stripe={stripePromise}
                          options={{
                            clientSecret,
                            appearance: {
                              theme: 'stripe',
                            },
                          }}
                        >
                          <StripeCheckoutForm
                            orderId={createdOrderId!}
                            returnUrl={`${window.location.origin}/ordini/${createdOrderId}`}
                            onSuccess={handlePaymentSuccess}
                            onError={handlePaymentError}
                          />
                        </Elements>
                      )}
                    </CardContent>
                  </Card>
                )}
              </div>

              {/* Right Column - Order Summary */}
              <div className="lg:col-span-1">
                <div className="sticky top-24">
                  <Card>
                    <CardHeader>
                      <CardTitle>Riepilogo Ordine</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {/* Service Item */}
                      <div className="pb-4 border-b">
                        <div className="font-semibold mb-1">{service.name}</div>
                        <div className="text-sm text-muted-foreground mb-2">
                          {service.short_description}
                        </div>
                        <div className="text-sm">
                          <span className="text-muted-foreground">Quantità:</span> 1
                        </div>
                      </div>

                      {/* Price Breakdown */}
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">Subtotale</span>
                          <span>€{formatPrice(calculateSubtotal())}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-muted-foreground">IVA (22%)</span>
                          <span>€{formatPrice(calculateTax(calculateSubtotal()))}</span>
                        </div>
                        <div className="flex justify-between text-lg font-bold pt-2 border-t">
                          <span>Totale</span>
                          <span className="text-primary">€{formatPrice(calculateTotal())}</span>
                        </div>
                      </div>

                      {/* Submit Button - Only show if no clientSecret yet */}
                      {!clientSecret && (
                        <Button
                          type="submit"
                          className="w-full"
                          size="lg"
                          disabled={isSubmitting}
                        >
                          {isSubmitting ? 'Creazione ordine...' : 'Procedi al Pagamento'}
                        </Button>
                      )}

                      {/* Security Note */}
                      <div className="text-xs text-center text-muted-foreground pt-4 border-t">
                        <div className="flex items-center justify-center gap-2 mb-2">
                          <span>🔒</span>
                          <span className="font-semibold">Pagamento Sicuro</span>
                        </div>
                        <p>
                          I tuoi dati sono protetti con crittografia SSL e gestiti da Stripe
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </div>
          </form>
        )}
      </main>
    </>
  );
}
