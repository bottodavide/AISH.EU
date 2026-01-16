/**
 * Footer Component
 * Descrizione: Footer globale del sito con link e social
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

import Link from 'next/link';
import { Linkedin } from 'lucide-react';

export function Footer() {
  return (
    <footer className="border-t py-8 bg-background">
      <div className="container">
        <div className="grid md:grid-cols-4 gap-8">
          {/* Brand Column */}
          <div>
            <h3 className="font-semibold mb-4">AI Strategy Hub</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Consulenza AI, GDPR e Cybersecurity per aziende che innovano responsabilmente
            </p>
            <div className="flex gap-3">
              <a
                href="https://www.linkedin.com/in/davidebotto/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="LinkedIn"
              >
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Services Column */}
          <div>
            <h4 className="font-semibold mb-4">Servizi</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/servizi" className="text-muted-foreground hover:text-foreground">
                  Tutti i Servizi
                </Link>
              </li>
              <li>
                <Link href="/servizi/ai-compliance" className="text-muted-foreground hover:text-foreground">
                  AI Compliance
                </Link>
              </li>
              <li>
                <Link href="/servizi/cybersecurity" className="text-muted-foreground hover:text-foreground">
                  Cybersecurity NIS2
                </Link>
              </li>
            </ul>
          </div>

          {/* Company Column */}
          <div>
            <h4 className="font-semibold mb-4">Azienda</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/about" className="text-muted-foreground hover:text-foreground">
                  Chi Siamo
                </Link>
              </li>
              <li>
                <Link href="/blog" className="text-muted-foreground hover:text-foreground">
                  Blog
                </Link>
              </li>
              <li>
                <Link href="/contatti" className="text-muted-foreground hover:text-foreground">
                  Contatti
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal Column */}
          <div>
            <h4 className="font-semibold mb-4">Legale</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/privacy" className="text-muted-foreground hover:text-foreground">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/termini" className="text-muted-foreground hover:text-foreground">
                  Termini di Servizio
                </Link>
              </li>
              <li>
                <Link href="/cookie" className="text-muted-foreground hover:text-foreground">
                  Cookie Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
          <p>&copy; {new Date().getFullYear()} AI Strategy Hub. Tutti i diritti riservati.</p>
        </div>
      </div>
    </footer>
  );
}
