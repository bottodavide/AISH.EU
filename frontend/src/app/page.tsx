/**
 * Homepage
 * Descrizione: Landing page principale con hero e sezioni CTA
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Navigation } from '@/components/Navigation';
import { NewsletterForm } from '@/components/NewsletterForm';
import { Footer } from '@/components/Footer';
import { BannerHero } from '@/components/BannerHero';

export default function HomePage() {
  return (
    <>
      <Navigation />

      <main>
        {/* Dynamic Hero Banner */}
        <BannerHero />

        {/* Per Chi Section */}
        <section className="py-16 bg-background">
          <div className="container">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Per Chi Lavoriamo</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Supportiamo organizzazioni che vogliono innovare con l'AI mantenendo
                conformità normativa e sicurezza dei dati
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>PMI Innovative</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Piccole e medie imprese che vogliono implementare soluzioni AI
                    per migliorare efficienza e competitività
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Grandi Aziende</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Enterprise che necessitano di governance AI, compliance GDPR
                    e gestione rischi su larga scala
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>PA e Sanità</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">
                    Pubblica Amministrazione e settore sanitario con requisiti
                    stringenti di privacy e sicurezza dei dati
                  </p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Cosa Facciamo Section */}
        <section className="py-16 bg-muted/50">
          <div className="container">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Cosa Facciamo</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Servizi specializzati per l'adozione responsabile dell'AI
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="mb-4">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                    <span className="text-2xl">🤖</span>
                  </div>
                </div>
                <h3 className="text-xl font-semibold mb-2">AI Compliance</h3>
                <p className="text-muted-foreground">
                  Audit GDPR, AI Act readiness, valutazione rischi e conformità
                  normativa per sistemi di Intelligenza Artificiale
                </p>
              </div>

              <div className="text-center">
                <div className="mb-4">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                    <span className="text-2xl">🔒</span>
                  </div>
                </div>
                <h3 className="text-xl font-semibold mb-2">Cybersecurity & NIS2</h3>
                <p className="text-muted-foreground">
                  Assessment NIS2, penetration testing, vulnerability management
                  e implementazione controlli di sicurezza
                </p>
              </div>

              <div className="text-center">
                <div className="mb-4">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
                    <span className="text-2xl">📚</span>
                  </div>
                </div>
                <h3 className="text-xl font-semibold mb-2">Toolkit & Formazione</h3>
                <p className="text-muted-foreground">
                  Template documentali, checklist operative, guide pratiche e
                  corsi di formazione per il tuo team
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Come Lavoriamo Section */}
        <section className="py-16 bg-background">
          <div className="container">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold mb-4">Come Lavoriamo</h2>
              <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                Un approccio strutturato in 3 fasi
              </p>
            </div>

            <div className="max-w-4xl mx-auto space-y-8">
              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-xl">
                  1
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Assessment Iniziale</h3>
                  <p className="text-muted-foreground">
                    Analizziamo il tuo contesto: sistemi AI attuali, processi di gestione dati,
                    livello di conformità GDPR/NIS2, gap di sicurezza e opportunità di miglioramento
                  </p>
                </div>
              </div>

              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-xl">
                  2
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Strategia & Roadmap</h3>
                  <p className="text-muted-foreground">
                    Definiamo insieme un piano d'azione concreto: priorità di intervento,
                    timeline realistiche, responsabilità chiare e KPI misurabili
                  </p>
                </div>
              </div>

              <div className="flex gap-6 items-start">
                <div className="flex-shrink-0 w-12 h-12 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-xl">
                  3
                </div>
                <div>
                  <h3 className="text-xl font-semibold mb-2">Implementazione & Supporto</h3>
                  <p className="text-muted-foreground">
                    Ti affianchiamo nell'esecuzione: documentazione operativa, setup tecnico,
                    formazione team e supporto continuativo per mantenere la compliance nel tempo
                  </p>
                </div>
              </div>
            </div>

            <div className="text-center mt-12">
              <Link href="/servizi">
                <Button size="lg">Scopri Tutti i Servizi</Button>
              </Link>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-primary text-primary-foreground">
          <div className="container text-center">
            <h2 className="text-3xl font-bold mb-4">Pronto a Innovare in Sicurezza?</h2>
            <p className="text-lg mb-8 max-w-2xl mx-auto opacity-90">
              Richiedi una consulenza gratuita per valutare come integrare l'AI
              nella tua organizzazione nel rispetto delle normative
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <Link href="/contatti">
                <Button size="lg" variant="secondary">
                  Richiedi Consulenza
                </Button>
              </Link>
              <Link href="/blog">
                <Button size="lg" variant="outline" className="bg-transparent border-primary-foreground text-primary-foreground hover:bg-primary-foreground/10">
                  Leggi il Blog
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Newsletter Section */}
        <section className="py-16 bg-muted">
          <div className="container">
            <div className="max-w-2xl mx-auto text-center">
              <h2 className="text-3xl font-bold mb-4">
                Rimani Aggiornato
              </h2>
              <p className="text-lg text-muted-foreground mb-8">
                Iscriviti alla nostra newsletter per ricevere insights su AI, GDPR e Cybersecurity
              </p>
              <div className="flex justify-center">
                <NewsletterForm variant="compact" showUnsubscribe={true} />
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
