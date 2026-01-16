/**
 * User Services Page
 * Descrizione: Servizi acquistati dall'utente
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
import { Loader2, Package, Calendar, CheckCircle2 } from 'lucide-react';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { formatDate } from '@/lib/utils';

interface UserService {
  id: string;
  order_id: string;
  service_name: string;
  status: string;
  purchased_at: string;
  expires_at?: string;
}

export default function MyServicesPage() {
  const { user } = useAuth();
  const [services, setServices] = useState<UserService[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadServices();
    }
  }, [user]);

  const loadServices = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // TODO: Create this endpoint in backend
      // For now, we'll show a message
      setServices([]);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
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
        <h1 className="text-3xl font-bold">I Miei Servizi</h1>
        <p className="text-muted-foreground mt-2">
          Servizi attivi e acquistati
        </p>
      </div>

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {services.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Package className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-xl font-semibold mb-2">Nessun servizio attivo</h3>
            <p className="text-muted-foreground text-center mb-6">
              Non hai ancora acquistato servizi
            </p>
            <Button asChild>
              <a href="/servizi">Scopri i Servizi</a>
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {services.map((service) => (
            <Card key={service.id}>
              <CardHeader>
                <CardTitle className="text-lg">{service.service_name}</CardTitle>
                <CardDescription>
                  Acquistato il {formatDate(service.purchased_at)}
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Stato</span>
                  <Badge variant="default" className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" />
                    Attivo
                  </Badge>
                </div>

                {service.expires_at && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Scadenza</span>
                    <span className="text-sm font-medium flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      {formatDate(service.expires_at)}
                    </span>
                  </div>
                )}

                <Button variant="outline" className="w-full">
                  Dettagli Servizio
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
