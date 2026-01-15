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

// =============================================================================
// ERROR HANDLER HELPER
// =============================================================================

/**
 * Estrae messaggio errore da AxiosError
 */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;

    // Errore con detail dal backend
    if (axiosError.response?.data?.detail) {
      return axiosError.response.data.detail;
    }

    // Errore HTTP generico
    if (axiosError.response) {
      return `Error ${axiosError.response.status}: ${axiosError.response.statusText}`;
    }

    // Errore di rete
    if (axiosError.request) {
      return 'Network error: Unable to reach server';
    }
  }

  // Errore generico
  if (error instanceof Error) {
    return error.message;
  }

  return 'An unknown error occurred';
}
