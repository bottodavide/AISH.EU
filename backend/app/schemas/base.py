"""
Modulo: base.py
Descrizione: Pydantic schemas base comuni
Autore: Claude per Davide
Data: 2026-01-15
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# =============================================================================
# BASE SCHEMAS
# =============================================================================


class BaseSchema(BaseModel):
    """
    Base schema con configurazione comune.

    Features:
    - from_attributes: Permette creazione da ORM models
    - use_enum_values: Serializza Enum come valori invece di nomi
    - populate_by_name: Permette popolazione tramite field name o alias
    """

    model_config = ConfigDict(
        from_attributes=True,
        use_enum_values=True,
        populate_by_name=True,
    )


class TimestampSchema(BaseSchema):
    """Schema con timestamps (created_at, updated_at)"""

    created_at: datetime = Field(description="Data creazione")
    updated_at: datetime = Field(description="Data ultima modifica")


class UUIDSchema(BaseSchema):
    """Schema con UUID id"""

    id: UUID = Field(description="ID univoco")


class UUIDTimestampSchema(UUIDSchema, TimestampSchema):
    """Schema con UUID + timestamps"""

    pass


# =============================================================================
# RESPONSE SCHEMAS
# =============================================================================


class SuccessResponse(BaseSchema):
    """Response generica di successo"""

    success: bool = True
    message: str = Field(description="Messaggio di successo")
    data: Optional[dict] = Field(None, description="Dati aggiuntivi opzionali")


class ErrorResponse(BaseSchema):
    """Response generica di errore"""

    error: bool = True
    message: str = Field(description="Messaggio di errore")
    details: Optional[dict] = Field(None, description="Dettagli errore")
    path: Optional[str] = Field(None, description="Path API che ha generato errore")


class PaginatedResponse(BaseSchema):
    """Response con paginazione"""

    items: list = Field(description="Lista items")
    total: int = Field(description="Totale items disponibili")
    skip: int = Field(description="Numero items saltati")
    limit: int = Field(description="Numero items per pagina")
    has_more: bool = Field(description="Ci sono altre pagine")


# =============================================================================
# HEALTH CHECK
# =============================================================================


class HealthCheckResponse(BaseSchema):
    """Response health check"""

    status: str = Field(description="Status: ok | degraded | down")
    version: str = Field(description="Versione API")
    environment: str = Field(description="Ambiente: development | staging | production")
    database: str = Field(description="Status database: ok | down")
    redis: str = Field(description="Status Redis: ok | down")
    timestamp: datetime = Field(description="Timestamp check")


# =============================================================================
# FILTERS & SORTING
# =============================================================================


class FilterBase(BaseSchema):
    """Base per filtri di ricerca"""

    skip: int = Field(0, ge=0, description="Numero record da saltare")
    limit: int = Field(100, ge=1, le=1000, description="Numero massimo record da restituire")
    sort_by: Optional[str] = Field(None, description="Campo per ordinamento")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Ordine: asc | desc")


class SearchQuery(BaseSchema):
    """Query di ricerca generica"""

    q: str = Field(min_length=1, max_length=255, description="Query di ricerca")
    fields: Optional[list[str]] = Field(None, description="Campi in cui cercare")


# =============================================================================
# FILE UPLOAD
# =============================================================================


class FileUploadResponse(BaseSchema):
    """Response per file upload"""

    filename: str = Field(description="Nome file")
    file_path: str = Field(description="Path file salvato")
    file_size: int = Field(description="Dimensione file (bytes)")
    mime_type: str = Field(description="MIME type")
    url: Optional[str] = Field(None, description="URL pubblico (se applicabile)")


# =============================================================================
# BULK OPERATIONS
# =============================================================================


class BulkOperationResponse(BaseSchema):
    """Response per operazioni bulk"""

    total: int = Field(description="Totale items processati")
    success: int = Field(description="Items con successo")
    failed: int = Field(description="Items falliti")
    errors: list[dict] = Field(default_factory=list, description="Lista errori")
