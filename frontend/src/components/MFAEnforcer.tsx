/**
 * MFA Enforcer Component
 * Descrizione: Forza admin/editor ad abilitare MFA
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

/**
 * Component that enforces MFA for admin/editor roles
 * Redirects to /setup-mfa if user is admin/editor without MFA
 */
export default function MFAEnforcer({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isLoading } = useAuth();

  useEffect(() => {
    // Skip if still loading or no user
    if (isLoading || !user) return;

    // Skip if already on setup-mfa page
    if (pathname === '/setup-mfa') return;

    // Skip if already on login/register pages
    if (pathname === '/login' || pathname === '/register') return;

    // Check if MFA is required for this user role
    const requiresMFA = ['admin', 'super_admin', 'editor'].includes(user.role);

    // If MFA is required but not enabled, redirect to setup
    if (requiresMFA && !user.mfa_enabled) {
      console.log(`MFA required for role ${user.role}, redirecting to setup`);
      router.push('/setup-mfa');
    }
  }, [user, isLoading, pathname, router]);

  return <>{children}</>;
}
