/**
 * Admin 404 Page
 * Descrizione: Pagina 404 personalizzata per l'area admin
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertCircle } from 'lucide-react';

export default function AdminNotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <Card className="max-w-md w-full">
        <CardHeader>
          <div className="flex items-center gap-3 mb-2">
            <AlertCircle className="h-8 w-8 text-destructive" />
            <CardTitle className="text-2xl">Pagina Non Trovata</CardTitle>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">
            La pagina amministrativa che stai cercando non esiste o è stata spostata.
          </p>

          <div className="flex flex-col gap-2">
            <Link href="/admin">
              <Button className="w-full">Torna alla Dashboard</Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="outline" className="w-full">Vai al Sito</Button>
            </Link>
          </div>

          <div className="text-xs text-muted-foreground pt-4 border-t">
            <p className="font-semibold mb-1">Errore: 404 - Not Found</p>
            <p>Se pensi che questa sia un errore, contatta il supporto tecnico.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
