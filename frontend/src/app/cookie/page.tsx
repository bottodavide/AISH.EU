/**
 * Cookie Policy Page
 * Descrizione: Informativa sui cookie (GDPR compliance)
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import {
  getCookiePreferences,
  saveCookiePreferences,
  acceptAllCookies,
  rejectAllCookies,
  type CookiePreferences,
} from '@/lib/cookies';
import { Check, Settings } from 'lucide-react';

interface PageContent {
  id: string;
  slug: string;
  title: string;
  content_sections: any[];
}

export default function CookiePage() {
  const [page, setPage] = useState<PageContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    analytics: false,
    marketing: false,
    timestamp: Date.now(),
  });
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    loadPage();

    // Load current preferences
    const currentPrefs = getCookiePreferences();
    if (currentPrefs) {
      setPreferences(currentPrefs);
    }
  }, []);

  const loadPage = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<PageContent>(
        '/cms/pages/slug/cookie'
      );
      setPage(response);
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleTogglePreference = (category: 'analytics' | 'marketing') => {
    setPreferences((prev) => ({
      ...prev,
      [category]: !prev[category],
    }));
  };

  const handleSavePreferences = () => {
    saveCookiePreferences(preferences);
    setSuccess('Preferenze salvate con successo!');
    setTimeout(() => setSuccess(null), 3000);
  };

  const handleAcceptAll = () => {
    acceptAllCookies();
    setPreferences({
      necessary: true,
      analytics: true,
      marketing: true,
      timestamp: Date.now(),
    });
    setSuccess('Tutti i cookie accettati!');
    setTimeout(() => setSuccess(null), 3000);
  };

  const handleRejectAll = () => {
    rejectAllCookies();
    setPreferences({
      necessary: true,
      analytics: false,
      marketing: false,
      timestamp: Date.now(),
    });
    setSuccess('Cookie non necessari rifiutati!');
    setTimeout(() => setSuccess(null), 3000);
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
          <h1>{page?.title || 'Cookie Policy'}</h1>

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

              <h2>1. Cosa sono i Cookie</h2>
              <p>
                I cookie sono piccoli file di testo che vengono memorizzati sul tuo dispositivo
                quando visiti un sito web. Vengono utilizzati per migliorare la tua esperienza
                di navigazione e per fornire funzionalità specifiche.
              </p>

              <h2>2. Tipologie di Cookie Utilizzati</h2>

              <h3>Cookie Tecnici (Necessari)</h3>
              <p>
                Questi cookie sono essenziali per il corretto funzionamento del sito
                e non possono essere disabilitati.
              </p>
              <ul>
                <li><strong>Cookie di sessione:</strong> Mantengono la tua sessione di navigazione attiva</li>
                <li><strong>Cookie di autenticazione:</strong> Ti permettono di accedere all'area riservata</li>
                <li><strong>Cookie di sicurezza:</strong> Proteggono il sito da attacchi informatici</li>
              </ul>

              <h3>Cookie Analitici</h3>
              <p>
                Raccolgono informazioni anonime su come gli utenti utilizzano il sito,
                aiutandoci a migliorare i nostri servizi.
              </p>
              <ul>
                <li><strong>Google Analytics:</strong> Analisi del traffico e comportamento degli utenti</li>
              </ul>

              <h3>Cookie di Profilazione</h3>
              <p>
                Al momento non utilizziamo cookie di profilazione per pubblicità personalizzata.
              </p>

              <h2>3. Durata dei Cookie</h2>
              <p>I cookie possono essere:</p>
              <ul>
                <li><strong>Cookie di sessione:</strong> Vengono eliminati alla chiusura del browser</li>
                <li><strong>Cookie persistenti:</strong> Rimangono memorizzati per un periodo specifico (da 1 mese a 2 anni)</li>
              </ul>

              <h2>4. Cookie di Terze Parti</h2>
              <p>
                Alcuni cookie provengono da servizi di terze parti che utilizziamo:
              </p>
              <ul>
                <li>Google Analytics - Analisi del traffico</li>
                <li>Stripe - Gestione dei pagamenti (se applicabile)</li>
              </ul>

              <h2>5. Come Gestire i Cookie</h2>
              <p>
                Puoi gestire o disabilitare i cookie attraverso le impostazioni del tuo browser:
              </p>
              <ul>
                <li>
                  <strong>Chrome:</strong> Impostazioni → Privacy e sicurezza → Cookie e altri dati dei siti
                </li>
                <li>
                  <strong>Firefox:</strong> Impostazioni → Privacy e sicurezza → Cookie e dati dei siti web
                </li>
                <li>
                  <strong>Safari:</strong> Preferenze → Privacy → Gestisci i dati dei siti web
                </li>
                <li>
                  <strong>Edge:</strong> Impostazioni → Cookie e autorizzazioni del sito
                </li>
              </ul>

              <p className="text-sm bg-muted p-4 rounded-lg">
                <strong>Nota:</strong> Disabilitando i cookie tecnici, alcune funzionalità del sito
                potrebbero non funzionare correttamente.
              </p>

              <h2>6. Base Giuridica</h2>
              <p>
                L'utilizzo dei cookie tecnici si basa sull'interesse legittimo del titolare
                (art. 6, par. 1, lett. f del GDPR). Per i cookie analitici e di profilazione,
                richiediamo il consenso esplicito dell'utente.
              </p>

              <h2>7. Modifiche alla Cookie Policy</h2>
              <p>
                Ci riserviamo il diritto di modificare questa Cookie Policy.
                Le modifiche saranno pubblicate su questa pagina con indicazione
                della data di aggiornamento.
              </p>

              <h2>8. Contatti</h2>
              <p>
                Per domande sulla Cookie Policy o per esercitare i tuoi diritti
                relativi ai dati personali, contattaci all'indirizzo: info@aistrategyhub.eu
              </p>

              <p className="text-sm text-muted-foreground">
                Per maggiori informazioni sulla protezione dei dati personali,
                consulta la nostra{' '}
                <a href="/privacy" className="text-primary hover:underline">
                  Privacy Policy
                </a>
                .
              </p>
            </div>
          )}

          {/* Cookie Preferences Management */}
          <div className="mt-12 not-prose">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Gestisci Preferenze Cookie
                </CardTitle>
                <CardDescription>
                  Modifica le tue preferenze sui cookie in qualsiasi momento
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {success && (
                  <Alert className="border-green-500/50 text-green-700 dark:text-green-400">
                    <AlertDescription className="flex items-center gap-2">
                      <Check className="h-4 w-4" />
                      {success}
                    </AlertDescription>
                  </Alert>
                )}

                {/* Necessary Cookies */}
                <div className="flex items-start justify-between p-4 border rounded-lg bg-muted/50">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold">Cookie Necessari</h4>
                      <span className="text-xs px-2 py-0.5 bg-primary/20 text-primary rounded-full">
                        Sempre Attivi
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      Essenziali per il funzionamento del sito (autenticazione, sessione, sicurezza)
                    </p>
                  </div>
                  <div className="ml-4">
                    <div className="w-12 h-6 bg-primary rounded-full flex items-center justify-end px-1">
                      <div className="w-4 h-4 bg-white rounded-full" />
                    </div>
                  </div>
                </div>

                {/* Analytics Cookies */}
                <div className="flex items-start justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-semibold mb-1">Cookie Analytics</h4>
                    <p className="text-sm text-muted-foreground">
                      Ci aiutano a capire come gli utenti utilizzano il sito (Google Analytics)
                    </p>
                  </div>
                  <button
                    onClick={() => handleTogglePreference('analytics')}
                    className="ml-4"
                    type="button"
                  >
                    <div
                      className={`w-12 h-6 rounded-full flex items-center transition-colors ${
                        preferences.analytics
                          ? 'bg-primary justify-end'
                          : 'bg-gray-300 justify-start'
                      } px-1`}
                    >
                      <div className="w-4 h-4 bg-white rounded-full transition-transform" />
                    </div>
                  </button>
                </div>

                {/* Marketing Cookies */}
                <div className="flex items-start justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <h4 className="font-semibold mb-1">Cookie Marketing</h4>
                    <p className="text-sm text-muted-foreground">
                      Utilizzati per mostrare pubblicità personalizzate e misurare l'efficacia
                      delle campagne
                    </p>
                  </div>
                  <button
                    onClick={() => handleTogglePreference('marketing')}
                    className="ml-4"
                    type="button"
                  >
                    <div
                      className={`w-12 h-6 rounded-full flex items-center transition-colors ${
                        preferences.marketing
                          ? 'bg-primary justify-end'
                          : 'bg-gray-300 justify-start'
                      } px-1`}
                    >
                      <div className="w-4 h-4 bg-white rounded-full transition-transform" />
                    </div>
                  </button>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-2 pt-4">
                  <Button onClick={handleSavePreferences} size="lg" className="flex-1">
                    <Check className="h-4 w-4 mr-2" />
                    Salva Preferenze
                  </Button>
                  <Button onClick={handleAcceptAll} variant="outline" size="lg" className="flex-1">
                    Accetta Tutti
                  </Button>
                  <Button onClick={handleRejectAll} variant="ghost" size="lg" className="flex-1">
                    Rifiuta Tutti
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </>
  );
}
