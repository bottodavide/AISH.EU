/**
 * Service Detail Page
 * Descrizione: Pagina dettaglio singolo servizio
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface ServiceFeature {
  title: string;
  description: string;
  icon?: string;
}

interface ServiceIncluded {
  item: string;
}

interface ServiceContentSection {
  section_type: 'TEXT' | 'FEATURES' | 'PRICING' | 'FAQ';
  title: string;
  content?: string;
  features?: ServiceFeature[];
  items?: ServiceIncluded[];
}

interface Service {
  id: string;
  slug: string;
  name: string;
  category: 'ai_compliance' | 'cybersecurity_nis2' | 'toolkit_formazione';
  type: 'pacchetto_fisso' | 'custom_quote' | 'abbonamento';
  short_description: string;
  long_description: string;
  pricing_type: 'fixed' | 'range' | 'custom';
  price_min?: number;
  price_max?: number;
  currency: string;
  is_featured: boolean;
  is_published: boolean;
  content_sections: ServiceContentSection[];
  features: string[];
  deliverables: string[];
  target_audience: string[];
  duration_weeks?: number;
}

interface ServiceDetailPageProps {
  params: {
    slug: string;
  };
}

export default function ServiceDetailPage({ params }: ServiceDetailPageProps) {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [service, setService] = useState<Service | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load service
  useEffect(() => {
    loadService();
  }, [params.slug]);

  const loadService = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<Service>(
        `/services/by-slug/${params.slug}`
      );

      setService(response);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const formatPrice = (service: Service): string => {
    if (service.pricing_type === 'custom') {
      return 'Su preventivo';
    }

    if (service.pricing_type === 'range' && service.price_min && service.price_max) {
      return `€${service.price_min.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} - €${service.price_max.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }

    if (service.pricing_type === 'fixed' && service.price_min) {
      return `€${service.price_min.toLocaleString('it-IT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }

    return 'Contattaci';
  };

  const getCategoryLabel = (category: string): string => {
    const labels: Record<string, string> = {
      ai_compliance: 'AI & Compliance',
      cybersecurity_nis2: 'Cybersecurity & NIS2',
      toolkit_formazione: 'Toolkit & Formazione',
    };
    return labels[category] || category;
  };

  const getTypeLabel = (type: string): string => {
    const labels: Record<string, string> = {
      pacchetto_fisso: 'Pacchetto Fisso',
      custom_quote: 'Su Misura',
      abbonamento: 'Abbonamento',
    };
    return labels[type] || type;
  };

  const handlePurchase = () => {
    if (!isAuthenticated) {
      router.push(`/login?redirect=/servizi/${params.slug}/checkout`);
      return;
    }
    router.push(`/servizi/${params.slug}/checkout`);
  };

  const handleContactUs = () => {
    router.push(`/contatti?servizio=${params.slug}`);
  };

  return (
    <>
      <Navigation />

      <main className="container py-12">
        {/* Back Button */}
        <div className="mb-6">
          <Link href="/servizi">
            <Button variant="ghost" size="sm">
              ← Torna ai Servizi
            </Button>
          </Link>
        </div>

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento servizio...</p>
          </div>
        )}

        {/* Error Alert with Retry */}
        {error && (
          <Alert variant="destructive" className="mb-8">
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <Button
                variant="outline"
                size="sm"
                onClick={loadService}
                className="ml-4 bg-white hover:bg-gray-100"
              >
                Riprova
              </Button>
            </AlertDescription>
          </Alert>
        )}

        {/* Service Content */}
        {!isLoading && service && (
          <div className="grid lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-8">
              {/* Header */}
              <div>
                {service.is_featured && (
                  <div className="mb-4">
                    <span className="inline-block px-3 py-1 text-sm font-semibold rounded-full bg-primary/10 text-primary">
                      In Evidenza
                    </span>
                  </div>
                )}
                <div className="mb-2">
                  <span className="text-sm text-muted-foreground">
                    {getCategoryLabel(service.category)} • {getTypeLabel(service.type)}
                  </span>
                </div>
                <h1 className="text-4xl font-bold mb-4">{service.name}</h1>
                <p className="text-xl text-muted-foreground">{service.short_description}</p>
              </div>

              {/* Long Description */}
              <div className="prose max-w-none">
                <p className="text-lg">{service.long_description}</p>
              </div>

              {/* Features */}
              {service.features && service.features.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Cosa Include</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {service.features.map((feature, index) => (
                        <li key={index} className="flex items-start">
                          <span className="mr-2 text-primary">✓</span>
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Deliverables */}
              {service.deliverables && service.deliverables.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Cosa Riceverai</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {service.deliverables.map((deliverable, index) => (
                        <li key={index} className="flex items-start">
                          <span className="mr-2 text-primary">📦</span>
                          <span>{deliverable}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Target Audience */}
              {service.target_audience && service.target_audience.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Per Chi È Questo Servizio</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {service.target_audience.map((audience, index) => (
                        <li key={index} className="flex items-start">
                          <span className="mr-2 text-primary">👥</span>
                          <span>{audience}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Content Sections */}
              {service.content_sections && service.content_sections.length > 0 && (
                <div className="space-y-6">
                  {service.content_sections.map((section, index) => (
                    <Card key={index}>
                      <CardHeader>
                        <CardTitle>{section.title}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        {section.section_type === 'TEXT' && section.content && (
                          <div className="prose max-w-none">
                            <p>{section.content}</p>
                          </div>
                        )}
                        {section.section_type === 'FEATURES' && section.features && (
                          <div className="grid md:grid-cols-2 gap-4">
                            {section.features.map((feature, fIndex) => (
                              <div key={fIndex} className="flex items-start space-x-3">
                                {feature.icon && <span className="text-2xl">{feature.icon}</span>}
                                <div>
                                  <h4 className="font-semibold mb-1">{feature.title}</h4>
                                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                        {section.section_type === 'PRICING' && section.items && (
                          <ul className="space-y-2">
                            {section.items.map((item, iIndex) => (
                              <li key={iIndex} className="flex items-start">
                                <span className="mr-2 text-primary">•</span>
                                <span>{item.item}</span>
                              </li>
                            ))}
                          </ul>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </div>

            {/* Sidebar - Pricing & CTA */}
            <div className="lg:col-span-1">
              <div className="sticky top-24 space-y-6">
                {/* Pricing Card */}
                <Card>
                  <CardHeader>
                    <CardTitle>Prezzo</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-3xl font-bold text-primary">
                      {formatPrice(service)}
                    </div>

                    {service.duration_weeks && (
                      <div className="text-sm text-muted-foreground">
                        Durata stimata: {service.duration_weeks} settimane
                      </div>
                    )}

                    <div className="space-y-2">
                      {service.pricing_type === 'custom' ? (
                        <Button className="w-full" size="lg" onClick={handleContactUs}>
                          Richiedi Preventivo
                        </Button>
                      ) : (
                        <Button className="w-full" size="lg" onClick={handlePurchase}>
                          Acquista Ora
                        </Button>
                      )}

                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={handleContactUs}
                      >
                        Hai Domande? Contattaci
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Info Card */}
                <Card>
                  <CardHeader>
                    <CardTitle>Informazioni</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3 text-sm">
                    <div>
                      <div className="font-semibold mb-1">Categoria</div>
                      <div className="text-muted-foreground">
                        {getCategoryLabel(service.category)}
                      </div>
                    </div>
                    <div>
                      <div className="font-semibold mb-1">Tipo</div>
                      <div className="text-muted-foreground">
                        {getTypeLabel(service.type)}
                      </div>
                    </div>
                    {service.duration_weeks && (
                      <div>
                        <div className="font-semibold mb-1">Durata</div>
                        <div className="text-muted-foreground">
                          {service.duration_weeks} settimane
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Support Card */}
                <Card className="bg-muted">
                  <CardContent className="pt-6">
                    <div className="text-center space-y-2">
                      <div className="text-4xl mb-2">💬</div>
                      <h3 className="font-semibold">Hai bisogno di aiuto?</h3>
                      <p className="text-sm text-muted-foreground">
                        Il nostro team è disponibile per rispondere alle tue domande
                      </p>
                      <Link href="/contatti" className="block">
                        <Button variant="outline" size="sm" className="mt-2">
                          Contatta il Supporto
                        </Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>
        )}

        {/* Not Found State */}
        {!isLoading && !error && !service && (
          <div className="text-center py-12">
            <p className="text-muted-foreground text-lg mb-4">
              Servizio non trovato
            </p>
            <Link href="/servizi">
              <Button>Torna ai Servizi</Button>
            </Link>
          </div>
        )}
      </main>
    </>
  );
}
