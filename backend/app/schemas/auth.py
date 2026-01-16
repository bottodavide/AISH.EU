"""
Modulo: auth.py
Descrizione: Pydantic schemas per autenticazione e autorizzazione
Autore: Claude per Davide
Data: 2026-01-15
"""

from typing import Optional

from pydantic import EmailStr, Field, field_validator

from app.schemas.base import BaseSchema
from app.models.user import UserRole


# =============================================================================
# AUTHENTICATION REQUESTS
# =============================================================================


class LoginRequest(BaseSchema):
    """Request per login"""

    email: EmailStr = Field(description="Email utente")
    password: str = Field(min_length=1, description="Password")
    mfa_token: Optional[str] = Field(None, min_length=6, max_length=6, description="Token MFA (se abilitato)")


class RefreshTokenRequest(BaseSchema):
    """Request per refresh token"""

    refresh_token: str = Field(description="Refresh token JWT")


class MFAVerifyRequest(BaseSchema):
    """Request per verifica MFA"""

    token: str = Field(min_length=6, max_length=6, description="Token TOTP 6 cifre")


class MFABackupCodeRequest(BaseSchema):
    """Request per uso backup code MFA"""

    backup_code: str = Field(min_length=8, max_length=8, description="Backup code 8 caratteri")


# =============================================================================
# REGISTRATION
# =============================================================================


class RegisterRequest(BaseSchema):
    """Request per registrazione nuovo utente"""

    email: EmailStr = Field(description="Email utente (deve essere univoca)")
    password: str = Field(min_length=8, description="Password")
    confirm_password: str = Field(min_length=8, description="Conferma password")
    first_name: str = Field(min_length=1, max_length=100, description="Nome (obbligatorio)")
    last_name: str = Field(min_length=1, max_length=100, description="Cognome (obbligatorio)")
    company_name: Optional[str] = Field(None, max_length=255, description="Ragione sociale (opzionale)")
    accept_terms: bool = Field(description="Accettazione termini e condizioni")
    accept_privacy: bool = Field(description="Accettazione privacy policy")

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Valida che password e confirm_password coincidano"""
        password = info.data.get("password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Valida complessità password.

        Requirements:
        - Min 8 caratteri
        - Almeno 1 maiuscola
        - Almeno 1 numero
        - Almeno 1 carattere speciale
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")

        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one number")

        # Check for special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in v):
            raise ValueError("Password must contain at least one special character")

        return v

    @field_validator("accept_terms", "accept_privacy")
    @classmethod
    def must_accept(cls, v: bool) -> bool:
        """Valida che termini e privacy siano accettati"""
        if not v:
            raise ValueError("You must accept terms and privacy policy")
        return v


# =============================================================================
# PASSWORD MANAGEMENT
# =============================================================================


class PasswordResetRequest(BaseSchema):
    """Request per reset password"""

    email: EmailStr = Field(description="Email utente")


class PasswordResetConfirm(BaseSchema):
    """Request per conferma reset password"""

    token: str = Field(description="Token di reset")
    new_password: str = Field(min_length=8, description="Nuova password")
    confirm_password: str = Field(min_length=8, description="Conferma nuova password")

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Valida che password e confirm_password coincidano"""
        password = info.data.get("new_password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v


class PasswordChangeRequest(BaseSchema):
    """Request per cambio password (utente autenticato)"""

    current_password: str = Field(description="Password corrente")
    new_password: str = Field(min_length=8, description="Nuova password")
    confirm_password: str = Field(min_length=8, description="Conferma nuova password")

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        """Valida che password e confirm_password coincidano"""
        password = info.data.get("new_password")
        if password and v != password:
            raise ValueError("Passwords do not match")
        return v


# =============================================================================
# EMAIL VERIFICATION
# =============================================================================


class EmailVerificationRequest(BaseSchema):
    """Request per verifica email"""

    token: str = Field(description="Token di verifica email")


class ResendVerificationRequest(BaseSchema):
    """Request per re-invio email di verifica"""

    email: EmailStr = Field(description="Email utente")


# =============================================================================
# MFA MANAGEMENT
# =============================================================================


class MFAEnableRequest(BaseSchema):
    """Request per abilitazione MFA"""

    password: str = Field(description="Password corrente per conferma")


class MFAEnableConfirm(BaseSchema):
    """Request per conferma abilitazione MFA"""

    token: str = Field(min_length=6, max_length=6, description="Token TOTP per verifica setup")


class MFADisableRequest(BaseSchema):
    """Request per disabilitazione MFA"""

    password: str = Field(description="Password corrente per conferma")
    token: str = Field(min_length=6, max_length=6, description="Token TOTP corrente")


# =============================================================================
# AUTHENTICATION RESPONSES
# =============================================================================


class TokenResponse(BaseSchema):
    """Response con JWT tokens"""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Tipo token")
    expires_in: int = Field(description="Durata access token (secondi)")


class MFASetupResponse(BaseSchema):
    """Response per setup MFA"""

    secret: str = Field(description="MFA secret (base32)")
    qr_code_url: str = Field(description="URL QR code per app authenticator")
    backup_codes: list[str] = Field(description="Backup codes (mostrati UNA SOLA VOLTA)")


class MFARequiredResponse(BaseSchema):
    """Response quando MFA è richiesto"""

    mfa_required: bool = True
    message: str = "MFA verification required"


class LoginResponse(BaseSchema):
    """Response completa per login"""

    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Tipo token")
    expires_in: int = Field(description="Durata access token (secondi)")
    user: dict = Field(description="Dati utente")


# =============================================================================
# SESSION MANAGEMENT
# =============================================================================


class ActiveSession(BaseSchema):
    """Informazioni sessione attiva"""

    session_id: str = Field(description="ID sessione")
    ip_address: Optional[str] = Field(None, description="IP address")
    user_agent: Optional[str] = Field(None, description="User agent")
    created_at: str = Field(description="Data creazione sessione")
    expires_at: str = Field(description="Data scadenza sessione")
    is_current: bool = Field(description="Se è la sessione corrente")


class SessionListResponse(BaseSchema):
    """Lista sessioni attive"""

    sessions: list[ActiveSession] = Field(description="Sessioni attive")
    total: int = Field(description="Numero totale sessioni")
