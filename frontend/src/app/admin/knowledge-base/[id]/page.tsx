'use client';

import React, { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  ArrowLeft,
  FileText,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';

interface Chunk {
  id: string;
  document_id: string;
  chunk_index: number;
  chunk_text: string;
  token_count: number;
  chunk_metadata: Record<string, any>;
}

interface DocumentDetail {
  id: string;
  title: string;
  document_type: string;
  topic: string;
  description: string | null;
  source_url: string | null;
  author: string | null;
  file_size: number | null;
  chunk_count: number;
  processing_status: string;
  is_active: boolean;
  created_at: string;
  processed_at: string | null;
  chunks: Chunk[];
}

export default function KnowledgeBaseDetailPage() {
  const router = useRouter();
  const params = useParams();
  const documentId = params?.id as string;

  const [document, setDocument] = useState<DocumentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showChunks, setShowChunks] = useState(false);

  useEffect(() => {
    if (documentId) {
      loadDocument();
    }
  }, [documentId]);

  const loadDocument = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get<DocumentDetail>(
        `/knowledge-base/documents/${documentId}?include_chunks=true`
      );

      setDocument(response);
    } catch (err: any) {
      console.error('Error loading document:', err);
      setError(err.response?.data?.detail || 'Errore nel caricamento del documento');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string | null): string => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatFileSize = (bytes: number | null): string => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'FAILED':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'PROCESSING':
        return <RefreshCw className="h-5 w-5 animate-spin text-blue-500" />;
      case 'PENDING':
        return <Clock className="h-5 w-5 text-yellow-500" />;
      default:
        return <AlertCircle className="h-5 w-5 text-gray-500" />;
    }
  };

  const getTopicColor = (topic: string): string => {
    const colors: Record<string, string> = {
      AI: 'bg-blue-100 text-blue-800',
      GDPR: 'bg-purple-100 text-purple-800',
      NIS2: 'bg-orange-100 text-orange-800',
      CYBERSECURITY: 'bg-red-100 text-red-800',
      GENERAL: 'bg-gray-100 text-gray-800',
    };
    return colors[topic] || colors.GENERAL;
  };

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <RefreshCw className="mx-auto h-8 w-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">Caricamento...</p>
        </div>
      </div>
    );
  }

  if (error || !document) {
    return (
      <div className="space-y-4">
        <Button variant="ghost" onClick={() => router.push('/admin/knowledge-base')}>
          <ArrowLeft className="mr-2 h-4 w-4" />
          Torna alla lista
        </Button>
        <Alert variant="destructive">
          <AlertDescription>{error || 'Documento non trovato'}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <Button
          variant="ghost"
          onClick={() => router.push('/admin/knowledge-base')}
          className="mb-4"
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Torna alla lista
        </Button>

        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{document.title}</h1>
              {document.is_active ? (
                <Badge variant="default" className="flex items-center gap-1">
                  <CheckCircle className="h-3 w-3" />
                  Attivo
                </Badge>
              ) : (
                <Badge variant="outline" className="flex items-center gap-1">
                  <XCircle className="h-3 w-3" />
                  Inattivo
                </Badge>
              )}
            </div>
            {document.description && (
              <p className="text-muted-foreground">{document.description}</p>
            )}
          </div>
        </div>
      </div>

      {/* Document Info */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Left Column */}
        <div className="space-y-4 rounded-lg border p-6">
          <h2 className="text-lg font-semibold">Informazioni Documento</h2>

          <div className="space-y-3">
            <div>
              <div className="text-sm font-medium text-muted-foreground">Topic</div>
              <Badge className={getTopicColor(document.topic)}>{document.topic}</Badge>
            </div>

            <div>
              <div className="text-sm font-medium text-muted-foreground">Tipo</div>
              <div className="text-sm">{document.document_type}</div>
            </div>

            {document.author && (
              <div>
                <div className="text-sm font-medium text-muted-foreground">Autore</div>
                <div className="text-sm">{document.author}</div>
              </div>
            )}

            {document.source_url && (
              <div>
                <div className="text-sm font-medium text-muted-foreground">URL Sorgente</div>
                <a
                  href={document.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 text-sm text-primary hover:underline"
                >
                  {document.source_url}
                  <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            )}

            <div>
              <div className="text-sm font-medium text-muted-foreground">Dimensione File</div>
              <div className="text-sm">{formatFileSize(document.file_size)}</div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-4 rounded-lg border p-6">
          <h2 className="text-lg font-semibold">Stato Processing</h2>

          <div className="space-y-3">
            <div>
              <div className="text-sm font-medium text-muted-foreground">Stato</div>
              <div className="flex items-center gap-2 mt-1">
                {getStatusIcon(document.processing_status)}
                <span className="text-sm font-medium">{document.processing_status}</span>
              </div>
            </div>

            <div>
              <div className="text-sm font-medium text-muted-foreground">Numero Chunks</div>
              <div className="text-sm">{document.chunk_count}</div>
            </div>

            <div>
              <div className="text-sm font-medium text-muted-foreground">Data Creazione</div>
              <div className="text-sm">{formatDate(document.created_at)}</div>
            </div>

            <div>
              <div className="text-sm font-medium text-muted-foreground">Data Processing</div>
              <div className="text-sm">{formatDate(document.processed_at)}</div>
            </div>
          </div>

          {document.processing_status === 'FAILED' && (
            <Alert variant="destructive">
              <AlertDescription>
                Il processing è fallito. Verifica il contenuto del documento e riprova.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>

      {/* Chunks Section */}
      {document.chunk_count > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">
              Chunks ({document.chunks?.length || document.chunk_count})
            </h2>
            <Button
              variant="outline"
              onClick={() => setShowChunks(!showChunks)}
            >
              {showChunks ? 'Nascondi' : 'Mostra'} Chunks
            </Button>
          </div>

          {showChunks && document.chunks && document.chunks.length > 0 && (
            <div className="space-y-3">
              {document.chunks.map((chunk) => (
                <div key={chunk.id} className="rounded-lg border p-4">
                  <div className="mb-2 flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline">Chunk #{chunk.chunk_index}</Badge>
                      <span className="text-xs text-muted-foreground">
                        {chunk.token_count} tokens
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      ID: {chunk.id.substring(0, 8)}...
                    </span>
                  </div>
                  <div className="prose prose-sm max-w-none">
                    <p className="whitespace-pre-wrap text-sm">{chunk.chunk_text}</p>
                  </div>
                  {chunk.chunk_metadata && Object.keys(chunk.chunk_metadata).length > 0 && (
                    <div className="mt-2 rounded bg-muted p-2">
                      <div className="text-xs text-muted-foreground">
                        Metadata: {JSON.stringify(chunk.chunk_metadata)}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {showChunks && (!document.chunks || document.chunks.length === 0) && (
            <div className="rounded-lg border p-8 text-center text-muted-foreground">
              <FileText className="mx-auto mb-2 h-12 w-12 opacity-50" />
              <p>Nessun chunk disponibile</p>
            </div>
          )}
        </div>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-2">
        <Button
          variant="outline"
          onClick={() => router.push(`/admin/knowledge-base`)}
        >
          Chiudi
        </Button>
      </div>
    </div>
  );
}
