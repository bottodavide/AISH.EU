/**
 * Public Use Cases Page
 * Descrizione: Pagina pubblica per visualizzare i casi d'uso
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Footer } from '@/components/Footer';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import {
  Building2,
  Heart,
  ShoppingCart,
  Factory,
  Laptop,
  ArrowRight,
  Loader2
} from 'lucide-react';

interface UseCase {
  id: string;
  title: string;
  slug: string;
  industry: string;
  icon: string | null;
  challenge_title: string;
  challenge_description: string;
  solution_title: string;
  solution_description: string;
  result_title: string;
  result_description: string;
}

// Icon mapping
const iconMap: Record<string, any> = {
  Building2,
  Heart,
  ShoppingCart,
  Factory,
  Laptop,
};

export default function CasiUsoPage() {
  const [useCases, setUseCases] = useState<UseCase[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadUseCases = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const response = await apiClient.get('/use-cases?page=1&page_size=100');
        setUseCases(response.use_cases || []);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setIsLoading(false);
      }
    };

    loadUseCases();
  }, []);

  const getIcon = (iconName: string | null) => {
    if (!iconName) return Building2;
    return iconMap[iconName] || Building2;
  };

  const getIndustryColor = (industry: string): string => {
    const colors: Record<string, string> = {
      Finance: 'bg-blue-100 text-blue-800',
      Sanità: 'bg-green-100 text-green-800',
      Retail: 'bg-purple-100 text-purple-800',
      'E-commerce': 'bg-pink-100 text-pink-800',
      Manufacturing: 'bg-orange-100 text-orange-800',
      'Industria 4.0': 'bg-cyan-100 text-cyan-800',
    };
    return colors[industry] || 'bg-gray-100 text-gray-800';
  };

  return (
    <>
      <Navigation />

      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-950">
        {/* Hero Section */}
        <section className="container py-16 md:py-24">
          <div className="max-w-4xl mx-auto text-center">
            <Badge variant="outline" className="mb-4">
              Success Stories
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Casi d'Uso Reali
            </h1>
            <p className="text-xl text-muted-foreground mb-8">
              Scopri come ho aiutato aziende di diversi settori a trasformare le sfide normative
              in opportunità di crescita sicura.
            </p>
          </div>
        </section>

        {/* Loading State */}
        {isLoading && (
          <section className="container py-12">
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
              <p className="text-muted-foreground">Caricamento casi d'uso...</p>
            </div>
          </section>
        )}

        {/* Error State */}
        {error && (
          <section className="container py-12">
            <div className="max-w-2xl mx-auto">
              <Card className="border-red-200 bg-red-50">
                <CardContent className="pt-6">
                  <p className="text-red-800 text-center">{error}</p>
                </CardContent>
              </Card>
            </div>
          </section>
        )}

        {/* Use Cases Grid */}
        {!isLoading && !error && useCases.length > 0 && (
          <section className="container pb-16">
            <div className="space-y-8">
              {useCases.map((useCase) => {
                const Icon = getIcon(useCase.icon);

                return (
                  <Card key={useCase.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                    <CardContent className="p-8">
                      <div className="grid md:grid-cols-[auto_1fr] gap-8">
                        {/* Icon Column */}
                        <div className="flex flex-col items-center md:items-start">
                          <div className="w-16 h-16 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                            <Icon className="h-8 w-8 text-primary" />
                          </div>
                          <Badge className={getIndustryColor(useCase.industry)}>
                            {useCase.industry}
                          </Badge>
                        </div>

                        {/* Content Column */}
                        <div>
                          {/* Title */}
                          <h3 className="text-2xl font-bold mb-6">{useCase.title}</h3>

                          {/* Three Columns: Challenge, Solution, Result */}
                          <div className="grid md:grid-cols-3 gap-8">
                            {/* LA SFIDA */}
                            <div>
                              <h4 className="text-sm font-semibold text-primary uppercase mb-3">
                                {useCase.challenge_title}
                              </h4>
                              <p className="text-sm text-muted-foreground leading-relaxed">
                                {useCase.challenge_description}
                              </p>
                            </div>

                            {/* LA SOLUZIONE */}
                            <div>
                              <h4 className="text-sm font-semibold text-primary uppercase mb-3">
                                {useCase.solution_title}
                              </h4>
                              <p className="text-sm text-muted-foreground leading-relaxed">
                                {useCase.solution_description}
                              </p>
                            </div>

                            {/* IL RISULTATO */}
                            <div>
                              <h4 className="text-sm font-semibold text-primary uppercase mb-3">
                                {useCase.result_title}
                              </h4>
                              <p className="text-sm text-muted-foreground leading-relaxed">
                                {useCase.result_description}
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </section>
        )}

        {/* Empty State */}
        {!isLoading && !error && useCases.length === 0 && (
          <section className="container py-12">
            <Card>
              <CardContent className="py-12 text-center">
                <p className="text-muted-foreground text-lg mb-4">
                  Nessun caso d'uso disponibile al momento.
                </p>
                <p className="text-sm text-muted-foreground">
                  Torna presto per scoprire i nostri success stories!
                </p>
              </CardContent>
            </Card>
          </section>
        )}

        {/* CTA Section */}
        <section className="container pb-24">
          <Card className="bg-gradient-to-r from-primary/10 to-primary/5 border-primary/20">
            <CardContent className="py-12 text-center">
              <h2 className="text-3xl font-bold mb-4">Hai una sfida simile?</h2>
              <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
                Ogni azienda è unica, ma i principi di sicurezza e compliance sono universali.
                Parliamo del tuo caso specifico.
              </p>
              <Link href="/contatti">
                <Button size="lg">
                  Discuti il tuo progetto
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </section>
      </main>

      <Footer />
    </>
  );
}
