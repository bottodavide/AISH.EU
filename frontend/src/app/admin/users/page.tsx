/**
 * Admin Users Management Page
 * Descrizione: Gestione completa utenti
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';

// Types
interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'super_admin' | 'admin' | 'editor' | 'support' | 'customer' | 'guest';
  is_active: boolean;
  is_verified: boolean;
  mfa_enabled: boolean;
  created_at: string;
  last_login_at?: string;
}

interface UsersResponse {
  users: User[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export default function AdminUsersPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();

  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterRole, setFilterRole] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load users
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadUsers();
    }
  }, [isAuthenticated, isAdmin, currentPage, filterRole]);

  const loadUsers = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', '20');

      if (filterRole) {
        params.append('role', filterRole);
      }

      if (searchQuery) {
        params.append('search', searchQuery);
      }

      const response = await apiClient.get<UsersResponse>(
        `/admin/users?${params.toString()}`
      );

      setUsers(response.users);
      setTotalPages(response.total_pages);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    loadUsers();
  };

  const handleToggleActive = async (userId: string, currentStatus: boolean) => {
    if (!confirm(`Sei sicuro di voler ${currentStatus ? 'disattivare' : 'attivare'} questo utente?`)) {
      return;
    }

    try {
      await apiClient.put(`/admin/users/${userId}`, {
        is_active: !currentStatus,
      });
      await loadUsers();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const handleChangeRole = async (userId: string, userEmail: string) => {
    const newRole = prompt(
      `Cambia ruolo per ${userEmail}:\n\nRuoli disponibili:\n- admin\n- editor\n- customer\n- support\n- guest\n\nInserisci il nuovo ruolo:`
    );

    if (!newRole) return;

    const validRoles = ['super_admin', 'admin', 'editor', 'support', 'customer', 'guest'];
    const lowerRole = newRole.toLowerCase().replace(/\s+/g, '_');

    if (!validRoles.includes(lowerRole)) {
      alert('Ruolo non valido');
      return;
    }

    try {
      await apiClient.put(`/admin/users/${userId}`, {
        role: lowerRole,
      });
      await loadUsers();
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  const getRoleBadge = (role: string) => {
    const styles: Record<string, string> = {
      super_admin: 'bg-purple-100 text-purple-800',
      admin: 'bg-red-100 text-red-800',
      editor: 'bg-blue-100 text-blue-800',
      support: 'bg-yellow-100 text-yellow-800',
      customer: 'bg-green-100 text-green-800',
      guest: 'bg-gray-100 text-gray-800',
    };
    const labels: Record<string, string> = {
      super_admin: 'Super Admin',
      admin: 'Admin',
      editor: 'Editor',
      support: 'Support',
      customer: 'Cliente',
      guest: 'Ospite',
    };
    return (
      <span className={`text-xs px-2 py-1 rounded-full font-medium ${styles[role] || 'bg-gray-100 text-gray-800'}`}>
        {labels[role] || role}
      </span>
    );
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (authLoading || !isAuthenticated || !isAdmin) {
    return (
      <>
        <Navigation />
        <div className="container flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navigation />

      <main className="container py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold mb-2">Gestione Utenti</h1>
            <p className="text-muted-foreground">
              Visualizza e gestisci tutti gli utenti della piattaforma
            </p>
          </div>
        </div>

        {/* Filters & Search */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="flex flex-col md:flex-row gap-4">
              {/* Search */}
              <form onSubmit={handleSearch} className="flex-1 flex gap-2">
                <Input
                  type="search"
                  placeholder="Cerca utenti per email o nome..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1"
                />
                <Button type="submit">Cerca</Button>
              </form>

              {/* Role Filter */}
              <div className="flex gap-2">
                <Button
                  variant={filterRole === null ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterRole(null);
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Tutti
                </Button>
                <Button
                  variant={filterRole === 'admin' ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterRole('admin');
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Admin
                </Button>
                <Button
                  variant={filterRole === 'customer' ? 'default' : 'outline'}
                  onClick={() => {
                    setFilterRole('customer');
                    setCurrentPage(1);
                  }}
                  size="sm"
                >
                  Clienti
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error Alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Caricamento utenti...</p>
          </div>
        )}

        {/* Users Table */}
        {!isLoading && users.length > 0 && (
          <>
            <Card>
              <CardContent className="p-0">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-muted">
                      <tr>
                        <th className="text-left p-4 font-semibold">Utente</th>
                        <th className="text-left p-4 font-semibold">Ruolo</th>
                        <th className="text-center p-4 font-semibold">Status</th>
                        <th className="text-center p-4 font-semibold">Security</th>
                        <th className="text-center p-4 font-semibold">Registrato</th>
                        <th className="text-center p-4 font-semibold">Ultimo Accesso</th>
                        <th className="text-right p-4 font-semibold">Azioni</th>
                      </tr>
                    </thead>
                    <tbody>
                      {users.map((user) => (
                        <tr key={user.id} className="border-t hover:bg-muted/50">
                          <td className="p-4">
                            <div>
                              <div className="font-semibold">
                                {user.first_name} {user.last_name}
                              </div>
                              <div className="text-sm text-muted-foreground">{user.email}</div>
                            </div>
                          </td>
                          <td className="p-4">{getRoleBadge(user.role)}</td>
                          <td className="p-4 text-center">
                            <div className="flex flex-col gap-1">
                              <span
                                className={`text-xs px-2 py-1 rounded-full ${
                                  user.is_active
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-red-100 text-red-800'
                                }`}
                              >
                                {user.is_active ? 'Attivo' : 'Disattivato'}
                              </span>
                              {!user.is_verified && (
                                <span className="text-xs px-2 py-1 rounded-full bg-yellow-100 text-yellow-800">
                                  Non Verificato
                                </span>
                              )}
                            </div>
                          </td>
                          <td className="p-4 text-center">
                            {user.mfa_enabled ? (
                              <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800">
                                MFA Attivo
                              </span>
                            ) : (
                              <span className="text-xs px-2 py-1 rounded-full bg-gray-100 text-gray-800">
                                MFA Off
                              </span>
                            )}
                          </td>
                          <td className="p-4 text-center text-sm text-muted-foreground">
                            {formatDate(user.created_at)}
                          </td>
                          <td className="p-4 text-center text-sm text-muted-foreground">
                            {user.last_login_at ? formatDate(user.last_login_at) : 'Mai'}
                          </td>
                          <td className="p-4">
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => handleChangeRole(user.id, user.email)}
                              >
                                Cambia Ruolo
                              </Button>
                              <Button
                                variant={user.is_active ? 'destructive' : 'default'}
                                size="sm"
                                onClick={() => handleToggleActive(user.id, user.is_active)}
                              >
                                {user.is_active ? 'Disattiva' : 'Attiva'}
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex justify-center items-center gap-2 mt-6">
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                >
                  Precedente
                </Button>
                <span className="text-sm text-muted-foreground px-4">
                  Pagina {currentPage} di {totalPages}
                </span>
                <Button
                  variant="outline"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                >
                  Successiva
                </Button>
              </div>
            )}
          </>
        )}

        {/* Empty State */}
        {!isLoading && users.length === 0 && (
          <Card>
            <CardContent className="text-center py-12">
              <p className="text-muted-foreground text-lg">
                {searchQuery || filterRole
                  ? 'Nessun utente trovato con questi filtri'
                  : 'Nessun utente registrato'}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Back to Admin */}
        <div className="mt-8">
          <Link href="/admin">
            <Button variant="ghost">← Torna alla Dashboard Admin</Button>
          </Link>
        </div>
      </main>
    </>
  );
}
