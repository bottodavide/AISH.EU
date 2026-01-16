/**
 * Admin Sidebar Component
 * Descrizione: Barra laterale fissa per navigazione admin
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  Users,
  FileText,
  BookOpen,
  Tag,
  FolderOpen,
  ShoppingCart,
  Mail,
  Database,
  Settings,
  Package,
  Image as ImageIcon,
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
    href: '/admin',
    icon: LayoutDashboard,
    description: 'Statistiche e panoramica',
  },
  {
    title: 'Banner Homepage',
    href: '/admin/banners',
    icon: ImageIcon,
    description: 'Banner e sezioni',
  },
  {
    title: 'Utenti',
    href: '/admin/users',
    icon: Users,
    description: 'Gestione utenti',
  },
  {
    title: 'Articoli Blog',
    href: '/admin/blog',
    icon: FileText,
    description: 'Gestione post del blog',
  },
  {
    title: 'Categorie & Tag',
    href: '/admin/blog/categories',
    icon: FolderOpen,
    description: 'Categorie e tag del blog',
  },
  {
    title: 'Servizi',
    href: '/admin/services',
    icon: Package,
    description: 'Servizi consulenziali',
  },
  {
    title: 'Ordini',
    href: '/admin/orders',
    icon: ShoppingCart,
    description: 'Gestione ordini',
  },
  {
    title: 'Newsletter',
    href: '/admin/newsletter',
    icon: Mail,
    description: 'Iscritti newsletter',
  },
  {
    title: 'Knowledge Base',
    href: '/admin/knowledge-base',
    icon: Database,
    description: 'Gestione knowledge base',
  },
  // TODO: Implementare pagina settings
  // {
  //   title: 'Impostazioni',
  //   href: '/admin/settings',
  //   icon: Settings,
  //   description: 'Configurazione sistema',
  // },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 border-r bg-background overflow-y-auto">
      {/* Header */}
      <div className="p-6 border-b">
        <Link href="/admin">
          <h2 className="text-xl font-bold text-primary">Admin Panel</h2>
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
          href="/dashboard"
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-accent transition-colors"
        >
          <BookOpen className="h-4 w-4" />
          Torna al Sito
        </Link>
      </div>
    </aside>
  );
}
