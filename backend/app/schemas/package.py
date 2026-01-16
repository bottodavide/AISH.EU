"""
Modulo: package.py
Descrizione: Schemi Pydantic per pacchetti consulenza
Autore: Claude per Davide
Data: 2026-01-16
"""

from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from pydantic import Field, field_validator
from uuid import UUID

from app.schemas.base import BaseSchema


# =============================================================================
# SERVICE REFERENCE (per evitare circular import)
# =============================================================================

class ServiceReference(BaseSchema):
    """Riferimento minimale a un servizio incluso nel pacchetto"""
    id: str
    slug: str
    name: str
    short_description: Optional[str] = None

    class Config:
        from_attributes = True


# =============================================================================
# PACKAGE SCHEMAS
# =============================================================================

class ConsultingPackageBase(BaseSchema):
    """Schema base per pacchetto consulenza"""
    name: str = Field(min_length=1, max_length=255, description="Nome del pacchetto")
    slug: str = Field(min_length=1, max_length=255, description="Slug URL-friendly")
    short_description: Optional[str] = Field(None, max_length=500, description="Descrizione breve")
    description: Optional[str] = Field(None, description="Descrizione dettagliata (HTML)")
    price: Decimal = Field(gt=0, description="Prezzo fisso del pacchetto (EUR)")
    original_price: Optional[Decimal] = Field(None, gt=0, description="Prezzo originale (per mostrare sconto)")
    badge: Optional[str] = Field(None, max_length=50, description="Badge promozionale")
    badge_color: Optional[str] = Field(None, max_length=50, description="Colore badge")
    features_json: Optional[str] = Field(None, description="Features in JSON array")
    duration_days: Optional[int] = Field(None, gt=0, description="Durata in giorni")
    validity_info: Optional[str] = Field(None, max_length=255, description="Info validità")
    cta_text: Optional[str] = Field(default="Acquista Ora", max_length=100, description="Testo CTA")
    is_active: bool = Field(default=True, description="Pacchetto visibile")
    is_featured: bool = Field(default=False, description="Pacchetto in evidenza")
    display_order: int = Field(default=0, ge=0, description="Ordine di visualizzazione")
    max_purchases: Optional[int] = Field(None, gt=0, description="Max acquisti disponibili")


class ConsultingPackageCreate(ConsultingPackageBase):
    """Schema per creazione pacchetto"""
    service_ids: List[UUID] = Field(default_factory=list, description="IDs dei servizi inclusi")

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Valida che lo slug sia URL-friendly"""
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug deve contenere solo lettere minuscole, numeri e trattini')
        return v


class ConsultingPackageUpdate(BaseSchema):
    """Schema per aggiornamento pacchetto (tutti campi opzionali)"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    slug: Optional[str] = Field(None, min_length=1, max_length=255)
    short_description: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    original_price: Optional[Decimal] = Field(None, gt=0)
    badge: Optional[str] = Field(None, max_length=50)
    badge_color: Optional[str] = Field(None, max_length=50)
    features_json: Optional[str] = None
    duration_days: Optional[int] = Field(None, gt=0)
    validity_info: Optional[str] = Field(None, max_length=255)
    cta_text: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)
    max_purchases: Optional[int] = Field(None, gt=0)
    service_ids: Optional[List[UUID]] = None

    @field_validator('slug')
    @classmethod
    def validate_slug(cls, v: Optional[str]) -> Optional[str]:
        """Valida che lo slug sia URL-friendly"""
        if v is None:
            return v
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Slug deve contenere solo lettere minuscole, numeri e trattini')
        return v


class ConsultingPackageResponse(ConsultingPackageBase):
    """Schema per response pacchetto"""
    id: str
    services: List[ServiceReference] = Field(default_factory=list, description="Servizi inclusi")
    purchased_count: int = Field(description="Numero di acquisti")
    discount_percentage: Optional[int] = Field(None, description="Percentuale di sconto")
    is_available: bool = Field(description="Disponibile per acquisto")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ConsultingPackageListResponse(BaseSchema):
    """Response per lista pacchetti con paginazione"""
    packages: List[ConsultingPackageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ConsultingPackagePublicResponse(BaseSchema):
    """Schema pubblico semplificato per listing frontend"""
    id: str
    name: str
    slug: str
    short_description: Optional[str]
    price: Decimal
    original_price: Optional[Decimal]
    badge: Optional[str]
    badge_color: Optional[str]
    features: List[str] = Field(default_factory=list, description="Lista features parsata")
    cta_text: str
    is_featured: bool
    discount_percentage: Optional[int]
    service_count: int = Field(description="Numero di servizi inclusi")

    class Config:
        from_attributes = True
