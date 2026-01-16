/**
 * ImageUpload Component
 * Descrizione: Componente per upload immagini con drag & drop, preview e validazione
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState, useRef, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Upload, X, Image as ImageIcon, Loader2 } from 'lucide-react';
import apiClient from '@/lib/api-client';

interface ImageUploadProps {
  /**
   * Callback quando upload completo con successo
   */
  onUploadSuccess: (imageUrl: string, metadata: ImageMetadata) => void;

  /**
   * Callback per errori
   */
  onError?: (error: string) => void;

  /**
   * Valore corrente (URL immagine) - per mostrare preview
   */
  value?: string;

  /**
   * Dimensioni massime consigliate
   */
  maxWidth?: number;
  maxHeight?: number;

  /**
   * Peso massimo in KB
   */
  maxSizeKB?: number;

  /**
   * Formati ammessi
   */
  acceptedFormats?: string[];

  /**
   * Label personalizzato
   */
  label?: string;

  /**
   * Mostra specifiche tecniche
   */
  showSpecs?: boolean;

  /**
   * Tipo di categoria per upload backend
   */
  category?: 'image' | 'avatar';

  /**
   * Se true, l'immagine è pubblica
   */
  isPublic?: boolean;
}

interface ImageMetadata {
  filename: string;
  url: string;
  size: number;
  width?: number;
  height?: number;
  mime_type: string;
}

export function ImageUpload({
  onUploadSuccess,
  onError,
  value,
  maxWidth = 1200,
  maxHeight = 630,
  maxSizeKB = 500,
  acceptedFormats = ['image/jpeg', 'image/png', 'image/webp'],
  label = 'Carica Immagine',
  showSpecs = true,
  category = 'image',
  isPublic = true,
}: ImageUploadProps) {
  const [preview, setPreview] = useState<string | null>(value || null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  /**
   * Valida file prima dell'upload
   */
  const validateFile = (file: File): string | null => {
    // Check formato
    if (!acceptedFormats.includes(file.type)) {
      return `Formato non supportato. Usa: ${acceptedFormats.map(f => f.split('/')[1].toUpperCase()).join(', ')}`;
    }

    // Check dimensione
    const sizeKB = file.size / 1024;
    if (sizeKB > maxSizeKB) {
      return `File troppo grande (${Math.round(sizeKB)} KB). Massimo: ${maxSizeKB} KB`;
    }

    return null;
  };

  /**
   * Valida dimensioni immagine
   */
  const validateImageDimensions = (file: File): Promise<string | null> => {
    return new Promise((resolve) => {
      const img = new Image();
      const url = URL.createObjectURL(file);

      img.onload = () => {
        URL.revokeObjectURL(url);

        if (img.width > maxWidth || img.height > maxHeight) {
          resolve(
            `Dimensioni troppo grandi (${img.width}x${img.height}px). Massimo: ${maxWidth}x${maxHeight}px`
          );
        } else {
          resolve(null);
        }
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        resolve('Impossibile leggere le dimensioni dell\'immagine');
      };

      img.src = url;
    });
  };

  /**
   * Upload file al backend
   */
  const uploadFile = async (file: File) => {
    setError(null);
    setIsUploading(true);

    try {
      // Validazione base
      const fileError = validateFile(file);
      if (fileError) {
        setError(fileError);
        if (onError) onError(fileError);
        return;
      }

      // Validazione dimensioni
      const dimensionError = await validateImageDimensions(file);
      if (dimensionError) {
        setError(dimensionError);
        if (onError) onError(dimensionError);
        return;
      }

      // Crea FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', category);
      formData.append('is_public', isPublic.toString());
      formData.append('description', `Uploaded via admin panel - ${file.name}`);

      // Upload
      const response = await apiClient.post<any>('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      // Crea preview locale
      const previewUrl = URL.createObjectURL(file);
      setPreview(previewUrl);

      // Callback con metadata
      const metadata: ImageMetadata = {
        filename: response.filename,
        url: response.url,
        size: response.file_size,
        width: response.image_metadata?.width,
        height: response.image_metadata?.height,
        mime_type: response.mime_type,
      };

      onUploadSuccess(response.url, metadata);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Errore durante l\'upload';
      setError(errorMsg);
      if (onError) onError(errorMsg);
    } finally {
      setIsUploading(false);
    }
  };

  /**
   * Handle file selection
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      uploadFile(file);
    }
  };

  /**
   * Handle drag & drop
   */
  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const file = e.dataTransfer.files?.[0];
    if (file) {
      uploadFile(file);
    }
  }, []);

  /**
   * Remove image
   */
  const handleRemove = () => {
    setPreview(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    // Notify parent con URL vuoto
    onUploadSuccess('', {
      filename: '',
      url: '',
      size: 0,
      mime_type: '',
    });
  };

  return (
    <div className="space-y-3">
      {/* Preview o Dropzone */}
      {preview ? (
        <div className="relative">
          <img
            src={preview}
            alt="Preview"
            className="w-full max-w-md rounded-lg border border-border"
          />
          <Button
            type="button"
            variant="destructive"
            size="sm"
            className="absolute top-2 right-2"
            onClick={handleRemove}
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
      ) : (
        <div
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
            ${isDragging ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'}
            ${isUploading ? 'opacity-50 pointer-events-none' : ''}
          `}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          {isUploading ? (
            <div className="flex flex-col items-center gap-3">
              <Loader2 className="h-12 w-12 text-primary animate-spin" />
              <p className="text-sm text-muted-foreground">Caricamento in corso...</p>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-3">
              <div className="p-3 rounded-full bg-primary/10">
                <Upload className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-sm font-medium">{label}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  Trascina un'immagine o clicca per selezionare
                </p>
              </div>
            </div>
          )}

          <input
            ref={fileInputRef}
            type="file"
            accept={acceptedFormats.join(',')}
            onChange={handleFileSelect}
            className="hidden"
          />
        </div>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Specifiche tecniche */}
      {showSpecs && !preview && (
        <div className="text-sm text-muted-foreground space-y-1 bg-muted/50 p-3 rounded-md">
          <p className="font-medium">Specifiche immagine:</p>
          <ul className="list-disc list-inside ml-2 space-y-0.5 text-xs">
            <li>
              <strong>Dimensioni massime:</strong> {maxWidth}x{maxHeight}px
            </li>
            <li>
              <strong>Formati ammessi:</strong>{' '}
              {acceptedFormats.map((f) => f.split('/')[1].toUpperCase()).join(', ')}
            </li>
            <li>
              <strong>Peso massimo:</strong> {maxSizeKB} KB
            </li>
            <li>
              <strong>Nota:</strong> L'immagine verrà validata automaticamente
            </li>
          </ul>
        </div>
      )}
    </div>
  );
}
