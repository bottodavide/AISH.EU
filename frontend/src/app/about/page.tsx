/**
 * Public About Page (Chi Siamo)
 * Descrizione: Pagina Chi Siamo con layout sidebar + competenze
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { Navigation } from '@/components/Navigation';
import { Footer } from '@/components/Footer';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import {
  BookOpen,
  Users,
  Shield,
  Check,
  Loader2,
  Building2,
  Heart,
  ShoppingCart,
  Factory,
  Laptop,
} from 'lucide-react';

interface SpecializationArea {
  name: string;
  percentage: number;
  display_order: number;
}

interface CompetenceSection {
  title: string;
  icon: string;
  description: string;
  features: string[];
  display_order: number;
}

interface AboutPage {
  profile_name: string;
  profile_title: string;
  profile_description: string;
  profile_image_url: string | null;
  profile_badges: string[];
  specialization_areas: SpecializationArea[];
  competence_sections: CompetenceSection[];
}

// Icon mapping for competence sections
const iconMap: Record<string, any> = {
  BookOpen,
  Users,
  Shield,
  Building2,
  Heart,
  ShoppingCart,
  Factory,
  Laptop,
};

export default function AboutPage() {
  const [aboutData, setAboutData] = useState<AboutPage | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAboutPage();
  }, []);

  const loadAboutPage = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<AboutPage>('/about');
      setAboutData(response);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const getIcon = (iconName: string) => {
    return iconMap[iconName] || BookOpen;
  };

  // Loading state
  if (isLoading) {
    return (
      <>
        <Navigation />
        <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-950">
          <div className="container py-12">
            <div className="flex flex-col items-center justify-center py-12">
              <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
              <p className="text-muted-foreground">Caricamento...</p>
            </div>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  // Error state
  if (error || !aboutData) {
    return (
      <>
        <Navigation />
        <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-950">
          <div className="container py-12">
            <Alert variant="destructive" className="max-w-2xl mx-auto">
              <AlertDescription>
                {error || 'Pagina About non disponibile al momento.'}
              </AlertDescription>
            </Alert>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Navigation />

      <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-950">
        <div className="container py-12">
          <div className="grid lg:grid-cols-[400px_1fr] gap-8">
            {/* Sidebar Sinistra - Profilo */}
            <aside className="space-y-6">
              {/* Card Profilo */}
              <Card className="overflow-hidden">
                <div className="bg-gradient-to-br from-primary/10 to-primary/5 p-8">
                  {/* Immagine Profilo */}
                  {aboutData.profile_image_url && (
                    <div className="w-24 h-24 rounded-lg overflow-hidden mb-4 border-4 border-white shadow-lg">
                      <img
                        src={aboutData.profile_image_url}
                        alt={aboutData.profile_name}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}

                  {/* Nome e Titolo */}
                  <h2 className="text-2xl font-bold mb-1">{aboutData.profile_name}</h2>
                  <p className="text-primary font-medium mb-4">{aboutData.profile_title}</p>

                  {/* Descrizione */}
                  <p className="text-sm text-muted-foreground mb-4">
                    {aboutData.profile_description}
                  </p>

                  {/* Badges */}
                  {aboutData.profile_badges.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {aboutData.profile_badges.map((badge, index) => (
                        <Badge key={index} variant="secondary" className="bg-green-100 text-green-800">
                          {badge}
                        </Badge>
                      ))}
                    </div>
                  )}
                </div>
              </Card>

              {/* Card Aree di Specializzazione */}
              {aboutData.specialization_areas.length > 0 && (
                <Card>
                  <CardContent className="pt-6">
                    <h3 className="font-semibold text-lg mb-4">Aree di Specializzazione</h3>
                    <div className="space-y-4">
                      {aboutData.specialization_areas
                        .sort((a, b) => a.display_order - b.display_order)
                        .map((area, index) => (
                          <div key={index}>
                            <div className="flex justify-between mb-2">
                              <span className="text-sm font-medium">{area.name}</span>
                              <span className="text-sm font-semibold text-primary">
                                {area.percentage}%
                              </span>
                            </div>
                            <Progress value={area.percentage} className="h-2" />
                          </div>
                        ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </aside>

            {/* Contenuto Principale - Sezioni di Competenza */}
            <div className="space-y-8">
              {aboutData.competence_sections
                .sort((a, b) => a.display_order - b.display_order)
                .map((section, index) => {
                  const Icon = getIcon(section.icon);

                  return (
                    <Card key={index} className="overflow-hidden">
                      <CardContent className="p-8">
                        {/* Header Sezione */}
                        <div className="flex items-start gap-4 mb-6">
                          <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <Icon className="h-6 w-6 text-primary" />
                          </div>
                          <div className="flex-1">
                            <h3 className="text-2xl font-bold mb-2">{section.title}</h3>
                            <p className="text-muted-foreground leading-relaxed">
                              {section.description}
                            </p>
                          </div>
                        </div>

                        {/* Features Grid */}
                        {section.features.length > 0 && (
                          <div className="grid md:grid-cols-2 gap-4">
                            {section.features.map((feature, featureIndex) => (
                              <div
                                key={featureIndex}
                                className="flex items-start gap-3 p-4 rounded-lg bg-muted/50"
                              >
                                <Check className="h-5 w-5 text-primary mt-0.5 flex-shrink-0" />
                                <span className="text-sm leading-relaxed">{feature}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}

              {/* Empty State */}
              {aboutData.competence_sections.length === 0 && (
                <Card>
                  <CardContent className="py-12 text-center">
                    <p className="text-muted-foreground">
                      Nessuna sezione di competenza disponibile al momento.
                    </p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </>
  );
}
