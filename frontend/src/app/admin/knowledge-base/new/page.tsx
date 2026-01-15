'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Upload, FileText, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { apiClient } from '@/lib/api-client';

export default function NewKnowledgeBasePage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: '',
    topic: 'GENERAL',
    description: '',
    source_url: '',
    author: '',
    is_active: true,
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [autoProcess, setAutoProcess] = useState(true);

  const topics = ['AI', 'GDPR', 'NIS2', 'CYBERSECURITY', 'GENERAL'];

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];

      // Validate file type
      const validTypes = ['text/plain', 'application/pdf'];
      if (!validTypes.includes(file.type)) {
        setError('Tipo file non supportato. Usa TXT o PDF.');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('File troppo grande. Massimo 10MB.');
        return;
      }

      setSelectedFile(file);
      setError(null);

      // Auto-populate title if empty
      if (!formData.title) {
        const fileName = file.name.replace(/\.[^/.]+$/, '');
        setFormData((prev) => ({ ...prev, title: fileName }));
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      // Validate
      if (!formData.title) {
        throw new Error('Il titolo è obbligatorio');
      }

      if (!selectedFile && !formData.source_url) {
        throw new Error('Carica un file o inserisci un URL sorgente');
      }

      // Prepare FormData
      const formDataToSend = new FormData();
      formDataToSend.append('title', formData.title);
      formDataToSend.append('topic', formData.topic);
      formDataToSend.append('is_active', formData.is_active.toString());

      if (formData.description) {
        formDataToSend.append('description', formData.description);
      }

      if (formData.source_url) {
        formDataToSend.append('source_url', formData.source_url);
      }

      if (formData.author) {
        formDataToSend.append('author', formData.author);
      }

      if (selectedFile) {
        formDataToSend.append('file', selectedFile);
      }

      // Create document
      const response = await apiClient.post<{ id: string }>(
        '/api/v1/knowledge-base/documents',
        formDataToSend,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      // Auto-process if enabled
      if (autoProcess) {
        try {
          await apiClient.post(
            `/api/v1/knowledge-base/documents/${response.id}/process`,
            {}
          );
          alert('Documento caricato e processato con successo!');
        } catch (err) {
          console.error('Error processing:', err);
          alert('Documento caricato ma errore nel processing. Processalo manualmente dalla lista.');
        }
      } else {
        alert('Documento caricato con successo!');
      }

      // Redirect to list
      router.push('/admin/knowledge-base');
    } catch (err: any) {
      console.error('Error creating document:', err);
      setError(err.response?.data?.detail || err.message || 'Errore nel caricamento del documento');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mx-auto max-w-3xl space-y-6">
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

        <h1 className="text-3xl font-bold">Nuovo Documento Knowledge Base</h1>
        <p className="text-muted-foreground">
          Carica un documento per arricchire la knowledge base del RAG system
        </p>
      </div>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6 rounded-lg border p-6">
        {/* File Upload */}
        <div className="space-y-2">
          <Label htmlFor="file">File (TXT o PDF) *</Label>
          <div className="flex items-center gap-4">
            <Input
              id="file"
              type="file"
              accept=".txt,.pdf,text/plain,application/pdf"
              onChange={handleFileChange}
              disabled={loading}
            />
            {selectedFile && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <FileText className="h-4 w-4" />
                <span>{selectedFile.name}</span>
                <span>({(selectedFile.size / 1024).toFixed(1)} KB)</span>
              </div>
            )}
          </div>
          <p className="text-xs text-muted-foreground">
            Supporto per file TXT e PDF fino a 10MB
          </p>
        </div>

        <div className="text-center text-sm text-muted-foreground">
          <span>— oppure —</span>
        </div>

        {/* Source URL */}
        <div className="space-y-2">
          <Label htmlFor="source_url">URL Sorgente</Label>
          <Input
            id="source_url"
            type="url"
            value={formData.source_url}
            onChange={(e) => setFormData({ ...formData, source_url: e.target.value })}
            placeholder="https://..."
            disabled={loading}
          />
          <p className="text-xs text-muted-foreground">
            URL della risorsa originale (alternativo al file)
          </p>
        </div>

        <hr />

        {/* Title */}
        <div className="space-y-2">
          <Label htmlFor="title">Titolo *</Label>
          <Input
            id="title"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            placeholder="es. Guida GDPR 2024"
            required
            disabled={loading}
          />
        </div>

        {/* Topic */}
        <div className="space-y-2">
          <Label htmlFor="topic">Topic *</Label>
          <select
            id="topic"
            value={formData.topic}
            onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
            className="w-full rounded-md border border-input bg-background px-3 py-2"
            disabled={loading}
          >
            {topics.map((topic) => (
              <option key={topic} value={topic}>
                {topic}
              </option>
            ))}
          </select>
          <p className="text-xs text-muted-foreground">
            Categoria tematica per il filtro RAG
          </p>
        </div>

        {/* Description */}
        <div className="space-y-2">
          <Label htmlFor="description">Descrizione</Label>
          <Textarea
            id="description"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Breve descrizione del contenuto..."
            rows={3}
            maxLength={1000}
            disabled={loading}
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>Opzionale ma consigliato per la ricerca</span>
            <span>{formData.description.length}/1000</span>
          </div>
        </div>

        {/* Author */}
        <div className="space-y-2">
          <Label htmlFor="author">Autore</Label>
          <Input
            id="author"
            value={formData.author}
            onChange={(e) => setFormData({ ...formData, author: e.target.value })}
            placeholder="Nome autore o fonte"
            maxLength={100}
            disabled={loading}
          />
        </div>

        {/* Active Toggle */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="is_active"
            checked={formData.is_active}
            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            className="h-4 w-4 rounded border-gray-300"
            disabled={loading}
          />
          <Label htmlFor="is_active" className="cursor-pointer font-normal">
            Attiva subito (disponibile per RAG)
          </Label>
        </div>

        {/* Auto-process Toggle */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="auto_process"
            checked={autoProcess}
            onChange={(e) => setAutoProcess(e.target.checked)}
            className="h-4 w-4 rounded border-gray-300"
            disabled={loading}
          />
          <Label htmlFor="auto_process" className="cursor-pointer font-normal">
            Processa automaticamente dopo il caricamento
          </Label>
          <p className="text-xs text-muted-foreground">
            (genera embeddings e chunk)
          </p>
        </div>

        {/* Submit */}
        <div className="flex items-center justify-end gap-4">
          <Button
            type="button"
            variant="outline"
            onClick={() => router.push('/admin/knowledge-base')}
            disabled={loading}
          >
            Annulla
          </Button>
          <Button type="submit" disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Caricamento...
              </>
            ) : (
              <>
                <Upload className="mr-2 h-4 w-4" />
                Carica Documento
              </>
            )}
          </Button>
        </div>
      </form>

      {/* Info Box */}
      <div className="rounded-lg border bg-muted/50 p-4">
        <h3 className="mb-2 font-semibold">ℹ️ Come funziona</h3>
        <ul className="space-y-1 text-sm text-muted-foreground">
          <li>
            1. <strong>Carica</strong>: Seleziona un file TXT/PDF o inserisci un URL
          </li>
          <li>
            2. <strong>Processa</strong>: Il sistema divide il testo in chunk e genera embeddings
          </li>
          <li>
            3. <strong>RAG</strong>: Il contenuto diventa disponibile per il chatbot AI
          </li>
        </ul>
      </div>
    </div>
  );
}
