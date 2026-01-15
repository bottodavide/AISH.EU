"""
Modulo: files.py
Descrizione: API routes per file upload e gestione storage
Autore: Claude per Davide
Data: 2026-01-15

Endpoints:
- POST /api/v1/files/upload - Upload file
- GET /api/v1/files - Lista file (con filtri)
- GET /api/v1/files/{file_id} - Metadata file
- GET /api/v1/files/{file_id}/download - Download file
- PATCH /api/v1/files/{file_id} - Aggiorna metadata (owner/admin)
- DELETE /api/v1/files/{file_id} - Soft delete (owner/admin)

Note:
- Storage locale organizzato per categoria
- Thumbnails automatici per immagini
- Access control basato su ownership
- Secure serving con autenticazione
"""

import logging
from datetime import datetime, timezone
from typing import Annotated, Optional
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File as FastAPIFile,
    Form,
    HTTPException,
    status,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy import desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_active_user, require_admin
from app.models.file import File, FileCategory, FileStatus
from app.models.user import User, UserRole
from app.schemas.base import SuccessResponse
from app.schemas.file import (
    FileFilters,
    FileListResponse,
    FileResponse,
    FileUpdateRequest,
    FileUploadResponse,
)
from app.services.file_storage import file_storage_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1/files", tags=["files"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def _build_file_url(file_id: UUID, filename: str) -> str:
    """
    Costruisce URL per download file.

    Format: /api/v1/files/{file_id}/download

    Args:
        file_id: UUID file
        filename: Nome file (non usato ma utile per SEO)

    Returns:
        URL string
    """
    return f"/api/v1/files/{file_id}/download"


async def _get_file_or_404(db: AsyncSession, file_id: UUID) -> File:
    """Recupera file o solleva 404"""
    result = await db.execute(select(File).where(File.id == file_id))
    file = result.scalar_one_or_none()

    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {file_id} non trovato",
        )

    if file.status == FileStatus.DELETED:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File eliminato",
        )

    return file


def _check_file_access(file: File, current_user: User) -> None:
    """
    Verifica che utente possa accedere al file.

    Rules:
    - File pubblici: tutti
    - File privati: owner o admin

    Args:
        file: File da verificare
        current_user: Utente corrente

    Raises:
        HTTPException: 403 se non autorizzato
    """
    # File pubblici accessibili a tutti
    if file.is_public:
        return

    # Admin possono accedere a tutti i file
    if current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        return

    # Owner può accedere ai propri file
    if file.uploaded_by_id == current_user.id:
        return

    # Altrimenti 403
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Non autorizzato ad accedere a questo file",
    )


# =============================================================================
# FILE UPLOAD ENDPOINT
# =============================================================================


@router.post(
    "/upload",
    response_model=FileUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload file",
    description="Carica file sul server con validazione e processing automatico",
)
async def upload_file(
    file: UploadFile = FastAPIFile(..., description="File da caricare"),
    category: FileCategory = Form(default=FileCategory.DOCUMENT, description="Categoria file"),
    description: Optional[str] = Form(None, max_length=500, description="Descrizione file"),
    is_public: bool = Form(False, description="File pubblico"),
    reference_type: Optional[str] = Form(None, max_length=50, description="Tipo entità collegata"),
    reference_id: Optional[str] = Form(None, description="ID entità collegata"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload file con validazione e processing.

    Workflow:
    1. Valida MIME type e dimensione per categoria
    2. Salva file su disco con nome univoco
    3. Calcola SHA256 hash
    4. Crea thumbnail se immagine
    5. Ridimensiona se avatar
    6. Salva metadata in database

    Security:
    - Validazione file type server-side
    - Size limits per categoria
    - Hash integrity check
    - Access control su ownership
    """
    logger.info(f"Uploading file: {file.filename} (category: {category}) by user {current_user.email}")

    try:
        # Salva file su disco
        stored_filename, file_path, sha256_hash, file_size, mime_type = (
            await file_storage_service.save_file(file, category)
        )

        # Crea record database
        db_file = File(
            uploaded_by_id=current_user.id,
            category=category,
            status=FileStatus.ACTIVE,
            filename=file.filename,
            stored_filename=stored_filename,
            file_path=file_path,
            mime_type=mime_type,
            file_size=file_size,
            file_extension=stored_filename.split(".")[-1] if "." in stored_filename else None,
            sha256_hash=sha256_hash,
            is_public=is_public,
            description=description,
            reference_type=reference_type,
            reference_id=UUID(reference_id) if reference_id else None,
        )

        # Image processing
        thumbnail_url = None
        if db_file.is_image():
            # Estrai metadata immagine
            image_metadata = file_storage_service.get_image_metadata(file_path)
            if image_metadata:
                db_file.image_metadata = image_metadata

            # Crea thumbnail per immagini generiche
            if category == FileCategory.IMAGE:
                thumb_path = file_storage_service.create_thumbnail(file_path)
                if thumb_path and image_metadata:
                    image_metadata["has_thumbnail"] = True
                    image_metadata["thumbnail_path"] = thumb_path
                    db_file.image_metadata = image_metadata
                    thumbnail_url = f"/api/v1/files/{db_file.id}/thumbnail"

            # Ridimensiona avatar
            elif category == FileCategory.AVATAR:
                file_storage_service.resize_avatar(file_path)
                # Ricarica metadata dopo resize
                db_file.image_metadata = file_storage_service.get_image_metadata(file_path)

        # Salva in database
        db.add(db_file)
        await db.commit()
        await db.refresh(db_file)

        logger.info(f"File uploaded successfully: {db_file.id} ({db_file.stored_filename})")

        # Build response
        return FileUploadResponse(
            file_id=db_file.id,
            filename=db_file.filename,
            stored_filename=db_file.stored_filename,
            file_path=db_file.file_path,
            mime_type=db_file.mime_type,
            file_size=db_file.file_size,
            category=db_file.category,
            url=_build_file_url(db_file.id, db_file.filename),
            thumbnail_url=thumbnail_url,
            created_at=db_file.created_at,
        )

    except ValueError as e:
        # Errori di validazione file
        logger.warning(f"File upload validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante upload file",
        )


# =============================================================================
# FILE LIST ENDPOINT
# =============================================================================


@router.get(
    "",
    response_model=list[FileListResponse],
    summary="Lista file",
    description="Lista file con filtri. Utenti vedono solo i propri file (eccetto pubblici), admin vedono tutti.",
)
async def list_files(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
    filters: FileFilters = Depends(),
):
    """
    Lista file con filtri.

    Permessi:
    - Customer: Solo propri file + file pubblici
    - Admin: Tutti i file
    """
    logger.info(f"Listing files for user {current_user.email}")

    query = select(File).where(File.status == FileStatus.ACTIVE)

    # Filtro per utente (se non admin)
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        # Mostra file propri O file pubblici
        query = query.where(
            or_(
                File.uploaded_by_id == current_user.id,
                File.is_public == True,
            )
        )
    elif filters.uploaded_by_id:
        # Admin può filtrare per uploader specifico
        query = query.where(File.uploaded_by_id == filters.uploaded_by_id)

    # Applica filtri
    if filters.category:
        query = query.where(File.category == filters.category)

    if filters.mime_type:
        query = query.where(File.mime_type == filters.mime_type)

    if filters.reference_type:
        query = query.where(File.reference_type == filters.reference_type)

    if filters.reference_id:
        query = query.where(File.reference_id == filters.reference_id)

    if filters.is_public is not None:
        query = query.where(File.is_public == filters.is_public)

    if filters.filename:
        query = query.where(File.filename.ilike(f"%{filters.filename}%"))

    # Ordinamento
    if filters.sort_order == "desc":
        query = query.order_by(desc(getattr(File, filters.sort_by)))
    else:
        query = query.order_by(getattr(File, filters.sort_by))

    # Paginazione
    query = query.offset(filters.skip).limit(filters.limit)

    result = await db.execute(query)
    files = result.scalars().all()

    # Build response con URLs
    response = []
    for file in files:
        file_dict = {
            "id": file.id,
            "created_at": file.created_at,
            "updated_at": file.updated_at,
            "filename": file.filename,
            "category": file.category,
            "mime_type": file.mime_type,
            "file_size": file.file_size,
            "is_public": file.is_public,
            "download_count": file.download_count,
            "url": _build_file_url(file.id, file.filename),
        }
        response.append(FileListResponse(**file_dict))

    return response


# =============================================================================
# FILE METADATA ENDPOINT
# =============================================================================


@router.get(
    "/{file_id}",
    response_model=FileResponse,
    summary="Dettaglio file",
    description="Recupera metadata completi file",
)
async def get_file_metadata(
    file_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Recupera metadata file con access control"""
    file = await _get_file_or_404(db, file_id)
    _check_file_access(file, current_user)

    # Build response con URLs e helper fields
    return FileResponse(
        **file.__dict__,
        url=_build_file_url(file.id, file.filename),
        thumbnail_url=(
            f"/api/v1/files/{file.id}/thumbnail"
            if file.is_image() and file.image_metadata and file.image_metadata.get("has_thumbnail")
            else None
        ),
        size_human=file.size_human_readable(),
    )


# =============================================================================
# FILE DOWNLOAD ENDPOINT
# =============================================================================


@router.get(
    "/{file_id}/download",
    response_class=FileResponse,
    summary="Download file",
    description="Download file con access control",
)
async def download_file(
    file_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Download file dal server.

    Security:
    - Access control su ownership
    - File pubblici accessibili a tutti
    - Incrementa download counter
    - Aggiorna last_accessed_at
    """
    file = await _get_file_or_404(db, file_id)
    _check_file_access(file, current_user)

    # Verifica che file esista su disco
    if not file_storage_service.file_exists(file.file_path):
        logger.error(f"File not found on disk: {file.file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File non trovato su disco",
        )

    # Aggiorna stats
    file.download_count += 1
    file.last_accessed_at = datetime.now(timezone.utc)
    await db.commit()

    # Serve file
    full_path = file_storage_service.get_file_path(file.file_path)

    logger.info(f"File downloaded: {file.id} by user {current_user.email}")

    return FileResponse(
        path=str(full_path),
        filename=file.filename,
        media_type=file.mime_type,
    )


# =============================================================================
# FILE THUMBNAIL ENDPOINT
# =============================================================================


@router.get(
    "/{file_id}/thumbnail",
    response_class=FileResponse,
    summary="Get thumbnail",
    description="Recupera thumbnail immagine (se disponibile)",
)
async def get_thumbnail(
    file_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Recupera thumbnail per immagine"""
    file = await _get_file_or_404(db, file_id)
    _check_file_access(file, current_user)

    # Verifica che sia un'immagine con thumbnail
    if not file.is_image() or not file.image_metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail non disponibile",
        )

    thumbnail_path = file.image_metadata.get("thumbnail_path")
    if not thumbnail_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail non disponibile",
        )

    if not file_storage_service.file_exists(thumbnail_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail non trovata su disco",
        )

    full_path = file_storage_service.get_file_path(thumbnail_path)

    return FileResponse(
        path=str(full_path),
        media_type="image/jpeg",
    )


# =============================================================================
# FILE UPDATE ENDPOINT
# =============================================================================


@router.patch(
    "/{file_id}",
    response_model=FileResponse,
    summary="Aggiorna file metadata",
    description="Aggiorna metadata file (owner o admin)",
)
async def update_file(
    file_id: UUID,
    data: FileUpdateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Aggiorna metadata file (solo owner o admin)"""
    file = await _get_file_or_404(db, file_id)

    # Verifica permessi (owner o admin)
    is_owner = file.uploaded_by_id == current_user.id
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a modificare questo file",
        )

    # Aggiorna campi
    if data.description is not None:
        file.description = data.description

    if data.is_public is not None:
        file.is_public = data.is_public

    if data.reference_type is not None:
        file.reference_type = data.reference_type

    if data.reference_id is not None:
        file.reference_id = data.reference_id

    await db.commit()
    await db.refresh(file)

    logger.info(f"File metadata updated: {file.id}")

    return FileResponse(
        **file.__dict__,
        url=_build_file_url(file.id, file.filename),
        thumbnail_url=(
            f"/api/v1/files/{file.id}/thumbnail"
            if file.is_image() and file.image_metadata and file.image_metadata.get("has_thumbnail")
            else None
        ),
        size_human=file.size_human_readable(),
    )


# =============================================================================
# FILE DELETE ENDPOINT
# =============================================================================


@router.delete(
    "/{file_id}",
    response_model=SuccessResponse,
    summary="Elimina file",
    description="Soft delete file (owner o admin)",
)
async def delete_file(
    file_id: UUID,
    hard_delete: bool = False,  # Admin only per hard delete
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Elimina file (soft delete di default).

    Args:
        file_id: UUID file da eliminare
        hard_delete: Se True, elimina fisicamente da disco (admin only)

    Permessi:
    - Soft delete: owner o admin
    - Hard delete: solo admin
    """
    file = await _get_file_or_404(db, file_id)

    # Verifica permessi (owner o admin)
    is_owner = file.uploaded_by_id == current_user.id
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a eliminare questo file",
        )

    # Hard delete solo per admin
    if hard_delete and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hard delete permesso solo agli admin",
        )

    if hard_delete:
        # Hard delete: rimuovi da disco e database
        file_storage_service.delete_file(file.file_path)

        # Elimina anche thumbnail se esiste
        if file.is_image() and file.image_metadata:
            thumb_path = file.image_metadata.get("thumbnail_path")
            if thumb_path:
                file_storage_service.delete_file(thumb_path)

        await db.delete(file)
        await db.commit()

        logger.warning(f"File HARD deleted: {file.id} by {current_user.email}")

        return SuccessResponse(
            message="File eliminato permanentemente",
            data={"file_id": str(file_id)},
        )

    else:
        # Soft delete: marca come eliminato
        file.status = FileStatus.DELETED
        file.deleted_at = datetime.now(timezone.utc)
        file.deleted_by_id = current_user.id

        await db.commit()

        logger.info(f"File soft deleted: {file.id} by {current_user.email}")

        return SuccessResponse(
            message="File eliminato",
            data={"file_id": str(file_id)},
        )
