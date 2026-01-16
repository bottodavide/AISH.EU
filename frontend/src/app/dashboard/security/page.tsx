/**
 * Security Settings Page
 * Descrizione: Gestione MFA (Multi-Factor Authentication)
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Label } from '@/components/ui/label';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { QRCodeSVG } from 'qrcode.react';
import { Shield, ShieldCheck, ShieldAlert, Copy, Check } from 'lucide-react';

// =============================================================================
// TYPES
// =============================================================================

interface MFASetupResponse {
  secret: string;
  qr_code_url: string;
  backup_codes: string[];
}

// =============================================================================
// COMPONENT
// =============================================================================

export default function SecurityPage() {
  const { user, refreshUser } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // MFA Setup State
  const [showSetup, setShowSetup] = useState(false);
  const [mfaSecret, setMfaSecret] = useState<string | null>(null);
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationToken, setVerificationToken] = useState('');

  // MFA Disable State
  const [showDisable, setShowDisable] = useState(false);
  const [disablePassword, setDisablePassword] = useState('');
  const [disableToken, setDisableToken] = useState('');

  // Backup codes copied state
  const [copiedCodes, setCopiedCodes] = useState(false);

  /**
   * Start MFA Setup - Get QR code
   */
  const handleStartSetup = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.post<MFASetupResponse>('/api/v1/auth/mfa/setup', {
        password: '', // Backend doesn't require password for setup, only for enable
      });

      setMfaSecret(response.secret);
      setQrCodeUrl(response.qr_code_url);
      setBackupCodes(response.backup_codes);
      setShowSetup(true);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Complete MFA Setup - Verify token and enable
   */
  const handleEnableMFA = async () => {
    if (!verificationToken || verificationToken.length !== 6) {
      setError('Inserisci un codice di 6 cifre');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.post('/api/v1/auth/mfa/enable', {
        token: verificationToken,
      });

      setSuccess('MFA abilitato con successo! Salva i backup codes in un luogo sicuro.');
      await refreshUser();

      // Reset setup state after a delay
      setTimeout(() => {
        setShowSetup(false);
        setMfaSecret(null);
        setQrCodeUrl(null);
        setVerificationToken('');
      }, 5000);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Disable MFA
   */
  const handleDisableMFA = async () => {
    if (!disablePassword) {
      setError('Inserisci la tua password');
      return;
    }

    if (!disableToken || disableToken.length !== 6) {
      setError('Inserisci un codice di 6 cifre');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await apiClient.post('/api/v1/auth/mfa/disable', {
        password: disablePassword,
        token: disableToken,
      });

      setSuccess('MFA disabilitato con successo');
      setShowDisable(false);
      setDisablePassword('');
      setDisableToken('');
      setBackupCodes([]);
      await refreshUser();
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Copy backup codes to clipboard
   */
  const handleCopyBackupCodes = () => {
    const codesText = backupCodes.join('\n');
    navigator.clipboard.writeText(codesText);
    setCopiedCodes(true);
    setTimeout(() => setCopiedCodes(false), 2000);
  };

  /**
   * Cancel setup
   */
  const handleCancelSetup = () => {
    setShowSetup(false);
    setMfaSecret(null);
    setQrCodeUrl(null);
    setBackupCodes([]);
    setVerificationToken('');
    setError(null);
  };

  // =============================================================================
  // RENDER
  // =============================================================================

  return (
    <div className="container max-w-4xl py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Impostazioni di Sicurezza</h1>
        <p className="text-muted-foreground">
          Gestisci l'autenticazione a due fattori per proteggere il tuo account
        </p>
      </div>

      {/* Success Alert */}
      {success && (
        <Alert className="mb-6 border-green-500 bg-green-50">
          <ShieldCheck className="h-4 w-4 text-green-600" />
          <AlertDescription className="text-green-800">{success}</AlertDescription>
        </Alert>
      )}

      {/* Error Alert */}
      {error && (
        <Alert variant="destructive" className="mb-6">
          <ShieldAlert className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* MFA Status Card */}
      {!showSetup && !showDisable && (
        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              {user?.mfa_enabled ? (
                <ShieldCheck className="h-6 w-6 text-green-600" />
              ) : (
                <Shield className="h-6 w-6 text-muted-foreground" />
              )}
              <div>
                <CardTitle>Autenticazione a Due Fattori (MFA)</CardTitle>
                <CardDescription>
                  {user?.mfa_enabled
                    ? 'Il tuo account è protetto con MFA'
                    : 'Aumenta la sicurezza del tuo account abilitando MFA'}
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <p className="font-medium">Stato MFA</p>
                  <p className="text-sm text-muted-foreground">
                    {user?.mfa_enabled ? (
                      <span className="text-green-600">Abilitato</span>
                    ) : (
                      <span className="text-muted-foreground">Disabilitato</span>
                    )}
                  </p>
                </div>
                {user?.mfa_enabled ? (
                  <Button variant="outline" onClick={() => setShowDisable(true)}>
                    Disabilita MFA
                  </Button>
                ) : (
                  <Button onClick={handleStartSetup} disabled={isLoading}>
                    {isLoading ? 'Caricamento...' : 'Abilita MFA'}
                  </Button>
                )}
              </div>

              {!user?.mfa_enabled && (
                <div className="bg-muted p-4 rounded-lg">
                  <h3 className="font-medium mb-2">Cos'è l'MFA?</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    L'autenticazione a due fattori aggiunge un ulteriore livello di sicurezza richiedendo
                    un codice temporaneo dal tuo smartphone oltre alla password.
                  </p>
                  <ul className="text-sm text-muted-foreground space-y-1">
                    <li>• Protegge il tuo account anche se la password viene compromessa</li>
                    <li>• Usa app come Google Authenticator, Microsoft Authenticator o Authy</li>
                    <li>• Riceverai backup codes per accedere se perdi il telefono</li>
                  </ul>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* MFA Setup Flow */}
      {showSetup && !user?.mfa_enabled && (
        <Card>
          <CardHeader>
            <CardTitle>Configura Autenticazione a Due Fattori</CardTitle>
            <CardDescription>
              Segui questi passaggi per abilitare MFA sul tuo account
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Step 1: Scan QR Code */}
            {qrCodeUrl && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-medium mb-2">1. Scansiona il QR Code</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Usa la tua app di autenticazione (Google Authenticator, Microsoft Authenticator, Authy)
                    per scansionare questo codice QR:
                  </p>
                  <div className="flex justify-center p-6 bg-white border rounded-lg">
                    <QRCodeSVG value={qrCodeUrl} size={200} />
                  </div>
                </div>

                {/* Manual Entry Option */}
                {mfaSecret && (
                  <div className="bg-muted p-4 rounded-lg">
                    <p className="text-sm font-medium mb-2">Oppure inserisci manualmente:</p>
                    <code className="text-xs bg-white px-2 py-1 rounded border">
                      {mfaSecret}
                    </code>
                  </div>
                )}

                {/* Step 2: Verify Token */}
                <div>
                  <h3 className="font-medium mb-2">2. Verifica il Codice</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    Inserisci il codice di 6 cifre mostrato nella tua app:
                  </p>
                  <div className="flex gap-2">
                    <Input
                      type="text"
                      placeholder="000000"
                      maxLength={6}
                      value={verificationToken}
                      onChange={(e) => setVerificationToken(e.target.value.replace(/\D/g, ''))}
                      className="max-w-xs font-mono text-center text-lg"
                    />
                    <Button onClick={handleEnableMFA} disabled={isLoading || verificationToken.length !== 6}>
                      {isLoading ? 'Verifica...' : 'Verifica e Abilita'}
                    </Button>
                  </div>
                </div>

                {/* Step 3: Backup Codes */}
                {backupCodes.length > 0 && (
                  <div>
                    <h3 className="font-medium mb-2 flex items-center gap-2">
                      3. Salva i Backup Codes
                      <ShieldAlert className="h-4 w-4 text-orange-500" />
                    </h3>
                    <Alert className="mb-4">
                      <AlertDescription>
                        <strong>Importante:</strong> Questi codici possono essere usati una sola volta per
                        accedere se perdi il tuo dispositivo. Salvali in un luogo sicuro!
                      </AlertDescription>
                    </Alert>
                    <div className="bg-muted p-4 rounded-lg space-y-2">
                      {backupCodes.map((code, index) => (
                        <code key={index} className="block text-sm font-mono">
                          {code}
                        </code>
                      ))}
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      className="mt-2"
                      onClick={handleCopyBackupCodes}
                    >
                      {copiedCodes ? (
                        <>
                          <Check className="h-4 w-4 mr-2" />
                          Copiato!
                        </>
                      ) : (
                        <>
                          <Copy className="h-4 w-4 mr-2" />
                          Copia Codici
                        </>
                      )}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </CardContent>
          <CardFooter>
            <Button variant="outline" onClick={handleCancelSetup}>
              Annulla
            </Button>
          </CardFooter>
        </Card>
      )}

      {/* MFA Disable Flow */}
      {showDisable && user?.mfa_enabled && (
        <Card>
          <CardHeader>
            <CardTitle>Disabilita Autenticazione a Due Fattori</CardTitle>
            <CardDescription>
              Per disabilitare MFA, inserisci la tua password e un codice dalla tua app
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <ShieldAlert className="h-4 w-4" />
              <AlertDescription>
                Disabilitare MFA ridurrà la sicurezza del tuo account. Procedi solo se sei sicuro.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label htmlFor="disable-password">Password</Label>
              <Input
                id="disable-password"
                type="password"
                value={disablePassword}
                onChange={(e) => setDisablePassword(e.target.value)}
                placeholder="Inserisci la tua password"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="disable-token">Codice MFA</Label>
              <Input
                id="disable-token"
                type="text"
                maxLength={6}
                value={disableToken}
                onChange={(e) => setDisableToken(e.target.value.replace(/\D/g, ''))}
                placeholder="000000"
                className="font-mono text-center text-lg"
              />
            </div>
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button variant="outline" onClick={() => setShowDisable(false)}>
              Annulla
            </Button>
            <Button
              variant="destructive"
              onClick={handleDisableMFA}
              disabled={isLoading || !disablePassword || disableToken.length !== 6}
            >
              {isLoading ? 'Disabilitazione...' : 'Disabilita MFA'}
            </Button>
          </CardFooter>
        </Card>
      )}
    </div>
  );
}
