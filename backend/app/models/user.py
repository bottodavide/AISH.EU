"""
Modulo: user.py
Descrizione: Modelli SQLAlchemy per utenti, autenticazione e sessioni
Autore: Claude per Davide
Data: 2026-01-15

Modelli inclusi:
- User: Utente principale con credenziali e MFA
- UserProfile: Dati anagrafici e fatturazione
- Session: Sessioni JWT (access + refresh tokens)
- LoginAttempt: Log tentativi login per security

Note sulla sicurezza:
- Password hashate con Argon2 (mai in chiaro)
- MFA (TOTP) con backup codes
- Email verification obbligatoria
- Tracking login attempts per prevenire brute force
"""

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

# Setup logger per questo modulo
logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

import enum


class UserRole(str, enum.Enum):
    """
    Ruoli utente per sistema RBAC.

    Livelli di accesso (dal più alto al più basso):
    - SUPER_ADMIN: Accesso completo, può modificare settings critici
    - ADMIN: Gestione utenti, ordini, fatture, tutto eccetto settings
    - EDITOR: Solo CMS e blog, view-only per fatture
    - SUPPORT: Solo tickets e view utenti
    - CUSTOMER: Area cliente standard
    - GUEST: Utente non registrato (limitato)
    """

    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    EDITOR = "editor"
    SUPPORT = "support"
    CUSTOMER = "customer"
    GUEST = "guest"


# =============================================================================
# USER MODEL
# =============================================================================


class User(Base, UUIDMixin, TimestampMixin):
    """
    Modello User principale.

    Gestisce:
    - Credenziali login (email + password hash)
    - Email verification
    - Multi-Factor Authentication (TOTP)
    - Ruoli e permessi (RBAC)
    - Status attivo/sospeso

    Relationships:
    - profile: UserProfile (1-to-1)
    - sessions: Session[] (1-to-many)
    - login_attempts: LoginAttempt[] (1-to-many)
    - orders, invoices, tickets, etc. (vedi modelli relativi)

    Security:
    - Password DEVE essere hashata con Argon2 prima di salvare
    - MFA raccomandato per admin e editor
    - Email verification obbligatoria per attivazione account
    """

    __tablename__ = "users"

    # -------------------------------------------------------------------------
    # Credenziali
    # -------------------------------------------------------------------------

    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Email univoca per login",
    )

    password_hash = Column(
        String(255),
        nullable=False,
        comment="Password hash con Argon2 (NEVER in chiaro!)",
    )

    # -------------------------------------------------------------------------
    # Ruolo e Permessi
    # -------------------------------------------------------------------------

    role = Column(
        Enum(UserRole),
        nullable=False,
        default=UserRole.CUSTOMER,
        index=True,
        comment="Ruolo RBAC per controllo accessi",
    )

    # -------------------------------------------------------------------------
    # Status Account
    # -------------------------------------------------------------------------

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Account attivo (False = sospeso)",
    )

    email_verified = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Email verificata (richiesto per login)",
    )

    email_verification_token = Column(
        String(255),
        nullable=True,
        unique=True,
        index=True,
        comment="Token verifica email (time-limited)",
    )

    email_verification_expires = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Scadenza token verifica email",
    )

    # -------------------------------------------------------------------------
    # Multi-Factor Authentication (MFA)
    # -------------------------------------------------------------------------

    mfa_enabled = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="MFA TOTP abilitato",
    )

    mfa_secret = Column(
        String(255),
        nullable=True,
        comment="Secret TOTP per MFA (encrypted in production)",
    )

    backup_codes = Column(
        ARRAY(String),
        nullable=True,
        comment="Backup codes per recovery MFA (hashed)",
    )

    # -------------------------------------------------------------------------
    # Login Tracking
    # -------------------------------------------------------------------------

    last_login = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp ultimo login successo",
    )

    last_login_ip = Column(
        INET,
        nullable=True,
        comment="IP ultimo login successo",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    # One-to-One con UserProfile
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # One-to-Many con Session
    sessions = relationship(
        "Session",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # One-to-Many con LoginAttempt
    login_attempts = relationship(
        "LoginAttempt",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )

    # TODO: Aggiungere relationships con:
    # - orders, invoices, tickets, notifications, etc.

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_users_email_active", "email", "is_active"),
        Index("ix_users_role_active", "role", "is_active"),
        {"comment": "Tabella utenti con autenticazione e MFA"},
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"


# =============================================================================
# USER PROFILE MODEL
# =============================================================================


class UserProfile(Base, UUIDMixin, TimestampMixin):
    """
    Profilo utente con dati anagrafici e fatturazione.

    Separato da User per:
    - Performance (User table più leggera per auth)
    - Privacy (dati sensibili separati)
    - Normalizzazione (dati non necessari per ogni query)

    Relationships:
    - user: User (1-to-1)

    GDPR:
    - Contiene dati personali sensibili
    - Eliminazione account DEVE eliminare anche profile
    - Export dati DEVE includere profile
    """

    __tablename__ = "user_profiles"

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="FK a users (one-to-one)",
    )

    # -------------------------------------------------------------------------
    # Dati Anagrafici
    # -------------------------------------------------------------------------

    first_name = Column(
        String(100),
        nullable=True,
        comment="Nome",
    )

    last_name = Column(
        String(100),
        nullable=True,
        comment="Cognome",
    )

    phone = Column(
        String(20),
        nullable=True,
        comment="Telefono (formato internazionale)",
    )

    # -------------------------------------------------------------------------
    # Dati Azienda (opzionali per B2B)
    # -------------------------------------------------------------------------

    company_name = Column(
        String(255),
        nullable=True,
        comment="Ragione sociale (B2B)",
    )

    vat_number = Column(
        String(20),
        nullable=True,
        index=True,
        comment="Partita IVA (formato: ITXXXXXXXXXXX)",
    )

    fiscal_code = Column(
        String(16),
        nullable=True,
        comment="Codice Fiscale italiano",
    )

    # -------------------------------------------------------------------------
    # Fatturazione Elettronica
    # -------------------------------------------------------------------------

    pec_email = Column(
        String(255),
        nullable=True,
        comment="Email PEC per fatture elettroniche",
    )

    sdi_code = Column(
        String(7),
        nullable=True,
        comment="Codice SDI destinatario (7 caratteri)",
    )

    # -------------------------------------------------------------------------
    # Indirizzo Fatturazione
    # -------------------------------------------------------------------------

    billing_address = Column(
        JSONB,
        nullable=True,
        comment="Indirizzo fatturazione (JSON: street, city, zip, province, country)",
    )

    # Example structure:
    # {
    #   "street": "Via Example 123",
    #   "city": "Milano",
    #   "zip": "20100",
    #   "province": "MI",
    #   "country": "IT"
    # }

    # -------------------------------------------------------------------------
    # Preferenze
    # -------------------------------------------------------------------------

    language = Column(
        String(5),
        nullable=False,
        default="it_IT",
        comment="Lingua preferita (default italiano)",
    )

    timezone = Column(
        String(50),
        nullable=False,
        default="Europe/Rome",
        comment="Timezone preferito",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    user = relationship("User", back_populates="profile")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_user_profiles_vat", "vat_number"),
        Index("ix_user_profiles_company", "company_name"),
        {"comment": "Profili utente con dati anagrafici e fatturazione"},
    )

    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, name={self.first_name} {self.last_name})>"


# =============================================================================
# SESSION MODEL
# =============================================================================


class Session(Base, UUIDMixin, TimestampMixin):
    """
    Sessioni JWT per tracking access/refresh tokens.

    Gestisce:
    - Access token (short-lived, 15min)
    - Refresh token (long-lived, 7 giorni)
    - Session tracking per security
    - Revoke capability

    Note:
    - Access token NON salvato in DB (stateless JWT)
    - Refresh token salvato per validazione e revoke
    - Session può essere invalidata lato server
    """

    __tablename__ = "sessions"

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a users",
    )

    # -------------------------------------------------------------------------
    # Tokens
    # -------------------------------------------------------------------------

    access_token = Column(
        String(500),
        unique=True,
        nullable=True,
        index=True,
        comment="Access token JWT (opzionale, per tracking)",
    )

    refresh_token = Column(
        String(500),
        unique=True,
        nullable=False,
        index=True,
        comment="Refresh token JWT (required)",
    )

    # -------------------------------------------------------------------------
    # Expiration
    # -------------------------------------------------------------------------

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Scadenza access token",
    )

    refresh_expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Scadenza refresh token",
    )

    # -------------------------------------------------------------------------
    # Session Info
    # -------------------------------------------------------------------------

    ip_address = Column(
        INET,
        nullable=True,
        comment="IP address sessione",
    )

    user_agent = Column(
        Text,
        nullable=True,
        comment="User agent browser/device",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    user = relationship("User", back_populates="sessions")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_sessions_user_expires", "user_id", "expires_at"),
        Index("ix_sessions_refresh_token", "refresh_token"),
        {"comment": "Sessioni JWT con access/refresh tokens"},
    )

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, user_id={self.user_id}, expires={self.expires_at})>"


# =============================================================================
# LOGIN ATTEMPT MODEL
# =============================================================================


class LoginAttempt(Base, UUIDMixin):
    """
    Log tentativi login per security e brute-force prevention.

    Traccia:
    - Login riusciti e falliti
    - IP address per geo-blocking
    - Timestamp per rate limiting
    - Motivo fallimento per analytics

    Security:
    - Rate limiting basato su IP + email
    - Alert per tentativi ripetuti falliti
    - Geo-blocking automatico opzionale
    """

    __tablename__ = "login_attempts"

    # -------------------------------------------------------------------------
    # Identificazione
    # -------------------------------------------------------------------------

    email = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Email tentativo login",
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK a users (NULL se utente non esiste)",
    )

    # -------------------------------------------------------------------------
    # Risultato
    # -------------------------------------------------------------------------

    success = Column(
        Boolean,
        nullable=False,
        index=True,
        comment="Login riuscito (True) o fallito (False)",
    )

    failure_reason = Column(
        String(100),
        nullable=True,
        comment="Motivo fallimento (invalid_password, email_not_verified, etc.)",
    )

    # -------------------------------------------------------------------------
    # Context
    # -------------------------------------------------------------------------

    ip_address = Column(
        INET,
        nullable=False,
        index=True,
        comment="IP address tentativo",
    )

    user_agent = Column(
        Text,
        nullable=True,
        comment="User agent browser/device",
    )

    attempted_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        index=True,
        comment="Timestamp tentativo",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    user = relationship("User", back_populates="login_attempts")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_login_attempts_email_timestamp", "email", "attempted_at"),
        Index("ix_login_attempts_ip_timestamp", "ip_address", "attempted_at"),
        Index("ix_login_attempts_success", "success", "attempted_at"),
        {"comment": "Log tentativi login per security"},
    )

    def __repr__(self) -> str:
        status = "SUCCESS" if self.success else "FAILED"
        return f"<LoginAttempt({status}, email={self.email}, ip={self.ip_address})>"


# =============================================================================
# LOGGING
# =============================================================================

# Log quando i modelli vengono importati (per debugging migrations)
logger.debug("User models loaded: User, UserProfile, Session, LoginAttempt")
