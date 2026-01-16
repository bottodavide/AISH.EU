"""
About Page Models
Descrizione: Modelli per la gestione della pagina Chi Siamo
Autore: Claude per Davide
Data: 2026-01-16
"""

from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.models.base import Base, UUIDMixin, TimestampMixin


class AboutPage(Base, UUIDMixin, TimestampMixin):
    """
    Pagina Chi Siamo (singleton - dovrebbe esserci solo un record)
    Contiene profilo personale e informazioni generali
    """
    __tablename__ = "about_pages"

    # Profilo personale
    profile_name = Column(String(255), nullable=False)
    profile_title = Column(String(255), nullable=False)
    profile_description = Column(Text, nullable=False)
    profile_image_url = Column(String(500), nullable=True)
    profile_badges = Column(JSON, nullable=False, default=list)  # ["ISO 27001 LA", "CIPP/E", etc.]

    # Meta
    is_published = Column(Boolean, nullable=False, default=True)

    # Relationships
    specialization_areas = relationship(
        "SpecializationArea",
        back_populates="about_page",
        cascade="all, delete-orphan",
        order_by="SpecializationArea.display_order"
    )

    competence_sections = relationship(
        "CompetenceSection",
        back_populates="about_page",
        cascade="all, delete-orphan",
        order_by="CompetenceSection.display_order"
    )


class SpecializationArea(Base, UUIDMixin, TimestampMixin):
    """
    Aree di specializzazione con percentuale (progress bars nella sidebar)
    """
    __tablename__ = "specialization_areas"

    about_page_id = Column(UUID(as_uuid=True), ForeignKey("about_pages.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    percentage = Column(Integer, nullable=False)  # 0-100
    display_order = Column(Integer, nullable=False, default=0)

    # Relationships
    about_page = relationship("AboutPage", back_populates="specialization_areas")


class CompetenceSection(Base, UUIDMixin, TimestampMixin):
    """
    Sezioni di competenze (AI Governance, GDPR, Cybersecurity, etc.)
    Ogni sezione ha titolo, icona, descrizione e lista di features
    """
    __tablename__ = "competence_sections"

    about_page_id = Column(UUID(as_uuid=True), ForeignKey("about_pages.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    icon = Column(String(100), nullable=False)  # Nome icona lucide-react (es: "BookOpen", "Users")
    description = Column(Text, nullable=False)
    features = Column(JSON, nullable=False, default=list)  # Lista di stringhe con i servizi/features
    display_order = Column(Integer, nullable=False, default=0)

    # Relationships
    about_page = relationship("AboutPage", back_populates="competence_sections")
