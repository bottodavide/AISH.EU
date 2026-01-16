/**
 * Terms of Service Page (Termini di Servizio)
 * Descrizione: Condizioni generali di servizio
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
  content_sections: any[];
}

export default function TermsPage() {
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
        '/cms/pages/slug/termini'
      );
      setPage(response);
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <>
        <Navigation />
        <main className="container py-12">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navigation />
      <main className="container py-12">
        <div className="max-w-4xl mx-auto prose prose-lg">
          <h1>{page?.title || 'Termini di Servizio'}</h1>

          {error && (
            <Alert variant="destructive" className="my-4">
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
          )}

          {page?.content_sections && page.content_sections.map((section: any, index: number) => (
            <div key={index}>
              {section.section_type === 'text' && (
                <div dangerouslySetInnerHTML={{ __html: section.content.html || section.content.text || '' }} />
              )}
            </div>
          ))}

          {/* Fallback content */}
          {(!page || !page.content_sections || page.content_sections.length === 0) && (
            <div>
              <p className="text-sm text-muted-foreground">
                Ultimo aggiornamento: 15 Gennaio 2026
              </p>

              <h2>1. Accettazione dei Termini</h2>
              <p>
                Utilizzando i servizi di AI Strategy Hub, l'utente accetta integralmente
                i presenti Termini di Servizio. Se non si accettano questi termini,
                si prega di non utilizzare i nostri servizi.
              </p>

              <h2>2. Descrizione dei Servizi</h2>
              <p>
                AI Strategy Hub offre servizi di consulenza in materia di:
              </p>
              <ul>
                <li>Intelligenza Artificiale e compliance normativa</li>
                <li>GDPR e protezione dei dati</li>
                <li>Cybersecurity e NIS2</li>
                <li>Formazione e toolkit operativi</li>
              </ul>

              <h2>3. Registrazione e Account</h2>
              <p>
                Per accedere ad alcuni servizi è necessario registrarsi e creare un account.
                L'utente è responsabile della sicurezza delle proprie credenziali e di tutte
                le attività svolte tramite il proprio account.
              </p>

              <h2>4. Obblighi dell'Utente</h2>
              <p>L'utente si impegna a:</p>
              <ul>
                <li>Fornire informazioni veritiere e aggiornate</li>
                <li>Utilizzare i servizi in modo lecito e conforme</li>
                <li>Non violare diritti di terzi</li>
                <li>Non compromettere la sicurezza dei sistemi</li>
              </ul>

              <h2>5. Servizi a Pagamento</h2>
              <p>
                Alcuni servizi sono soggetti a pagamento. Le condizioni economiche,
                le modalità di pagamento e le eventuali penali sono specificate nei
                singoli contratti di servizio.
              </p>

              <h2>6. Proprietà Intellettuale</h2>
              <p>
                Tutti i contenuti presenti sul sito (testi, immagini, loghi, software)
                sono di proprietà di AI Strategy Hub o dei rispettivi proprietari e
                sono protetti dalle leggi sulla proprietà intellettuale.
              </p>

              <h2>7. Limitazione di Responsabilità</h2>
              <p>
                AI Strategy Hub non è responsabile per danni indiretti, incidentali
                o consequenziali derivanti dall'utilizzo o dall'impossibilità di
                utilizzo dei servizi.
              </p>

              <h2>8. Modifiche ai Termini</h2>
              <p>
                Ci riserviamo il diritto di modificare questi Termini in qualsiasi momento.
                Le modifiche saranno pubblicate su questa pagina e l'uso continuato
                dei servizi costituisce accettazione delle modifiche.
              </p>

              <h2>9. Risoluzione</h2>
              <p>
                Ci riserviamo il diritto di sospendere o terminare l'accesso ai servizi
                in caso di violazione dei presenti Termini.
              </p>

              <h2>10. Legge Applicabile e Foro Competente</h2>
              <p>
                I presenti Termini sono regolati dalla legge italiana. Per qualsiasi
                controversia sarà competente il foro di [Città], Italia.
              </p>

              <h2>11. Contatti</h2>
              <p>
                Per domande sui Termini di Servizio, contattaci all'indirizzo:
                info@aistrategyhub.eu
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
