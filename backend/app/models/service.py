"""
Modulo: service.py
Descrizione: Modelli SQLAlchemy per servizi di consulenza
Autore: Claude per Davide
Data: 2026-01-15

Modelli inclusi:
- Service: Servizio consulenza principale
- ServiceContent: Contenuti CMS per pagina servizio
- ServiceFAQ: FAQ associate a servizio
- ServiceImage: Galleria immagini servizio

Note:
- Servizi sono il "prodotto" venduto (non prodotti fisici)
- Supporto per pacchetti fissi, custom quote e abbonamenti
- CMS-driven per modificare contenuti da admin panel
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
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

import enum


class ServiceCategory(str, enum.Enum):
    """
    Categorie servizi consulenza.

    Categorie principali:
    - AI_COMPLIANCE: AI Strategy & GDPR compliance
    - CYBERSECURITY_NIS2: Cybersecurity e direttiva NIS2
    - TOOLKIT_FORMAZIONE: Toolkit operativi e formazione team
    """

    AI_COMPLIANCE = "ai_compliance"
    CYBERSECURITY_NIS2 = "cybersecurity_nis2"
    TOOLKIT_FORMAZIONE = "toolkit_formazione"


class ServiceType(str, enum.Enum):
    """
    Tipologie di servizio per pricing.

    - PACCHETTO_FISSO: Prezzo fisso, acquisto diretto
    - CUSTOM_QUOTE: Preventivo personalizzato su richiesta
    - ABBONAMENTO: Subscription ricorrente (mensile/annuale)
    """

    PACCHETTO_FISSO = "pacchetto_fisso"
    CUSTOM_QUOTE = "custom_quote"
    ABBONAMENTO = "abbonamento"


class PricingType(str, enum.Enum):
    """
    Tipo di pricing per visualizzazione.

    - FIXED: Prezzo fisso (es: €1500)
    - RANGE: Range di prezzo (es: €1000-3000)
    - CUSTOM: "Preventivo su misura" (no prezzo mostrato)
    """

    FIXED = "fixed"
    RANGE = "range"
    CUSTOM = "custom"


# =============================================================================
# SERVICE MODEL
# =============================================================================


class Service(Base, UUIDMixin, TimestampMixin):
    """
    Modello Service principale.

    Rappresenta un servizio di consulenza vendibile.

    Features:
    - Categorizzazione (AI, Cybersecurity, Toolkit)
    - Pricing flessibile (fisso, range, custom)
    - CMS-driven content (separato in ServiceContent)
    - Draft/Published workflow
    - SEO optimization (slug, featured)

    Relationships:
    - content: ServiceContent (1-to-1)
    - faqs: ServiceFAQ[] (1-to-many)
    - images: ServiceImage[] (1-to-many)
    - orders: OrderItem[] (1-to-many)
    - quote_requests: QuoteRequest[] (1-to-many)
    """

    __tablename__ = "services"

    # -------------------------------------------------------------------------
    # Identificazione
    # -------------------------------------------------------------------------

    slug = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="URL-friendly slug (es: audit-gdpr-completo)",
    )

    name = Column(
        String(255),
        nullable=False,
        comment="Nome servizio (es: Audit GDPR Completo)",
    )

    # -------------------------------------------------------------------------
    # Categorizzazione
    # -------------------------------------------------------------------------

    category = Column(
        Enum(ServiceCategory),
        nullable=False,
        index=True,
        comment="Categoria principale servizio",
    )

    type = Column(
        Enum(ServiceType),
        nullable=False,
        index=True,
        comment="Tipo servizio per workflow acquisto",
    )

    # -------------------------------------------------------------------------
    # Descrizioni
    # -------------------------------------------------------------------------

    short_description = Column(
        Text,
        nullable=True,
        comment="Descrizione breve per listing (max 200 char)",
    )

    long_description = Column(
        Text,
        nullable=True,
        comment="Descrizione completa (HTML rich text)",
    )

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------

    pricing_type = Column(
        Enum(PricingType),
        nullable=False,
        default=PricingType.CUSTOM,
        comment="Tipo pricing per visualizzazione",
    )

    price_min = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Prezzo minimo (per RANGE) o fisso (per FIXED) in EUR",
    )

    price_max = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Prezzo massimo (per RANGE) in EUR",
    )

    currency = Column(
        String(3),
        nullable=False,
        default="EUR",
        comment="Valuta (sempre EUR per Italia)",
    )

    # -------------------------------------------------------------------------
    # Status & Visibility
    # -------------------------------------------------------------------------

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Servizio attivo e visibile",
    )

    is_featured = Column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
        comment="Servizio in evidenza (homepage)",
    )

    sort_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordinamento per listing (ASC)",
    )

    # -------------------------------------------------------------------------
    # Publishing
    # -------------------------------------------------------------------------

    published_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp pubblicazione (NULL = bozza)",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    # One-to-One con ServiceContent
    content = relationship(
        "ServiceContent",
        back_populates="service",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # One-to-Many con ServiceFAQ
    faqs = relationship(
        "ServiceFAQ",
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="ServiceFAQ.sort_order",
    )

    # One-to-Many con ServiceImage
    images = relationship(
        "ServiceImage",
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="ServiceImage.sort_order",
    )

    # TODO: Aggiungere relationships con OrderItem, QuoteRequest

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def is_published(self) -> bool:
        """Check se servizio è pubblicato."""
        return self.published_at is not None and self.published_at <= datetime.utcnow()

    @property
    def price_display(self) -> str:
        """Formatta prezzo per display."""
        if self.pricing_type == PricingType.CUSTOM:
            return "Preventivo su misura"
        elif self.pricing_type == PricingType.FIXED:
            return f"€{self.price_min:,.2f}"
        elif self.pricing_type == PricingType.RANGE:
            return f"€{self.price_min:,.2f} - €{self.price_max:,.2f}"
        return "Prezzo da definire"

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_services_category_active", "category", "is_active"),
        Index("ix_services_featured_active", "is_featured", "is_active"),
        Index("ix_services_published", "published_at"),
        {"comment": "Servizi consulenza vendibili"},
    )

    def __repr__(self) -> str:
        return f"<Service(id={self.id}, slug={self.slug}, category={self.category})>"


# =============================================================================
# SERVICE CONTENT MODEL
# =============================================================================


class ServiceContent(Base, UUIDMixin, TimestampMixin):
    """
    Contenuti CMS per pagina servizio.

    Separato da Service per:
    - Performance (Service table più leggera)
    - CMS management (modifiche content senza touch Service)
    - Versionamento futuro

    Struttura pagina servizio:
    - Hero section (title, subtitle, CTA, image)
    - Per chi è / Non è (target audience)
    - Il Problema (pain points)
    - La Soluzione (methodology)
    - Cosa include (deliverables)
    - Testimonials

    Note:
    - Tutti i campi HTML supportano rich text
    - JSONB per dati strutturati (steps, testimonials)
    """

    __tablename__ = "service_content"

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
        comment="FK a services (one-to-one)",
    )

    # -------------------------------------------------------------------------
    # Hero Section
    # -------------------------------------------------------------------------

    hero_title = Column(
        String(255),
        nullable=True,
        comment="Titolo hero (override service.name se presente)",
    )

    hero_subtitle = Column(
        Text,
        nullable=True,
        comment="Sottotitolo hero",
    )

    hero_image_url = Column(
        String(500),
        nullable=True,
        comment="URL immagine hero (da media library)",
    )

    hero_cta_text = Column(
        String(100),
        nullable=True,
        comment="Testo CTA primaria (es: Richiedi Preventivo)",
    )

    hero_cta_url = Column(
        String(500),
        nullable=True,
        comment="URL CTA (es: /contatti o #quote-form)",
    )

    # -------------------------------------------------------------------------
    # Content Sections (HTML rich text)
    # -------------------------------------------------------------------------

    problem_section = Column(
        Text,
        nullable=True,
        comment="Sezione 'Il Problema' (HTML)",
    )

    solution_section = Column(
        Text,
        nullable=True,
        comment="Sezione 'La Soluzione' (HTML)",
    )

    what_includes = Column(
        Text,
        nullable=True,
        comment="Cosa include il servizio (HTML bullet list)",
    )

    for_who_section = Column(
        Text,
        nullable=True,
        comment="Per chi è questo servizio (HTML)",
    )

    not_for_who_section = Column(
        Text,
        nullable=True,
        comment="Per chi NON è questo servizio (HTML)",
    )

    # -------------------------------------------------------------------------
    # Structured Content (JSONB)
    # -------------------------------------------------------------------------

    process_steps = Column(
        JSONB,
        nullable=True,
        comment="Step processo (JSON array: [{number, title, description}])",
    )
    # Example:
    # [
    #   {"number": 1, "title": "Analisi", "description": "..."},
    #   {"number": 2, "title": "Implementazione", "description": "..."}
    # ]

    testimonials = Column(
        JSONB,
        nullable=True,
        comment="Testimonials (JSON array: [{text, author, company, rating}])",
    )
    # Example:
    # [
    #   {
    #     "text": "Ottimo servizio...",
    #     "author": "Marco Rossi",
    #     "company": "Acme Corp",
    #     "rating": 5
    #   }
    # ]

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    service = relationship("Service", back_populates="content")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_service_content_service_id", "service_id"),
        {"comment": "Contenuti CMS per pagine servizi"},
    )

    def __repr__(self) -> str:
        return f"<ServiceContent(service_id={self.service_id})>"


# =============================================================================
# SERVICE FAQ MODEL
# =============================================================================


class ServiceFAQ(Base, UUIDMixin, TimestampMixin):
    """
    FAQ associate a un servizio.

    Features:
    - Ordinamento manuale (sort_order)
    - Rich text per risposte
    - SEO benefit (structured data)
    """

    __tablename__ = "service_faqs"

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a services",
    )

    # -------------------------------------------------------------------------
    # Content
    # -------------------------------------------------------------------------

    question = Column(
        String(500),
        nullable=False,
        comment="Domanda FAQ",
    )

    answer = Column(
        Text,
        nullable=False,
        comment="Risposta FAQ (HTML rich text)",
    )

    # -------------------------------------------------------------------------
    # Ordering
    # -------------------------------------------------------------------------

    sort_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordinamento display (ASC)",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    service = relationship("Service", back_populates="faqs")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_service_faqs_service_order", "service_id", "sort_order"),
        {"comment": "FAQ per servizi"},
    )

    def __repr__(self) -> str:
        return f"<ServiceFAQ(id={self.id}, service_id={self.service_id})>"


# =============================================================================
# SERVICE IMAGE MODEL
# =============================================================================


class ServiceImage(Base, UUIDMixin, TimestampMixin):
    """
    Galleria immagini per servizio.

    Features:
    - Multiple images per servizio
    - Primary image (featured)
    - Alt text per accessibilità e SEO
    - Ordinamento manuale
    """

    __tablename__ = "service_images"

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a services",
    )

    # -------------------------------------------------------------------------
    # Image Data
    # -------------------------------------------------------------------------

    image_url = Column(
        String(500),
        nullable=False,
        comment="URL immagine (da media library o CDN)",
    )

    alt_text = Column(
        String(255),
        nullable=True,
        comment="Testo alternativo per accessibilità e SEO",
    )

    # -------------------------------------------------------------------------
    # Display
    # -------------------------------------------------------------------------

    is_primary = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Immagine primaria (featured)",
    )

    sort_order = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordinamento gallery (ASC)",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    service = relationship("Service", back_populates="images")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_service_images_service_order", "service_id", "sort_order"),
        Index("ix_service_images_primary", "service_id", "is_primary"),
        {"comment": "Galleria immagini servizi"},
    )

    def __repr__(self) -> str:
        return f"<ServiceImage(id={self.id}, service_id={self.service_id}, primary={self.is_primary})>"


# =============================================================================
# LOGGING
# =============================================================================

logger.debug("Service models loaded: Service, ServiceContent, ServiceFAQ, ServiceImage")
