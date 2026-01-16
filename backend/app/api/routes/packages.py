"""
Modulo: packages.py
Descrizione: API routes per pacchetti consulenza
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_db
from app.core.dependencies import require_admin
from app.core.exceptions import ResourceNotFoundError, BusinessLogicError
from app.models.package import ConsultingPackage
from app.models.service import Service
from app.models.user import User
from app.schemas.package import (
    ConsultingPackageCreate,
    ConsultingPackageUpdate,
    ConsultingPackageResponse,
    ConsultingPackageListResponse,
    ConsultingPackagePublicResponse,
    ServiceReference,
)
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/packages", tags=["Packages"])


# =============================================================================
# PUBLIC ENDPOINTS - Pacchetti visibili
# =============================================================================

@router.get("", response_model=ConsultingPackageListResponse)
async def list_packages(
    active_only: bool = Query(True, description="Mostra solo pacchetti attivi"),
    featured_only: bool = Query(False, description="Mostra solo pacchetti in evidenza"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
) -> ConsultingPackageListResponse:
    """
    Get list of consulting packages (public endpoint).

    - Filter by active status
    - Filter by featured
    - Ordered by display_order
    - Includes services
    """
    logger.info(f"Fetching packages (active_only={active_only}, featured_only={featured_only})")

    # Build query
    query = select(ConsultingPackage).options(selectinload(ConsultingPackage.services))

    # Filter active
    if active_only:
        query = query.where(ConsultingPackage.is_active == True)

    # Filter featured
    if featured_only:
        query = query.where(ConsultingPackage.is_featured == True)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by display_order, then created_at
    query = query.order_by(ConsultingPackage.display_order.asc(), ConsultingPackage.created_at.desc())

    # Pagination
    query = query.limit(page_size).offset((page - 1) * page_size)

    # Execute
    result = await db.execute(query)
    packages = result.scalars().all()

    # Convert to response
    package_responses = []
    for pkg in packages:
        pkg_dict = {
            "id": str(pkg.id),
            "name": pkg.name,
            "slug": pkg.slug,
            "short_description": pkg.short_description,
            "description": pkg.description,
            "price": pkg.price,
            "original_price": pkg.original_price,
            "badge": pkg.badge,
            "badge_color": pkg.badge_color,
            "features_json": pkg.features_json,
            "duration_days": pkg.duration_days,
            "validity_info": pkg.validity_info,
            "cta_text": pkg.cta_text or "Acquista Ora",
            "is_active": pkg.is_active,
            "is_featured": pkg.is_featured,
            "display_order": pkg.display_order,
            "max_purchases": pkg.max_purchases,
            "purchased_count": pkg.purchased_count,
            "discount_percentage": pkg.discount_percentage,
            "is_available": pkg.is_available,
            "created_at": pkg.created_at,
            "updated_at": pkg.updated_at,
            "services": [
                ServiceReference(
                    id=str(svc.id),
                    slug=svc.slug,
                    name=svc.name,
                    short_description=svc.short_description
                )
                for svc in pkg.services
            ],
        }
        package_responses.append(ConsultingPackageResponse(**pkg_dict))

    total_pages = (total + page_size - 1) // page_size

    return ConsultingPackageListResponse(
        packages=package_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/{package_id}", response_model=ConsultingPackageResponse)
async def get_package(
    package_id: UUID,
    db: AsyncSession = Depends(get_async_db),
) -> ConsultingPackageResponse:
    """Get single package by ID (public endpoint)."""
    logger.info(f"Fetching package {package_id}")

    result = await db.execute(
        select(ConsultingPackage)
        .options(selectinload(ConsultingPackage.services))
        .where(ConsultingPackage.id == package_id)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise ResourceNotFoundError(resource_type="ConsultingPackage", resource_id=str(package_id))

    # Convert to response
    pkg_dict = {
        "id": str(package.id),
        "name": package.name,
        "slug": package.slug,
        "short_description": package.short_description,
        "description": package.description,
        "price": package.price,
        "original_price": package.original_price,
        "badge": package.badge,
        "badge_color": package.badge_color,
        "features_json": package.features_json,
        "duration_days": package.duration_days,
        "validity_info": package.validity_info,
        "cta_text": package.cta_text or "Acquista Ora",
        "is_active": package.is_active,
        "is_featured": package.is_featured,
        "display_order": package.display_order,
        "max_purchases": package.max_purchases,
        "purchased_count": package.purchased_count,
        "discount_percentage": package.discount_percentage,
        "is_available": package.is_available,
        "created_at": package.created_at,
        "updated_at": package.updated_at,
        "services": [
            ServiceReference(
                id=str(svc.id),
                slug=svc.slug,
                name=svc.name,
                short_description=svc.short_description
            )
            for svc in package.services
        ],
    }

    return ConsultingPackageResponse(**pkg_dict)


@router.get("/slug/{slug}", response_model=ConsultingPackageResponse)
async def get_package_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_async_db),
) -> ConsultingPackageResponse:
    """Get package by slug (public endpoint)."""
    logger.info(f"Fetching package by slug: {slug}")

    result = await db.execute(
        select(ConsultingPackage)
        .options(selectinload(ConsultingPackage.services))
        .where(ConsultingPackage.slug == slug)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise ResourceNotFoundError(resource_type="ConsultingPackage", resource_id=f"slug:{slug}")

    # Convert to response (same as get_package)
    pkg_dict = {
        "id": str(package.id),
        "name": package.name,
        "slug": package.slug,
        "short_description": package.short_description,
        "description": package.description,
        "price": package.price,
        "original_price": package.original_price,
        "badge": package.badge,
        "badge_color": package.badge_color,
        "features_json": package.features_json,
        "duration_days": package.duration_days,
        "validity_info": package.validity_info,
        "cta_text": package.cta_text or "Acquista Ora",
        "is_active": package.is_active,
        "is_featured": package.is_featured,
        "display_order": package.display_order,
        "max_purchases": package.max_purchases,
        "purchased_count": package.purchased_count,
        "discount_percentage": package.discount_percentage,
        "is_available": package.is_available,
        "created_at": package.created_at,
        "updated_at": package.updated_at,
        "services": [
            ServiceReference(
                id=str(svc.id),
                slug=svc.slug,
                name=svc.name,
                short_description=svc.short_description
            )
            for svc in package.services
        ],
    }

    return ConsultingPackageResponse(**pkg_dict)


# =============================================================================
# ADMIN ENDPOINTS - Gestione completa pacchetti
# =============================================================================

@router.post("", response_model=ConsultingPackageResponse)
async def create_package(
    data: ConsultingPackageCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> ConsultingPackageResponse:
    """
    Create new consulting package.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} creating package {data.name}")

    # Check slug uniqueness
    existing = await db.execute(
        select(ConsultingPackage).where(ConsultingPackage.slug == data.slug)
    )
    if existing.scalar_one_or_none():
        raise BusinessLogicError(message=f"Package with slug '{data.slug}' already exists")

    # Load services
    services = []
    if data.service_ids:
        services_result = await db.execute(
            select(Service).where(Service.id.in_(data.service_ids))
        )
        services = list(services_result.scalars().all())

        if len(services) != len(data.service_ids):
            raise BusinessLogicError(message="One or more service IDs are invalid")

    # Create package
    package = ConsultingPackage(
        name=data.name,
        slug=data.slug,
        short_description=data.short_description,
        description=data.description,
        price=data.price,
        original_price=data.original_price,
        badge=data.badge,
        badge_color=data.badge_color,
        features_json=data.features_json,
        duration_days=data.duration_days,
        validity_info=data.validity_info,
        cta_text=data.cta_text,
        is_active=data.is_active,
        is_featured=data.is_featured,
        display_order=data.display_order,
        max_purchases=data.max_purchases,
        services=services,
    )

    db.add(package)
    await db.commit()
    await db.refresh(package, ["services"])

    logger.info(f"Package {package.id} created successfully")

    # Convert to response
    pkg_dict = {
        "id": str(package.id),
        "name": package.name,
        "slug": package.slug,
        "short_description": package.short_description,
        "description": package.description,
        "price": package.price,
        "original_price": package.original_price,
        "badge": package.badge,
        "badge_color": package.badge_color,
        "features_json": package.features_json,
        "duration_days": package.duration_days,
        "validity_info": package.validity_info,
        "cta_text": package.cta_text or "Acquista Ora",
        "is_active": package.is_active,
        "is_featured": package.is_featured,
        "display_order": package.display_order,
        "max_purchases": package.max_purchases,
        "purchased_count": package.purchased_count,
        "discount_percentage": package.discount_percentage,
        "is_available": package.is_available,
        "created_at": package.created_at,
        "updated_at": package.updated_at,
        "services": [
            ServiceReference(
                id=str(svc.id),
                slug=svc.slug,
                name=svc.name,
                short_description=svc.short_description
            )
            for svc in package.services
        ],
    }

    return ConsultingPackageResponse(**pkg_dict)


@router.put("/{package_id}", response_model=ConsultingPackageResponse)
async def update_package(
    package_id: UUID,
    data: ConsultingPackageUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> ConsultingPackageResponse:
    """
    Update consulting package.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} updating package {package_id}")

    # Load package
    result = await db.execute(
        select(ConsultingPackage)
        .options(selectinload(ConsultingPackage.services))
        .where(ConsultingPackage.id == package_id)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise ResourceNotFoundError(resource_type="ConsultingPackage", resource_id=str(package_id))

    # Check slug uniqueness if changed
    if data.slug and data.slug != package.slug:
        existing = await db.execute(
            select(ConsultingPackage).where(ConsultingPackage.slug == data.slug)
        )
        if existing.scalar_one_or_none():
            raise BusinessLogicError(message=f"Package with slug '{data.slug}' already exists")

    # Update fields
    update_data = data.model_dump(exclude_unset=True, exclude={"service_ids"})
    for field, value in update_data.items():
        setattr(package, field, value)

    # Update services if provided
    if data.service_ids is not None:
        services_result = await db.execute(
            select(Service).where(Service.id.in_(data.service_ids))
        )
        services = list(services_result.scalars().all())

        if len(services) != len(data.service_ids):
            raise BusinessLogicError(message="One or more service IDs are invalid")

        package.services = services

    await db.commit()
    await db.refresh(package, ["services"])

    logger.info(f"Package {package_id} updated successfully")

    # Convert to response
    pkg_dict = {
        "id": str(package.id),
        "name": package.name,
        "slug": package.slug,
        "short_description": package.short_description,
        "description": package.description,
        "price": package.price,
        "original_price": package.original_price,
        "badge": package.badge,
        "badge_color": package.badge_color,
        "features_json": package.features_json,
        "duration_days": package.duration_days,
        "validity_info": package.validity_info,
        "cta_text": package.cta_text or "Acquista Ora",
        "is_active": package.is_active,
        "is_featured": package.is_featured,
        "display_order": package.display_order,
        "max_purchases": package.max_purchases,
        "purchased_count": package.purchased_count,
        "discount_percentage": package.discount_percentage,
        "is_available": package.is_available,
        "created_at": package.created_at,
        "updated_at": package.updated_at,
        "services": [
            ServiceReference(
                id=str(svc.id),
                slug=svc.slug,
                name=svc.name,
                short_description=svc.short_description
            )
            for svc in package.services
        ],
    }

    return ConsultingPackageResponse(**pkg_dict)


@router.delete("/{package_id}", response_model=SuccessResponse)
async def delete_package(
    package_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Delete consulting package.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} deleting package {package_id}")

    # Check package exists
    result = await db.execute(
        select(ConsultingPackage).where(ConsultingPackage.id == package_id)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise ResourceNotFoundError(resource_type="ConsultingPackage", resource_id=str(package_id))

    # Delete package
    await db.execute(
        delete(ConsultingPackage).where(ConsultingPackage.id == package_id)
    )
    await db.commit()

    logger.info(f"Package {package_id} deleted successfully")

    return SuccessResponse(
        message="Package deleted successfully",
        data={"package_id": str(package_id)},
    )


@router.patch("/{package_id}/reorder", response_model=SuccessResponse)
async def reorder_package(
    package_id: UUID,
    new_order: int = Query(..., ge=0, description="Nuovo ordine di visualizzazione"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Change package display order.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} reordering package {package_id} to {new_order}")

    # Load package
    result = await db.execute(
        select(ConsultingPackage).where(ConsultingPackage.id == package_id)
    )
    package = result.scalar_one_or_none()

    if not package:
        raise ResourceNotFoundError(resource_type="ConsultingPackage", resource_id=str(package_id))

    # Update order
    package.display_order = new_order
    await db.commit()

    logger.info(f"Package {package_id} reordered to {new_order}")

    return SuccessResponse(
        message="Package reordered successfully",
        data={"package_id": str(package_id), "new_order": new_order},
    )


logger.info("Packages router initialized")
