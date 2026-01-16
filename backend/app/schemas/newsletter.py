"""
Modulo: newsletter.py
Descrizione: Schemas Pydantic per newsletter management
Autore: Claude per Davide
Data: 2026-01-15
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.newsletter import SubscriberStatus


# =============================================================================
# SUBSCRIBER SCHEMAS
# =============================================================================


class NewsletterSubscribeRequest(BaseModel):
    """Schema per iscrizione newsletter"""

    email: EmailStr = Field(..., description="Email iscritto")
    first_name: Optional[str] = Field(None, max_length=100, description="Nome")
    last_name: Optional[str] = Field(None, max_length=100, description="Cognome")
    accept_terms: bool = Field(..., description="Accettazione termini e privacy")
    source: Optional[str] = Field("web_form", max_length=100, description="Fonte iscrizione")


class NewsletterUnsubscribeRequest(BaseModel):
    """Schema per disiscrizione newsletter"""

    email: EmailStr = Field(..., description="Email da disiscrivere")


class NewsletterSubscriberResponse(BaseModel):
    """Schema per risposta subscriber"""

    id: UUID
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    status: SubscriberStatus
    subscribed_at: datetime
    confirmed_at: Optional[datetime]
    unsubscribed_at: Optional[datetime]
    source: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NewsletterSubscriberListResponse(BaseModel):
    """Schema per lista subscribers paginata"""

    subscribers: list[NewsletterSubscriberResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class NewsletterSubscriberFilters(BaseModel):
    """Filtri per lista subscribers"""

    status: Optional[SubscriberStatus] = Field(None, description="Filtra per status")
    search: Optional[str] = Field(None, max_length=255, description="Cerca in email o nome")
    page: int = Field(default=1, ge=1, description="Numero pagina")
    page_size: int = Field(default=50, ge=1, le=500, description="Items per pagina")


class NewsletterStatsResponse(BaseModel):
    """Schema per statistiche newsletter"""

    total_subscribers: int
    active_subscribers: int
    pending_subscribers: int
    unsubscribed_subscribers: int
    subscribed_today: int
    subscribed_this_week: int
    subscribed_this_month: int


# =============================================================================
# CAMPAIGN SCHEMAS (TODO - per future implementazioni)
# =============================================================================


class CampaignBase(BaseModel):
    """Base schema per Campaign"""

    name: str = Field(..., max_length=255, description="Nome campagna")
    subject: str = Field(..., max_length=255, description="Oggetto email")
    from_name: str = Field(..., max_length=255, description="Nome mittente")
    from_email: EmailStr = Field(..., description="Email mittente")
    html_content: str = Field(..., description="Contenuto HTML")
    text_content: Optional[str] = Field(None, description="Contenuto testo")


class CampaignCreate(CampaignBase):
    """Schema per creazione Campaign"""

    pass


class CampaignResponse(CampaignBase):
    """Schema per risposta Campaign"""

    id: UUID
    status: str
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    total_recipients: int
    total_sent: int
    total_opened: int
    total_clicked: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
