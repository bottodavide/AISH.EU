/**
 * CookieInitializer Component
 * Descrizione: Inizializza le preferenze cookie all'avvio dell'app
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect } from 'react';
import { initializeCookiePreferences } from '@/lib/cookies';

export function CookieInitializer() {
  useEffect(() => {
    // Initialize cookie preferences on mount
    initializeCookiePreferences();
  }, []);

  return null; // This component doesn't render anything
}
