/**
 * Privacy Policy Page
 * Descrizione: Informativa privacy (GDPR compliance)
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

export default function PrivacyPage() {
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
        '/cms/pages/slug/privacy'
      );
      setPage(response);
    } catch (err: any) {
      // Se è 404, usa il contenuto fallback senza mostrare errore
      if (err.response?.status === 404) {
        setPage(null); // Mostra il contenuto fallback statico
      } else {
        // Altri errori (500, ecc.) vengono mostrati
        setError(getErrorMessage(err));
      }
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
          <h1>{page?.title || 'Privacy Policy'}</h1>

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

              <h2>1. Titolare del Trattamento</h2>
              <p>
                Il Titolare del trattamento è AI Strategy Hub, con sede in Italia.
                Email: info@aistrategyhub.eu
              </p>

              <h2>2. Tipologia di Dati Raccolti</h2>
              <p>I dati personali raccolti includono:</p>
              <ul>
                <li>Dati identificativi (nome, cognome, email)</li>
                <li>Dati di navigazione (cookie tecnici, analytics)</li>
                <li>Dati relativi ai servizi richiesti</li>
              </ul>

              <h2>3. Finalità del Trattamento</h2>
              <p>I dati vengono trattati per:</p>
              <ul>
                <li>Erogazione dei servizi richiesti</li>
                <li>Gestione delle richieste di contatto</li>
                <li>Adempimenti contrattuali e legali</li>
                <li>Miglioramento dei servizi offerti</li>
              </ul>

              <h2>4. Base Giuridica</h2>
              <p>
                Il trattamento dei dati si basa su: consenso dell'interessato,
                esecuzione di un contratto, adempimenti legali, interesse legittimo del titolare.
              </p>

              <h2>5. Conservazione dei Dati</h2>
              <p>
                I dati saranno conservati per il tempo necessario alle finalità per cui
                sono stati raccolti e secondo quanto previsto dalla normativa vigente.
              </p>

              <h2>6. Diritti dell'Interessato</h2>
              <p>Ai sensi del GDPR (Regolamento UE 2016/679), l'interessato ha diritto a:</p>
              <ul>
                <li>Accesso ai propri dati personali</li>
                <li>Rettifica e cancellazione dei dati</li>
                <li>Limitazione del trattamento</li>
                <li>Portabilità dei dati</li>
                <li>Opposizione al trattamento</li>
                <li>Revoca del consenso</li>
              </ul>

              <h2>7. Modalità di Esercizio dei Diritti</h2>
              <p>
                Per esercitare i propri diritti, l'interessato può contattarci all'indirizzo:
                info@aistrategyhub.eu
              </p>

              <h2>8. Sicurezza</h2>
              <p>
                Adottiamo misure di sicurezza tecniche e organizzative adeguate per proteggere
                i dati personali da accessi non autorizzati, perdita o distruzione.
              </p>

              <h2>9. Cookie</h2>
              <p>
                Per informazioni sull'uso dei cookie, consultare la nostra{' '}
                <a href="/cookie" className="text-primary hover:underline">
                  Cookie Policy
                </a>
                .
              </p>

              <h2>10. Modifiche</h2>
              <p>
                Ci riserviamo il diritto di modificare questa informativa. Le modifiche
                saranno pubblicate su questa pagina con indicazione della data di aggiornamento.
              </p>

              <h2>11. Contatti</h2>
              <p>
                Per qualsiasi domanda relativa a questa Privacy Policy, contattaci all'indirizzo:
                info@aistrategyhub.eu
              </p>
            </div>
          )}
        </div>
      </main>
    </>
  );
}
