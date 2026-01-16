/**
 * Admin Edit Banner Page
 * Descrizione: Form per modificare un banner esistente
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Switch } from '@/components/ui/switch';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { ArrowLeft, Save, Loader2, Upload, X } from 'lucide-react';

interface BannerFormData {
  title: string;
  subtitle: string;
  description: string;
  image_url: string;
  video_url: string;
  cta_text: string;
  cta_link: string;
  cta_variant: string;
  position: string;
  display_order: number;
  background_color: string;
  text_color: string;
  is_active: boolean;
  start_date: string;
  end_date: string;
}

export default function AdminEditBannerPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isUploadingImage, setIsUploadingImage] = useState(false);
  const [isUploadingVideo, setIsUploadingVideo] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [formData, setFormData] = useState<BannerFormData>({
    title: '',
    subtitle: '',
    description: '',
    image_url: '',
    video_url: '',
    cta_text: '',
    cta_link: '',
    cta_variant: 'primary',
    position: 'hero',
    display_order: 0,
    background_color: '',
    text_color: '',
    is_active: true,
    start_date: '',
    end_date: '',
  });

  // Load banner data on mount
  useEffect(() => {
    const loadBanner = async () => {
      try {
        setIsLoading(true);
        setError(null);

        const banner = await apiClient.get(`/homepage/banners/${params.id}`);

        // Format dates for datetime-local input
        const formatDateForInput = (dateStr: string | null) => {
          if (!dateStr) return '';
          const date = new Date(dateStr);
          return date.toISOString().slice(0, 16); // Format: YYYY-MM-DDTHH:mm
        };

        setFormData({
          title: banner.title || '',
          subtitle: banner.subtitle || '',
          description: banner.description || '',
          image_url: banner.image_url || '',
          video_url: banner.video_url || '',
          cta_text: banner.cta_text || '',
          cta_link: banner.cta_link || '',
          cta_variant: banner.cta_variant || 'primary',
          position: banner.position || 'hero',
          display_order: banner.display_order || 0,
          background_color: banner.background_color || '',
          text_color: banner.text_color || '',
          is_active: banner.is_active !== false,
          start_date: formatDateForInput(banner.start_date),
          end_date: formatDateForInput(banner.end_date),
        });
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setIsLoading(false);
      }
    };

    loadBanner();
  }, [params.id]);

  const handleChange = (field: keyof BannerFormData, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setError('Formato immagine non valido. Usa JPG, PNG o WEBP.');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('Immagine troppo grande. Dimensione massima: 10MB.');
      return;
    }

    setIsUploadingImage(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', 'banner');
      formData.append('is_public', 'true');

      const response = await apiClient.postFormData('/files/upload', formData);

      setFormData((prev) => ({
        ...prev,
        image_url: response.url,
      }));

      setSuccess('Immagine caricata con successo!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsUploadingImage(false);
    }
  };

  const handleVideoUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const validTypes = ['video/mp4', 'video/webm'];
    if (!validTypes.includes(file.type)) {
      setError('Formato video non valido. Usa MP4 o WEBM.');
      return;
    }

    // Validate file size (50MB)
    if (file.size > 50 * 1024 * 1024) {
      setError('Video troppo grande. Dimensione massima: 50MB.');
      return;
    }

    setIsUploadingVideo(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('category', 'banner');
      formData.append('is_public', 'true');

      const response = await apiClient.postFormData('/files/upload', formData);

      setFormData((prev) => ({
        ...prev,
        video_url: response.url,
      }));

      setSuccess('Video caricato con successo!');
      setTimeout(() => setSuccess(null), 3000);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsUploadingVideo(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validation
    if (!formData.title.trim()) {
      setError('Il titolo è obbligatorio');
      return;
    }

    setIsSaving(true);

    try {
      // Prepare data
      const payload: any = {
        title: formData.title,
        subtitle: formData.subtitle || undefined,
        description: formData.description || undefined,
        image_url: formData.image_url || undefined,
        video_url: formData.video_url || undefined,
        cta_text: formData.cta_text || undefined,
        cta_link: formData.cta_link || undefined,
        cta_variant: formData.cta_variant,
        position: formData.position,
        display_order: formData.display_order,
        background_color: formData.background_color || undefined,
        text_color: formData.text_color || undefined,
        is_active: formData.is_active,
        start_date: formData.start_date || undefined,
        end_date: formData.end_date || undefined,
      };

      await apiClient.put(`/homepage/banners/${params.id}`, payload);

      setSuccess('Banner aggiornato con successo!');

      // Redirect dopo 1 secondo
      setTimeout(() => {
        router.push('/admin/banners');
      }, 1000);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <>
        <Navigation />
        <main className="container py-12">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-center min-h-[400px]">
              <div className="flex flex-col items-center gap-4">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
                <p className="text-muted-foreground">Caricamento banner...</p>
              </div>
            </div>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navigation />

      <main className="container py-12">
        <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-8 flex items-center gap-4">
        <Link href="/admin/banners">
          <Button variant="ghost" size="icon">
            <ArrowLeft className="h-5 w-5" />
          </Button>
        </Link>
        <div>
          <h1 className="text-4xl font-bold mb-2">Modifica Banner</h1>
          <p className="text-muted-foreground">
            Aggiorna le informazioni del banner
          </p>
        </div>
      </div>

      {/* Alerts */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {success && (
        <Alert className="mb-6 border-green-500/50 text-green-700 dark:text-green-400">
          <AlertDescription>{success}</AlertDescription>
        </Alert>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Contenuto Principale */}
        <Card>
          <CardHeader>
            <CardTitle>Contenuto</CardTitle>
            <CardDescription>Testo principale del banner</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="title">Titolo *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => handleChange('title', e.target.value)}
                placeholder="Scopri i nostri servizi AI"
                required
                disabled={isSaving}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="subtitle">Sottotitolo</Label>
              <Input
                id="subtitle"
                value={formData.subtitle}
                onChange={(e) => handleChange('subtitle', e.target.value)}
                placeholder="Innovazione sicura e conforme"
                disabled={isSaving}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descrizione</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleChange('description', e.target.value)}
                placeholder="Descrizione dettagliata del banner..."
                rows={4}
                disabled={isSaving}
              />
            </div>
          </CardContent>
        </Card>

        {/* Media */}
        <Card>
          <CardHeader>
            <CardTitle>Media</CardTitle>
            <CardDescription>Immagine o video di sfondo (uno dei due)</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Upload Immagine */}
            <div className="space-y-2">
              <Label htmlFor="image_file">Immagine di Sfondo</Label>
              <Input
                id="image_file"
                type="file"
                accept=".jpg,.jpeg,.png,.webp"
                onChange={handleImageUpload}
                disabled={isSaving || isUploadingImage || isUploadingVideo}
                className="cursor-pointer"
              />
              <div className="text-xs text-muted-foreground space-y-1">
                <p><strong>Formati supportati:</strong> JPG, PNG, WEBP</p>
                <p><strong>Dimensione massima:</strong> 10 MB</p>
                <p><strong>Dimensioni consigliate:</strong> 1920x1080 px per banner hero</p>
              </div>
              {isUploadingImage && (
                <p className="text-sm text-blue-600 dark:text-blue-400 flex items-center gap-2">
                  <Upload className="h-4 w-4 animate-pulse" />
                  Caricamento immagine in corso...
                </p>
              )}
              {formData.image_url && (
                <div className="flex items-center gap-2 p-2 bg-green-50 dark:bg-green-900/20 rounded-md">
                  <p className="text-sm text-green-700 dark:text-green-400 flex-1">
                    Immagine caricata
                  </p>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleChange('image_url', '')}
                    disabled={isSaving}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>

            {/* Upload Video */}
            <div className="space-y-2">
              <Label htmlFor="video_file">Video di Sfondo (alternativa)</Label>
              <Input
                id="video_file"
                type="file"
                accept=".mp4,.webm"
                onChange={handleVideoUpload}
                disabled={isSaving || isUploadingImage || isUploadingVideo}
                className="cursor-pointer"
              />
              <div className="text-xs text-muted-foreground space-y-1">
                <p><strong>Formati supportati:</strong> MP4, WEBM</p>
                <p><strong>Dimensione massima:</strong> 50 MB</p>
                <p><strong>Nota:</strong> Il video sovrascrive l'immagine se entrambi sono presenti</p>
              </div>
              {isUploadingVideo && (
                <p className="text-sm text-blue-600 dark:text-blue-400 flex items-center gap-2">
                  <Upload className="h-4 w-4 animate-pulse" />
                  Caricamento video in corso...
                </p>
              )}
              {formData.video_url && (
                <div className="flex items-center gap-2 p-2 bg-green-50 dark:bg-green-900/20 rounded-md">
                  <p className="text-sm text-green-700 dark:text-green-400 flex-1">
                    Video caricato
                  </p>
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    onClick={() => handleChange('video_url', '')}
                    disabled={isSaving}
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
            </div>

            {/* Preview */}
            {formData.image_url && !formData.video_url && (
              <div className="mt-4">
                <Label>Preview Immagine</Label>
                <img
                  src={formData.image_url}
                  alt="Preview"
                  className="w-full max-h-64 object-cover rounded-md mt-2 border"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            )}

            {formData.video_url && (
              <div className="mt-4">
                <Label>Preview Video</Label>
                <video
                  src={formData.video_url}
                  controls
                  className="w-full max-h-64 rounded-md mt-2 border"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                  }}
                />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Call to Action */}
        <Card>
          <CardHeader>
            <CardTitle>Call to Action</CardTitle>
            <CardDescription>Bottone di azione</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="cta_text">Testo Bottone</Label>
                <Input
                  id="cta_text"
                  value={formData.cta_text}
                  onChange={(e) => handleChange('cta_text', e.target.value)}
                  placeholder="Scopri di più"
                  disabled={isSaving}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="cta_link">Link</Label>
                <Input
                  id="cta_link"
                  type="url"
                  value={formData.cta_link}
                  onChange={(e) => handleChange('cta_link', e.target.value)}
                  placeholder="/servizi"
                  disabled={isSaving}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="cta_variant">Variante Bottone</Label>
              <Select
                value={formData.cta_variant}
                onValueChange={(value) => handleChange('cta_variant', value)}
                disabled={isSaving}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="primary">Primary</SelectItem>
                  <SelectItem value="secondary">Secondary</SelectItem>
                  <SelectItem value="outline">Outline</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Posizionamento e Stile */}
        <Card>
          <CardHeader>
            <CardTitle>Posizionamento e Stile</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="position">Posizione</Label>
                <Select
                  value={formData.position}
                  onValueChange={(value) => handleChange('position', value)}
                  disabled={isSaving}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hero">Hero Principal</SelectItem>
                    <SelectItem value="slider">Slider</SelectItem>
                    <SelectItem value="section">Sezione</SelectItem>
                    <SelectItem value="footer">Footer</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="display_order">Ordine</Label>
                <Input
                  id="display_order"
                  type="number"
                  min="0"
                  value={formData.display_order}
                  onChange={(e) => handleChange('display_order', parseInt(e.target.value) || 0)}
                  disabled={isSaving}
                />
              </div>

              <div className="space-y-2 flex items-end">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="is_active"
                    checked={formData.is_active}
                    onCheckedChange={(checked) => handleChange('is_active', checked)}
                    disabled={isSaving}
                  />
                  <Label htmlFor="is_active">Attivo</Label>
                </div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="background_color">Colore Sfondo</Label>
                <Input
                  id="background_color"
                  value={formData.background_color}
                  onChange={(e) => handleChange('background_color', e.target.value)}
                  placeholder="#ffffff o primary"
                  disabled={isSaving}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="text_color">Colore Testo</Label>
                <Input
                  id="text_color"
                  value={formData.text_color}
                  onChange={(e) => handleChange('text_color', e.target.value)}
                  placeholder="#000000 o white"
                  disabled={isSaving}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Date Validità */}
        <Card>
          <CardHeader>
            <CardTitle>Validità Temporale</CardTitle>
            <CardDescription>Opzionale - Limita la visibilità del banner a un periodo specifico</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date">Data Inizio</Label>
                <Input
                  id="start_date"
                  type="datetime-local"
                  value={formData.start_date}
                  onChange={(e) => handleChange('start_date', e.target.value)}
                  disabled={isSaving}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="end_date">Data Fine</Label>
                <Input
                  id="end_date"
                  type="datetime-local"
                  value={formData.end_date}
                  onChange={(e) => handleChange('end_date', e.target.value)}
                  disabled={isSaving}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex gap-4">
          <Button type="submit" size="lg" disabled={isSaving}>
            <Save className="h-5 w-5 mr-2" />
            {isSaving ? 'Salvataggio...' : 'Salva Modifiche'}
          </Button>
          <Link href="/admin/banners">
            <Button type="button" variant="outline" size="lg" disabled={isSaving}>
              Annulla
            </Button>
          </Link>
        </div>
      </form>
        </div>
      </main>
    </>
  );
}
