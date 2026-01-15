"""
Modulo: settings.py
Descrizione: Modelli SQLAlchemy per configurazione globale applicazione
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from sqlalchemy import Boolean, Column, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from app.models.base import Base, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class SiteSetting(Base, UUIDMixin, TimestampMixin):
    """
    Configurazione globale sito (database-driven settings).

    Permette di modificare configurazioni senza riavviare l'app.
    Esempi: nome sito, email contatto, feature flags, limiti API, ecc.

    Note:
    - setting_key deve essere univoco
    - setting_value è JSONB per flessibilità (supporta string, int, bool, array, object)
    - is_public determina se il setting è esposto via API pubblica (es: site_name)
    - is_encrypted indica se il valore è criptato (es: API keys, secrets)
    """
    __tablename__ = "site_settings"

    setting_key = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Chiave univoca setting (es: site_name, smtp_host, feature_ai_chat_enabled)"
    )

    setting_value = Column(
        JSONB,
        nullable=False,
        comment="Valore configurazione (JSON flessibile: string, number, boolean, array, object)"
    )

    setting_type = Column(
        String(50),
        nullable=False,
        default="string",
        comment="Tipo dato: string, number, boolean, json, encrypted"
    )

    description = Column(
        Text,
        nullable=True,
        comment="Descrizione setting per admin panel"
    )

    category = Column(
        String(100),
        nullable=False,
        default="general",
        index=True,
        comment="Categoria: general, email, payment, ai, security, feature_flags, limits"
    )

    is_public = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Se True, esposto via API pubblica (es: nome sito, logo). Se False, solo admin."
    )

    is_encrypted = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Se True, il valore è criptato nel DB (es: API keys, SMTP password)"
    )

    validation_rules = Column(
        JSONB,
        nullable=True,
        comment="Regole validazione (es: min, max, regex, enum) per admin UI"
    )

    updated_by = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="Ultimo utente che ha modificato il setting"
    )

    # Relationship
    updater = relationship("User")

    __table_args__ = (
        Index("ix_site_settings_category_key", "category", "setting_key"),
        Index("ix_site_settings_is_public", "is_public"),
        {"comment": "Configurazione globale sito (database-driven)"},
    )

    def __repr__(self) -> str:
        return f"<SiteSetting {self.setting_key}={self.setting_value}>"


logger.debug("Settings model loaded")
