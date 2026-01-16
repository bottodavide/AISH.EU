/**
 * Admin About Page Editor
 * Descrizione: Gestione completa della pagina Chi Siamo
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { useAuth } from '@/contexts/AuthContext';
import { Plus, Trash2, Loader2, Save, Eye, EyeOff, X } from 'lucide-react';

interface SpecializationArea {
  name: string;
  percentage: number;
  display_order: number;
}

interface CompetenceSection {
  title: string;
  icon: string;
  description: string;
  features: string[];
  display_order: number;
}

interface AboutPage {
  id?: string;
  profile_name: string;
  profile_title: string;
  profile_description: string;
  profile_image_url: string | null;
  profile_badges: string[];
  is_published: boolean;
  specialization_areas: SpecializationArea[];
  competence_sections: CompetenceSection[];
}

export default function AdminAboutPage() {
  const router = useRouter();
  const { isAuthenticated, isAdmin, isLoading: authLoading } = useAuth();
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Form data
  const [formData, setFormData] = useState<AboutPage>({
    profile_name: '',
    profile_title: '',
    profile_description: '',
    profile_image_url: null,
    profile_badges: [],
    is_published: false,
    specialization_areas: [],
    competence_sections: [],
  });

  // Temporary states for adding items
  const [newBadge, setNewBadge] = useState('');
  const [newFeature, setNewFeature] = useState<{ [key: number]: string }>({});

  // Redirect if not admin
  useEffect(() => {
    if (!authLoading && (!isAuthenticated || !isAdmin)) {
      router.push('/');
    }
  }, [authLoading, isAuthenticated, isAdmin, router]);

  // Load data only if authenticated and admin
  useEffect(() => {
    if (isAuthenticated && isAdmin) {
      loadAboutPage();
    }
  }, [isAuthenticated, isAdmin]);

  const loadAboutPage = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get<AboutPage>('/about/admin');
      setFormData(response);
    } catch (err: any) {
      // Se è 404, significa che non esiste ancora, creiamo un form vuoto
      if (err.response?.status === 404) {
        // Form vuoto già impostato nello state iniziale
      } else {
        setError(getErrorMessage(err));
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      await apiClient.put('/about/admin', formData);
      setSuccess('Pagina About salvata con successo!');

      // Ricarica i dati dopo il salvataggio
      await loadAboutPage();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsSaving(false);
    }
  };

  // Profile handlers
  const handleProfileChange = (field: keyof AboutPage, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const addBadge = () => {
    if (newBadge.trim()) {
      setFormData((prev) => ({
        ...prev,
        profile_badges: [...prev.profile_badges, newBadge.trim()],
      }));
      setNewBadge('');
    }
  };

  const removeBadge = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      profile_badges: prev.profile_badges.filter((_, i) => i !== index),
    }));
  };

  // Specialization handlers
  const addSpecialization = () => {
    setFormData((prev) => ({
      ...prev,
      specialization_areas: [
        ...prev.specialization_areas,
        { name: '', percentage: 0, display_order: prev.specialization_areas.length },
      ],
    }));
  };

  const updateSpecialization = (index: number, field: keyof SpecializationArea, value: any) => {
    setFormData((prev) => ({
      ...prev,
      specialization_areas: prev.specialization_areas.map((spec, i) =>
        i === index ? { ...spec, [field]: value } : spec
      ),
    }));
  };

  const removeSpecialization = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      specialization_areas: prev.specialization_areas.filter((_, i) => i !== index),
    }));
  };

  // Competence handlers
  const addCompetence = () => {
    setFormData((prev) => ({
      ...prev,
      competence_sections: [
        ...prev.competence_sections,
        {
          title: '',
          icon: 'BookOpen',
          description: '',
          features: [],
          display_order: prev.competence_sections.length,
        },
      ],
    }));
  };

  const updateCompetence = (index: number, field: keyof CompetenceSection, value: any) => {
    setFormData((prev) => ({
      ...prev,
      competence_sections: prev.competence_sections.map((comp, i) =>
        i === index ? { ...comp, [field]: value } : comp
      ),
    }));
  };

  const removeCompetence = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      competence_sections: prev.competence_sections.filter((_, i) => i !== index),
    }));
  };

  const addFeatureToCompetence = (compIndex: number) => {
    const feature = newFeature[compIndex];
    if (feature && feature.trim()) {
      updateCompetence(compIndex, 'features', [
        ...formData.competence_sections[compIndex].features,
        feature.trim(),
      ]);
      setNewFeature((prev) => ({ ...prev, [compIndex]: '' }));
    }
  };

  const removeFeatureFromCompetence = (compIndex: number, featureIndex: number) => {
    const features = formData.competence_sections[compIndex].features.filter(
      (_, i) => i !== featureIndex
    );
    updateCompetence(compIndex, 'features', features);
  };

  if (authLoading || !isAuthenticated || !isAdmin) {
    return (
      <>
        <Navigation />
        <main className="container py-12">
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Caricamento...</p>
          </div>
        </main>
      </>
    );
  }

  if (isLoading) {
    return (
      <>
        <Navigation />
        <main className="container py-12">
          <div className="flex flex-col items-center justify-center py-12">
            <Loader2 className="h-12 w-12 animate-spin text-primary mb-4" />
            <p className="text-muted-foreground">Caricamento dati...</p>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <Navigation />

      <main className="container py-12">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold mb-2">Gestione Pagina Chi Siamo</h1>
            <p className="text-muted-foreground">
              Modifica profilo, aree di specializzazione e sezioni di competenza
            </p>
          </div>

          {/* Alerts */}
          {error && (
            <Alert variant="destructive" className="mb-6">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {success && (
            <Alert className="mb-6 border-green-200 bg-green-50">
              <AlertDescription className="text-green-800">{success}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Profilo */}
            <Card>
              <CardHeader>
                <CardTitle>Profilo Personale</CardTitle>
                <CardDescription>Informazioni principali visualizzate nella sidebar</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="profile_name">Nome Completo *</Label>
                    <Input
                      id="profile_name"
                      value={formData.profile_name}
                      onChange={(e) => handleProfileChange('profile_name', e.target.value)}
                      required
                      placeholder="Mario Rossi"
                    />
                  </div>

                  <div>
                    <Label htmlFor="profile_title">Titolo Professionale *</Label>
                    <Input
                      id="profile_title"
                      value={formData.profile_title}
                      onChange={(e) => handleProfileChange('profile_title', e.target.value)}
                      required
                      placeholder="Senior AI & Privacy Consultant"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="profile_description">Descrizione Breve *</Label>
                  <Textarea
                    id="profile_description"
                    value={formData.profile_description}
                    onChange={(e) => handleProfileChange('profile_description', e.target.value)}
                    required
                    rows={3}
                    placeholder="Descrizione del profilo professionale..."
                  />
                </div>

                <div>
                  <Label htmlFor="profile_image_url">URL Immagine Profilo</Label>
                  <Input
                    id="profile_image_url"
                    type="url"
                    value={formData.profile_image_url || ''}
                    onChange={(e) => handleProfileChange('profile_image_url', e.target.value || null)}
                    placeholder="https://..."
                  />
                </div>

                {/* Badges */}
                <div>
                  <Label>Badge / Certificazioni</Label>
                  <div className="flex gap-2 mb-2">
                    <Input
                      value={newBadge}
                      onChange={(e) => setNewBadge(e.target.value)}
                      placeholder="Es: ISO 27001 LA"
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addBadge())}
                    />
                    <Button type="button" onClick={addBadge} variant="outline">
                      <Plus className="h-4 w-4" />
                    </Button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {formData.profile_badges.map((badge, index) => (
                      <Badge key={index} variant="secondary" className="flex items-center gap-1">
                        {badge}
                        <X
                          className="h-3 w-3 cursor-pointer"
                          onClick={() => removeBadge(index)}
                        />
                      </Badge>
                    ))}
                  </div>
                </div>

                {/* Pubblicazione */}
                <div className="flex items-center gap-3">
                  <Button
                    type="button"
                    variant={formData.is_published ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => handleProfileChange('is_published', !formData.is_published)}
                  >
                    {formData.is_published ? (
                      <>
                        <Eye className="h-4 w-4 mr-2" />
                        Pubblicata
                      </>
                    ) : (
                      <>
                        <EyeOff className="h-4 w-4 mr-2" />
                        Bozza
                      </>
                    )}
                  </Button>
                  <span className="text-sm text-muted-foreground">
                    {formData.is_published
                      ? 'La pagina è visibile al pubblico'
                      : 'La pagina è in bozza e non visibile'}
                  </span>
                </div>
              </CardContent>
            </Card>

            {/* Aree di Specializzazione */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Aree di Specializzazione</CardTitle>
                    <CardDescription>
                      Progress bars mostrate nella sidebar (0-100%)
                    </CardDescription>
                  </div>
                  <Button type="button" onClick={addSpecialization} variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Aggiungi Area
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {formData.specialization_areas.length === 0 && (
                  <p className="text-muted-foreground text-sm">
                    Nessuna area di specializzazione. Clicca &quot;Aggiungi Area&quot; per iniziare.
                  </p>
                )}

                {formData.specialization_areas.map((spec, index) => (
                  <div key={index} className="flex gap-2 items-start p-4 border rounded-lg">
                    <div className="flex-1 grid md:grid-cols-2 gap-4">
                      <div>
                        <Label>Nome Area *</Label>
                        <Input
                          value={spec.name}
                          onChange={(e) => updateSpecialization(index, 'name', e.target.value)}
                          required
                          placeholder="Es: AI Governance"
                        />
                      </div>
                      <div>
                        <Label>Percentuale (0-100) *</Label>
                        <Input
                          type="number"
                          min="0"
                          max="100"
                          value={spec.percentage}
                          onChange={(e) =>
                            updateSpecialization(index, 'percentage', parseInt(e.target.value))
                          }
                          required
                        />
                      </div>
                    </div>
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => removeSpecialization(index)}
                      className="text-red-600 hover:text-red-700"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Sezioni di Competenza */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Sezioni di Competenza</CardTitle>
                    <CardDescription>
                      AI Governance, GDPR, Cybersecurity, etc.
                    </CardDescription>
                  </div>
                  <Button type="button" onClick={addCompetence} variant="outline" size="sm">
                    <Plus className="h-4 w-4 mr-2" />
                    Aggiungi Sezione
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-6">
                {formData.competence_sections.length === 0 && (
                  <p className="text-muted-foreground text-sm">
                    Nessuna sezione di competenza. Clicca &quot;Aggiungi Sezione&quot; per iniziare.
                  </p>
                )}

                {formData.competence_sections.map((comp, compIndex) => (
                  <div key={compIndex} className="border rounded-lg p-6 space-y-4">
                    <div className="flex items-start justify-between">
                      <h4 className="font-semibold">Sezione {compIndex + 1}</h4>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => removeCompetence(compIndex)}
                        className="text-red-600 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <Label>Titolo Sezione *</Label>
                        <Input
                          value={comp.title}
                          onChange={(e) => updateCompetence(compIndex, 'title', e.target.value)}
                          required
                          placeholder="Es: AI Governance & Ethics"
                        />
                      </div>
                      <div>
                        <Label>Icona (Lucide React) *</Label>
                        <Input
                          value={comp.icon}
                          onChange={(e) => updateCompetence(compIndex, 'icon', e.target.value)}
                          required
                          placeholder="Es: BookOpen, Users, Shield"
                        />
                      </div>
                    </div>

                    <div>
                      <Label>Descrizione *</Label>
                      <Textarea
                        value={comp.description}
                        onChange={(e) => updateCompetence(compIndex, 'description', e.target.value)}
                        required
                        rows={3}
                        placeholder="Descrizione della competenza..."
                      />
                    </div>

                    {/* Features */}
                    <div>
                      <Label>Servizi / Features</Label>
                      <div className="flex gap-2 mb-2">
                        <Input
                          value={newFeature[compIndex] || ''}
                          onChange={(e) =>
                            setNewFeature((prev) => ({ ...prev, [compIndex]: e.target.value }))
                          }
                          placeholder="Es: Gap Analysis rispetto all'AI Act"
                          onKeyPress={(e) =>
                            e.key === 'Enter' &&
                            (e.preventDefault(), addFeatureToCompetence(compIndex))
                          }
                        />
                        <Button
                          type="button"
                          onClick={() => addFeatureToCompetence(compIndex)}
                          variant="outline"
                          size="sm"
                        >
                          <Plus className="h-4 w-4" />
                        </Button>
                      </div>
                      <div className="space-y-1">
                        {comp.features.map((feature, featureIndex) => (
                          <div
                            key={featureIndex}
                            className="flex items-center gap-2 text-sm p-2 bg-muted rounded"
                          >
                            <span className="flex-1">{feature}</span>
                            <X
                              className="h-4 w-4 cursor-pointer text-muted-foreground hover:text-foreground"
                              onClick={() => removeFeatureFromCompetence(compIndex, featureIndex)}
                            />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Actions */}
            <div className="flex gap-4">
              <Button type="submit" size="lg" disabled={isSaving}>
                {isSaving ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Salvataggio...
                  </>
                ) : (
                  <>
                    <Save className="h-5 w-5 mr-2" />
                    Salva Modifiche
                  </>
                )}
              </Button>

              <Button
                type="button"
                variant="outline"
                size="lg"
                onClick={() => router.push('/admin')}
              >
                Annulla
              </Button>
            </div>
          </form>
        </div>
      </main>
    </>
  );
}
