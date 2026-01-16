'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Navigation } from '@/components/Navigation';
import {
  FileText,
  Plus,
  Search,
  Filter,
  Trash2,
  Eye,
  RefreshCw,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  FileUp,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { apiClient } from '@/lib/api-client';

interface Document {
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
}

interface DocumentsResponse {
  documents: Document[];
  total: number;
  page: number;
  page_size: number;
}

export default function KnowledgeBasePage() {
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTopic, setFilterTopic] = useState<string>('');
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [filterActive, setFilterActive] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [processingDocId, setProcessingDocId] = useState<string | null>(null);

  const topics = ['AI', 'GDPR', 'NIS2', 'CYBERSECURITY', 'GENERAL'];
  const statuses = ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED'];

  useEffect(() => {
    loadDocuments();
  }, [currentPage, filterTopic, filterStatus, filterActive, searchQuery]);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams();
      params.append('page', currentPage.toString());
      params.append('page_size', '20');

      if (searchQuery) params.append('search', searchQuery);
      if (filterTopic) params.append('topic', filterTopic);
      if (filterStatus) params.append('status', filterStatus);
      if (filterActive) params.append('is_active', filterActive);

      const response = await apiClient.get<DocumentsResponse>(
        `/knowledge-base/documents?${params.toString()}`
      );

      setDocuments(response.documents);
      setTotalPages(Math.ceil(response.total / response.page_size));
    } catch (err: any) {
      console.error('Error loading documents:', err);
      setError(err.response?.data?.detail || 'Errore nel caricamento dei documenti');
    } finally {
      setLoading(false);
    }
  };

  const processDocument = async (documentId: string) => {
    if (!confirm('Vuoi processare questo documento e generare gli embeddings?')) return;

    try {
      setProcessingDocId(documentId);
      await apiClient.post(`/knowledge-base/documents/${documentId}/process`, {});
      await loadDocuments();
      alert('Documento processato con successo!');
    } catch (err: any) {
      console.error('Error processing document:', err);
      alert(err.response?.data?.detail || 'Errore nel processing del documento');
    } finally {
      setProcessingDocId(null);
    }
  };

  const toggleActive = async (documentId: string) => {
    try {
      await apiClient.patch(`/knowledge-base/documents/${documentId}/toggle-active`, {});
      await loadDocuments();
    } catch (err: any) {
      console.error('Error toggling active:', err);
      alert(err.response?.data?.detail || 'Errore nel cambio stato');
    }
  };

  const deleteDocument = async (documentId: string, title: string) => {
    if (!confirm(`Sei sicuro di voler eliminare "${title}"?\n\nQuesta azione è irreversibile e cancellerà anche tutti i chunk.`)) {
      return;
    }

    try {
      await apiClient.delete(`/knowledge-base/documents/${documentId}`);
      await loadDocuments();
    } catch (err: any) {
      console.error('Error deleting document:', err);
      alert(err.response?.data?.detail || 'Errore nell\'eliminazione');
    }
  };

  const formatFileSize = (bytes: number | null): string => {
    if (!bytes) return 'N/A';
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    return `${(kb / 1024).toFixed(1)} MB`;
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('it-IT', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'FAILED':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'PROCESSING':
        return <RefreshCw className="h-4 w-4 animate-spin text-blue-500" />;
      case 'PENDING':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
      COMPLETED: 'default',
      FAILED: 'destructive',
      PROCESSING: 'secondary',
      PENDING: 'outline',
    };

    return (
      <Badge variant={variants[status] || 'outline'} className="flex items-center gap-1">
        {getStatusIcon(status)}
        {status}
      </Badge>
    );
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

  if (loading && documents.length === 0) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <RefreshCw className="mx-auto h-8 w-8 animate-spin text-primary" />
          <p className="mt-2 text-sm text-muted-foreground">Caricamento...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Navigation />

      <main className="container py-12">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold">Knowledge Base</h1>
              <p className="text-muted-foreground">
                Gestisci i documenti della knowledge base per il RAG system
              </p>
            </div>
        <Button onClick={() => router.push('/admin/knowledge-base/new')}>
          <Plus className="mr-2 h-4 w-4" />
          Nuovo Documento
        </Button>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-4">
        <div className="flex-1 min-w-[300px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              type="search"
              placeholder="Cerca per titolo o descrizione..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </div>

        <select
          value={filterTopic}
          onChange={(e) => setFilterTopic(e.target.value)}
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">Tutti i topic</option>
          {topics.map((topic) => (
            <option key={topic} value={topic}>
              {topic}
            </option>
          ))}
        </select>

        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">Tutti gli stati</option>
          {statuses.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>

        <select
          value={filterActive}
          onChange={(e) => setFilterActive(e.target.value)}
          className="rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">Attivi e Inattivi</option>
          <option value="true">Solo Attivi</option>
          <option value="false">Solo Inattivi</option>
        </select>

        {(searchQuery || filterTopic || filterStatus || filterActive) && (
          <Button
            variant="outline"
            onClick={() => {
              setSearchQuery('');
              setFilterTopic('');
              setFilterStatus('');
              setFilterActive('');
            }}
          >
            Reset Filtri
          </Button>
        )}
      </div>

      {/* Documents Table */}
      <div className="rounded-lg border">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="border-b bg-muted/50">
              <tr>
                <th className="p-4 text-left text-sm font-medium">Documento</th>
                <th className="p-4 text-left text-sm font-medium">Topic</th>
                <th className="p-4 text-left text-sm font-medium">Tipo</th>
                <th className="p-4 text-left text-sm font-medium">Stato</th>
                <th className="p-4 text-left text-sm font-medium">Chunks</th>
                <th className="p-4 text-left text-sm font-medium">Dimensione</th>
                <th className="p-4 text-left text-sm font-medium">Data</th>
                <th className="p-4 text-left text-sm font-medium">Azioni</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {documents.length === 0 ? (
                <tr>
                  <td colSpan={8} className="p-8 text-center text-muted-foreground">
                    <FileText className="mx-auto mb-2 h-12 w-12 opacity-50" />
                    <p>Nessun documento trovato</p>
                    <Button
                      variant="link"
                      onClick={() => router.push('/admin/knowledge-base/new')}
                      className="mt-2"
                    >
                      Aggiungi il primo documento
                    </Button>
                  </td>
                </tr>
              ) : (
                documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-muted/50">
                    <td className="p-4">
                      <div className="flex items-start gap-2">
                        <FileText className="mt-1 h-4 w-4 text-muted-foreground" />
                        <div>
                          <div className="font-medium">{doc.title}</div>
                          {doc.description && (
                            <div className="text-xs text-muted-foreground line-clamp-1">
                              {doc.description}
                            </div>
                          )}
                          {!doc.is_active && (
                            <Badge variant="outline" className="mt-1 text-xs">
                              Inattivo
                            </Badge>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <Badge className={getTopicColor(doc.topic)}>{doc.topic}</Badge>
                    </td>
                    <td className="p-4 text-sm">{doc.document_type}</td>
                    <td className="p-4">{getStatusBadge(doc.processing_status)}</td>
                    <td className="p-4 text-sm">{doc.chunk_count}</td>
                    <td className="p-4 text-sm">{formatFileSize(doc.file_size)}</td>
                    <td className="p-4 text-xs text-muted-foreground">
                      {formatDate(doc.created_at)}
                    </td>
                    <td className="p-4">
                      <div className="flex items-center gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => router.push(`/admin/knowledge-base/${doc.id}`)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>

                        {doc.processing_status === 'PENDING' && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => processDocument(doc.id)}
                            disabled={processingDocId === doc.id}
                          >
                            {processingDocId === doc.id ? (
                              <RefreshCw className="h-4 w-4 animate-spin" />
                            ) : (
                              <FileUp className="h-4 w-4" />
                            )}
                          </Button>
                        )}

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => toggleActive(doc.id)}
                        >
                          {doc.is_active ? (
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          ) : (
                            <XCircle className="h-4 w-4 text-gray-400" />
                          )}
                        </Button>

                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteDocument(doc.id, doc.title)}
                        >
                          <Trash2 className="h-4 w-4 text-destructive" />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            disabled={currentPage === 1}
          >
            Precedente
          </Button>
          <span className="text-sm text-muted-foreground">
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
        </div>
      </main>
    </>
  );
}
