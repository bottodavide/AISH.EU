"""
Modulo: file_storage.py
Descrizione: Service per gestione storage file locale
Autore: Claude per Davide
Data: 2026-01-15

Funzionalità:
- Upload file con validazione
- Storage organizzato per categoria e data
- Image processing (resize, thumbnail)
- Secure file serving
- File deletion (soft + hard)
- Hash calculation per integrity
"""

import hashlib
import logging
import mimetypes
import os
import shutil
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Tuple
from uuid import UUID, uuid4

from fastapi import UploadFile
from PIL import Image

from app.core.config import settings
from app.models.file import FileCategory

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS & CONFIGURATION
# =============================================================================

# Allowed MIME types per categoria
ALLOWED_MIME_TYPES = {
    FileCategory.INVOICE: [
        "application/pdf",
    ],
    FileCategory.DOCUMENT: [
        "application/pdf",
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-excel",  # .xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "text/plain",  # .txt
        "text/csv",  # .csv
    ],
    FileCategory.IMAGE: [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
    ],
    FileCategory.AVATAR: [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/webp",
    ],
    FileCategory.ATTACHMENT: [
        "application/pdf",
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/zip",
        "text/plain",
    ],
    FileCategory.TEMP: [
        "*",  # Accept all for temp
    ],
}

# Max file size per categoria (in bytes)
MAX_FILE_SIZE = {
    FileCategory.INVOICE: 10 * 1024 * 1024,  # 10 MB
    FileCategory.DOCUMENT: 20 * 1024 * 1024,  # 20 MB
    FileCategory.IMAGE: 10 * 1024 * 1024,  # 10 MB
    FileCategory.AVATAR: 5 * 1024 * 1024,  # 5 MB
    FileCategory.ATTACHMENT: 20 * 1024 * 1024,  # 20 MB
    FileCategory.TEMP: 50 * 1024 * 1024,  # 50 MB
}

# Image thumbnail settings
THUMBNAIL_SIZE = (300, 300)  # Max width/height
THUMBNAIL_QUALITY = 85

# Avatar settings
AVATAR_SIZE = (400, 400)  # Fixed size for avatars
AVATAR_QUALITY = 90


# =============================================================================
# FILE STORAGE SERVICE
# =============================================================================


class FileStorageService:
    """
    Service per gestione storage file locale.

    Gestisce:
    - Upload e validazione
    - Storage organizzato (uploads/category/YYYY/MM/)
    - Image processing
    - Hash calculation
    - File serving e download
    """

    def __init__(self, upload_dir: Optional[Path] = None):
        """
        Inizializza FileStorageService.

        Args:
            upload_dir: Directory base per uploads (default da settings)
        """
        self.upload_dir = upload_dir or Path(settings.UPLOAD_DIR)
        self._ensure_directories()

    def _ensure_directories(self):
        """Crea directory structure se non esiste"""
        categories = [
            "invoices",
            "documents",
            "images",
            "avatars",
            "attachments",
            "temp",
        ]

        for category in categories:
            category_dir = self.upload_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Upload directories ensured at: {self.upload_dir}")

    def _get_category_directory(self, category: FileCategory) -> Path:
        """
        Ritorna directory per categoria.

        Per invoices, documents, images, attachments: usa sottodirectory YYYY/MM
        Per avatars e temp: direttamente nella categoria

        Args:
            category: Categoria file

        Returns:
            Path directory
        """
        category_map = {
            FileCategory.INVOICE: "invoices",
            FileCategory.DOCUMENT: "documents",
            FileCategory.IMAGE: "images",
            FileCategory.AVATAR: "avatars",
            FileCategory.ATTACHMENT: "attachments",
            FileCategory.TEMP: "temp",
        }

        base_dir = self.upload_dir / category_map[category]

        # Usa YYYY/MM per categorie con molti file
        if category in [
            FileCategory.INVOICE,
            FileCategory.DOCUMENT,
            FileCategory.IMAGE,
            FileCategory.ATTACHMENT,
        ]:
            now = datetime.now(timezone.utc)
            year_month_dir = base_dir / str(now.year) / f"{now.month:02d}"
            year_month_dir.mkdir(parents=True, exist_ok=True)
            return year_month_dir

        # Direttamente nella categoria per avatars e temp
        return base_dir

    def _generate_stored_filename(self, original_filename: str) -> Tuple[str, str]:
        """
        Genera nome file univoco per storage.

        Format: {uuid}.{extension}

        Args:
            original_filename: Nome file originale

        Returns:
            Tuple (stored_filename, extension)
        """
        # Estrai estensione
        _, ext = os.path.splitext(original_filename)
        ext = ext.lower() if ext else ""

        # Genera UUID
        file_uuid = uuid4()
        stored_filename = f"{file_uuid}{ext}"

        extension = ext[1:] if ext.startswith(".") else ext

        return stored_filename, extension

    def _calculate_file_hash(self, file_content: bytes) -> str:
        """
        Calcola SHA256 hash del file.

        Args:
            file_content: Contenuto file in bytes

        Returns:
            Hash SHA256 hex string
        """
        return hashlib.sha256(file_content).hexdigest()

    def _validate_mime_type(self, mime_type: str, category: FileCategory) -> bool:
        """
        Valida MIME type per categoria.

        Args:
            mime_type: MIME type da validare
            category: Categoria file

        Returns:
            True se valido, False altrimenti
        """
        allowed = ALLOWED_MIME_TYPES.get(category, [])

        if "*" in allowed:
            return True

        return mime_type in allowed

    def _validate_file_size(self, file_size: int, category: FileCategory) -> bool:
        """
        Valida dimensione file per categoria.

        Args:
            file_size: Dimensione in bytes
            category: Categoria file

        Returns:
            True se valido, False altrimenti
        """
        max_size = MAX_FILE_SIZE.get(category, 10 * 1024 * 1024)
        return file_size <= max_size

    async def save_file(
        self,
        upload_file: UploadFile,
        category: FileCategory,
    ) -> Tuple[str, str, str, int, str]:
        """
        Salva file su disco.

        Args:
            upload_file: File da FastAPI UploadFile
            category: Categoria file

        Returns:
            Tuple (stored_filename, file_path, sha256_hash, file_size, mime_type)

        Raises:
            ValueError: Se validazione fallisce
        """
        # Leggi contenuto file
        file_content = await upload_file.read()
        file_size = len(file_content)

        # Determina MIME type
        mime_type = upload_file.content_type or mimetypes.guess_type(upload_file.filename)[0] or "application/octet-stream"

        # Validazioni
        if not self._validate_mime_type(mime_type, category):
            raise ValueError(f"MIME type '{mime_type}' non permesso per categoria {category}")

        if not self._validate_file_size(file_size, category):
            max_mb = MAX_FILE_SIZE[category] / (1024 * 1024)
            raise ValueError(f"File troppo grande. Max {max_mb:.1f} MB per categoria {category}")

        # Genera nome file e path
        stored_filename, extension = self._generate_stored_filename(upload_file.filename)
        category_dir = self._get_category_directory(category)
        full_path = category_dir / stored_filename

        # Calcola hash
        sha256_hash = self._calculate_file_hash(file_content)

        # Salva file
        with open(full_path, "wb") as f:
            f.write(file_content)

        # Path relativo da upload_dir
        relative_path = str(full_path.relative_to(self.upload_dir))

        logger.info(f"File saved: {stored_filename} ({file_size} bytes) at {relative_path}")

        return stored_filename, relative_path, sha256_hash, file_size, mime_type

    def get_file_path(self, relative_path: str) -> Path:
        """
        Ritorna path assoluto da path relativo.

        Args:
            relative_path: Path relativo da upload_dir

        Returns:
            Path assoluto
        """
        return self.upload_dir / relative_path

    def file_exists(self, relative_path: str) -> bool:
        """
        Verifica se file esiste.

        Args:
            relative_path: Path relativo

        Returns:
            True se esiste
        """
        return self.get_file_path(relative_path).exists()

    def delete_file(self, relative_path: str) -> bool:
        """
        Elimina file da disco (hard delete).

        Args:
            relative_path: Path relativo

        Returns:
            True se eliminato
        """
        try:
            file_path = self.get_file_path(relative_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {relative_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {relative_path}: {e}")
            return False

    # =========================================================================
    # IMAGE PROCESSING
    # =========================================================================

    def _is_image(self, mime_type: str) -> bool:
        """Verifica se file è un'immagine"""
        return mime_type.startswith("image/")

    def create_thumbnail(
        self,
        source_path: str,
        max_size: Tuple[int, int] = THUMBNAIL_SIZE,
        quality: int = THUMBNAIL_QUALITY,
    ) -> Optional[str]:
        """
        Crea thumbnail per immagine.

        Args:
            source_path: Path relativo immagine sorgente
            max_size: Dimensione massima (width, height)
            quality: Qualità JPEG (1-100)

        Returns:
            Path relativo thumbnail o None se errore
        """
        try:
            source_full_path = self.get_file_path(source_path)

            if not source_full_path.exists():
                logger.warning(f"Source image not found: {source_path}")
                return None

            # Apri immagine
            with Image.open(source_full_path) as img:
                # Converti RGBA in RGB se necessario
                if img.mode in ("RGBA", "LA", "P"):
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                    img = background

                # Ridimensiona mantenendo aspect ratio
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

                # Genera nome thumbnail
                source_name = Path(source_path).stem
                source_dir = Path(source_path).parent
                thumb_name = f"{source_name}_thumb.jpg"
                thumb_relative_path = str(source_dir / thumb_name)
                thumb_full_path = self.get_file_path(thumb_relative_path)

                # Salva thumbnail
                img.save(thumb_full_path, "JPEG", quality=quality, optimize=True)

                logger.info(f"Thumbnail created: {thumb_relative_path}")
                return thumb_relative_path

        except Exception as e:
            logger.error(f"Error creating thumbnail for {source_path}: {e}")
            return None

    def resize_avatar(
        self,
        source_path: str,
        size: Tuple[int, int] = AVATAR_SIZE,
        quality: int = AVATAR_QUALITY,
    ) -> Optional[str]:
        """
        Ridimensiona e ottimizza avatar.

        Crop al centro per mantenere aspect ratio quadrato.

        Args:
            source_path: Path relativo immagine sorgente
            size: Dimensione finale (width, height)
            quality: Qualità JPEG

        Returns:
            Path relativo avatar processato
        """
        try:
            source_full_path = self.get_file_path(source_path)

            with Image.open(source_full_path) as img:
                # Converti in RGB
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Crop al centro per quadrato
                width, height = img.size
                min_dimension = min(width, height)

                left = (width - min_dimension) // 2
                top = (height - min_dimension) // 2
                right = left + min_dimension
                bottom = top + min_dimension

                img = img.crop((left, top, right, bottom))

                # Resize
                img = img.resize(size, Image.Resampling.LANCZOS)

                # Sovrascrivi file originale
                img.save(source_full_path, "JPEG", quality=quality, optimize=True)

                logger.info(f"Avatar resized: {source_path}")
                return source_path

        except Exception as e:
            logger.error(f"Error resizing avatar {source_path}: {e}")
            return None

    def get_image_metadata(self, file_path: str) -> Optional[dict]:
        """
        Estrae metadata da immagine.

        Args:
            file_path: Path relativo immagine

        Returns:
            Dict con metadata o None
        """
        try:
            full_path = self.get_file_path(file_path)

            with Image.open(full_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "format": img.format,
                    "mode": img.mode,
                }

        except Exception as e:
            logger.error(f"Error extracting image metadata from {file_path}: {e}")
            return None


# =============================================================================
# GLOBAL INSTANCE
# =============================================================================

# Singleton instance
file_storage_service = FileStorageService()
