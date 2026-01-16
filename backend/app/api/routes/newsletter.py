"""
Modulo: newsletter.py
Descrizione: API routes per newsletter management
Autore: Claude per Davide
Data: 2026-01-15
"""

import csv
import io
import logging
from datetime import datetime, timedelta, timezone
from math import ceil
from typing import Optional

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import StreamingResponse
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user_optional, require_admin
from app.core.exceptions import DuplicateResourceError, ValidationError
from app.models.newsletter import NewsletterSubscriber, SubscriberStatus
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.newsletter import (
    NewsletterStatsResponse,
    NewsletterSubscribeRequest,
    NewsletterSubscriberFilters,
    NewsletterSubscriberListResponse,
    NewsletterSubscriberResponse,
    NewsletterUnsubscribeRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/newsletter", tags=["Newsletter"])


# =============================================================================
# PUBLIC ENDPOINTS - Iscrizione/Disiscrizione
# =============================================================================


@router.post("/subscribe", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_newsletter(
    request: NewsletterSubscribeRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Iscrizione alla newsletter.

    - **Pubblico**: Accessibile a tutti

    Args:
        request: Dati iscrizione
        current_user: Utente corrente (opzionale)
        db: Database session

    Returns:
        SuccessResponse: Conferma iscrizione

    Raises:
        ValidationError: Se termini non accettati
        DuplicateResourceError: Se email già iscritta
    """
    logger.info(f"Newsletter subscription request: {request.email}")

    # Valida accettazione termini
    if not request.accept_terms:
        raise ValidationError("Devi accettare i Termini di Servizio e la Privacy Policy")

    # Verifica se email già iscritta
    result = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == request.email)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Se già attivo, errore
        if existing.status == SubscriberStatus.ACTIVE:
            raise DuplicateResourceError("Questa email è già iscritta alla newsletter")

        # Se disiscritto, riattiva
        if existing.status == SubscriberStatus.UNSUBSCRIBED:
            existing.status = SubscriberStatus.ACTIVE
            existing.subscribed_at = datetime.now(timezone.utc)
            existing.confirmed_at = datetime.now(timezone.utc)
            existing.unsubscribed_at = None
            existing.first_name = request.first_name or existing.first_name
            existing.last_name = request.last_name or existing.last_name

            await db.commit()

            logger.info(f"Newsletter subscriber reactivated: {request.email}")
            return SuccessResponse(
                message="Iscrizione alla newsletter confermata! Ti invieremo i nostri aggiornamenti."
            )

        # Se pending, aggiorna e conferma
        if existing.status == SubscriberStatus.PENDING:
            existing.status = SubscriberStatus.ACTIVE
            existing.confirmed_at = datetime.now(timezone.utc)
            existing.first_name = request.first_name or existing.first_name
            existing.last_name = request.last_name or existing.last_name

            await db.commit()

            logger.info(f"Newsletter subscriber confirmed: {request.email}")
            return SuccessResponse(
                message="Iscrizione alla newsletter confermata! Ti invieremo i nostri aggiornamenti."
            )

    # Crea nuovo subscriber (confermato subito - no double opt-in per ora)
    subscriber = NewsletterSubscriber(
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        status=SubscriberStatus.ACTIVE,
        subscribed_at=datetime.now(timezone.utc),
        confirmed_at=datetime.now(timezone.utc),
        source=request.source or "web_form",
        user_id=current_user.id if current_user else None,
    )

    db.add(subscriber)
    await db.commit()

    logger.info(f"New newsletter subscriber: {request.email}")

    return SuccessResponse(
        message="Iscrizione alla newsletter completata! Ti invieremo i nostri aggiornamenti su AI, GDPR e Cybersecurity."
    )


@router.post("/unsubscribe", response_model=SuccessResponse)
async def unsubscribe_from_newsletter(
    request: NewsletterUnsubscribeRequest,
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Disiscrizione dalla newsletter.

    - **Pubblico**: Accessibile a tutti

    Args:
        request: Email da disiscrivere
        db: Database session

    Returns:
        SuccessResponse: Conferma disiscrizione
    """
    logger.info(f"Newsletter unsubscribe request: {request.email}")

    # Trova subscriber
    result = await db.execute(
        select(NewsletterSubscriber).where(NewsletterSubscriber.email == request.email)
    )
    subscriber = result.scalar_one_or_none()

    if not subscriber:
        # Anche se non trovato, conferma (privacy)
        logger.warning(f"Unsubscribe request for non-existent email: {request.email}")
        return SuccessResponse(
            message="Se eri iscritto, la tua disiscrizione è stata confermata."
        )

    # Se già disiscritto, conferma
    if subscriber.status == SubscriberStatus.UNSUBSCRIBED:
        logger.info(f"Unsubscribe request for already unsubscribed: {request.email}")
        return SuccessResponse(message="Sei già disiscritto dalla newsletter.")

    # Disiscrivi
    subscriber.status = SubscriberStatus.UNSUBSCRIBED
    subscriber.unsubscribed_at = datetime.now(timezone.utc)

    await db.commit()

    logger.info(f"Newsletter subscriber unsubscribed: {request.email}")

    return SuccessResponse(
        message="Disiscrizione completata. Non riceverai più le nostre newsletter. Ci dispiace vederti andare!"
    )


# =============================================================================
# ADMIN ENDPOINTS - Gestione Subscribers
# =============================================================================


@router.get("/subscribers", response_model=NewsletterSubscriberListResponse)
async def list_subscribers(
    filters: NewsletterSubscriberFilters = Depends(),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> NewsletterSubscriberListResponse:
    """
    Lista iscritti newsletter con filtri e paginazione.

    **Richiede**: Admin

    Args:
        filters: Filtri di ricerca
        current_user: Utente corrente
        db: Database session

    Returns:
        NewsletterSubscriberListResponse: Lista subscribers paginata
    """
    logger.info("Listing newsletter subscribers")

    # Build query
    query = select(NewsletterSubscriber)

    # Apply filters
    if filters.status:
        query = query.where(NewsletterSubscriber.status == filters.status)

    if filters.search:
        search_pattern = f"%{filters.search}%"
        query = query.where(
            or_(
                NewsletterSubscriber.email.ilike(search_pattern),
                NewsletterSubscriber.first_name.ilike(search_pattern),
                NewsletterSubscriber.last_name.ilike(search_pattern),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (filters.page - 1) * filters.page_size
    query = query.offset(offset).limit(filters.page_size)

    # Order by subscribed_at desc
    query = query.order_by(desc(NewsletterSubscriber.subscribed_at))

    # Execute query
    result = await db.execute(query)
    subscribers = result.scalars().all()

    logger.info(f"Found {total} subscribers, returning page {filters.page}")

    return NewsletterSubscriberListResponse(
        subscribers=[
            NewsletterSubscriberResponse.model_validate(sub) for sub in subscribers
        ],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=ceil(total / filters.page_size) if total > 0 else 0,
    )


@router.get("/subscribers/export")
async def export_subscribers_csv(
    status_filter: Optional[SubscriberStatus] = None,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> StreamingResponse:
    """
    Esporta iscritti newsletter in CSV.

    **Richiede**: Admin

    Args:
        status_filter: Filtra per status (opzionale)
        current_user: Utente corrente
        db: Database session

    Returns:
        StreamingResponse: File CSV
    """
    logger.info(f"Exporting newsletter subscribers (status={status_filter})")

    # Build query
    query = select(NewsletterSubscriber)

    if status_filter:
        query = query.where(NewsletterSubscriber.status == status_filter)

    # Order by subscribed_at desc
    query = query.order_by(desc(NewsletterSubscriber.subscribed_at))

    # Execute query
    result = await db.execute(query)
    subscribers = result.scalars().all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Email",
        "Nome",
        "Cognome",
        "Status",
        "Data Iscrizione",
        "Data Conferma",
        "Data Disiscrizione",
        "Fonte",
    ])

    # Data rows
    for sub in subscribers:
        writer.writerow([
            sub.email,
            sub.first_name or "",
            sub.last_name or "",
            sub.status.value,
            sub.subscribed_at.strftime("%Y-%m-%d %H:%M:%S") if sub.subscribed_at else "",
            sub.confirmed_at.strftime("%Y-%m-%d %H:%M:%S") if sub.confirmed_at else "",
            sub.unsubscribed_at.strftime("%Y-%m-%d %H:%M:%S") if sub.unsubscribed_at else "",
            sub.source or "",
        ])

    # Prepare response
    output.seek(0)
    filename = f"newsletter_subscribers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    logger.info(f"Exported {len(subscribers)} subscribers to CSV")

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/stats", response_model=NewsletterStatsResponse)
async def get_newsletter_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> NewsletterStatsResponse:
    """
    Statistiche newsletter.

    **Richiede**: Admin

    Args:
        current_user: Utente corrente
        db: Database session

    Returns:
        NewsletterStatsResponse: Statistiche
    """
    logger.info("Getting newsletter stats")

    # Total subscribers
    total_result = await db.execute(select(func.count(NewsletterSubscriber.id)))
    total_subscribers = total_result.scalar()

    # Active subscribers
    active_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.status == SubscriberStatus.ACTIVE
        )
    )
    active_subscribers = active_result.scalar()

    # Pending subscribers
    pending_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.status == SubscriberStatus.PENDING
        )
    )
    pending_subscribers = pending_result.scalar()

    # Unsubscribed subscribers
    unsubscribed_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.status == SubscriberStatus.UNSUBSCRIBED
        )
    )
    unsubscribed_subscribers = unsubscribed_result.scalar()

    # Subscribed today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.subscribed_at >= today_start
        )
    )
    subscribed_today = today_result.scalar()

    # Subscribed this week
    week_start = today_start - timedelta(days=today_start.weekday())
    week_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.subscribed_at >= week_start
        )
    )
    subscribed_this_week = week_result.scalar()

    # Subscribed this month
    month_start = today_start.replace(day=1)
    month_result = await db.execute(
        select(func.count(NewsletterSubscriber.id)).where(
            NewsletterSubscriber.subscribed_at >= month_start
        )
    )
    subscribed_this_month = month_result.scalar()

    return NewsletterStatsResponse(
        total_subscribers=total_subscribers,
        active_subscribers=active_subscribers,
        pending_subscribers=pending_subscribers,
        unsubscribed_subscribers=unsubscribed_subscribers,
        subscribed_today=subscribed_today,
        subscribed_this_week=subscribed_this_week,
        subscribed_this_month=subscribed_this_month,
    )
