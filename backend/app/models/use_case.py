"""
Modulo: use_case.py
Descrizione: Modello SQLAlchemy per casi d'uso (success stories)
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from sqlalchemy import Boolean, Column, Integer, String, Text
from app.models.base import Base, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class UseCase(Base, UUIDMixin, TimestampMixin):
    """
    Modello per casi d'uso / success stories.

    Mostra come AI Strategy Hub ha aiutato aziende a risolvere sfide
    specifiche in ambito AI, GDPR, Cybersecurity, NIS2.

    Struttura:
    - Titolo e categoria (industry)
    - Icona rappresentativa
    - LA SFIDA: problema del cliente
    - LA SOLUZIONE: come è stato risolto
    - IL RISULTATO: outcome ottenuto
    """

    __tablename__ = "use_cases"

    # -------------------------------------------------------------------------
    # Identificazione e Metadati
    # -------------------------------------------------------------------------

    title = Column(
        String(255),
        nullable=False,
        comment="Titolo caso d'uso (es: 'Fintech: AI Credit Scoring Compliance')",
    )

    slug = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Slug URL-friendly per SEO",
    )

    industry = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Settore/Categoria (es: 'Finance', 'Sanità', 'Retail', 'Industria 4.0')",
    )

    icon = Column(
        String(255),
        nullable=True,
        comment="Nome icona Lucide o URL immagine",
    )

    # -------------------------------------------------------------------------
    # LA SFIDA
    # -------------------------------------------------------------------------

    challenge_title = Column(
        String(255),
        nullable=False,
        default="LA SFIDA",
        comment="Titolo sezione sfida",
    )

    challenge_description = Column(
        Text,
        nullable=False,
        comment="Descrizione del problema/sfida del cliente",
    )

    # -------------------------------------------------------------------------
    # LA SOLUZIONE
    # -------------------------------------------------------------------------

    solution_title = Column(
        String(255),
        nullable=False,
        default="LA SOLUZIONE",
        comment="Titolo sezione soluzione",
    )

    solution_description = Column(
        Text,
        nullable=False,
        comment="Descrizione della soluzione implementata",
    )

    # -------------------------------------------------------------------------
    # IL RISULTATO
    # -------------------------------------------------------------------------

    result_title = Column(
        String(255),
        nullable=False,
        default="IL RISULTATO",
        comment="Titolo sezione risultato",
    )

    result_description = Column(
        Text,
        nullable=False,
        comment="Descrizione dell'outcome/risultato ottenuto",
    )

    # -------------------------------------------------------------------------
    # Ordinamento e Pubblicazione
    # -------------------------------------------------------------------------

    display_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordine di visualizzazione (0 = primo)",
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Se attivo e visibile pubblicamente",
    )

    def __repr__(self):
        return f"<UseCase {self.title} ({self.industry})>"


logger.debug("UseCase model loaded")
