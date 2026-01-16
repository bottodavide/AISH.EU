"""
Modulo: package.py
Descrizione: Modelli per pacchetti consulenza (bundle di servizi a prezzo fisso)
Autore: Claude per Davide
Data: 2026-01-16
"""

from decimal import Decimal
from typing import Optional, List
from sqlalchemy import String, Text, Numeric, Integer, Boolean, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.models.base import Base, UUIDMixin, TimestampMixin


# Association table per relazione many-to-many tra pacchetti e servizi
package_services = Table(
    "package_services",
    Base.metadata,
    Column("package_id", UUID(as_uuid=True), ForeignKey("consulting_packages.id", ondelete="CASCADE"), primary_key=True),
    Column("service_id", UUID(as_uuid=True), ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
)


class ConsultingPackage(Base, UUIDMixin, TimestampMixin):
    """
    Pacchetto consulenza - Bundle di servizi a prezzo fisso.

    Permette di creare offerte predefinite con set di servizi inclusi
    a un prezzo promozionale rispetto alla somma dei singoli servizi.
    """

    __tablename__ = "consulting_packages"

    # Identificazione
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        comment="Nome del pacchetto (es: 'Starter AI Compliance')"
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Slug URL-friendly per il pacchetto"
    )

    # Descrizione
    short_description: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment="Descrizione breve per card/preview"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Descrizione dettagliata del pacchetto"
    )

    # Pricing
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        comment="Prezzo fisso del pacchetto (EUR)"
    )
    original_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2),
        nullable=True,
        comment="Prezzo originale prima dello sconto (opzionale)"
    )

    # Badge e marketing
    badge: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Badge promozionale (es: 'PIÙ POPOLARE', 'BEST VALUE')"
    )
    badge_color: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Colore del badge (es: 'primary', 'success', '#ff5733')"
    )

    # Features/Benefici (stored as comma-separated or use separate table)
    features_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Features in formato JSON array"
    )

    # Durata e validità
    duration_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Durata del pacchetto in giorni (se applicabile)"
    )
    validity_info: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="Info validità (es: 'Valido 6 mesi dall\\'acquisto')"
    )

    # CTA customizzata
    cta_text: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        default="Acquista Ora",
        comment="Testo bottone call-to-action"
    )

    # Stato e visibilità
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
        comment="Pacchetto visibile nel sito"
    )
    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        comment="Pacchetto in evidenza (highlighted)"
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordine di visualizzazione (0=primo)"
    )

    # Max acquisti (opzionale per offerte limitate)
    max_purchases: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Numero massimo di acquisti disponibili (null=illimitato)"
    )
    purchased_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Numero di volte che è stato acquistato"
    )

    # Relationships
    services: Mapped[List["Service"]] = relationship(
        "Service",
        secondary=package_services,
        back_populates="packages",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<ConsultingPackage(name='{self.name}', price={self.price}, active={self.is_active})>"

    @property
    def discount_percentage(self) -> Optional[int]:
        """Calcola percentuale di sconto se original_price è impostato"""
        if self.original_price and self.original_price > 0 and self.price < self.original_price:
            discount = ((self.original_price - self.price) / self.original_price) * 100
            return int(discount)
        return None

    @property
    def is_available(self) -> bool:
        """Check se il pacchetto è ancora disponibile per l'acquisto"""
        if not self.is_active:
            return False
        if self.max_purchases and self.purchased_count >= self.max_purchases:
            return False
        return True

    def get_features_list(self) -> List[str]:
        """Parse features_json e ritorna lista di features"""
        if not self.features_json:
            return []

        try:
            import json
            return json.loads(self.features_json)
        except (json.JSONDecodeError, TypeError):
            # Fallback: split by newline or comma
            if '\n' in self.features_json:
                return [f.strip() for f in self.features_json.split('\n') if f.strip()]
            return [f.strip() for f in self.features_json.split(',') if f.strip()]
