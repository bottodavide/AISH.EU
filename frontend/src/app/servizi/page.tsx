/**
 * Servizi Listing Page
 * Descrizione: Lista servizi consulenza con filtri
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';

// Types
interface Service {
  id: string;
  slug: string;
  name: string;
  category: 'AI_COMPLIANCE' | 'CYBERSECURITY_NIS2' | 'TOOLKIT_FORMAZIONE';
  type: 'PACCHETTO_FISSO' | 'CUSTOM_QUOTE' | 'ABBONAMENTO';
  short_description: string;
  pricing_type: 'FIXED' | 'RANGE' | 'CUSTOM';
  price_min?: number;
  price_max?: number;
  currency: string;
  is_featured: boolean;
}

interface ServicesResponse {
  services: Service[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function ServiziPage() {
  const [services, setServices] = useState<Service[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Load services
  useEffect(() => {
    loadServices();
  }, [selectedCategory]);

  const loadServices = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      if (selectedCategory) {
        params.append('category', selectedCategory);
      }

      const response = await apiClient.get<ServicesResponse>(
        `/api/v1/services?${params.toString()}`
      );

      setServices(response.services);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (service: Service): string => {
    if (service.pricing_type === 'CUSTOM') {
      return 'Su preventivo';
    }

    if (service.pricing_type === 'RANGE' && service.price_min && service.price_max) {
      return `€${service.price_min} - €${service.price_max}`;
    }

    if (service.pricing_type === 'FIXED' && service.price_min) {
      return `€${service.price_min}`;
    }

    return 'Contattaci';
  };

  const getCategoryLabel = (category: string): string => {
    const labels: Record<string, string> = {
      AI_COMPLIANCE: 'AI & Compliance',
      CYBERSECURITY_NIS2: 'Cybersecurity & NIS2',
      TOOLKIT_FORMAZIONE: 'Toolkit & Formazione',
    };
    return labels[category] || category;
  };

  const getTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      PACCHETTO_FISSO: 'Pacchetto Fisso',
      CUSTOM_QUOTE: 'Su Misura',
      ABBONAMENTO: 'Abbonamento',
    };
    return labels[type] || type;
  };

  return (
    <>
      <Navigation />

      <main className="container py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">I Nostri Servizi</h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Soluzioni complete per integrare l'AI nella tua azienda in sicurezza e compliance
          </p>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap justify-center gap-4 mb-8">
          <Button
            variant={selectedCategory === null ? 'default' : 'outline'}
            onClick={() => setSelectedCategory(null)}
          >
            Tutti i Servizi
          </Button>
          <Button
            variant={selectedCategory === 'AI_COMPLIANCE' ? 'default' : 'outline'}
            onClick={() => setSelectedCategory('AI_COMPLIANCE')}
          >
            AI & Compliance
          </Button>
          <Button
            variant={selectedCategory === 'CYBERSECURITY_NIS2' ? 'default' : 'outline'}
            onClick={() => setSelectedCategory('CYBERSECURITY_NIS2')}
          >
            Cybersecurity & NIS2
          </Button>
          <Button
            variant={selectedCategory === 'TOOLKIT_FORMAZIONE' ? 'default' : 'outline'}
            onClick={() => setSelectedCategory('TOOLKIT_FORMAZIONE')}
          >
            Toolkit & Formazione
          </Button>
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
            <p className="text-muted-foreground">Caricamento servizi...</p>
          </div>
        )}

        {/* Services Grid */}
        {!isLoading && services.length > 0 && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {services.map((service) => (
              <Card key={service.id} className="flex flex-col">
                <CardHeader>
                  {service.is_featured && (
                    <div className="mb-2">
                      <span className="inline-block px-2 py-1 text-xs font-semibold rounded-full bg-primary/10 text-primary">
                        In Evidenza
                      </span>
                    </div>
                  )}
                  <div className="mb-2">
                    <span className="text-xs text-muted-foreground">
                      {getCategoryLabel(service.category)} • {getTypeLabel(service.type)}
                    </span>
                  </div>
                  <CardTitle className="text-xl">{service.name}</CardTitle>
                  <CardDescription>{service.short_description}</CardDescription>
                </CardHeader>
                <CardContent className="flex-grow">
                  <div className="text-2xl font-bold text-primary">
                    {formatPrice(service)}
                  </div>
                </CardContent>
                <CardFooter>
                  <Link href={`/servizi/${service.slug}`} className="w-full">
                    <Button className="w-full">Scopri di Più</Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}

        {/* Empty State */}
        {!isLoading && services.length === 0 && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg">
              Nessun servizio trovato
              {selectedCategory && ' in questa categoria'}.
            </p>
            {selectedCategory && (
              <Button
                variant="outline"
                className="mt-4"
                onClick={() => setSelectedCategory(null)}
              >
                Mostra Tutti i Servizi
              </Button>
            )}
          </div>
        )}

        {/* CTA Section */}
        <div className="mt-16 text-center bg-muted rounded-lg p-8">
          <h2 className="text-2xl font-bold mb-4">Non Trovi Quello Che Cerchi?</h2>
          <p className="text-muted-foreground mb-6 max-w-2xl mx-auto">
            Offriamo anche consulenze personalizzate. Contattaci per discutere le tue esigenze specifiche.
          </p>
          <Link href="/contatti">
            <Button size="lg">Richiedi Preventivo Personalizzato</Button>
          </Link>
        </div>
      </main>
    </>
  );
}
