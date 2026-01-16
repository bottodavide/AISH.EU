"""
Modulo: homepage.py
Descrizione: Modelli per contenuti homepage (banner, hero, sezioni)
Autore: Claude per Davide
Data: 2026-01-16
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin, TimestampMixin


class HomepageBanner(Base, UUIDMixin, TimestampMixin):
    """
    Banner dinamici per homepage.
    Supporta hero banner, slider, CTA sections, etc.
    """

    __tablename__ = "homepage_banners"

    # Contenuto
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="Titolo principale")
    subtitle: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="Sottotitolo")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="Descrizione dettagliata")

    # Media
    image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="URL immagine banner")
    video_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="URL video (alternativa a immagine)")

    # Call to Action
    cta_text: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="Testo bottone CTA")
    cta_link: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, comment="Link CTA")
    cta_variant: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="primary",
        comment="Variante bottone: primary, secondary, outline"
    )

    # Posizionamento e stile
    position: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="hero",
        comment="Posizione: hero, slider, section, footer"
    )
    display_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Ordine di visualizzazione (0=primo)"
    )
    background_color: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Colore di sfondo (es: #ffffff, primary, muted)"
    )
    text_color: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
        comment="Colore del testo (es: #000000, white, foreground)"
    )

    # Stato e validità
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        comment="Banner visibile o nascosto"
    )
    start_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data inizio validità (opzionale)"
    )
    end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment="Data fine validità (opzionale)"
    )

    def __repr__(self) -> str:
        return f"<HomepageBanner(title='{self.title}', position='{self.position}', active={self.is_active})>"

    def is_valid_now(self) -> bool:
        """Check if banner is valid at current time"""
        if not self.is_active:
            return False

        now = datetime.utcnow()

        if self.start_date and now < self.start_date:
            return False

        if self.end_date and now > self.end_date:
            return False

        return True
