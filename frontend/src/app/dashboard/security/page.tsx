/**
 * Security Settings Page
 * Descrizione: Gestione sicurezza account - MFA, password, sessioni
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useEffect, useState } from 'react';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@/contexts/AuthContext';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { Shield, Smartphone, Key, Lock, CheckCircle, Copy, Download } from 'lucide-react';
import Image from 'next/image';

interface MFASetupResponse {
  secret: string;
  qr_code_url: string;
  backup_codes: string[];
}

export default function SecurityPage() {
  const { user, isAuthenticated } = useAuth();

  // MFA State
  const [mfaEnabled, setMfaEnabled] = useState(false);
  const [isSettingUpMFA, setIsSettingUpMFA] = useState(false);
  const [mfaSetupData, setMfaSetupData] = useState<MFASetupResponse | null>(null);
  const [mfaToken, setMfaToken] = useState('');
  const [showBackupCodes, setShowBackupCodes] = useState(false);

  // Password Change State
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  });

  // UI State
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user) {
      setMfaEnabled(user.mfa_enabled || false);
    }
  }, [isAuthenticated, user]);

  // =============================================================================
  // MFA SETUP
  // =============================================================================

  const handleStartMFASetup = async () => {
    setError(null);
    setSuccess(null);
    setIsLoading(true);

    try {
      // Chiedi password per conferma
      const password = prompt('Inserisci la tua password per continuare:');
      if (!password) {
        setIsLoading(false);
        return;
      }

      // Call setup endpoint
      const response = await apiClient.post<MFASetupResponse>('/api/v1/auth/mfa/setup', {
        password,
      });

      setMfaSetupData(response);
      setIsSettingUpMFA(true);
      setShowBackupCodes(true);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleEnableMFA = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setIsLoading(true);

    try {
      await apiClient.post('/api/v1/auth/mfa/enable', {
        token: mfaToken,
      });

      setMfaEnabled(true);
      setIsSettingUpMFA(false);
      setSuccess('MFA abilitato con successo! Il tuo account è ora più sicuro.');
      setMfaToken('');
      setShowBackupCodes(false);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleDisableMFA = async () => {
    setError(null);
    setSuccess(null);

    // Conferma
    const confirmed = confirm(
      'Sei sicuro di voler disabilitare MFA? Il tuo account sarà meno sicuro.'
    );
    if (!confirmed) return;

    const password = prompt('Inserisci la tua password per confermare:');
    if (!password) return;

    const token = prompt('Inserisci il codice MFA corrente:');
    if (!token) return;

    setIsLoading(true);

    try {
      await apiClient.post('/api/v1/auth/mfa/disable', {
        password,
        token,
      });

      setMfaEnabled(false);
      setMfaSetupData(null);
      setSuccess('MFA disabilitato con successo.');
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCopyBackupCodes = () => {
    if (mfaSetupData?.backup_codes) {
      const text = mfaSetupData.backup_codes.join('\n');
      navigator.clipboard.writeText(text);
      setSuccess('Backup codes copiati negli appunti');
    }
  };

  const handleDownloadBackupCodes = () => {
    if (mfaSetupData?.backup_codes) {
      const text = mfaSetupData.backup_codes.join('\n');
      const blob = new Blob([text], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'aistrategyhub-mfa-backup-codes.txt';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      setSuccess('Backup codes scaricati');
    }
  };

  // =============================================================================
  // PASSWORD CHANGE
  // =============================================================================

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    // Validate passwords match
    if (passwordData.new_password !== passwordData.confirm_password) {
      setError('Le password non corrispondono');
      return;
    }

    setIsLoading(true);

    try {
      await apiClient.post('/api/v1/auth/password-change', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      });

      setSuccess('Password cambiata con successo');
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <Navigation />
      <main className="container py-12 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Sicurezza</h1>
          <p className="text-muted-foreground">
            Gestisci le impostazioni di sicurezza del tuo account
          </p>
        </div>

        {/* Global Alerts */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {success && (
          <Alert className="mb-6 border-green-500/50 text-green-700 dark:text-green-400">
            <AlertDescription className="flex items-center gap-2">
              <CheckCircle className="h-4 w-4" />
              {success}
            </AlertDescription>
          </Alert>
        )}

        <div className="space-y-6">
          {/* MFA Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Smartphone className="h-5 w-5" />
                Autenticazione a Due Fattori (MFA)
              </CardTitle>
              <CardDescription>
                Aggiungi un ulteriore livello di sicurezza al tuo account richiedendo un codice
                temporaneo oltre alla password
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* MFA Status */}
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">
                    Stato MFA:{' '}
                    {mfaEnabled ? (
                      <span className="text-green-600">Abilitato</span>
                    ) : (
                      <span className="text-muted-foreground">Disabilitato</span>
                    )}
                  </p>
                  <p className="text-sm text-muted-foreground mt-1">
                    {mfaEnabled
                      ? 'Il tuo account è protetto da MFA'
                      : 'Abilita MFA per una maggiore sicurezza'}
                  </p>
                </div>
                {!mfaEnabled && !isSettingUpMFA && (
                  <Button onClick={handleStartMFASetup} disabled={isLoading}>
                    <Shield className="h-4 w-4 mr-2" />
                    Abilita MFA
                  </Button>
                )}
                {mfaEnabled && (
                  <Button variant="outline" onClick={handleDisableMFA} disabled={isLoading}>
                    Disabilita MFA
                  </Button>
                )}
              </div>

              {/* MFA Setup Flow */}
              {isSettingUpMFA && mfaSetupData && (
                <div className="space-y-6 p-6 border-2 border-primary rounded-lg bg-primary/5">
                  <div className="text-center">
                    <h3 className="text-xl font-semibold mb-2">
                      Configura Autenticazione a Due Fattori
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Segui i passaggi seguenti per abilitare MFA
                    </p>
                  </div>

                  {/* Step 1: QR Code */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-bold">
                        1
                      </div>
                      <h4 className="font-semibold">Scansiona il codice QR</h4>
                    </div>
                    <p className="text-sm text-muted-foreground ml-10">
                      Usa un'app di autenticazione come Google Authenticator, Authy o Microsoft
                      Authenticator per scansionare il codice QR
                    </p>
                    <div className="ml-10 flex justify-center p-4 bg-white rounded-lg">
                      <Image
                        src={mfaSetupData.qr_code_url}
                        alt="QR Code MFA"
                        width={200}
                        height={200}
                      />
                    </div>
                    <div className="ml-10 p-3 bg-muted rounded-lg">
                      <p className="text-xs font-mono break-all">{mfaSetupData.secret}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Codice segreto (se non riesci a scansionare il QR)
                      </p>
                    </div>
                  </div>

                  {/* Step 2: Backup Codes */}
                  {showBackupCodes && (
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-bold">
                          2
                        </div>
                        <h4 className="font-semibold">Salva i codici di backup</h4>
                      </div>
                      <Alert className="ml-10">
                        <AlertDescription>
                          <p className="font-medium mb-2">
                            Salva questi codici in un luogo sicuro!
                          </p>
                          <p className="text-sm">
                            Potrai usarli per accedere al tuo account se perdi l'accesso
                            all'app di autenticazione. Ogni codice può essere usato una sola volta.
                          </p>
                        </AlertDescription>
                      </Alert>
                      <div className="ml-10 p-4 bg-muted rounded-lg font-mono text-sm space-y-1">
                        {mfaSetupData.backup_codes.map((code, idx) => (
                          <div key={idx}>{code}</div>
                        ))}
                      </div>
                      <div className="ml-10 flex gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleCopyBackupCodes}
                        >
                          <Copy className="h-4 w-4 mr-2" />
                          Copia
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={handleDownloadBackupCodes}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Scarica
                        </Button>
                      </div>
                    </div>
                  )}

                  {/* Step 3: Verify */}
                  <form onSubmit={handleEnableMFA} className="space-y-3">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-primary-foreground font-bold">
                        3
                      </div>
                      <h4 className="font-semibold">Verifica il codice</h4>
                    </div>
                    <p className="text-sm text-muted-foreground ml-10">
                      Inserisci il codice a 6 cifre generato dalla tua app di autenticazione
                    </p>
                    <div className="ml-10 space-y-2">
                      <Label htmlFor="mfa_token">Codice MFA</Label>
                      <Input
                        id="mfa_token"
                        type="text"
                        placeholder="123456"
                        value={mfaToken}
                        onChange={(e) => setMfaToken(e.target.value)}
                        maxLength={6}
                        required
                        className="max-w-xs"
                      />
                    </div>
                    <div className="ml-10 flex gap-2">
                      <Button type="submit" disabled={isLoading || mfaToken.length !== 6}>
                        {isLoading ? 'Verifica...' : 'Abilita MFA'}
                      </Button>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                          setIsSettingUpMFA(false);
                          setMfaSetupData(null);
                          setMfaToken('');
                        }}
                      >
                        Annulla
                      </Button>
                    </div>
                  </form>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Password Change Section */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lock className="h-5 w-5" />
                Cambia Password
              </CardTitle>
              <CardDescription>
                Aggiorna la tua password per mantenere il tuo account sicuro
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePasswordChange} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="current_password">Password Corrente</Label>
                  <Input
                    id="current_password"
                    type="password"
                    value={passwordData.current_password}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, current_password: e.target.value })
                    }
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new_password">Nuova Password</Label>
                  <Input
                    id="new_password"
                    type="password"
                    value={passwordData.new_password}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, new_password: e.target.value })
                    }
                    required
                  />
                  <p className="text-xs text-muted-foreground">
                    Min 8 caratteri, 1 maiuscola, 1 numero, 1 carattere speciale
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Conferma Nuova Password</Label>
                  <Input
                    id="confirm_password"
                    type="password"
                    value={passwordData.confirm_password}
                    onChange={(e) =>
                      setPasswordData({ ...passwordData, confirm_password: e.target.value })
                    }
                    required
                  />
                </div>

                <Button type="submit" disabled={isLoading}>
                  <Key className="h-4 w-4 mr-2" />
                  {isLoading ? 'Aggiornamento...' : 'Aggiorna Password'}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </>
  );
}
