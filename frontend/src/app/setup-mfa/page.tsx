/**
 * Mandatory MFA Setup Page
 * Descrizione: Setup MFA obbligatorio per admin/editor
 * Autore: Claude per Davide
 * Data: 2026-01-16
 */

'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { Navigation } from '@/components/Navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Label } from '@/components/ui/label';
import apiClient, { getErrorMessage } from '@/lib/api-client';
import { QRCodeSVG } from 'qrcode.react';
import { Shield, ShieldCheck, ShieldAlert, Copy, Check, AlertTriangle } from 'lucide-react';

interface MFASetupResponse {
  secret: string;
  qr_code_url: string;
  backup_codes: string[];
}

export default function SetupMFAPage() {
  const router = useRouter();
  const { user, refreshUser } = useAuth();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Setup state
  const [step, setStep] = useState<'password' | 'qrcode' | 'complete'>('password');
  const [password, setPassword] = useState('');
  const [mfaSecret, setMfaSecret] = useState<string | null>(null);
  const [qrCodeUrl, setQrCodeUrl] = useState<string | null>(null);
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationToken, setVerificationToken] = useState('');
  const [copiedCodes, setCopiedCodes] = useState(false);

  // Check if user already has MFA or is not admin
  useEffect(() => {
    if (!user) return;

    // If MFA already enabled, redirect
    if (user.mfa_enabled) {
      router.push('/dashboard');
      return;
    }

    // If not admin/editor, redirect (MFA not mandatory)
    const requiresMFA = ['admin', 'super_admin', 'editor'].includes(user.role);
    if (!requiresMFA) {
      router.push('/dashboard');
    }
  }, [user, router]);

  /**
   * Start MFA Setup - Get QR code
   */
  const handleStartSetup = async () => {
    if (!password) {
      setError('Inserisci la tua password');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.post<MFASetupResponse>('/auth/mfa/setup', {
        password: password,
      });

      setMfaSecret(response.secret);
      setQrCodeUrl(response.qr_code_url);
      setBackupCodes(response.backup_codes);
      setStep('qrcode');
      setPassword(''); // Clear password
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
      await apiClient.post('/auth/mfa/enable', {
        token: verificationToken,
      });

      setSuccess('MFA abilitato con successo!');
      setStep('complete');
      await refreshUser();

      // Redirect after delay - to admin dashboard for admins
      setTimeout(() => {
        const isAdmin = ['admin', 'super_admin', 'editor'].includes(user?.role || '');
        router.push(isAdmin ? '/admin' : '/dashboard');
      }, 3000);
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

  if (!user) {
    return (
      <div className="min-h-screen">
        <Navigation />
        <div className="flex items-center justify-center pt-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navigation />
      <div className="flex items-center justify-center p-4 pt-20">
        <div className="w-full max-w-2xl">
          {/* Warning Banner */}
          <Alert className="mb-6 border-orange-500 bg-orange-50">
          <AlertTriangle className="h-5 w-5 text-orange-600" />
          <AlertDescription className="text-orange-900 font-medium">
            <strong>Setup obbligatorio:</strong> Come {user.role === 'super_admin' ? 'Super Admin' : user.role === 'admin' ? 'Admin' : 'Editor'},
            devi abilitare l'autenticazione a due fattori (MFA) per proteggere il tuo account.
          </AlertDescription>
        </Alert>

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

        {/* Step 1: Password Confirmation */}
        {step === 'password' && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <Shield className="h-8 w-8 text-primary" />
                <div>
                  <CardTitle>Abilita Autenticazione a Due Fattori</CardTitle>
                  <CardDescription>
                    Passo 1 di 3: Conferma la tua password
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">Cos'è l'MFA?</h3>
                <p className="text-sm text-blue-800">
                  L'autenticazione a due fattori aggiunge un ulteriore livello di sicurezza al tuo account.
                  Oltre alla password, dovrai inserire un codice temporaneo generato da un'app sul tuo smartphone.
                </p>
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Inserisci la tua password"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' && password) {
                      handleStartSetup();
                    }
                  }}
                />
                <p className="text-xs text-muted-foreground">
                  Inserisci la tua password per continuare con il setup MFA
                </p>
              </div>
            </CardContent>
            <CardFooter>
              <Button
                onClick={handleStartSetup}
                disabled={isLoading || !password}
                className="w-full"
              >
                {isLoading ? 'Verifica...' : 'Continua'}
              </Button>
            </CardFooter>
          </Card>
        )}

        {/* Step 2: QR Code and Verification */}
        {step === 'qrcode' && (
          <Card>
            <CardHeader>
              <CardTitle>Configura la tua App di Autenticazione</CardTitle>
              <CardDescription>
                Passo 2 di 3: Scansiona il QR code e verifica
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* QR Code */}
              {qrCodeUrl && (
                <div className="space-y-4">
                  <div>
                    <h3 className="font-medium mb-2">1. Scansiona il QR Code</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Usa Google Authenticator, Microsoft Authenticator, o Authy per scansionare:
                    </p>
                    <div className="flex justify-center p-6 bg-white border rounded-lg">
                      <QRCodeSVG value={qrCodeUrl} size={200} />
                    </div>
                  </div>

                  {/* Manual Entry */}
                  {mfaSecret && (
                    <div className="bg-muted p-4 rounded-lg">
                      <p className="text-sm font-medium mb-2">Oppure inserisci manualmente:</p>
                      <code className="text-xs bg-white px-2 py-1 rounded border break-all">
                        {mfaSecret}
                      </code>
                    </div>
                  )}

                  {/* Verification */}
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
                        className="flex-1 font-mono text-center text-lg"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter' && verificationToken.length === 6) {
                            handleEnableMFA();
                          }
                        }}
                      />
                      <Button onClick={handleEnableMFA} disabled={isLoading || verificationToken.length !== 6}>
                        {isLoading ? 'Verifica...' : 'Verifica'}
                      </Button>
                    </div>
                  </div>

                  {/* Backup Codes */}
                  {backupCodes.length > 0 && (
                    <div className="border-t pt-4">
                      <h3 className="font-medium mb-2 flex items-center gap-2">
                        3. Backup Codes (Importante!)
                        <ShieldAlert className="h-4 w-4 text-orange-500" />
                      </h3>
                      <Alert className="mb-4">
                        <AlertDescription>
                          <strong>Salva questi codici!</strong> Potrai usarli per accedere se perdi il tuo dispositivo.
                          Ogni codice può essere usato una sola volta.
                        </AlertDescription>
                      </Alert>
                      <div className="bg-muted p-4 rounded-lg space-y-2 max-h-48 overflow-y-auto">
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
          </Card>
        )}

        {/* Step 3: Complete */}
        {step === 'complete' && (
          <Card>
            <CardHeader>
              <div className="flex items-center gap-3">
                <ShieldCheck className="h-8 w-8 text-green-600" />
                <div>
                  <CardTitle>MFA Abilitato!</CardTitle>
                  <CardDescription>
                    Il tuo account è ora protetto con l'autenticazione a due fattori
                  </CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm text-green-900">
                  Al prossimo login, ti verrà chiesto di inserire sia la password che il codice dalla tua app di autenticazione.
                  Assicurati di aver salvato i backup codes in un luogo sicuro!
                </p>
              </div>
            </CardContent>
            <CardFooter>
              <p className="text-sm text-muted-foreground">
                Verrai reindirizzato alla dashboard tra pochi secondi...
              </p>
            </CardFooter>
          </Card>
        )}

          {/* Footer Info */}
          <div className="mt-6 text-center text-sm text-muted-foreground">
            <p>Hai bisogno di aiuto? Contatta il supporto tecnico</p>
          </div>
        </div>
      </div>
    </div>
  );
}
