"""
About Page Schemas
Descrizione: Schemas Pydantic per la gestione della pagina Chi Siamo
Autore: Claude per Davide
Data: 2026-01-16
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


# ========== Specialization Area Schemas ==========

class SpecializationAreaBase(BaseModel):
    """Base schema per area di specializzazione"""
    name: str = Field(..., max_length=255, description="Nome dell'area di specializzazione")
    percentage: int = Field(..., ge=0, le=100, description="Percentuale di competenza (0-100)")
    display_order: int = Field(default=0, ge=0, description="Ordine di visualizzazione")


class SpecializationAreaCreate(SpecializationAreaBase):
    """Schema per creazione area di specializzazione"""
    pass


class SpecializationAreaUpdate(BaseModel):
    """Schema per aggiornamento area di specializzazione"""
    name: Optional[str] = Field(None, max_length=255)
    percentage: Optional[int] = Field(None, ge=0, le=100)
    display_order: Optional[int] = Field(None, ge=0)


class SpecializationAreaResponse(SpecializationAreaBase):
    """Schema per risposta area di specializzazione"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== Competence Section Schemas ==========

class CompetenceSectionBase(BaseModel):
    """Base schema per sezione di competenza"""
    title: str = Field(..., max_length=255, description="Titolo della sezione")
    icon: str = Field(..., max_length=100, description="Nome icona Lucide React")
    description: str = Field(..., description="Descrizione della competenza")
    features: List[str] = Field(default_factory=list, description="Lista di servizi/features")
    display_order: int = Field(default=0, ge=0, description="Ordine di visualizzazione")


class CompetenceSectionCreate(CompetenceSectionBase):
    """Schema per creazione sezione di competenza"""
    pass


class CompetenceSectionUpdate(BaseModel):
    """Schema per aggiornamento sezione di competenza"""
    title: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    features: Optional[List[str]] = None
    display_order: Optional[int] = Field(None, ge=0)


class CompetenceSectionResponse(CompetenceSectionBase):
    """Schema per risposta sezione di competenza"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ========== About Page Schemas ==========

class AboutPageBase(BaseModel):
    """Base schema per pagina About"""
    profile_name: str = Field(..., max_length=255, description="Nome del professionista")
    profile_title: str = Field(..., max_length=255, description="Titolo/ruolo professionale")
    profile_description: str = Field(..., description="Descrizione breve del profilo")
    profile_image_url: Optional[str] = Field(None, max_length=500, description="URL immagine profilo")
    profile_badges: List[str] = Field(default_factory=list, description="Lista di badge/certificazioni")
    is_published: bool = Field(default=True, description="Pagina pubblicata e visibile")


class AboutPageCreate(AboutPageBase):
    """Schema per creazione pagina About"""
    specialization_areas: List[SpecializationAreaCreate] = Field(default_factory=list)
    competence_sections: List[CompetenceSectionCreate] = Field(default_factory=list)


class AboutPageUpdate(BaseModel):
    """Schema per aggiornamento pagina About"""
    profile_name: Optional[str] = Field(None, max_length=255)
    profile_title: Optional[str] = Field(None, max_length=255)
    profile_description: Optional[str] = None
    profile_image_url: Optional[str] = Field(None, max_length=500)
    profile_badges: Optional[List[str]] = None
    is_published: Optional[bool] = None
    specialization_areas: Optional[List[SpecializationAreaCreate]] = None
    competence_sections: Optional[List[CompetenceSectionCreate]] = None


class AboutPageResponse(AboutPageBase):
    """Schema per risposta pagina About"""
    id: UUID
    specialization_areas: List[SpecializationAreaResponse] = Field(default_factory=list)
    competence_sections: List[CompetenceSectionResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
