"""
Modulo: homepage.py
Descrizione: Schemi Pydantic per contenuti homepage
Autore: Claude per Davide
Data: 2026-01-16
"""

from datetime import datetime
from typing import Optional
from pydantic import Field, HttpUrl

from app.schemas.base import BaseSchema


class HomepageBannerBase(BaseSchema):
    """Schema base per banner homepage"""
    title: str = Field(min_length=1, max_length=255, description="Titolo principale")
    subtitle: Optional[str] = Field(None, max_length=255, description="Sottotitolo")
    description: Optional[str] = Field(None, description="Descrizione dettagliata")
    image_url: Optional[str] = Field(None, max_length=500, description="URL immagine banner")
    video_url: Optional[str] = Field(None, max_length=500, description="URL video")
    cta_text: Optional[str] = Field(None, max_length=100, description="Testo bottone CTA")
    cta_link: Optional[str] = Field(None, max_length=500, description="Link CTA")
    cta_variant: str = Field(default="primary", description="Variante bottone: primary, secondary, outline")
    position: str = Field(default="hero", description="Posizione: hero, slider, section, footer")
    display_order: int = Field(default=0, ge=0, description="Ordine di visualizzazione")
    background_color: Optional[str] = Field(None, max_length=50, description="Colore di sfondo")
    text_color: Optional[str] = Field(None, max_length=50, description="Colore del testo")
    is_active: bool = Field(default=True, description="Banner visibile")
    start_date: Optional[datetime] = Field(None, description="Data inizio validità")
    end_date: Optional[datetime] = Field(None, description="Data fine validità")


class HomepageBannerCreate(HomepageBannerBase):
    """Schema per creazione banner"""
    pass


class HomepageBannerUpdate(BaseSchema):
    """Schema per aggiornamento banner (tutti campi opzionali)"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=500)
    video_url: Optional[str] = Field(None, max_length=500)
    cta_text: Optional[str] = Field(None, max_length=100)
    cta_link: Optional[str] = Field(None, max_length=500)
    cta_variant: Optional[str] = None
    position: Optional[str] = None
    display_order: Optional[int] = Field(None, ge=0)
    background_color: Optional[str] = Field(None, max_length=50)
    text_color: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class HomepageBannerResponse(HomepageBannerBase):
    """Schema per response banner"""
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HomepageBannerListResponse(BaseSchema):
    """Response per lista banner con paginazione"""
    banners: list[HomepageBannerResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
