/**
 * Error Handler Utility
 * Sistema centralizzato per gestione errori con redirect a pagina errore
 */

import { AxiosError } from 'axios';
import axios from 'axios';

export type ErrorCode =
  | 'UNKNOWN_ERROR'
  | 'NETWORK_ERROR'
  | 'AUTH_ERROR'
  | 'VALIDATION_ERROR'
  | 'PERMISSION_ERROR'
  | 'NOT_FOUND'
  | 'SERVER_ERROR'
  | 'RATE_LIMIT'
  | 'CHAT_ERROR'
  | 'UPLOAD_ERROR';

export interface ErrorInfo {
  code: ErrorCode;
  message: string;
  timestamp: string;
  path?: string;
  details?: string;
}

/**
 * Mappa status code HTTP a error code
 */
function mapHttpStatusToErrorCode(status: number): ErrorCode {
  const statusMap: Record<number, ErrorCode> = {
    400: 'VALIDATION_ERROR',
    401: 'AUTH_ERROR',
    403: 'PERMISSION_ERROR',
    404: 'NOT_FOUND',
    429: 'RATE_LIMIT',
    500: 'SERVER_ERROR',
    502: 'SERVER_ERROR',
    503: 'SERVER_ERROR',
    504: 'SERVER_ERROR',
  };

  return statusMap[status] || 'UNKNOWN_ERROR';
}

/**
 * Estrae informazioni da errore Axios
 */
function parseAxiosError(error: AxiosError): ErrorInfo {
  const timestamp = new Date().toISOString();
  const path = typeof window !== 'undefined' ? window.location.pathname : undefined;

  // Network error (no response)
  if (!error.response) {
    return {
      code: 'NETWORK_ERROR',
      message: 'Impossibile connettersi al server',
      timestamp,
      path,
      details: error.message,
    };
  }

  // HTTP error (with response)
  const status = error.response.status;
  const data = error.response.data as any;

  // Estrai messaggio errore
  let message = 'Si è verificato un errore';
  let details: string | undefined;

  if (typeof data?.detail === 'string') {
    message = data.detail;
  } else if (Array.isArray(data?.detail)) {
    // Pydantic validation errors
    message = data.detail.map((e: any) => e.msg).join(', ');
    details = JSON.stringify(data.detail, null, 2);
  } else if (typeof data?.detail === 'object') {
    message = JSON.stringify(data.detail);
    details = JSON.stringify(data.detail, null, 2);
  } else if (data?.message) {
    message = data.message;
  }

  return {
    code: mapHttpStatusToErrorCode(status),
    message,
    timestamp,
    path,
    details,
  };
}

/**
 * Invia report errore al backend per notifica email
 */
async function reportErrorToBackend(errorInfo: ErrorInfo, stackTrace?: string): Promise<void> {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Generate tracking ID
    const timestamp = new Date(errorInfo.timestamp);
    const dateStr = timestamp.toISOString().split('T')[0].replace(/-/g, '');
    const timeStr = timestamp.toISOString().split('T')[1].split('.')[0].replace(/:/g, '');
    const trackingId = `ERR-${errorInfo.code}-${dateStr}-${timeStr}`;

    await axios.post(
      `${apiUrl}/api/v1/errors/report`,
      {
        error_code: trackingId,
        error_message: errorInfo.message,
        error_details: errorInfo.details,
        stack_trace: stackTrace,
        request_path: errorInfo.path,
        user_agent: typeof window !== 'undefined' ? window.navigator.userAgent : undefined,
        timestamp: errorInfo.timestamp,
      },
      {
        timeout: 5000, // Short timeout - non-blocking
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );
  } catch (reportError) {
    // Silently fail - don't block user flow if reporting fails
    console.error('Failed to report error to backend:', reportError);
  }
}

/**
 * Redirect a pagina errore con parametri
 */
export function redirectToError(errorInfo: ErrorInfo): void {
  if (typeof window === 'undefined') return;

  const params = new URLSearchParams({
    code: errorInfo.code,
    message: errorInfo.message,
    timestamp: errorInfo.timestamp,
  });

  if (errorInfo.path) {
    params.append('path', errorInfo.path);
  }

  if (errorInfo.details) {
    // Limita lunghezza details per URL
    const truncatedDetails = errorInfo.details.slice(0, 500);
    params.append('details', truncatedDetails);
  }

  window.location.href = `/error?${params.toString()}`;
}

/**
 * Handler globale per errori Axios
 */
export function handleApiError(error: unknown, customCode?: ErrorCode): void {
  console.error('API Error:', error);

  let errorInfo: ErrorInfo;
  let stackTrace: string | undefined;

  if (error instanceof AxiosError) {
    errorInfo = parseAxiosError(error);
    stackTrace = error.stack;
  } else if (error instanceof Error) {
    errorInfo = {
      code: customCode || 'UNKNOWN_ERROR',
      message: error.message,
      timestamp: new Date().toISOString(),
      path: typeof window !== 'undefined' ? window.location.pathname : undefined,
      details: error.stack,
    };
    stackTrace = error.stack;
  } else {
    errorInfo = {
      code: customCode || 'UNKNOWN_ERROR',
      message: 'Si è verificato un errore imprevisto',
      timestamp: new Date().toISOString(),
      path: typeof window !== 'undefined' ? window.location.pathname : undefined,
    };
  }

  // Report error to backend (non-blocking)
  reportErrorToBackend(errorInfo, stackTrace);

  // Redirect to error page
  redirectToError(errorInfo);
}

/**
 * Handler per errori specifici con codice custom
 */
export function handleChatError(error: unknown): void {
  handleApiError(error, 'CHAT_ERROR');
}

export function handleUploadError(error: unknown): void {
  handleApiError(error, 'UPLOAD_ERROR');
}

export function handleAuthError(error: unknown): void {
  handleApiError(error, 'AUTH_ERROR');
}

/**
 * Try-catch wrapper con error handling automatico
 */
export async function withErrorHandler<T>(
  fn: () => Promise<T>,
  errorCode?: ErrorCode
): Promise<T | null> {
  try {
    return await fn();
  } catch (error) {
    handleApiError(error, errorCode);
    return null;
  }
}

/**
 * Mostra errore inline senza redirect (per form validation)
 */
export function getErrorMessage(error: unknown): string {
  if (error instanceof AxiosError) {
    const data = error.response?.data as any;

    if (typeof data?.detail === 'string') {
      return data.detail;
    } else if (Array.isArray(data?.detail)) {
      return data.detail.map((e: any) => e.msg).join(', ');
    } else if (typeof data?.detail === 'object') {
      return JSON.stringify(data.detail);
    } else if (data?.message) {
      return data.message;
    }

    return `Errore ${error.response?.status || 'sconosciuto'}`;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return 'Si è verificato un errore';
}
