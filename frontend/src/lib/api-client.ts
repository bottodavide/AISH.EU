/**
 * API Client
 * Descrizione: Client HTTP per comunicare con backend FastAPI
 * Autore: Claude per Davide
 * Data: 2026-01-15
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

// =============================================================================
// TYPES
// =============================================================================

export interface ApiError {
  detail: string;
  status: number;
  code?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: int;
  page: number;
  page_size: number;
  total_pages: number;
}

// =============================================================================
// API CLIENT CLASS
// =============================================================================

class ApiClient {
  private client: AxiosInstance;
  private accessToken: string | null = null;
  private refreshToken: string | null = null;

  constructor() {
    // Base URL dal env o default
    const baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

    // Crea axios instance
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - Aggiungi JWT token
    this.client.interceptors.request.use(
      (config) => {
        // Recupera token da localStorage se non presente in memoria
        if (!this.accessToken && typeof window !== 'undefined') {
          this.accessToken = localStorage.getItem('access_token');
        }

        // Aggiungi Authorization header se token presente
        if (this.accessToken) {
          config.headers.Authorization = `Bearer ${this.accessToken}`;
        }

        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - Gestisci 401 e refresh token
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        // Se 401 e non è già un retry, prova refresh token
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            // Recupera refresh token
            if (!this.refreshToken && typeof window !== 'undefined') {
              this.refreshToken = localStorage.getItem('refresh_token');
            }

            if (this.refreshToken) {
              // Richiedi nuovo access token
              const response = await axios.post(`${this.client.defaults.baseURL}/api/v1/auth/refresh`, {
                refresh_token: this.refreshToken,
              });

              const { access_token, refresh_token } = response.data;

              // Aggiorna tokens
              this.setTokens(access_token, refresh_token);

              // Retry original request con nuovo token
              originalRequest.headers!.Authorization = `Bearer ${access_token}`;
              return this.client(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed - clear tokens e redirect a login
            this.clearTokens();
            if (typeof window !== 'undefined') {
              window.location.href = '/login?session_expired=true';
            }
            return Promise.reject(refreshError);
          }
        }

        // Log errori per debugging (solo in development)
        if (process.env.NODE_ENV === 'development') {
          console.error('API Error:', {
            url: error.config?.url,
            method: error.config?.method,
            status: error.response?.status,
            data: error.response?.data,
          });
        }

        return Promise.reject(error);
      }
    );
  }

  // ===========================================================================
  // TOKEN MANAGEMENT
  // ===========================================================================

  /**
   * Imposta access e refresh tokens
   */
  setTokens(accessToken: string, refreshToken: string): void {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;

    if (typeof window !== 'undefined') {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  /**
   * Cancella tokens (logout)
   */
  clearTokens(): void {
    this.accessToken = null;
    this.refreshToken = null;

    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user');
    }
  }

  /**
   * Verifica se utente è autenticato
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    return !!localStorage.getItem('access_token');
  }

  // ===========================================================================
  // HTTP METHODS
  // ===========================================================================

  /**
   * GET request
   */
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url, config);
    return response.data;
  }

  /**
   * POST request
   */
  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data, config);
    return response.data;
  }

  /**
   * PUT request
   */
  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data, config);
    return response.data;
  }

  /**
   * PATCH request
   */
  async patch<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response: AxiosResponse<T> = await this.client.patch(url, data, config);
    return response.data;
  }

  /**
   * DELETE request
   */
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response: AxesResponse<T> = await this.client.delete(url, config);
    return response.data;
  }

  // ===========================================================================
  // FILE UPLOAD
  // ===========================================================================

  /**
   * Upload file (multipart/form-data)
   */
  async uploadFile<T>(
    url: string,
    file: File,
    additionalData?: Record<string, any>,
    onProgress?: (progress: number) => void
  ): Promise<T> {
    const formData = new FormData();
    formData.append('file', file);

    // Aggiungi eventuali dati aggiuntivi
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        formData.append(key, value);
      });
    }

    const response: AxiosResponse<T> = await this.client.post(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    return response.data;
  }
}

// =============================================================================
// SINGLETON INSTANCE
// =============================================================================

const apiClient = new ApiClient();

export default apiClient;
export { apiClient }; // Named export for convenience

// =============================================================================
// ERROR HANDLER HELPER
// =============================================================================

/**
 * Traduce messaggi tecnici in messaggi user-friendly
 */
function translateErrorMessage(message: string): string {
  // Validation errors comuni
  const translations: Record<string, string> = {
    'Input should be': 'Valore non valido',
    'Field required': 'Campo obbligatorio',
    'Invalid email': 'Email non valida',
    'String should have at least': 'Testo troppo corto',
    'String should have at most': 'Testo troppo lungo',
    'value is not a valid email': 'Email non valida',
    'Unauthorized': 'Accesso non autorizzato',
    'Not found': 'Risorsa non trovata',
    'Forbidden': 'Accesso negato',
  };

  // Cerca corrispondenza
  for (const [key, value] of Object.entries(translations)) {
    if (message.includes(key)) {
      return value;
    }
  }

  return message;
}

/**
 * Estrae messaggio errore da AxiosError
 */
/**
 * Controlla se un errore è un 404 (risorsa non trovata)
 */
export function isNotFoundError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    return error.response?.status === 404;
  }
  return false;
}

/**
 * Controlla se un errore è un errore di rete (server non raggiungibile)
 */
export function isNetworkError(error: unknown): boolean {
  if (axios.isAxiosError(error)) {
    // Network error: request sent but no response received
    return !!error.request && !error.response;
  }
  return false;
}

export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;
    const data = axiosError.response?.data;

    // Handle Pydantic validation errors (array of error objects)
    if (Array.isArray(data?.detail)) {
      const errorMessages = data.detail
        .map((err: any) => {
          if (typeof err === 'string') return translateErrorMessage(err);
          if (err.msg) return translateErrorMessage(err.msg);
          return 'Errore di validazione';
        })
        .filter((msg: string, index: number, self: string[]) => self.indexOf(msg) === index); // Remove duplicates

      // Se ci sono più errori simili, raggruppa
      if (errorMessages.length > 3) {
        return 'Alcuni campi contengono errori. Verifica i dati inseriti.';
      }

      return errorMessages.join('. ');
    }

    // Handle object detail
    if (typeof data?.detail === 'object' && data?.detail !== null) {
      return 'Errore nei dati forniti';
    }

    // Handle string detail
    if (typeof data?.detail === 'string') {
      return translateErrorMessage(data.detail);
    }

    // Handle specific HTTP status codes
    if (axiosError.response) {
      const status = axiosError.response.status;

      switch (status) {
        case 400:
          return 'I dati forniti non sono validi';
        case 401:
          return 'Accesso non autorizzato. Effettua il login.';
        case 403:
          return 'Non hai i permessi necessari per questa operazione';
        case 404:
          return 'Risorsa non trovata';
        case 409:
          return 'Operazione non possibile: conflitto con dati esistenti';
        case 422:
          return 'I dati forniti contengono errori di validazione';
        case 429:
          return 'Troppe richieste. Riprova tra qualche istante.';
        case 500:
          return 'Errore del server. Riprova più tardi.';
        case 503:
          return 'Servizio temporaneamente non disponibile';
        default:
          return `Si è verificato un errore (${status})`;
      }
    }

    // Network error
    if (axiosError.request) {
      return 'Impossibile connettersi al server. Verifica la tua connessione internet.';
    }
  }

  // Generic error
  if (error instanceof Error) {
    return translateErrorMessage(error.message);
  }

  return 'Si è verificato un errore imprevisto';
}
