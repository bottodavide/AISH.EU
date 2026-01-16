"""
Modulo: services.py
Descrizione: API endpoints per gestione servizi di consulenza
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func, or_
from pydantic import BaseModel, Field

from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.service import Service, ServiceCategory, ServiceType, PricingType

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================


class ServiceResponse(BaseModel):
    """Response for single service"""

    id: str
    slug: str
    name: str
    category: str
    type: str
    short_description: Optional[str]
    pricing_type: str
    price_min: Optional[float]
    price_max: Optional[float]
    is_featured: bool
    is_published: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceListResponse(BaseModel):
    """Response for service list with pagination"""

    services: list[ServiceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ServiceCreateRequest(BaseModel):
    """Request for creating a new service"""

    slug: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    category: str
    type: str
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    pricing_type: str = "custom"
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: str = "EUR"
    is_active: bool = True
    is_featured: bool = False
    sort_order: int = 0
    published_at: Optional[datetime] = None

    # Frontend compatibility fields
    is_published: Optional[bool] = None  # Maps to published_at
    duration_weeks: Optional[int] = None  # Ignored for now
    features: Optional[list[str]] = None  # Ignored for now
    deliverables: Optional[list[str]] = None  # Ignored for now
    target_audience: Optional[list[str]] = None  # Ignored for now

    class Config:
        extra = "ignore"  # Ignore unknown fields


class ServiceUpdateRequest(BaseModel):
    """Request for updating a service"""

    slug: Optional[str] = Field(None, max_length=255)
    name: Optional[str] = Field(None, max_length=255)
    category: Optional[str] = None
    type: Optional[str] = None
    short_description: Optional[str] = None
    long_description: Optional[str] = None
    pricing_type: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    currency: Optional[str] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    sort_order: Optional[int] = None
    published_at: Optional[datetime] = None

    # Frontend compatibility fields
    is_published: Optional[bool] = None  # Maps to published_at
    duration_weeks: Optional[int] = None  # Ignored for now
    features: Optional[list[str]] = None  # Ignored for now
    deliverables: Optional[list[str]] = None  # Ignored for now
    target_audience: Optional[list[str]] = None  # Ignored for now

    class Config:
        extra = "ignore"  # Ignore unknown fields


# ============================================================================
# DEPENDENCIES
# ============================================================================


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin or editor role"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Editor role required",
        )
    return current_user


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get(
    "/services/public",
    response_model=ServiceListResponse,
    tags=["Services"],
)
async def list_services_public(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
):
    """
    List published services (public endpoint).

    Returns only active/published services.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        category: Filter by category

    Returns:
        List of services with pagination info
    """
    try:
        # Build base query - only show active services
        query = select(Service).where(Service.is_active == True)

        # Apply category filter
        if category:
            try:
                category_enum = ServiceCategory(category)
                query = query.where(Service.category == category_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category. Must be one of: {', '.join([c.value for c in ServiceCategory])}",
                )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order_by(Service.sort_order.asc(), desc(Service.created_at)).offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        services = result.scalars().all()

        # Build response
        service_responses = []
        for service in services:
            service_responses.append(
                ServiceResponse(
                    id=str(service.id),
                    slug=service.slug,
                    name=service.name,
                    category=service.category.value,
                    type=service.type.value,
                    short_description=service.short_description,
                    pricing_type=service.pricing_type.value,
                    price_min=float(service.price_min) if service.price_min else None,
                    price_max=float(service.price_max) if service.price_max else None,
                    is_featured=service.is_featured,
                    is_published=service.is_published,
                    created_at=service.created_at,
                    updated_at=service.updated_at,
                )
            )

        return ServiceListResponse(
            services=service_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing public services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing services: {str(e)}",
        )


@router.get(
    "/services",
    response_model=ServiceListResponse,
    tags=["Services"],
)
async def list_services(
    page: int = 1,
    page_size: int = 20,
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    List all services with pagination and filters.

    Admin/Editor only.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        category: Filter by category
        search: Search in name and description

    Returns:
        List of services with pagination info
    """
    try:
        # Build base query
        query = select(Service)

        # Apply category filter
        if category:
            try:
                category_enum = ServiceCategory(category)
                query = query.where(Service.category == category_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category. Must be one of: {', '.join([c.value for c in ServiceCategory])}",
                )

        # Apply search filter
        if search:
            search_filter = f"%{search}%"
            query = query.where(
                or_(
                    Service.name.ilike(search_filter),
                    Service.short_description.ilike(search_filter),
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Calculate total pages
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order_by(desc(Service.created_at)).offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        services = result.scalars().all()

        # Build response
        service_responses = []
        for service in services:
            service_responses.append(
                ServiceResponse(
                    id=str(service.id),
                    slug=service.slug,
                    name=service.name,
                    category=service.category.value,
                    type=service.type.value,
                    short_description=service.short_description,
                    pricing_type=service.pricing_type.value,
                    price_min=float(service.price_min) if service.price_min else None,
                    price_max=float(service.price_max) if service.price_max else None,
                    is_featured=service.is_featured,
                    is_published=service.is_published,
                    created_at=service.created_at,
                    updated_at=service.updated_at,
                )
            )

        return ServiceListResponse(
            services=service_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing services: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing services: {str(e)}",
        )


@router.get(
    "/services/by-slug/{slug}",
    response_model=ServiceResponse,
    tags=["Services"],
)
async def get_service_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_async_db),
):
    """
    Get a single service by slug (public endpoint).

    Args:
        slug: Service slug

    Returns:
        Service details

    Raises:
        404: Service not found
    """
    try:
        # Query for service by slug
        query = select(Service).where(Service.slug == slug)
        result = await db.execute(query)
        service = result.scalar_one_or_none()

        # Check if found
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with slug '{slug}' not found",
            )

        # Check if published (public endpoint should only show published services)
        if not service.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service not available",
            )

        # Build response
        return ServiceResponse(
            id=str(service.id),
            slug=service.slug,
            name=service.name,
            category=service.category.value,
            type=service.type.value,
            short_description=service.short_description,
            pricing_type=service.pricing_type.value,
            price_min=float(service.price_min) if service.price_min else None,
            price_max=float(service.price_max) if service.price_max else None,
            is_featured=service.is_featured,
            is_published=service.is_published,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching service by slug {slug}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching service: {str(e)}",
        )


@router.get(
    "/services/{service_id}",
    response_model=ServiceResponse,
    tags=["Services"],
)
async def get_service(
    service_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Get a single service by ID.

    Admin/Editor only.

    Args:
        service_id: Service UUID

    Returns:
        Service details

    Raises:
        404: Service not found
    """
    try:
        # Query for service
        query = select(Service).where(Service.id == service_id)
        result = await db.execute(query)
        service = result.scalar_one_or_none()

        # Check if found
        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID {service_id} not found",
            )

        # Build response
        return ServiceResponse(
            id=str(service.id),
            slug=service.slug,
            name=service.name,
            category=service.category.value,
            type=service.type.value,
            short_description=service.short_description,
            pricing_type=service.pricing_type.value,
            price_min=float(service.price_min) if service.price_min else None,
            price_max=float(service.price_max) if service.price_max else None,
            is_featured=service.is_featured,
            is_published=service.is_published,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching service {service_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching service: {str(e)}",
        )


@router.post(
    "/services",
    response_model=ServiceResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Services"],
)
async def create_service(
    request: ServiceCreateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Create a new service.

    Admin/Editor only.

    Args:
        request: Service data

    Returns:
        Created service

    Raises:
        400: Invalid data or duplicate slug
    """
    try:
        # Normalize enum values (convert to lowercase)
        category_value = request.category.lower()
        type_value = request.type.lower()
        pricing_type_value = request.pricing_type.lower()

        # Validate enums
        try:
            category_enum = ServiceCategory(category_value)
            type_enum = ServiceType(type_value)
            pricing_type_enum = PricingType(pricing_type_value)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid enum value: {str(e)}",
            )

        # Check slug uniqueness
        existing = await db.execute(
            select(Service).where(Service.slug == request.slug)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Service with slug '{request.slug}' already exists",
            )

        # Map is_published to is_active and published_at
        is_active = request.is_active
        published_at = request.published_at

        if request.is_published is not None:
            is_active = request.is_published
            if request.is_published:
                # Set published_at to now if not explicitly provided
                from datetime import timezone
                published_at = published_at or datetime.now(timezone.utc)
            else:
                published_at = None

        # Create service
        service = Service(
            slug=request.slug,
            name=request.name,
            category=category_enum,
            type=type_enum,
            short_description=request.short_description,
            long_description=request.long_description,
            pricing_type=pricing_type_enum,
            price_min=request.price_min,
            price_max=request.price_max,
            currency=request.currency,
            is_active=is_active,
            is_featured=request.is_featured,
            sort_order=request.sort_order,
            published_at=published_at,
        )

        db.add(service)
        await db.commit()
        await db.refresh(service)

        logger.info(f"Created service: {service.id} - {service.name}")

        # Build response
        return ServiceResponse(
            id=str(service.id),
            slug=service.slug,
            name=service.name,
            category=service.category.value,
            type=service.type.value,
            short_description=service.short_description,
            pricing_type=service.pricing_type.value,
            price_min=float(service.price_min) if service.price_min else None,
            price_max=float(service.price_max) if service.price_max else None,
            is_featured=service.is_featured,
            is_published=service.is_published,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating service: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating service: {str(e)}",
        )


@router.put(
    "/services/{service_id}",
    response_model=ServiceResponse,
    tags=["Services"],
)
async def update_service(
    service_id: UUID,
    request: ServiceUpdateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Update a service.

    Admin/Editor only.

    Args:
        service_id: Service UUID
        request: Updated service data

    Returns:
        Updated service

    Raises:
        404: Service not found
        400: Invalid data or duplicate slug
    """
    try:
        # Find service
        query = select(Service).where(Service.id == service_id)
        result = await db.execute(query)
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID {service_id} not found",
            )

        # Update fields if provided
        if request.slug is not None:
            # Check slug uniqueness
            existing = await db.execute(
                select(Service).where(
                    Service.slug == request.slug,
                    Service.id != service_id
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Service with slug '{request.slug}' already exists",
                )
            service.slug = request.slug

        if request.name is not None:
            service.name = request.name

        if request.category is not None:
            try:
                category_value = request.category.lower()
                service.category = ServiceCategory(category_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category. Must be one of: {', '.join([c.value for c in ServiceCategory])}",
                )

        if request.type is not None:
            try:
                type_value = request.type.lower()
                service.type = ServiceType(type_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid type. Must be one of: {', '.join([t.value for t in ServiceType])}",
                )

        if request.short_description is not None:
            service.short_description = request.short_description

        if request.long_description is not None:
            service.long_description = request.long_description

        if request.pricing_type is not None:
            try:
                pricing_type_value = request.pricing_type.lower()
                service.pricing_type = PricingType(pricing_type_value)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid pricing_type. Must be one of: {', '.join([p.value for p in PricingType])}",
                )

        if request.price_min is not None:
            service.price_min = request.price_min

        if request.price_max is not None:
            service.price_max = request.price_max

        if request.currency is not None:
            service.currency = request.currency

        if request.is_active is not None:
            service.is_active = request.is_active

        if request.is_featured is not None:
            service.is_featured = request.is_featured

        if request.sort_order is not None:
            service.sort_order = request.sort_order

        if request.published_at is not None:
            service.published_at = request.published_at

        # Map is_published to is_active and published_at
        if request.is_published is not None:
            service.is_active = request.is_published
            if request.is_published:
                # Set published_at to now if not already set
                if not service.published_at:
                    from datetime import timezone
                    service.published_at = datetime.now(timezone.utc)
            else:
                service.published_at = None

        # Commit changes
        await db.commit()
        await db.refresh(service)

        logger.info(f"Updated service: {service.id} - {service.name}")

        # Build response
        return ServiceResponse(
            id=str(service.id),
            slug=service.slug,
            name=service.name,
            category=service.category.value,
            type=service.type.value,
            short_description=service.short_description,
            pricing_type=service.pricing_type.value,
            price_min=float(service.price_min) if service.price_min else None,
            price_max=float(service.price_max) if service.price_max else None,
            is_featured=service.is_featured,
            is_published=service.is_published,
            created_at=service.created_at,
            updated_at=service.updated_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating service {service_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating service: {str(e)}",
        )


@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Services"],
)
async def delete_service(
    service_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Delete a service.

    Admin/Editor only.

    Args:
        service_id: Service UUID

    Raises:
        404: Service not found
    """
    try:
        # Find service
        query = select(Service).where(Service.id == service_id)
        result = await db.execute(query)
        service = result.scalar_one_or_none()

        if not service:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service with ID {service_id} not found",
            )

        # Delete service
        await db.delete(service)
        await db.commit()

        logger.info(f"Deleted service: {service_id}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting service {service_id}: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting service: {str(e)}",
        )


logger.debug("Services routes loaded")
