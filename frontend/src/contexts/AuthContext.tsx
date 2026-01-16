/**
 * Auth Context
 * Descrizione: Context per gestire autenticazione e stato utente
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiClient, { getErrorMessage } from '../lib/api-client';

// =============================================================================
// TYPES
// =============================================================================

export type UserRole =
  | 'super_admin'
  | 'admin'
  | 'editor'
  | 'support'
  | 'customer'
  | 'guest';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  is_email_verified: boolean;
  mfa_enabled: boolean;
  last_login: string | null;
  created_at: string;
  // Dati profilo (opzionali)
  first_name?: string | null;
  last_name?: string | null;
  company_name?: string | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
  mfa_token?: string; // Optional MFA token for 2FA
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
  mfa_required?: boolean;
  mfa_session_token?: string;
}

export interface RegisterData {
  email: string;
  password: string;
  confirm_password: string;
  first_name?: string;
  last_name?: string;
  company_name?: string;
  accept_terms: boolean;
  accept_privacy: boolean;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginCredentials) => Promise<LoginResponse>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
  refreshUser: () => Promise<void>;
  hasRole: (roles: UserRole | UserRole[]) => boolean;
  isAdmin: boolean;
  isEditor: boolean;
  isCustomer: boolean;
}

// =============================================================================
// CONTEXT
// =============================================================================

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// =============================================================================
// PROVIDER
// =============================================================================

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Carica utente corrente dal backend
   */
  const loadUser = useCallback(async () => {
    try {
      // Verifica se c'è token
      if (!apiClient.isAuthenticated()) {
        setUser(null);
        setIsLoading(false);
        return;
      }

      // Recupera user info dal backend
      const userData = await apiClient.get<User>('/api/v1/users/me');
      setUser(userData);

      // Salva user in localStorage per persistence
      if (typeof window !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(userData));
      }
    } catch (error) {
      console.error('Failed to load user:', getErrorMessage(error));
      // Clear tokens se errore
      apiClient.clearTokens();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Effettua login
   */
  const login = useCallback(async (credentials: LoginCredentials): Promise<LoginResponse> => {
    try {
      const response = await apiClient.post<LoginResponse>('/api/v1/auth/login', credentials);

      // Salva tokens
      apiClient.setTokens(response.access_token, response.refresh_token);

      // Salva user
      setUser(response.user);
      if (typeof window !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(response.user));
      }

      return response;
    } catch (error: any) {
      // Check if MFA is required (403 error with mfa_required flag)
      if (error?.response?.status === 403 && error?.response?.data?.details?.mfa_required) {
        // Create a special response to indicate MFA is needed
        const mfaResponse: LoginResponse = {
          access_token: '',
          refresh_token: '',
          token_type: 'bearer',
          user: {} as any,
          mfa_required: true,
        };
        return mfaResponse;
      }

      throw new Error(getErrorMessage(error));
    }
  }, []);

  /**
   * Effettua logout
   */
  const logout = useCallback(() => {
    // Clear tokens e user
    apiClient.clearTokens();
    setUser(null);

    // Redirect a homepage
    if (typeof window !== 'undefined') {
      window.location.href = '/';
    }
  }, []);

  /**
   * Registra nuovo utente
   */
  const register = useCallback(async (data: RegisterData): Promise<void> => {
    try {
      await apiClient.post('/api/v1/auth/register', data);
      // Non fa auto-login, richiede email verification
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  }, []);

  /**
   * Refresh user data dal backend
   */
  const refreshUser = useCallback(async (): Promise<void> => {
    await loadUser();
  }, [loadUser]);

  /**
   * Verifica se utente ha uno o più ruoli
   */
  const hasRole = useCallback(
    (roles: UserRole | UserRole[]): boolean => {
      if (!user) return false;

      const roleArray = Array.isArray(roles) ? roles : [roles];
      return roleArray.includes(user.role);
    },
    [user]
  );

  // Computed properties per ruoli comuni
  const isAdmin = hasRole(['super_admin', 'admin']);
  const isEditor = hasRole(['super_admin', 'admin', 'editor']);
  const isCustomer = hasRole('customer');

  /**
   * Load user on mount
   */
  useEffect(() => {
    // Prova a recuperare user da localStorage per evitare flash
    if (typeof window !== 'undefined') {
      const cachedUser = localStorage.getItem('user');
      if (cachedUser) {
        try {
          setUser(JSON.parse(cachedUser));
        } catch (e) {
          console.error('Failed to parse cached user');
        }
      }
    }

    loadUser();
  }, [loadUser]);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    logout,
    register,
    refreshUser,
    hasRole,
    isAdmin,
    isEditor,
    isCustomer,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// =============================================================================
// HOOK
// =============================================================================

/**
 * Hook per accedere al AuthContext
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);

  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }

  return context;
}

// =============================================================================
// ROUTE PROTECTION HOC
// =============================================================================

/**
 * HOC per proteggere routes che richiedono autenticazione
 */
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  requiredRoles?: UserRole[]
) {
  return function AuthenticatedComponent(props: P) {
    const { user, isLoading } = useAuth();

    // Loading state
    if (isLoading) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
            <p className="text-muted-foreground">Loading...</p>
          </div>
        </div>
      );
    }

    // Not authenticated
    if (!user) {
      if (typeof window !== 'undefined') {
        window.location.href = '/login?redirect=' + encodeURIComponent(window.location.pathname);
      }
      return null;
    }

    // Check required roles
    if (requiredRoles && requiredRoles.length > 0) {
      const hasRequiredRole = requiredRoles.includes(user.role);
      if (!hasRequiredRole) {
        return (
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <h1 className="text-2xl font-bold mb-2">Access Denied</h1>
              <p className="text-muted-foreground">
                You don't have permission to access this page.
              </p>
            </div>
          </div>
        );
      }
    }

    return <Component {...props} />;
  };
}
