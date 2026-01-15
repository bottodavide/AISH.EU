"""
Modulo: file.py
Descrizione: Pydantic schemas per file upload e gestione
Autore: Claude per Davide
Data: 2026-01-15

Schemas inclusi:
- FileUpload: Request upload file
- FileResponse: Response dettaglio file
- FileListResponse: Response lista file (lightweight)
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.file import FileCategory, FileStatus
from app.schemas.base import UUIDTimestampSchema


# =============================================================================
# FILE UPLOAD SCHEMAS
# =============================================================================


class FileUploadMetadata(BaseModel):
    """Metadata opzionali per file upload"""

    model_config = ConfigDict(from_attributes=True)

    description: Optional[str] = Field(None, max_length=500, description="Descrizione file")
    reference_type: Optional[str] = Field(None, max_length=50, description="Tipo entità (invoice, order, ticket)")
    reference_id: Optional[UUID] = Field(None, description="ID entità collegata")
    is_public: bool = Field(False, description="File accessibile pubblicamente")


class FileUploadResponse(BaseModel):
    """Response dopo upload file"""

    model_config = ConfigDict(from_attributes=True)

    file_id: UUID = Field(description="ID file caricato")
    filename: str = Field(description="Nome file originale")
    stored_filename: str = Field(description="Nome file salvato")
    file_path: str = Field(description="Path relativo file")
    mime_type: str = Field(description="MIME type")
    file_size: int = Field(description="Dimensione in bytes")
    category: FileCategory = Field(description="Categoria file")
    url: str = Field(description="URL per download/visualizzazione")
    thumbnail_url: Optional[str] = Field(None, description="URL thumbnail (se immagine)")
    created_at: datetime = Field(description="Data upload")


# =============================================================================
# FILE RESPONSE SCHEMAS
# =============================================================================


class FileResponse(UUIDTimestampSchema):
    """Schema response file completo"""

    uploaded_by_id: Optional[UUID] = Field(None, description="ID uploader")
    category: FileCategory = Field(description="Categoria file")
    status: FileStatus = Field(description="Status file")

    filename: str = Field(description="Nome file originale")
    stored_filename: str = Field(description="Nome file salvato")
    file_path: str = Field(description="Path relativo")
    mime_type: str = Field(description="MIME type")
    file_size: int = Field(description="Dimensione bytes")
    file_extension: Optional[str] = Field(None, description="Estensione")

    sha256_hash: Optional[str] = Field(None, description="Hash SHA256")
    is_public: bool = Field(description="Accessibile pubblicamente")

    image_metadata: Optional[dict] = Field(None, description="Metadata immagine")
    description: Optional[str] = Field(None, description="Descrizione")

    reference_type: Optional[str] = Field(None, description="Tipo entità")
    reference_id: Optional[UUID] = Field(None, description="ID entità")

    deleted_at: Optional[datetime] = Field(None, description="Data eliminazione")
    download_count: int = Field(description="Contatore download")
    last_accessed_at: Optional[datetime] = Field(None, description="Ultimo accesso")

    # Helper fields (computed)
    url: Optional[str] = Field(None, description="URL download")
    thumbnail_url: Optional[str] = Field(None, description="URL thumbnail")
    size_human: Optional[str] = Field(None, description="Dimensione human-readable")


class FileListResponse(UUIDTimestampSchema):
    """Schema response per lista file (versione leggera)"""

    filename: str = Field(description="Nome file")
    category: FileCategory = Field(description="Categoria")
    mime_type: str = Field(description="MIME type")
    file_size: int = Field(description="Dimensione bytes")
    is_public: bool = Field(description="Pubblico")
    download_count: int = Field(description="Download")
    url: Optional[str] = Field(None, description="URL download")


# =============================================================================
# FILE UPDATE SCHEMAS
# =============================================================================


class FileUpdateRequest(BaseModel):
    """Schema per aggiornare metadata file"""

    model_config = ConfigDict(from_attributes=True)

    description: Optional[str] = Field(None, max_length=500, description="Nuova descrizione")
    is_public: Optional[bool] = Field(None, description="Cambia visibilità")
    reference_type: Optional[str] = Field(None, max_length=50, description="Tipo entità")
    reference_id: Optional[UUID] = Field(None, description="ID entità")


# =============================================================================
# FILE FILTERS
# =============================================================================


class FileFilters(BaseModel):
    """Filtri per ricerca file"""

    model_config = ConfigDict(from_attributes=True)

    category: Optional[FileCategory] = Field(None, description="Filtra per categoria")
    uploaded_by_id: Optional[UUID] = Field(None, description="Filtra per uploader")
    mime_type: Optional[str] = Field(None, description="Filtra per MIME type")
    reference_type: Optional[str] = Field(None, description="Filtra per tipo entità")
    reference_id: Optional[UUID] = Field(None, description="Filtra per ID entità")
    is_public: Optional[bool] = Field(None, description="Filtra per visibilità")
    filename: Optional[str] = Field(None, description="Cerca per nome file (like)")

    skip: int = Field(default=0, ge=0, description="Paginazione: skip")
    limit: int = Field(default=50, ge=1, le=100, description="Paginazione: limit")
    sort_by: str = Field(default="created_at", description="Campo ordinamento")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Direzione")


# =============================================================================
# SIGNED URL SCHEMAS
# =============================================================================


class SignedUrlRequest(BaseModel):
    """Request per generare URL firmata con scadenza"""

    model_config = ConfigDict(from_attributes=True)

    expires_in: int = Field(
        default=3600,
        ge=60,
        le=86400,
        description="Durata validità URL in secondi (default 1h, max 24h)"
    )


class SignedUrlResponse(BaseModel):
    """Response con URL firmata temporanea"""

    model_config = ConfigDict(from_attributes=True)

    url: str = Field(description="URL firmata temporanea")
    expires_at: datetime = Field(description="Scadenza URL")
