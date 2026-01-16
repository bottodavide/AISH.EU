/**
 * User Sidebar Component
 * Descrizione: Barra laterale per navigazione area utente
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  ShoppingCart,
  Shield,
  User,
  Home,
  FileText,
  Package,
} from 'lucide-react';

interface NavItem {
  title: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  description?: string;
}

const navItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Panoramica account',
  },
  {
    title: 'I Miei Ordini',
    href: '/dashboard/orders',
    icon: ShoppingCart,
    description: 'Ordini e fatture',
  },
  {
    title: 'Servizi Acquistati',
    href: '/dashboard/my-services',
    icon: Package,
    description: 'I tuoi servizi attivi',
  },
  {
    title: 'Sicurezza',
    href: '/dashboard/security',
    icon: Shield,
    description: 'Password e MFA',
  },
  {
    title: 'Profilo',
    href: '/dashboard/profile',
    icon: User,
    description: 'Dati personali',
  },
];

export function UserSidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r bg-background overflow-y-auto z-40">
      {/* Header */}
      <div className="p-6 border-b">
        <Link href="/dashboard">
          <h2 className="text-xl font-bold text-primary">La Mia Area</h2>
          <p className="text-xs text-muted-foreground mt-1">AI Strategy Hub</p>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="p-4 space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-start gap-3 px-3 py-2.5 rounded-lg transition-colors',
                'hover:bg-accent',
                isActive && 'bg-primary text-primary-foreground hover:bg-primary/90'
              )}
            >
              <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="font-medium text-sm">{item.title}</div>
                {item.description && (
                  <div
                    className={cn(
                      'text-xs mt-0.5',
                      isActive ? 'text-primary-foreground/80' : 'text-muted-foreground'
                    )}
                  >
                    {item.description}
                  </div>
                )}
              </div>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-muted/50">
        <Link
          href="/"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-accent transition-colors"
        >
          <Home className="h-4 w-4" />
          Torna al Sito
        </Link>
      </div>
    </aside>
  );
}
