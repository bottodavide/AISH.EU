"""
Modulo: use_case.py
Descrizione: Pydantic schemas per use cases
Autore: Claude per Davide
Data: 2026-01-16
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import Field

from app.schemas.base import BaseSchema, UUIDTimestampSchema


# =============================================================================
# USE CASE SCHEMAS
# =============================================================================


class UseCaseBase(BaseSchema):
    """Base schema per use case"""

    title: str = Field(..., max_length=255, description="Titolo caso d'uso")
    slug: str = Field(..., max_length=255, description="Slug URL-friendly")
    industry: str = Field(..., max_length=100, description="Settore/Categoria")
    icon: Optional[str] = Field(None, max_length=255, description="Nome icona o URL")

    challenge_title: str = Field(default="LA SFIDA", max_length=255, description="Titolo sezione sfida")
    challenge_description: str = Field(..., description="Descrizione della sfida")

    solution_title: str = Field(default="LA SOLUZIONE", max_length=255, description="Titolo sezione soluzione")
    solution_description: str = Field(..., description="Descrizione della soluzione")

    result_title: str = Field(default="IL RISULTATO", max_length=255, description="Titolo sezione risultato")
    result_description: str = Field(..., description="Descrizione del risultato")

    display_order: int = Field(default=0, ge=0, description="Ordine di visualizzazione")
    is_active: bool = Field(default=True, description="Se attivo e visibile")


class UseCaseCreate(UseCaseBase):
    """Schema per creazione use case"""
    pass


class UseCaseUpdate(BaseSchema):
    """Schema per update use case"""

    title: Optional[str] = Field(None, max_length=255, description="Titolo caso d'uso")
    slug: Optional[str] = Field(None, max_length=255, description="Slug URL-friendly")
    industry: Optional[str] = Field(None, max_length=100, description="Settore/Categoria")
    icon: Optional[str] = Field(None, max_length=255, description="Nome icona o URL")

    challenge_title: Optional[str] = Field(None, max_length=255, description="Titolo sezione sfida")
    challenge_description: Optional[str] = Field(None, description="Descrizione della sfida")

    solution_title: Optional[str] = Field(None, max_length=255, description="Titolo sezione soluzione")
    solution_description: Optional[str] = Field(None, description="Descrizione della soluzione")

    result_title: Optional[str] = Field(None, max_length=255, description="Titolo sezione risultato")
    result_description: Optional[str] = Field(None, description="Descrizione del risultato")

    display_order: Optional[int] = Field(None, ge=0, description="Ordine di visualizzazione")
    is_active: Optional[bool] = Field(None, description="Se attivo e visibile")


class UseCaseResponse(UseCaseBase, UUIDTimestampSchema):
    """Schema per response use case"""
    pass


class UseCaseListResponse(BaseSchema):
    """Schema per lista use cases paginata"""

    use_cases: list[UseCaseResponse] = Field(description="Lista casi d'uso")
    total: int = Field(description="Totale casi d'uso")
    page: int = Field(description="Pagina corrente")
    page_size: int = Field(description="Dimensione pagina")
    total_pages: int = Field(description="Totale pagine")
