/**
 * Stripe Checkout Form Component
 * Descrizione: Form pagamento con Stripe Elements
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState } from 'react';
import { useStripe, useElements, PaymentElement } from '@stripe/react-stripe-js';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface StripeCheckoutFormProps {
  orderId: string;
  returnUrl: string;
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export default function StripeCheckoutForm({
  orderId,
  returnUrl,
  onSuccess,
  onError,
}: StripeCheckoutFormProps) {
  const stripe = useStripe();
  const elements = useElements();

  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) {
      // Stripe.js hasn't loaded yet
      return;
    }

    setIsProcessing(true);
    setErrorMessage(null);

    try {
      // Confirm payment
      const { error } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: returnUrl,
        },
      });

      if (error) {
        // Payment failed
        const message = error.message || 'Si è verificato un errore durante il pagamento';
        setErrorMessage(message);
        if (onError) {
          onError(message);
        }
      } else {
        // Payment succeeded
        if (onSuccess) {
          onSuccess();
        }
      }
    } catch (err: any) {
      const message = err.message || 'Errore imprevisto durante il pagamento';
      setErrorMessage(message);
      if (onError) {
        onError(message);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Error Message */}
      {errorMessage && (
        <Alert variant="destructive">
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      {/* Payment Element */}
      <div className="p-4 border rounded-lg bg-white">
        <PaymentElement
          options={{
            layout: 'tabs',
          }}
        />
      </div>

      {/* Submit Button */}
      <Button
        type="submit"
        className="w-full"
        size="lg"
        disabled={!stripe || !elements || isProcessing}
      >
        {isProcessing ? (
          <div className="flex items-center gap-2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <span>Elaborazione pagamento...</span>
          </div>
        ) : (
          'Conferma Pagamento'
        )}
      </Button>

      {/* Security Note */}
      <div className="text-xs text-center text-muted-foreground">
        <div className="flex items-center justify-center gap-2 mb-1">
          <span>🔒</span>
          <span className="font-semibold">Pagamento Sicuro</span>
        </div>
        <p>I tuoi dati di pagamento sono protetti con crittografia SSL</p>
      </div>
    </form>
  );
}
