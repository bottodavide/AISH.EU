'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { redirectToError } from '@/lib/error-handler';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

/**
 * Error Boundary per catturare errori React
 * Automaticamente redirect a pagina errore centralizzata
 */
export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught error:', error, errorInfo);

    // Redirect a pagina errore centralizzata
    redirectToError({
      code: 'UNKNOWN_ERROR',
      message: error.message || 'Si è verificato un errore nell\'applicazione',
      timestamp: new Date().toISOString(),
      path: typeof window !== 'undefined' ? window.location.pathname : undefined,
      details: `${error.stack}\n\nComponent Stack:\n${errorInfo.componentStack}`,
    });
  }

  public render() {
    if (this.state.hasError) {
      // Mostra fallback opzionale mentre fa redirect
      return (
        this.props.fallback || (
          <div className="flex items-center justify-center min-h-screen">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-muted-foreground">Reindirizzamento...</p>
            </div>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
