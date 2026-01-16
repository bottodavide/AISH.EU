"""
Modulo: homepage.py
Descrizione: API routes per contenuti homepage (banner)
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import require_admin
from app.core.exceptions import ResourceNotFoundError
from app.models.homepage import HomepageBanner
from app.models.user import User
from app.schemas.homepage import (
    HomepageBannerCreate,
    HomepageBannerUpdate,
    HomepageBannerResponse,
    HomepageBannerListResponse,
)
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/homepage", tags=["Homepage"])


# =============================================================================
# PUBLIC ENDPOINTS - Banner visibili
# =============================================================================

@router.get("/banners", response_model=HomepageBannerListResponse)
async def list_banners(
    position: Optional[str] = Query(None, description="Filtra per posizione (hero, slider, section)"),
    active_only: bool = Query(True, description="Mostra solo banner attivi"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
) -> HomepageBannerListResponse:
    """
    Get list of homepage banners (public endpoint).

    - Filter by position
    - Only active banners by default
    - Respects start_date and end_date validity
    - Ordered by display_order
    """
    logger.info(f"Fetching homepage banners (position={position}, active_only={active_only})")

    # Build query
    query = select(HomepageBanner)

    # Filter by position
    if position:
        query = query.where(HomepageBanner.position == position)

    # Filter active only
    if active_only:
        query = query.where(HomepageBanner.is_active == True)

        # Check date validity
        now = datetime.utcnow()
        query = query.where(
            (HomepageBanner.start_date.is_(None) | (HomepageBanner.start_date <= now)) &
            (HomepageBanner.end_date.is_(None) | (HomepageBanner.end_date >= now))
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Order by display_order
    query = query.order_by(HomepageBanner.display_order.asc())

    # Pagination
    query = query.limit(page_size).offset((page - 1) * page_size)

    # Execute
    result = await db.execute(query)
    banners = result.scalars().all()

    total_pages = (total + page_size - 1) // page_size

    return HomepageBannerListResponse(
        banners=[HomepageBannerResponse.model_validate(b) for b in banners],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/banners/{banner_id}", response_model=HomepageBannerResponse)
async def get_banner(
    banner_id: UUID,
    db: AsyncSession = Depends(get_async_db),
) -> HomepageBannerResponse:
    """Get single banner by ID (public endpoint)."""
    logger.info(f"Fetching banner {banner_id}")

    result = await db.execute(
        select(HomepageBanner).where(HomepageBanner.id == banner_id)
    )
    banner = result.scalar_one_or_none()

    if not banner:
        raise ResourceNotFoundError(resource_type="HomepageBanner", resource_id=str(banner_id))

    return HomepageBannerResponse.model_validate(banner)


# =============================================================================
# ADMIN ENDPOINTS - Gestione completa banner
# =============================================================================

@router.post("/banners", response_model=HomepageBannerResponse)
async def create_banner(
    data: HomepageBannerCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> HomepageBannerResponse:
    """
    Create new homepage banner.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} creating homepage banner")

    # Create banner
    banner = HomepageBanner(
        title=data.title,
        subtitle=data.subtitle,
        description=data.description,
        image_url=data.image_url,
        video_url=data.video_url,
        cta_text=data.cta_text,
        cta_link=data.cta_link,
        cta_variant=data.cta_variant,
        position=data.position,
        display_order=data.display_order,
        background_color=data.background_color,
        text_color=data.text_color,
        is_active=data.is_active,
        start_date=data.start_date,
        end_date=data.end_date,
    )

    db.add(banner)
    await db.commit()
    await db.refresh(banner)

    logger.info(f"Banner {banner.id} created successfully")

    return HomepageBannerResponse.model_validate(banner)


@router.put("/banners/{banner_id}", response_model=HomepageBannerResponse)
async def update_banner(
    banner_id: UUID,
    data: HomepageBannerUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> HomepageBannerResponse:
    """
    Update homepage banner.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} updating banner {banner_id}")

    # Load banner
    result = await db.execute(
        select(HomepageBanner).where(HomepageBanner.id == banner_id)
    )
    banner = result.scalar_one_or_none()

    if not banner:
        raise ResourceNotFoundError(resource_type="HomepageBanner", resource_id=str(banner_id))

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(banner, field, value)

    await db.commit()
    await db.refresh(banner)

    logger.info(f"Banner {banner_id} updated successfully")

    return HomepageBannerResponse.model_validate(banner)


@router.delete("/banners/{banner_id}", response_model=SuccessResponse)
async def delete_banner(
    banner_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Delete homepage banner.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} deleting banner {banner_id}")

    # Check banner exists
    result = await db.execute(
        select(HomepageBanner).where(HomepageBanner.id == banner_id)
    )
    banner = result.scalar_one_or_none()

    if not banner:
        raise ResourceNotFoundError(resource_type="HomepageBanner", resource_id=str(banner_id))

    # Delete banner
    await db.execute(
        delete(HomepageBanner).where(HomepageBanner.id == banner_id)
    )
    await db.commit()

    logger.info(f"Banner {banner_id} deleted successfully")

    return SuccessResponse(
        message="Banner deleted successfully",
        data={"banner_id": str(banner_id)},
    )


@router.patch("/banners/{banner_id}/reorder", response_model=SuccessResponse)
async def reorder_banner(
    banner_id: UUID,
    new_order: int = Query(..., ge=0, description="Nuovo ordine di visualizzazione"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Change banner display order.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} reordering banner {banner_id} to position {new_order}")

    # Load banner
    result = await db.execute(
        select(HomepageBanner).where(HomepageBanner.id == banner_id)
    )
    banner = result.scalar_one_or_none()

    if not banner:
        raise ResourceNotFoundError(resource_type="HomepageBanner", resource_id=str(banner_id))

    # Update order
    banner.display_order = new_order
    await db.commit()

    logger.info(f"Banner {banner_id} reordered to {new_order}")

    return SuccessResponse(
        message="Banner reordered successfully",
        data={"banner_id": str(banner_id), "new_order": new_order},
    )


logger.info("Homepage router initialized")
