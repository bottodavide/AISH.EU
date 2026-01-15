"""
Modulo: service.py
Descrizione: Pydantic schemas per services
Autore: Claude per Davide
Data: 2026-01-15
"""

from decimal import Decimal
from typing import Optional

from pydantic import Field

from app.schemas.base import BaseSchema, UUIDTimestampSchema
from app.models.service import ServiceCategory, PricingType


# =============================================================================
# SERVICE SCHEMAS
# =============================================================================


class ServiceBase(BaseSchema):
    """Base schema per service"""

    slug: str = Field(min_length=1, max_length=255, description="URL slug")
    title: str = Field(min_length=1, max_length=255, description="Titolo servizio")
    subtitle: Optional[str] = Field(None, max_length=500, description="Sottotitolo")
    category: ServiceCategory = Field(description="Categoria servizio")
    pricing_type: PricingType = Field(description="Tipo pricing")
    base_price: Optional[Decimal] = Field(None, ge=0, description="Prezzo base (se fixed o hourly)")
    currency: str = Field(default="EUR", max_length=3, description="Valuta")


class ServiceCreate(ServiceBase):
    """Schema per creazione service"""

    is_published: bool = Field(default=False, description="Se pubblicato")
    display_order: int = Field(default=0, description="Ordine visualizzazione")
    seo_title: Optional[str] = Field(None, max_length=255, description="SEO title")
    seo_description: Optional[str] = Field(None, description="SEO description")


class ServiceUpdate(BaseSchema):
    """Schema per update service"""

    slug: Optional[str] = Field(None, max_length=255, description="URL slug")
    title: Optional[str] = Field(None, max_length=255, description="Titolo")
    subtitle: Optional[str] = Field(None, max_length=500, description="Sottotitolo")
    category: Optional[ServiceCategory] = Field(None, description="Categoria")
    pricing_type: Optional[PricingType] = Field(None, description="Tipo pricing")
    base_price: Optional[Decimal] = Field(None, ge=0, description="Prezzo base")
    currency: Optional[str] = Field(None, max_length=3, description="Valuta")
    is_published: Optional[bool] = Field(None, description="Se pubblicato")
    display_order: Optional[int] = Field(None, description="Ordine visualizzazione")
    seo_title: Optional[str] = Field(None, max_length=255, description="SEO title")
    seo_description: Optional[str] = Field(None, description="SEO description")


class ServiceResponse(ServiceBase, UUIDTimestampSchema):
    """Schema per response service"""

    is_published: bool = Field(description="Se pubblicato")
    display_order: int = Field(description="Ordine visualizzazione")
    seo_title: Optional[str] = Field(None, description="SEO title")
    seo_description: Optional[str] = Field(None, description="SEO description")

    # Computed field
    price_display: Optional[str] = Field(None, description="Prezzo formattato per display")


class ServiceListResponse(BaseSchema):
    """Schema per lista services"""

    services: list[ServiceResponse] = Field(description="Lista servizi")
    total: int = Field(description="Totale servizi")


class ServiceDetailResponse(ServiceResponse):
    """Schema per dettaglio service con contenuti"""

    contents: list["ServiceContentResponse"] = Field(default_factory=list, description="Contenuti CMS")
    faqs: list["ServiceFAQResponse"] = Field(default_factory=list, description="FAQ")
    images: list["ServiceImageResponse"] = Field(default_factory=list, description="Immagini")


# =============================================================================
# SERVICE CONTENT SCHEMAS
# =============================================================================


class ServiceContentBase(BaseSchema):
    """Base schema per service content"""

    section_type: str = Field(max_length=50, description="Tipo sezione: description, benefits, etc.")
    title: Optional[str] = Field(None, max_length=255, description="Titolo sezione")
    content: str = Field(description="Contenuto (markdown)")
    display_order: int = Field(default=0, description="Ordine visualizzazione")


class ServiceContentCreate(ServiceContentBase):
    """Schema per creazione service content"""

    service_id: Optional[str] = Field(None, description="ID servizio (auto se creato con service)")


class ServiceContentUpdate(BaseSchema):
    """Schema per update service content"""

    section_type: Optional[str] = Field(None, max_length=50, description="Tipo sezione")
    title: Optional[str] = Field(None, max_length=255, description="Titolo sezione")
    content: Optional[str] = Field(None, description="Contenuto")
    display_order: Optional[int] = Field(None, description="Ordine visualizzazione")


class ServiceContentResponse(ServiceContentBase, UUIDTimestampSchema):
    """Schema per response service content"""

    service_id: str = Field(description="ID servizio")


# =============================================================================
# SERVICE FAQ SCHEMAS
# =============================================================================


class ServiceFAQBase(BaseSchema):
    """Base schema per service FAQ"""

    question: str = Field(min_length=1, max_length=500, description="Domanda")
    answer: str = Field(min_length=1, description="Risposta")
    display_order: int = Field(default=0, description="Ordine visualizzazione")


class ServiceFAQCreate(ServiceFAQBase):
    """Schema per creazione service FAQ"""

    service_id: Optional[str] = Field(None, description="ID servizio")


class ServiceFAQUpdate(BaseSchema):
    """Schema per update service FAQ"""

    question: Optional[str] = Field(None, max_length=500, description="Domanda")
    answer: Optional[str] = Field(None, description="Risposta")
    display_order: Optional[int] = Field(None, description="Ordine")


class ServiceFAQResponse(ServiceFAQBase, UUIDTimestampSchema):
    """Schema per response service FAQ"""

    service_id: str = Field(description="ID servizio")


# =============================================================================
# SERVICE IMAGE SCHEMAS
# =============================================================================


class ServiceImageBase(BaseSchema):
    """Base schema per service image"""

    image_type: str = Field(max_length=50, description="Tipo immagine: hero, gallery, thumbnail, icon")
    file_path: str = Field(max_length=500, description="Path file")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alt text per accessibility")
    display_order: int = Field(default=0, description="Ordine visualizzazione")


class ServiceImageCreate(ServiceImageBase):
    """Schema per creazione service image"""

    service_id: Optional[str] = Field(None, description="ID servizio")


class ServiceImageUpdate(BaseSchema):
    """Schema per update service image"""

    image_type: Optional[str] = Field(None, max_length=50, description="Tipo immagine")
    alt_text: Optional[str] = Field(None, max_length=255, description="Alt text")
    display_order: Optional[int] = Field(None, description="Ordine")


class ServiceImageResponse(ServiceImageBase, UUIDTimestampSchema):
    """Schema per response service image"""

    service_id: str = Field(description="ID servizio")


# =============================================================================
# SERVICE FILTERS
# =============================================================================


class ServiceFilters(BaseSchema):
    """Filtri per ricerca services"""

    category: Optional[ServiceCategory] = Field(None, description="Filtra per categoria")
    pricing_type: Optional[PricingType] = Field(None, description="Filtra per tipo pricing")
    is_published: Optional[bool] = Field(None, description="Filtra per pubblicati/bozze")
    search: Optional[str] = Field(None, description="Ricerca in title e subtitle")
    skip: int = Field(0, ge=0, description="Offset paginazione")
    limit: int = Field(100, ge=1, le=1000, description="Limit paginazione")


# Forward refs per references circolari
ServiceDetailResponse.model_rebuild()
