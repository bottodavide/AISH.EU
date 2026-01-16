"""
Modulo: services.py
Descrizione: API routes per gestione servizi consulenza
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_db
from app.core.dependencies import get_current_user_optional, require_admin
from app.core.exceptions import DuplicateResourceError, ResourceNotFoundError
from app.models.service import Service, ServiceContent, ServiceFAQ, ServiceImage
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.service import (
    ServiceContentCreate,
    ServiceContentResponse,
    ServiceContentUpdate,
    ServiceCreate,
    ServiceDetailResponse,
    ServiceFAQCreate,
    ServiceFAQResponse,
    ServiceFAQUpdate,
    ServiceFilters,
    ServiceImageCreate,
    ServiceImageResponse,
    ServiceImageUpdate,
    ServiceListResponse,
    ServiceResponse,
    ServiceUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/services", tags=["Services"])


# =============================================================================
# SERVICE CRUD
# =============================================================================


@router.get("", response_model=ServiceListResponse)
async def list_services(
    filters: ServiceFilters = Depends(),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> ServiceListResponse:
    """
    Lista servizi con filtri.

    Pubblico: Vede solo servizi pubblicati
    Admin: Vede tutti i servizi

    Args:
        filters: Filtri di ricerca
        current_user: Utente corrente (opzionale)

    Returns:
        ServiceListResponse: Lista servizi paginata
    """
    logger.info("Listing services")

    # Build query
    query = select(Service)

    # Se non admin, mostra solo pubblicati
    is_admin = current_user and current_user.role in ["super_admin", "admin"]
    if not is_admin:
        query = query.where(Service.is_published == True)

    # Apply filters
    if filters.category:
        query = query.where(Service.category == filters.category)

    if filters.pricing_type:
        query = query.where(Service.pricing_type == filters.pricing_type)

    if filters.is_published is not None and is_admin:
        query = query.where(Service.is_published == filters.is_published)

    if filters.search:
        search_pattern = f"%{filters.search}%"
        query = query.where(
            (Service.title.ilike(search_pattern))
            | (Service.subtitle.ilike(search_pattern))
        )

    # Order by created_at (TODO: Add display_order field to Service model)
    query = query.order_by(Service.created_at.desc())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.offset(filters.skip).limit(filters.limit)

    # Execute
    result = await db.execute(query)
    services = result.scalars().all()

    # Convert to response
    service_responses = []
    for service in services:
        # Compute price_display
        if service.pricing_type.value == "fixed":
            price_display = f"€{service.base_price}"
        elif service.pricing_type.value == "hourly":
            price_display = f"€{service.base_price}/ora"
        else:
            price_display = "Preventivo su misura"

        service_responses.append(
            ServiceResponse(
                id=service.id,
                slug=service.slug,
                title=service.title,
                subtitle=service.subtitle,
                category=service.category,
                pricing_type=service.pricing_type,
                base_price=service.base_price,
                currency=service.currency,
                is_published=service.is_published,
                # display_order=None,  # TODO: Add to model
                seo_title=service.seo_title,
                seo_description=service.seo_description,
                price_display=price_display,
                created_at=service.created_at,
                updated_at=service.updated_at,
            )
        )

    logger.info(f"Found {len(services)} services (total: {total})")

    return ServiceListResponse(
        services=service_responses,
        total=total,
    )


@router.get("/{service_identifier}", response_model=ServiceDetailResponse)
async def get_service(
    service_identifier: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> ServiceDetailResponse:
    """
    Ottiene dettaglio servizio con contenuti, FAQ e immagini.

    Pubblico: Solo servizi pubblicati
    Admin: Tutti i servizi

    Args:
        service_identifier: ID o slug del servizio
        current_user: Utente corrente (opzionale)

    Returns:
        ServiceDetailResponse: Dettaglio servizio completo
    """
    logger.info(f"Getting service {service_identifier}")

    # Try to parse as UUID first, otherwise use as slug
    try:
        service_id = UUID(service_identifier)
        where_clause = Service.id == service_id
    except ValueError:
        # Not a UUID, treat as slug
        where_clause = Service.slug == service_identifier

    # Load service with relationships
    query = (
        select(Service)
        .where(where_clause)
        .options(
            selectinload(Service.contents),
            selectinload(Service.faqs),
            selectinload(Service.images),
        )
    )

    result = await db.execute(query)
    service = result.scalar_one_or_none()

    if not service:
        logger.warning(f"Service not found: {service_identifier}")
        raise ResourceNotFoundError(
            resource_type="Service",
            resource_id=service_identifier,
        )

    # Se non admin, verifica che sia pubblicato
    is_admin = current_user and current_user.role in ["super_admin", "admin"]
    if not is_admin and not service.is_published:
        logger.warning(f"Unpublished service access denied: {service_identifier}")
        raise ResourceNotFoundError(
            resource_type="Service",
            resource_id=service_id,
        )

    # Compute price_display
    if service.pricing_type.value == "fixed":
        price_display = f"€{service.base_price}"
    elif service.pricing_type.value == "hourly":
        price_display = f"€{service.base_price}/ora"
    else:
        price_display = "Preventivo su misura"

    # Convert to response
    return ServiceDetailResponse(
        id=service.id,
        slug=service.slug,
        title=service.title,
        subtitle=service.subtitle,
        category=service.category,
        pricing_type=service.pricing_type,
        base_price=service.base_price,
        currency=service.currency,
        is_published=service.is_published,
        display_order=service.display_order,
        seo_title=service.seo_title,
        seo_description=service.seo_description,
        price_display=price_display,
        created_at=service.created_at,
        updated_at=service.updated_at,
        contents=[ServiceContentResponse.model_validate(c) for c in service.contents],
        faqs=[ServiceFAQResponse.model_validate(f) for f in service.faqs],
        images=[ServiceImageResponse.model_validate(i) for i in service.images],
    )


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: ServiceCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> ServiceResponse:
    """
    Crea nuovo servizio (solo admin).

    Args:
        data: Dati servizio
        current_user: Admin autenticato

    Returns:
        ServiceResponse: Servizio creato
    """
    logger.info(f"Creating service: {data.title} (by {current_user.email})")

    # Verifica slug univoco
    result = await db.execute(select(Service).where(Service.slug == data.slug))
    existing = result.scalar_one_or_none()

    if existing:
        logger.warning(f"Service slug already exists: {data.slug}")
        raise DuplicateResourceError(
            resource_type="Service",
            field="slug",
            value=data.slug,
        )

    # Crea service
    service = Service(**data.model_dump())
    db.add(service)
    await db.commit()
    await db.refresh(service)

    logger.info(f"Service created: {service.title} (ID: {service.id})")

    # Compute price_display
    if service.pricing_type.value == "fixed":
        price_display = f"€{service.base_price}"
    elif service.pricing_type.value == "hourly":
        price_display = f"€{service.base_price}/ora"
    else:
        price_display = "Preventivo su misura"

    return ServiceResponse(
        id=service.id,
        slug=service.slug,
        title=service.title,
        subtitle=service.subtitle,
        category=service.category,
        pricing_type=service.pricing_type,
        base_price=service.base_price,
        currency=service.currency,
        is_published=service.is_published,
        display_order=service.display_order,
        seo_title=service.seo_title,
        seo_description=service.seo_description,
        price_display=price_display,
        created_at=service.created_at,
        updated_at=service.updated_at,
    )


@router.put("/{service_id}", response_model=ServiceResponse)
async def update_service(
    service_id: UUID,
    data: ServiceUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> ServiceResponse:
    """
    Aggiorna servizio (solo admin).

    Args:
        service_id: ID servizio
        data: Dati da aggiornare
        current_user: Admin autenticato

    Returns:
        ServiceResponse: Servizio aggiornato
    """
    logger.info(f"Updating service {service_id} (by {current_user.email})")

    # Load service
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        logger.warning(f"Service not found: {service_id}")
        raise ResourceNotFoundError(
            resource_type="Service",
            resource_id=service_id,
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)

    if "slug" in update_data and update_data["slug"] != service.slug:
        # Verifica slug univoco
        result = await db.execute(
            select(Service).where(Service.slug == update_data["slug"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.warning(f"Service slug already exists: {update_data['slug']}")
            raise DuplicateResourceError(
                resource_type="Service",
                field="slug",
                value=update_data["slug"],
            )

    for field, value in update_data.items():
        setattr(service, field, value)

    await db.commit()
    await db.refresh(service)

    logger.info(f"Service updated: {service.title}")

    # Compute price_display
    if service.pricing_type.value == "fixed":
        price_display = f"€{service.base_price}"
    elif service.pricing_type.value == "hourly":
        price_display = f"€{service.base_price}/ora"
    else:
        price_display = "Preventivo su misura"

    return ServiceResponse(
        id=service.id,
        slug=service.slug,
        title=service.title,
        subtitle=service.subtitle,
        category=service.category,
        pricing_type=service.pricing_type,
        base_price=service.base_price,
        currency=service.currency,
        is_published=service.is_published,
        display_order=service.display_order,
        seo_title=service.seo_title,
        seo_description=service.seo_description,
        price_display=price_display,
        created_at=service.created_at,
        updated_at=service.updated_at,
    )


@router.delete("/{service_id}", response_model=SuccessResponse)
async def delete_service(
    service_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina servizio (solo admin).

    Args:
        service_id: ID servizio
        current_user: Admin autenticato

    Returns:
        SuccessResponse: Conferma eliminazione
    """
    logger.info(f"Deleting service {service_id} (by {current_user.email})")

    # Load service
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        logger.warning(f"Service not found: {service_id}")
        raise ResourceNotFoundError(
            resource_type="Service",
            resource_id=service_id,
        )

    await db.delete(service)
    await db.commit()

    logger.info(f"Service deleted: {service.title}")

    return SuccessResponse(
        message="Service deleted successfully",
        data={"service_id": str(service_id)},
    )


# =============================================================================
# SERVICE CONTENT MANAGEMENT
# =============================================================================


@router.post("/{service_id}/contents", response_model=ServiceContentResponse, status_code=status.HTTP_201_CREATED)
async def create_service_content(
    service_id: UUID,
    data: ServiceContentCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> ServiceContentResponse:
    """
    Aggiunge contenuto a servizio (solo admin).

    Args:
        service_id: ID servizio
        data: Dati contenuto
        current_user: Admin autenticato

    Returns:
        ServiceContentResponse: Contenuto creato
    """
    logger.info(f"Creating content for service {service_id} (by {current_user.email})")

    # Verifica service esiste
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        logger.warning(f"Service not found: {service_id}")
        raise ResourceNotFoundError(
            resource_type="Service",
            resource_id=service_id,
        )

    # Crea content
    content = ServiceContent(
        service_id=service_id,
        **data.model_dump(exclude={"service_id"})
    )
    db.add(content)
    await db.commit()
    await db.refresh(content)

    logger.info(f"Content created for service {service.title}")

    return ServiceContentResponse.model_validate(content)


@router.put("/{service_id}/contents/{content_id}", response_model=ServiceContentResponse)
async def update_service_content(
    service_id: UUID,
    content_id: UUID,
    data: ServiceContentUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> ServiceContentResponse:
    """
    Aggiorna contenuto servizio (solo admin).

    Args:
        service_id: ID servizio
        content_id: ID contenuto
        data: Dati da aggiornare
        current_user: Admin autenticato

    Returns:
        ServiceContentResponse: Contenuto aggiornato
    """
    logger.info(f"Updating content {content_id} for service {service_id} (by {current_user.email})")

    # Load content
    result = await db.execute(
        select(ServiceContent).where(
            ServiceContent.id == content_id,
            ServiceContent.service_id == service_id,
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        logger.warning(f"Content not found: {content_id}")
        raise ResourceNotFoundError(
            resource_type="ServiceContent",
            resource_id=content_id,
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)

    await db.commit()
    await db.refresh(content)

    logger.info(f"Content updated: {content_id}")

    return ServiceContentResponse.model_validate(content)


@router.delete("/{service_id}/contents/{content_id}", response_model=SuccessResponse)
async def delete_service_content(
    service_id: UUID,
    content_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina contenuto servizio (solo admin).

    Args:
        service_id: ID servizio
        content_id: ID contenuto
        current_user: Admin autenticato

    Returns:
        SuccessResponse: Conferma eliminazione
    """
    logger.info(f"Deleting content {content_id} for service {service_id} (by {current_user.email})")

    # Load content
    result = await db.execute(
        select(ServiceContent).where(
            ServiceContent.id == content_id,
            ServiceContent.service_id == service_id,
        )
    )
    content = result.scalar_one_or_none()

    if not content:
        logger.warning(f"Content not found: {content_id}")
        raise ResourceNotFoundError(
            resource_type="ServiceContent",
            resource_id=content_id,
        )

    await db.delete(content)
    await db.commit()

    logger.info(f"Content deleted: {content_id}")

    return SuccessResponse(
        message="Content deleted successfully",
        data={"content_id": str(content_id)},
    )


# =============================================================================
# SERVICE FAQ MANAGEMENT
# =============================================================================


@router.post("/{service_id}/faqs", response_model=ServiceFAQResponse, status_code=status.HTTP_201_CREATED)
async def create_service_faq(
    service_id: UUID,
    data: ServiceFAQCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> ServiceFAQResponse:
    """
    Aggiunge FAQ a servizio (solo admin).

    Args:
        service_id: ID servizio
        data: Dati FAQ
        current_user: Admin autenticato

    Returns:
        ServiceFAQResponse: FAQ creata
    """
    logger.info(f"Creating FAQ for service {service_id} (by {current_user.email})")

    # Verifica service esiste
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        logger.warning(f"Service not found: {service_id}")
        raise ResourceNotFoundError(
            resource_type="Service",
            resource_id=service_id,
        )

    # Crea FAQ
    faq = ServiceFAQ(
        service_id=service_id,
        **data.model_dump(exclude={"service_id"})
    )
    db.add(faq)
    await db.commit()
    await db.refresh(faq)

    logger.info(f"FAQ created for service {service.title}")

    return ServiceFAQResponse.model_validate(faq)


@router.put("/{service_id}/faqs/{faq_id}", response_model=ServiceFAQResponse)
async def update_service_faq(
    service_id: UUID,
    faq_id: UUID,
    data: ServiceFAQUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> ServiceFAQResponse:
    """
    Aggiorna FAQ servizio (solo admin).

    Args:
        service_id: ID servizio
        faq_id: ID FAQ
        data: Dati da aggiornare
        current_user: Admin autenticato

    Returns:
        ServiceFAQResponse: FAQ aggiornata
    """
    logger.info(f"Updating FAQ {faq_id} for service {service_id} (by {current_user.email})")

    # Load FAQ
    result = await db.execute(
        select(ServiceFAQ).where(
            ServiceFAQ.id == faq_id,
            ServiceFAQ.service_id == service_id,
        )
    )
    faq = result.scalar_one_or_none()

    if not faq:
        logger.warning(f"FAQ not found: {faq_id}")
        raise ResourceNotFoundError(
            resource_type="ServiceFAQ",
            resource_id=faq_id,
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(faq, field, value)

    await db.commit()
    await db.refresh(faq)

    logger.info(f"FAQ updated: {faq_id}")

    return ServiceFAQResponse.model_validate(faq)


@router.delete("/{service_id}/faqs/{faq_id}", response_model=SuccessResponse)
async def delete_service_faq(
    service_id: UUID,
    faq_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina FAQ servizio (solo admin).

    Args:
        service_id: ID servizio
        faq_id: ID FAQ
        current_user: Admin autenticato

    Returns:
        SuccessResponse: Conferma eliminazione
    """
    logger.info(f"Deleting FAQ {faq_id} for service {service_id} (by {current_user.email})")

    # Load FAQ
    result = await db.execute(
        select(ServiceFAQ).where(
            ServiceFAQ.id == faq_id,
            ServiceFAQ.service_id == service_id,
        )
    )
    faq = result.scalar_one_or_none()

    if not faq:
        logger.warning(f"FAQ not found: {faq_id}")
        raise ResourceNotFoundError(
            resource_type="ServiceFAQ",
            resource_id=faq_id,
        )

    await db.delete(faq)
    await db.commit()

    logger.info(f"FAQ deleted: {faq_id}")

    return SuccessResponse(
        message="FAQ deleted successfully",
        data={"faq_id": str(faq_id)},
    )


logger.info("Services router initialized with all endpoints")
