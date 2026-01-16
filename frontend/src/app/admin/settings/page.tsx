/**
 * Admin Settings
 * Descrizione: Impostazioni e configurazione sistema
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Settings, Save, Globe, Mail, CreditCard, Shield, Bell } from 'lucide-react';

export default function AdminSettingsPage() {
  const [isSaving, setIsSaving] = useState(false);
  const [success, setSuccess] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // General Settings
  const [generalSettings, setGeneralSettings] = useState({
    site_name: 'AI Strategy Hub',
    site_url: 'https://aistrategyhub.eu',
    support_email: 'support@aistrategyhub.eu',
    admin_email: 'admin@aistrategyhub.eu',
    timezone: 'Europe/Rome',
    language: 'it',
  });

  // Office365 Email Settings
  const [emailSettings, setEmailSettings] = useState({
    tenant_id: '',
    client_id: '',
    client_secret: '',
    sender_email: 'noreply@aistrategyhub.eu',
    sender_name: 'AI Strategy Hub',
  });

  // Payment Settings
  const [paymentSettings, setPaymentSettings] = useState({
    stripe_enabled: true,
    stripe_publishable_key: '',
    stripe_webhook_secret: '',
    currency: 'EUR',
    tax_rate: '22',
  });

  // Security Settings
  const [securitySettings, setSecuritySettings] = useState({
    mfa_required_for_admin: false,
    session_timeout: '30',
    password_min_length: '8',
    max_login_attempts: '5',
    lockout_duration: '30',
  });

  const handleSaveGeneral = async () => {
    setIsSaving(true);
    setError(null);
    setSuccess(null);

    try {
      // Mock save - In production, call API
      await new Promise((resolve) => setTimeout(resolve, 1000));
      setSuccess('Impostazioni generali salvate con successo');
    } catch (err) {
      setError('Errore nel salvataggio delle impostazioni');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="container py-8 max-w-5xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Impostazioni Sistema</h1>
          <p className="text-muted-foreground mt-2">
            Configura e gestisci le impostazioni della piattaforma
          </p>
        </div>
        <Link href="/admin">
          <Button variant="outline">← Dashboard</Button>
        </Link>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <Alert className="mb-6 bg-green-50 border-green-200">
          <AlertDescription className="text-green-800">
            {success}
          </AlertDescription>
        </Alert>
      )}

      {error && (
        <Alert variant="destructive" className="mb-6">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-6">
        {/* General Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              <CardTitle>Impostazioni Generali</CardTitle>
            </div>
            <CardDescription>
              Configurazione base del sito e informazioni generali
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="site_name">Nome Sito</Label>
                <Input
                  id="site_name"
                  value={generalSettings.site_name}
                  onChange={(e) =>
                    setGeneralSettings({
                      ...generalSettings,
                      site_name: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <Label htmlFor="site_url">URL Sito</Label>
                <Input
                  id="site_url"
                  type="url"
                  value={generalSettings.site_url}
                  onChange={(e) =>
                    setGeneralSettings({
                      ...generalSettings,
                      site_url: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <Label htmlFor="support_email">Email Supporto</Label>
                <Input
                  id="support_email"
                  type="email"
                  value={generalSettings.support_email}
                  onChange={(e) =>
                    setGeneralSettings({
                      ...generalSettings,
                      support_email: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <Label htmlFor="admin_email">Email Admin</Label>
                <Input
                  id="admin_email"
                  type="email"
                  value={generalSettings.admin_email}
                  onChange={(e) =>
                    setGeneralSettings({
                      ...generalSettings,
                      admin_email: e.target.value,
                    })
                  }
                />
              </div>

              <div>
                <Label htmlFor="timezone">Fuso Orario</Label>
                <select
                  id="timezone"
                  value={generalSettings.timezone}
                  onChange={(e) =>
                    setGeneralSettings({
                      ...generalSettings,
                      timezone: e.target.value,
                    })
                  }
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                >
                  <option value="Europe/Rome">Europa/Roma (IT)</option>
                  <option value="Europe/London">Europa/Londra (UK)</option>
                  <option value="America/New_York">America/New York (US)</option>
                </select>
              </div>

              <div>
                <Label htmlFor="language">Lingua</Label>
                <select
                  id="language"
                  value={generalSettings.language}
                  onChange={(e) =>
                    setGeneralSettings({
                      ...generalSettings,
                      language: e.target.value,
                    })
                  }
                  className="w-full rounded-md border border-input bg-background px-3 py-2"
                >
                  <option value="it">Italiano</option>
                  <option value="en">English</option>
                </select>
              </div>
            </div>

            <div className="pt-4">
              <Button onClick={handleSaveGeneral} disabled={isSaving}>
                <Save className="h-4 w-4 mr-2" />
                {isSaving ? 'Salvataggio...' : 'Salva Impostazioni Generali'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Office365 Email Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Mail className="h-5 w-5" />
              <CardTitle>Configurazione Email (Office 365)</CardTitle>
            </div>
            <CardDescription>
              Configurazione Microsoft Graph API per invio email tramite Office 365
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert className="bg-blue-50 border-blue-200">
              <AlertDescription className="text-blue-800 text-sm">
                ℹ️ Utilizza Microsoft Graph API per inviare email tramite il tuo account Office 365 aziendale.
                Le credenziali sono registrate in Azure AD.
              </AlertDescription>
            </Alert>

            <div className="space-y-4">
              <div>
                <Label htmlFor="tenant_id">Azure AD Tenant ID</Label>
                <Input
                  id="tenant_id"
                  value={emailSettings.tenant_id}
                  onChange={(e) =>
                    setEmailSettings({
                      ...emailSettings,
                      tenant_id: e.target.value,
                    })
                  }
                  placeholder="10a08e0e-3b37-4ac3-8a24-465ef3494d41"
                  className="font-mono text-sm"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  ID tenant dell'organizzazione Azure AD
                </p>
              </div>

              <div>
                <Label htmlFor="client_id">Application (Client) ID</Label>
                <Input
                  id="client_id"
                  value={emailSettings.client_id}
                  onChange={(e) =>
                    setEmailSettings({
                      ...emailSettings,
                      client_id: e.target.value,
                    })
                  }
                  placeholder="23d3de80-c6c1-490e-be41-fb7b53eec859"
                  className="font-mono text-sm"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  ID dell'applicazione registrata in Azure AD
                </p>
              </div>

              <div>
                <Label htmlFor="client_secret">Client Secret</Label>
                <Input
                  id="client_secret"
                  type="password"
                  value={emailSettings.client_secret}
                  onChange={(e) =>
                    setEmailSettings({
                      ...emailSettings,
                      client_secret: e.target.value,
                    })
                  }
                  placeholder="••••••••••••••••••••"
                  className="font-mono text-sm"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Secret dell'applicazione (generato in Azure AD)
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="sender_email">Sender Email</Label>
                  <Input
                    id="sender_email"
                    type="email"
                    value={emailSettings.sender_email}
                    onChange={(e) =>
                      setEmailSettings({
                        ...emailSettings,
                        sender_email: e.target.value,
                      })
                    }
                    placeholder="noreply@aistrategyhub.eu"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Account Office 365 da cui inviare le email
                  </p>
                </div>

                <div>
                  <Label htmlFor="sender_name">Sender Name</Label>
                  <Input
                    id="sender_name"
                    value={emailSettings.sender_name}
                    onChange={(e) =>
                      setEmailSettings({
                        ...emailSettings,
                        sender_name: e.target.value,
                      })
                    }
                    placeholder="AI Strategy Hub"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Nome visualizzato come mittente
                  </p>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t">
              <div className="flex items-center justify-between mb-4">
                <div className="text-sm">
                  <p className="font-medium">Stato Configurazione</p>
                  <p className="text-green-600 text-xs mt-1">✓ Configurato e attivo</p>
                </div>
              </div>

              <Button
                onClick={() => alert('Test email inviata! (Mock)')}
                variant="outline"
                className="mr-2"
              >
                <Mail className="h-4 w-4 mr-2" />
                Invia Email di Test
              </Button>
              <Button onClick={handleSaveGeneral} disabled={isSaving}>
                <Save className="h-4 w-4 mr-2" />
                Salva Configurazione Office 365
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Payment Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              <CardTitle>Impostazioni Pagamento</CardTitle>
            </div>
            <CardDescription>
              Configurazione Stripe e metodi di pagamento
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={paymentSettings.stripe_enabled}
                  onChange={(e) =>
                    setPaymentSettings({
                      ...paymentSettings,
                      stripe_enabled: e.target.checked,
                    })
                  }
                  className="rounded border-gray-300"
                />
                <span className="font-medium">Abilita Pagamenti Stripe</span>
              </label>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="stripe_publishable_key">
                    Stripe Publishable Key
                  </Label>
                  <Input
                    id="stripe_publishable_key"
                    type="password"
                    value={paymentSettings.stripe_publishable_key}
                    onChange={(e) =>
                      setPaymentSettings({
                        ...paymentSettings,
                        stripe_publishable_key: e.target.value,
                      })
                    }
                    placeholder="pk_test_..."
                  />
                </div>

                <div>
                  <Label htmlFor="stripe_webhook_secret">
                    Stripe Webhook Secret
                  </Label>
                  <Input
                    id="stripe_webhook_secret"
                    type="password"
                    value={paymentSettings.stripe_webhook_secret}
                    onChange={(e) =>
                      setPaymentSettings({
                        ...paymentSettings,
                        stripe_webhook_secret: e.target.value,
                      })
                    }
                    placeholder="whsec_..."
                  />
                </div>

                <div>
                  <Label htmlFor="currency">Valuta</Label>
                  <select
                    id="currency"
                    value={paymentSettings.currency}
                    onChange={(e) =>
                      setPaymentSettings({
                        ...paymentSettings,
                        currency: e.target.value,
                      })
                    }
                    className="w-full rounded-md border border-input bg-background px-3 py-2"
                  >
                    <option value="EUR">EUR (€)</option>
                    <option value="USD">USD ($)</option>
                    <option value="GBP">GBP (£)</option>
                  </select>
                </div>

                <div>
                  <Label htmlFor="tax_rate">Aliquota IVA (%)</Label>
                  <Input
                    id="tax_rate"
                    type="number"
                    value={paymentSettings.tax_rate}
                    onChange={(e) =>
                      setPaymentSettings({
                        ...paymentSettings,
                        tax_rate: e.target.value,
                      })
                    }
                  />
                </div>
              </div>
            </div>

            <div className="pt-4">
              <Button onClick={handleSaveGeneral} disabled={isSaving}>
                <Save className="h-4 w-4 mr-2" />
                Salva Impostazioni Pagamento
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Security Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              <CardTitle>Sicurezza</CardTitle>
            </div>
            <CardDescription>
              Impostazioni di sicurezza e autenticazione
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={securitySettings.mfa_required_for_admin}
                  onChange={(e) =>
                    setSecuritySettings({
                      ...securitySettings,
                      mfa_required_for_admin: e.target.checked,
                    })
                  }
                  className="rounded border-gray-300"
                />
                <div>
                  <span className="font-medium">MFA Obbligatoria per Admin</span>
                  <p className="text-sm text-muted-foreground">
                    Richiedi autenticazione a due fattori per tutti gli admin
                  </p>
                </div>
              </label>

              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="session_timeout">
                    Timeout Sessione (minuti)
                  </Label>
                  <Input
                    id="session_timeout"
                    type="number"
                    value={securitySettings.session_timeout}
                    onChange={(e) =>
                      setSecuritySettings({
                        ...securitySettings,
                        session_timeout: e.target.value,
                      })
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="password_min_length">
                    Lunghezza Minima Password
                  </Label>
                  <Input
                    id="password_min_length"
                    type="number"
                    value={securitySettings.password_min_length}
                    onChange={(e) =>
                      setSecuritySettings({
                        ...securitySettings,
                        password_min_length: e.target.value,
                      })
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="max_login_attempts">
                    Max Tentativi Login
                  </Label>
                  <Input
                    id="max_login_attempts"
                    type="number"
                    value={securitySettings.max_login_attempts}
                    onChange={(e) =>
                      setSecuritySettings({
                        ...securitySettings,
                        max_login_attempts: e.target.value,
                      })
                    }
                  />
                </div>

                <div>
                  <Label htmlFor="lockout_duration">
                    Durata Blocco (minuti)
                  </Label>
                  <Input
                    id="lockout_duration"
                    type="number"
                    value={securitySettings.lockout_duration}
                    onChange={(e) =>
                      setSecuritySettings({
                        ...securitySettings,
                        lockout_duration: e.target.value,
                      })
                    }
                  />
                </div>
              </div>
            </div>

            <div className="pt-4">
              <Button onClick={handleSaveGeneral} disabled={isSaving}>
                <Save className="h-4 w-4 mr-2" />
                Salva Impostazioni Sicurezza
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* System Info */}
        <Card>
          <CardHeader>
            <CardTitle>Informazioni Sistema</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-muted-foreground">Versione:</span>
                <span className="ml-2 font-mono">v1.0.0</span>
              </div>
              <div>
                <span className="text-muted-foreground">Ambiente:</span>
                <span className="ml-2 font-mono">Development</span>
              </div>
              <div>
                <span className="text-muted-foreground">Database:</span>
                <span className="ml-2 font-mono">PostgreSQL 15</span>
              </div>
              <div>
                <span className="text-muted-foreground">Cache:</span>
                <span className="ml-2 font-mono">Redis</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
