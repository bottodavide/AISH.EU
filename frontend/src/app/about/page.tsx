/**
 * About Page (Chi Siamo)
 * Descrizione: Pagina Chi Siamo con contenuto dinamico da CMS
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';

interface PageContent {
  id: string;
  slug: string;
  title: string;
  page_type: string;
  content_sections: any[];
  status: string;
  is_published: boolean;
  meta_title?: string;
  meta_description?: string;
}

export default function AboutPage() {
  const [page, setPage] = useState<PageContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPage();
  }, []);

  const loadPage = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<PageContent>(
        '/api/v1/cms/pages/slug/about'
      );
      setPage(response);
    } catch (err: any) {
      // Mostra sempre errore inline con possibilità di retry
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <>
        <Navigation />
        <main className="container py-12">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento...</p>
          </div>
        </main>
      </>
    );
  }

  // Error state
  if (error) {
    return (
      <>
        <Navigation />
        <main className="container py-12">
          <div className="max-w-4xl mx-auto">
            <Alert variant="destructive" className="mb-8">
              <AlertDescription className="flex items-center justify-between">
                <span>{error}</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={loadPage}
                  className="ml-4 bg-white hover:bg-gray-100"
                >
                  Riprova
                </Button>
              </AlertDescription>
            </Alert>

            {/* Fallback content */}
            <div className="text-center py-12">
              <h1 className="text-4xl font-bold mb-4">Chi Siamo</h1>
              <p className="text-xl text-muted-foreground mb-8">
                Questa pagina è temporaneamente non disponibile. Per informazioni, contattaci all'indirizzo{' '}
                <a href="mailto:info@aistrategyhub.eu" className="text-primary hover:underline">
                  info@aistrategyhub.eu
                </a>
              </p>
            </div>
          </div>
        </main>
      </>
    );
  }

  // Success state with CMS content
  return (
    <>
      <Navigation />
      <main className="container py-12">
        <div className="max-w-4xl mx-auto">
          {/* Page Title */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold mb-4">{page?.title || 'Chi Siamo'}</h1>
          </div>

          {/* CMS Content Sections */}
          <div className="space-y-8 prose prose-lg max-w-none">
            {page?.content_sections && Array.isArray(page.content_sections) && page.content_sections.map((section: any, index: number) => (
              <div key={index} className="space-y-4">
                {section.section_type === 'text' && (
                  <div
                    dangerouslySetInnerHTML={{ __html: section.content.html || section.content.text || '' }}
                  />
                )}

                {section.section_type === 'hero' && (
                  <div className="text-center py-8 px-4 bg-muted rounded-lg">
                    {section.content.title && (
                      <h2 className="text-3xl font-bold mb-4">{section.content.title}</h2>
                    )}
                    {section.content.subtitle && (
                      <p className="text-xl text-muted-foreground">{section.content.subtitle}</p>
                    )}
                  </div>
                )}

                {section.section_type === 'image' && section.content.url && (
                  <div className="my-8">
                    <img
                      src={section.content.url}
                      alt={section.content.alt || ''}
                      className="w-full rounded-lg"
                    />
                    {section.content.caption && (
                      <p className="text-sm text-muted-foreground text-center mt-2">
                        {section.content.caption}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}

            {/* Fallback if no content sections */}
            {(!page?.content_sections || page.content_sections.length === 0) && (
              <div>
                <h2 className="text-2xl font-bold mb-4">AI Strategy Hub</h2>
                <p className="mb-4">
                  AI Strategy Hub è il tuo partner strategico per l'integrazione dell'Intelligenza Artificiale
                  in sicurezza e conformità normativa.
                </p>
                <p className="mb-4">
                  Offriamo consulenza specializzata in AI Compliance, GDPR, Cybersecurity e NIS2, aiutando
                  le aziende a innovare in modo responsabile e sicuro.
                </p>
                <p>
                  Il nostro approccio combina competenze tecniche avanzate con una profonda conoscenza
                  del panorama normativo europeo, garantendo soluzioni su misura per ogni esigenza.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </>
  );
}
