/**
 * Admin Layout
 * Descrizione: Layout per tutte le pagine admin con sidebar fissa
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { AdminSidebar } from '@/components/AdminSidebar';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // DEBUG: Log user data in admin layout
    console.log('[AdminLayout] User:', user);
    console.log('[AdminLayout] User role:', user?.role);
    console.log('[AdminLayout] isAuthenticated:', isAuthenticated);
    console.log('[AdminLayout] isLoading:', isLoading);

    // Redirect non-authenticated users to login
    if (!isLoading && !isAuthenticated) {
      console.log('[AdminLayout] Redirecting to login - not authenticated');
      router.push('/login?redirect=/admin');
      return;
    }

    // Redirect non-admin users to dashboard
    if (!isLoading && isAuthenticated && user) {
      const isAdmin = user.role === 'admin' || user.role === 'super_admin';
      console.log('[AdminLayout] isAdmin check:', isAdmin);
      console.log('[AdminLayout] Checking role:', user.role, '=== admin?', user.role === 'admin', '|| === super_admin?', user.role === 'super_admin');

      if (!isAdmin) {
        console.log('[AdminLayout] Redirecting to dashboard - not admin');
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, user, router]);

  // Show loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  // Don't render until auth is confirmed
  if (!isAuthenticated || !user) {
    return null;
  }

  // Check if user is admin
  const isAdmin = user.role === 'admin' || user.role === 'super_admin';

  console.log('[AdminLayout] Final render check - isAdmin:', isAdmin);
  console.log('[AdminLayout] Final render check - user.role:', user.role);

  if (!isAdmin) {
    console.log('[AdminLayout] Not rendering - not admin');
    return null;
  }

  console.log('[AdminLayout] Rendering admin layout with sidebar');

  return (
    <div className="min-h-screen bg-background">
      <AdminSidebar />
      <div className="ml-64">
        <main className="p-8">{children}</main>
      </div>
    </div>
  );
}
