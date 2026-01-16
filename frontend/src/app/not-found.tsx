/**
 * 404 Not Found Page
 * Descrizione: Pagina personalizzata per errore 404
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Navigation } from '@/components/Navigation';
import { Footer } from '@/components/Footer';
import { FileQuestion, Home, ArrowLeft } from 'lucide-react';

export default function NotFound() {
  const router = useRouter();

  return (
    <>
      <Navigation />
      <main className="container flex items-center justify-center min-h-[calc(100vh-4rem)] py-12">
        <Card className="w-full max-w-lg text-center">
          <CardHeader className="space-y-4">
            <div className="flex justify-center">
              <div className="rounded-full bg-muted p-6">
                <FileQuestion className="h-16 w-16 text-muted-foreground" />
              </div>
            </div>
            <CardTitle className="text-4xl font-bold">404 - Pagina Non Trovata</CardTitle>
            <CardDescription className="text-base">
              La pagina che stai cercando non esiste o è stata spostata.
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <div className="text-sm text-muted-foreground space-y-2">
              <p>Cosa puoi fare:</p>
              <ul className="list-disc list-inside space-y-1 text-left max-w-md mx-auto">
                <li>Verifica l&apos;URL inserito</li>
                <li>Torna alla homepage</li>
                <li>Utilizza il menu di navigazione</li>
                <li>Contattaci se il problema persiste</li>
              </ul>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col sm:flex-row gap-3 justify-center">
            <Link href="/">
              <Button size="lg" className="w-full sm:w-auto">
                <Home className="mr-2 h-4 w-4" />
                Torna alla Homepage
              </Button>
            </Link>
            <Button
              size="lg"
              variant="outline"
              onClick={() => router.back()}
              className="w-full sm:w-auto"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Torna Indietro
            </Button>
          </CardFooter>
        </Card>
      </main>
      <Footer />
    </>
  );
}
