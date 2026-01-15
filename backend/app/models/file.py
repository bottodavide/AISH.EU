"""
Modulo: file.py
Descrizione: Modelli SQLAlchemy per gestione file e uploads
Autore: Claude per Davide
Data: 2026-01-15

Modelli inclusi:
- File: File caricati (documenti, immagini, PDF)
- FileCategory: Categoria file per organizzazione

Note:
- Storage locale nel filesystem del server
- Path relativi salvati in DB
- Metadata completi (mime type, size, hash)
- Soft delete per conservare history
- Access control basato su user ownership
"""

import enum
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    BigInteger,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================


class FileCategory(str, enum.Enum):
    """
    Categorie file per organizzazione storage.

    Ogni categoria ha una directory dedicata:
    - INVOICE: uploads/invoices/
    - DOCUMENT: uploads/documents/
    - IMAGE: uploads/images/
    - AVATAR: uploads/avatars/
    - ATTACHMENT: uploads/attachments/
    - TEMP: uploads/temp/
    """

    INVOICE = "invoice"  # PDF fatture
    DOCUMENT = "document"  # Documenti generici (PDF, DOCX, XLSX)
    IMAGE = "image"  # Immagini generiche
    AVATAR = "avatar"  # Avatar utenti
    ATTACHMENT = "attachment"  # Allegati (support tickets, email)
    TEMP = "temp"  # File temporanei (da eliminare dopo 24h)


class FileStatus(str, enum.Enum):
    """
    Status file lifecycle.

    Workflow:
    UPLOADING → ACTIVE → DELETED (soft delete)
    """

    UPLOADING = "uploading"  # Upload in corso
    ACTIVE = "active"  # File disponibile
    DELETED = "deleted"  # Soft delete (conservato per audit)


# =============================================================================
# FILE MODEL
# =============================================================================


class File(Base, UUIDMixin, TimestampMixin):
    """
    File caricati sul server.

    Gestisce:
    - Upload file con validazione
    - Storage locale organizzato per categoria
    - Metadata completi (mime, size, hash)
    - Thumbnails per immagini
    - Access control (ownership + permissions)
    - Soft delete per audit trail

    Relationships:
    - uploaded_by: User (uploader)
    - invoices: Invoice[] (se category=INVOICE)
    - support_messages: TicketMessage[] (allegati ticket)

    Security:
    - SHA256 hash per integrity check
    - File type validation server-side
    - Size limits per categoria
    - Virus scan (opzionale)

    Storage Structure:
    uploads/
      ├── invoices/YYYY/MM/          # Fatture per anno/mese
      ├── documents/YYYY/MM/         # Documenti per anno/mese
      ├── images/YYYY/MM/            # Immagini per anno/mese
      ├── avatars/                   # Avatar utenti
      ├── attachments/YYYY/MM/       # Allegati vari
      └── temp/                      # File temporanei
    """

    __tablename__ = "files"

    # -------------------------------------------------------------------------
    # Ownership & Category
    # -------------------------------------------------------------------------

    uploaded_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK a users (uploader)",
    )

    category = Column(
        Enum(FileCategory),
        nullable=False,
        default=FileCategory.DOCUMENT,
        index=True,
        comment="Categoria file (invoice, document, image, etc.)",
    )

    status = Column(
        Enum(FileStatus),
        nullable=False,
        default=FileStatus.ACTIVE,
        index=True,
        comment="Status file (uploading, active, deleted)",
    )

    # -------------------------------------------------------------------------
    # File Info
    # -------------------------------------------------------------------------

    filename = Column(
        String(255),
        nullable=False,
        comment="Nome file originale",
    )

    stored_filename = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
        comment="Nome file salvato (UUID + extension)",
    )

    file_path = Column(
        String(512),
        nullable=False,
        comment="Path relativo da UPLOAD_DIR (es: images/2026/01/uuid.jpg)",
    )

    mime_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="MIME type (image/jpeg, application/pdf, etc.)",
    )

    file_size = Column(
        BigInteger,
        nullable=False,
        comment="Dimensione file in bytes",
    )

    file_extension = Column(
        String(10),
        nullable=True,
        comment="Estensione file (jpg, pdf, docx, etc.)",
    )

    # -------------------------------------------------------------------------
    # Security & Integrity
    # -------------------------------------------------------------------------

    sha256_hash = Column(
        String(64),
        nullable=True,
        index=True,
        comment="SHA256 hash per integrity check",
    )

    is_public = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="File accessibile pubblicamente (senza auth)",
    )

    # -------------------------------------------------------------------------
    # Image Metadata (se categoria IMAGE o AVATAR)
    # -------------------------------------------------------------------------

    image_metadata = Column(
        JSONB,
        nullable=True,
        comment="Metadata immagine (width, height, format, etc.)",
    )
    # Example:
    # {
    #   "width": 1920,
    #   "height": 1080,
    #   "format": "JPEG",
    #   "mode": "RGB",
    #   "has_thumbnail": true,
    #   "thumbnail_path": "images/2026/01/uuid_thumb.jpg"
    # }

    # -------------------------------------------------------------------------
    # Reference & Description
    # -------------------------------------------------------------------------

    description = Column(
        String(500),
        nullable=True,
        comment="Descrizione file (opzionale)",
    )

    reference_type = Column(
        String(50),
        nullable=True,
        index=True,
        comment="Tipo entità collegata (invoice, order, ticket, user)",
    )

    reference_id = Column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
        comment="ID entità collegata",
    )

    # -------------------------------------------------------------------------
    # Soft Delete
    # -------------------------------------------------------------------------

    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp soft delete (NULL se attivo)",
    )

    deleted_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="FK a users (chi ha eliminato)",
    )

    # -------------------------------------------------------------------------
    # Access Tracking
    # -------------------------------------------------------------------------

    download_count = Column(
        Integer,
        nullable=False,
        default=0,
        comment="Contatore download",
    )

    last_accessed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Ultimo accesso file",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    uploaded_by = relationship("User", foreign_keys=[uploaded_by_id], backref="uploaded_files")
    deleted_by = relationship("User", foreign_keys=[deleted_by_id])

    # TODO: Aggiungere relationships quando necessario:
    # invoice = relationship("Invoice", back_populates="file")
    # user_avatar = relationship("UserProfile", back_populates="avatar_file")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_files_category_status", "category", "status"),
        Index("ix_files_uploader_category", "uploaded_by_id", "category"),
        Index("ix_files_reference", "reference_type", "reference_id"),
        Index("ix_files_deleted", "deleted_at"),
        {"comment": "File caricati e gestiti sul server locale"},
    )

    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename={self.filename}, category={self.category})>"

    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------

    def is_image(self) -> bool:
        """Verifica se file è un'immagine"""
        return self.mime_type.startswith("image/")

    def is_pdf(self) -> bool:
        """Verifica se file è un PDF"""
        return self.mime_type == "application/pdf"

    def is_document(self) -> bool:
        """Verifica se file è un documento (PDF, DOCX, XLSX)"""
        document_mimes = [
            "application/pdf",
            "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ]
        return self.mime_type in document_mimes

    def size_human_readable(self) -> str:
        """Ritorna dimensione file in formato human-readable"""
        size = self.file_size
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"


# =============================================================================
# LOGGING
# =============================================================================

logger.debug("File models loaded: File, FileCategory, FileStatus")
