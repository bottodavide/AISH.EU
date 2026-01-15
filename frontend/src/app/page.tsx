/**
 * Homepage - AI Strategy Hub
 * Landing page principale del sito
 */

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center space-y-6">
        <h1 className="text-6xl font-bold tracking-tight">
          AI Strategy Hub
        </h1>

        <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
          Consulenza AI, GDPR e Cybersecurity
        </p>

        <div className="mt-8 flex gap-4 justify-center">
          <a
            href="/servizi"
            className="inline-flex items-center justify-center rounded-md bg-primary px-8 py-3 text-sm font-medium text-primary-foreground shadow transition-colors hover:bg-primary/90 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
          >
            Esplora Servizi
          </a>

          <a
            href="/contatti"
            className="inline-flex items-center justify-center rounded-md border border-input bg-background px-8 py-3 text-sm font-medium shadow-sm transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50"
          >
            Contattaci
          </a>
        </div>

        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
            <h3 className="text-lg font-semibold mb-2">AI & Compliance</h3>
            <p className="text-sm text-muted-foreground">
              Implementa AI in modo sicuro e conforme a GDPR e normative europee
            </p>
          </div>

          <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Cybersecurity & NIS2</h3>
            <p className="text-sm text-muted-foreground">
              Proteggi la tua infrastruttura e rispetta i requisiti NIS2
            </p>
          </div>

          <div className="rounded-lg border bg-card p-6 text-card-foreground shadow-sm">
            <h3 className="text-lg font-semibold mb-2">Toolkit & Formazione</h3>
            <p className="text-sm text-muted-foreground">
              Checklist operative, audit tools e formazione per il tuo team
            </p>
          </div>
        </div>

        <p className="mt-12 text-sm text-muted-foreground">
          🚧 Sito in costruzione - Coming soon! 🚧
        </p>
      </div>
    </main>
  );
}
