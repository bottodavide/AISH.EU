/**
 * Dashboard Layout
 * Descrizione: Layout con sidebar per area utente
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

import { UserSidebar } from '@/components/UserSidebar';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen">
      <UserSidebar />
      <main className="flex-1 ml-64">
        {children}
      </main>
    </div>
  );
}
