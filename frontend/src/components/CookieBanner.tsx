/**
 * CookieBanner Component
 * Descrizione: Banner GDPR per consenso cookie con gestione preferenze
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { X, Cookie, Settings, Check } from 'lucide-react';
import {
  hasGivenConsent,
  acceptAllCookies,
  rejectAllCookies,
  saveCookiePreferences,
  getCookiePreferences,
  type CookiePreferences,
} from '@/lib/cookies';

export function CookieBanner() {
  const [isVisible, setIsVisible] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    necessary: true,
    analytics: false,
    marketing: false,
    timestamp: Date.now(),
  });

  useEffect(() => {
    // Check if user has already given consent
    const hasConsent = hasGivenConsent();
    setIsVisible(!hasConsent);

    // Load current preferences if they exist
    if (hasConsent) {
      const currentPrefs = getCookiePreferences();
      if (currentPrefs) {
        setPreferences(currentPrefs);
      }
    }
  }, []);

  const handleAcceptAll = () => {
    acceptAllCookies();
    setIsVisible(false);
  };

  const handleRejectAll = () => {
    rejectAllCookies();
    setIsVisible(false);
  };

  const handleSavePreferences = () => {
    saveCookiePreferences(preferences);
    setIsVisible(false);
  };

  const handleTogglePreference = (category: 'analytics' | 'marketing') => {
    setPreferences((prev) => ({
      ...prev,
      [category]: !prev[category],
    }));
  };

  if (!isVisible) {
    return null;
  }

  return (
    <>
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/50 z-[998] backdrop-blur-sm" />

      {/* Banner */}
      <div className="fixed bottom-0 left-0 right-0 z-[999] p-4 sm:p-6">
        <Card className="max-w-4xl mx-auto shadow-2xl border-2">
          <CardHeader className="pb-3">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Cookie className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-xl">Cookie e Privacy</CardTitle>
                  <CardDescription className="mt-1">
                    Utilizziamo cookie per migliorare la tua esperienza
                  </CardDescription>
                </div>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-4">
            {!showSettings ? (
              <>
                {/* Simple View */}
                <p className="text-sm text-muted-foreground">
                  Utilizziamo cookie essenziali per il funzionamento del sito e cookie opzionali
                  per analytics e marketing. Puoi scegliere quali categorie accettare.
                </p>

                <div className="text-sm text-muted-foreground">
                  Leggi la nostra{' '}
                  <Link href="/cookie" className="text-primary hover:underline font-medium">
                    Cookie Policy
                  </Link>{' '}
                  e{' '}
                  <Link href="/privacy" className="text-primary hover:underline font-medium">
                    Privacy Policy
                  </Link>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-2 pt-2">
                  <Button onClick={handleAcceptAll} size="lg" className="flex-1">
                    <Check className="h-4 w-4 mr-2" />
                    Accetta Tutti
                  </Button>
                  <Button
                    onClick={() => setShowSettings(true)}
                    variant="outline"
                    size="lg"
                    className="flex-1"
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Personalizza
                  </Button>
                  <Button
                    onClick={handleRejectAll}
                    variant="ghost"
                    size="lg"
                    className="flex-1"
                  >
                    Rifiuta Tutto
                  </Button>
                </div>
              </>
            ) : (
              <>
                {/* Settings View */}
                <div className="space-y-4">
                  <p className="text-sm text-muted-foreground">
                    Gestisci le tue preferenze cookie. I cookie necessari sono sempre attivi.
                  </p>

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
                </div>

                {/* Settings Actions */}
                <div className="flex flex-col sm:flex-row gap-2 pt-2">
                  <Button onClick={handleSavePreferences} size="lg" className="flex-1">
                    <Check className="h-4 w-4 mr-2" />
                    Salva Preferenze
                  </Button>
                  <Button
                    onClick={() => setShowSettings(false)}
                    variant="outline"
                    size="lg"
                    className="flex-1"
                  >
                    Indietro
                  </Button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </>
  );
}
