"""
Modulo: use_cases.py
Descrizione: API routes per casi d'uso
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import require_admin
from app.core.exceptions import ResourceNotFoundError, BusinessLogicError
from app.models.use_case import UseCase
from app.models.user import User
from app.schemas.use_case import (
    UseCaseCreate,
    UseCaseUpdate,
    UseCaseResponse,
    UseCaseListResponse,
)
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/use-cases", tags=["Use Cases"])


# =============================================================================
# PUBLIC ENDPOINTS
# =============================================================================


@router.get("", response_model=UseCaseListResponse)
async def list_use_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    industry: Optional[str] = Query(None, description="Filtra per settore"),
    db: AsyncSession = Depends(get_async_db),
) -> UseCaseListResponse:
    """
    Lista casi d'uso pubblici (solo attivi).

    Accessibile a tutti, non richiede autenticazione.
    """
    logger.info(f"Listing use cases - page: {page}, industry: {industry}")

    # Build query
    query = select(UseCase).where(UseCase.is_active == True)

    # Filter by industry
    if industry:
        query = query.where(UseCase.industry == industry)

    # Order by display_order
    query = query.order_by(UseCase.display_order.asc(), UseCase.created_at.desc())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    query = query.limit(page_size).offset(offset)

    # Execute
    result = await db.execute(query)
    use_cases = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return UseCaseListResponse(
        use_cases=[UseCaseResponse.model_validate(uc) for uc in use_cases],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{use_case_id}", response_model=UseCaseResponse)
async def get_use_case(
    use_case_id: UUID,
    db: AsyncSession = Depends(get_async_db),
) -> UseCaseResponse:
    """
    Ottieni dettagli caso d'uso per ID.

    Accessibile a tutti, non richiede autenticazione.
    Restituisce solo casi d'uso attivi.
    """
    logger.info(f"Getting use case {use_case_id}")

    query = select(UseCase).where(
        UseCase.id == use_case_id,
        UseCase.is_active == True,
    )
    result = await db.execute(query)
    use_case = result.scalar_one_or_none()

    if not use_case:
        raise ResourceNotFoundError(resource_type="UseCase", resource_id=str(use_case_id))

    return UseCaseResponse.model_validate(use_case)


@router.get("/by-slug/{slug}", response_model=UseCaseResponse)
async def get_use_case_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_async_db),
) -> UseCaseResponse:
    """
    Ottieni dettagli caso d'uso per slug.

    Accessibile a tutti, non richiede autenticazione.
    Restituisce solo casi d'uso attivi.
    """
    logger.info(f"Getting use case by slug: {slug}")

    query = select(UseCase).where(
        UseCase.slug == slug,
        UseCase.is_active == True,
    )
    result = await db.execute(query)
    use_case = result.scalar_one_or_none()

    if not use_case:
        raise ResourceNotFoundError(resource_type="UseCase", resource_id=slug)

    return UseCaseResponse.model_validate(use_case)


# =============================================================================
# ADMIN ENDPOINTS
# =============================================================================


@router.get("/admin/all", response_model=UseCaseListResponse)
async def admin_list_use_cases(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    industry: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UseCaseListResponse:
    """
    Lista tutti i casi d'uso (admin).

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} listing use cases")

    # Build query
    query = select(UseCase)

    # Filters
    if industry:
        query = query.where(UseCase.industry == industry)
    if is_active is not None:
        query = query.where(UseCase.is_active == is_active)

    # Order
    query = query.order_by(UseCase.display_order.asc(), UseCase.created_at.desc())

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Pagination
    offset = (page - 1) * page_size
    query = query.limit(page_size).offset(offset)

    # Execute
    result = await db.execute(query)
    use_cases = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return UseCaseListResponse(
        use_cases=[UseCaseResponse.model_validate(uc) for uc in use_cases],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.post("/admin", response_model=UseCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_use_case(
    data: UseCaseCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UseCaseResponse:
    """
    Crea nuovo caso d'uso (admin).

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} creating use case: {data.title}")

    # Check slug uniqueness
    existing = await db.execute(
        select(UseCase).where(UseCase.slug == data.slug)
    )
    if existing.scalar_one_or_none():
        raise BusinessLogicError(message=f"Slug '{data.slug}' già in uso")

    # Create
    use_case = UseCase(**data.model_dump())
    db.add(use_case)
    await db.commit()
    await db.refresh(use_case)

    logger.info(f"Use case created: {use_case.id}")

    return UseCaseResponse.model_validate(use_case)


@router.put("/admin/{use_case_id}", response_model=UseCaseResponse)
async def update_use_case(
    use_case_id: UUID,
    data: UseCaseUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UseCaseResponse:
    """
    Aggiorna caso d'uso (admin).

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} updating use case {use_case_id}")

    # Load
    result = await db.execute(select(UseCase).where(UseCase.id == use_case_id))
    use_case = result.scalar_one_or_none()

    if not use_case:
        raise ResourceNotFoundError(resource_type="UseCase", resource_id=str(use_case_id))

    # Check slug uniqueness if changing
    if data.slug and data.slug != use_case.slug:
        existing = await db.execute(
            select(UseCase).where(UseCase.slug == data.slug)
        )
        if existing.scalar_one_or_none():
            raise BusinessLogicError(message=f"Slug '{data.slug}' già in uso")

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(use_case, field, value)

    await db.commit()
    await db.refresh(use_case)

    logger.info(f"Use case updated: {use_case.id}")

    return UseCaseResponse.model_validate(use_case)


@router.delete("/admin/{use_case_id}", response_model=SuccessResponse)
async def delete_use_case(
    use_case_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina caso d'uso (admin).

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} deleting use case {use_case_id}")

    # Load
    result = await db.execute(select(UseCase).where(UseCase.id == use_case_id))
    use_case = result.scalar_one_or_none()

    if not use_case:
        raise ResourceNotFoundError(resource_type="UseCase", resource_id=str(use_case_id))

    # Delete
    await db.delete(use_case)
    await db.commit()

    logger.info(f"Use case deleted: {use_case_id}")

    return SuccessResponse(
        message="Use case eliminato con successo",
        data={"use_case_id": str(use_case_id)},
    )


@router.patch("/admin/{use_case_id}/reorder", response_model=SuccessResponse)
async def reorder_use_case(
    use_case_id: UUID,
    new_order: int = Query(..., ge=0, description="Nuovo ordine di visualizzazione"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Cambia ordine di visualizzazione (admin).

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} reordering use case {use_case_id} to {new_order}")

    # Load
    result = await db.execute(select(UseCase).where(UseCase.id == use_case_id))
    use_case = result.scalar_one_or_none()

    if not use_case:
        raise ResourceNotFoundError(resource_type="UseCase", resource_id=str(use_case_id))

    # Update order
    use_case.display_order = new_order
    await db.commit()

    logger.info(f"Use case reordered: {use_case_id}")

    return SuccessResponse(
        message="Ordine aggiornato con successo",
        data={"use_case_id": str(use_case_id), "display_order": new_order},
    )


logger.info("Use cases routes loaded")
