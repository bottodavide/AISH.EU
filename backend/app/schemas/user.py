"""
Modulo: user.py
Descrizione: Pydantic schemas per users e profiles
Autore: Claude per Davide
Data: 2026-01-15
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import EmailStr, Field

from app.schemas.base import BaseSchema, UUIDTimestampSchema
from app.models.user import UserRole


# =============================================================================
# USER PROFILE SCHEMAS
# =============================================================================


class UserProfileBase(BaseSchema):
    """Base schema per user profile"""

    company_name: Optional[str] = Field(None, max_length=255, description="Ragione sociale")
    first_name: Optional[str] = Field(None, max_length=100, description="Nome")
    last_name: Optional[str] = Field(None, max_length=100, description="Cognome")
    phone: Optional[str] = Field(None, max_length=50, description="Telefono (deprecated)")
    phone_mobile: Optional[str] = Field(None, max_length=50, description="Telefono mobile/cellulare")
    phone_landline: Optional[str] = Field(None, max_length=50, description="Telefono fisso")
    vat_number: Optional[str] = Field(None, max_length=50, description="Partita IVA")
    tax_code: Optional[str] = Field(None, max_length=50, description="Codice Fiscale")
    rea_number: Optional[str] = Field(None, max_length=50, description="Numero REA (es: MI-1234567)")
    sdi_code: Optional[str] = Field(None, max_length=7, description="Codice SDI fatturazione elettronica")
    pec_email: Optional[EmailStr] = Field(None, description="Email PEC per fatture")
    avatar_url: Optional[str] = Field(None, max_length=500, description="URL avatar")


class UserProfileCreate(UserProfileBase):
    """Schema per creazione profile"""

    address_street: Optional[str] = Field(None, max_length=255, description="Indirizzo")
    address_city: Optional[str] = Field(None, max_length=100, description="Città")
    address_state: Optional[str] = Field(None, max_length=100, description="Provincia/Stato")
    address_postal_code: Optional[str] = Field(None, max_length=20, description="CAP")
    address_country: str = Field(default="IT", max_length=2, description="Codice paese (ISO 3166-1 alpha-2)")


class UserProfileUpdate(UserProfileBase):
    """Schema per update profile"""

    address_street: Optional[str] = Field(None, max_length=255, description="Indirizzo")
    address_city: Optional[str] = Field(None, max_length=100, description="Città")
    address_state: Optional[str] = Field(None, max_length=100, description="Provincia/Stato")
    address_postal_code: Optional[str] = Field(None, max_length=20, description="CAP")
    address_country: Optional[str] = Field(None, max_length=2, description="Codice paese")

    # Indirizzo fatturazione (se diverso da principale)
    billing_same_as_address: Optional[bool] = Field(None, description="Se indirizzo fatturazione = indirizzo principale")
    billing_street: Optional[str] = Field(None, max_length=255, description="Indirizzo fatturazione")
    billing_city: Optional[str] = Field(None, max_length=100, description="Città fatturazione")
    billing_state: Optional[str] = Field(None, max_length=100, description="Provincia fatturazione")
    billing_postal_code: Optional[str] = Field(None, max_length=20, description="CAP fatturazione")
    billing_country: Optional[str] = Field(None, max_length=2, description="Paese fatturazione")


class UserProfileResponse(UserProfileBase, UUIDTimestampSchema):
    """Schema per response profile"""

    user_id: UUID = Field(description="ID utente")
    address_street: Optional[str] = Field(None, description="Indirizzo")
    address_city: Optional[str] = Field(None, description="Città")
    address_state: Optional[str] = Field(None, description="Provincia/Stato")
    address_postal_code: Optional[str] = Field(None, description="CAP")
    address_country: Optional[str] = Field(None, description="Codice paese")
    billing_same_as_address: Optional[bool] = Field(None, description="Se indirizzo fatturazione = principale")
    billing_street: Optional[str] = Field(None, description="Indirizzo fatturazione")
    billing_city: Optional[str] = Field(None, description="Città fatturazione")
    billing_state: Optional[str] = Field(None, description="Provincia fatturazione")
    billing_postal_code: Optional[str] = Field(None, description="CAP fatturazione")
    billing_country: Optional[str] = Field(None, description="Paese fatturazione")
    avatar_url: Optional[str] = Field(None, description="URL avatar")


# =============================================================================
# USER SCHEMAS
# =============================================================================


class UserBase(BaseSchema):
    """Base schema per user"""

    email: EmailStr = Field(description="Email univoca")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="Ruolo utente")


class UserCreate(BaseSchema):
    """Schema per creazione user (admin only)"""

    email: EmailStr = Field(description="Email univoca")
    password: str = Field(min_length=8, description="Password")
    role: UserRole = Field(default=UserRole.CUSTOMER, description="Ruolo utente")
    is_active: bool = Field(default=True, description="Se account è attivo")
    is_email_verified: bool = Field(default=False, description="Se email è verificata")


class UserUpdate(BaseSchema):
    """Schema per update user"""

    email: Optional[EmailStr] = Field(None, description="Email")
    role: Optional[UserRole] = Field(None, description="Ruolo utente (admin only)")
    is_active: Optional[bool] = Field(None, description="Se account è attivo (admin only)")
    is_email_verified: Optional[bool] = Field(None, description="Se email è verificata (admin only)")


class UserResponse(UUIDTimestampSchema):
    """Schema per response user (dati pubblici)"""

    email: EmailStr = Field(description="Email")
    role: UserRole = Field(description="Ruolo utente")
    is_active: bool = Field(description="Se account è attivo")
    is_email_verified: bool = Field(description="Se email è verificata")
    mfa_enabled: bool = Field(description="Se MFA è abilitato")
    last_login: Optional[datetime] = Field(None, description="Ultimo login")

    # Dati profilo diretti per comodità (derivati da profile)
    first_name: Optional[str] = Field(None, description="Nome (da profile)")
    last_name: Optional[str] = Field(None, description="Cognome (da profile)")
    company_name: Optional[str] = Field(None, description="Ragione sociale (da profile)")

    # Include profile se disponibile (full details)
    profile: Optional[UserProfileResponse] = Field(None, description="Profilo utente completo")


class UserDetailResponse(UserResponse):
    """Schema per response user dettagliata (admin only o self)"""

    failed_login_attempts: int = Field(description="Tentativi login falliti")
    locked_until: Optional[datetime] = Field(None, description="Account locked fino a")
    last_login_ip: Optional[str] = Field(None, description="IP ultimo login")


class UserListResponse(BaseSchema):
    """Schema per lista users paginata"""

    users: list[UserResponse] = Field(description="Lista utenti")
    total: int = Field(description="Totale utenti")
    skip: int = Field(description="Offset paginazione")
    limit: int = Field(description="Limit paginazione")


# =============================================================================
# USER FILTERS
# =============================================================================


class UserFilters(BaseSchema):
    """Filtri per ricerca users"""

    email: Optional[str] = Field(None, description="Filtra per email (partial match)")
    role: Optional[UserRole] = Field(None, description="Filtra per ruolo")
    is_active: Optional[bool] = Field(None, description="Filtra per account attivi/inattivi")
    is_email_verified: Optional[bool] = Field(None, description="Filtra per email verificata")
    skip: int = Field(0, ge=0, description="Offset paginazione")
    limit: int = Field(100, ge=1, le=1000, description="Limit paginazione")


# =============================================================================
# CURRENT USER (ME)
# =============================================================================


class CurrentUserResponse(UserResponse):
    """Schema per current user (GET /me)"""

    # Include più dettagli per utente corrente
    failed_login_attempts: int = Field(description="Tentativi login falliti")


class UpdateCurrentUserRequest(BaseSchema):
    """Schema per update current user (PUT /me)"""

    email: Optional[EmailStr] = Field(None, description="Nuova email (richiede re-verifica)")

    # Profile fields
    first_name: Optional[str] = Field(None, max_length=100, description="Nome")
    last_name: Optional[str] = Field(None, max_length=100, description="Cognome")
    company_name: Optional[str] = Field(None, max_length=255, description="Ragione sociale")
    phone_mobile: Optional[str] = Field(None, max_length=50, description="Telefono mobile")
    phone_landline: Optional[str] = Field(None, max_length=50, description="Telefono fisso")
    vat_number: Optional[str] = Field(None, max_length=50, description="Partita IVA")
    tax_code: Optional[str] = Field(None, max_length=50, description="Codice Fiscale")
    rea_number: Optional[str] = Field(None, max_length=50, description="Numero REA")
    sdi_code: Optional[str] = Field(None, max_length=7, description="Codice SDI")
    pec_email: Optional[EmailStr] = Field(None, description="Email PEC")
    legal_address: Optional[dict] = Field(None, description="Indirizzo sede legale")
    operational_address: Optional[dict] = Field(None, description="Indirizzo sede operativa")
    avatar_url: Optional[str] = Field(None, description="URL avatar")


# =============================================================================
# ADMIN USER MANAGEMENT
# =============================================================================


class UserActivateRequest(BaseSchema):
    """Request per attivare/disattivare user"""

    is_active: bool = Field(description="Attiva (true) o disattiva (false) account")
    reason: Optional[str] = Field(None, max_length=500, description="Motivo attivazione/disattivazione")


class UserRoleChangeRequest(BaseSchema):
    """Request per cambio ruolo user (super admin only)"""

    role: UserRole = Field(description="Nuovo ruolo")
    reason: Optional[str] = Field(None, max_length=500, description="Motivo cambio ruolo")


class UserDeleteRequest(BaseSchema):
    """Request per eliminazione user"""

    confirm: bool = Field(description="Conferma eliminazione (deve essere true)")
    reason: Optional[str] = Field(None, max_length=500, description="Motivo eliminazione")


# =============================================================================
# USER STATISTICS (ADMIN)
# =============================================================================


class UserStatistics(BaseSchema):
    """Statistiche users (admin dashboard)"""

    total_users: int = Field(description="Totale utenti")
    active_users: int = Field(description="Utenti attivi")
    inactive_users: int = Field(description="Utenti inattivi")
    verified_users: int = Field(description="Utenti con email verificata")
    unverified_users: int = Field(description="Utenti con email non verificata")
    users_with_mfa: int = Field(description="Utenti con MFA abilitato")
    users_by_role: dict[str, int] = Field(description="Utenti per ruolo")
    new_users_last_30_days: int = Field(description="Nuovi utenti ultimi 30 giorni")
