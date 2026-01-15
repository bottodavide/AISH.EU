"""
Modulo: orders.py
Descrizione: API routes per ordini, preventivi, carrello e pagamenti
Autore: Claude per Davide
Data: 2026-01-15

Endpoints:
- POST /api/v1/quote-requests - Crea richiesta preventivo
- GET /api/v1/quote-requests - Lista richieste preventivo
- GET /api/v1/quote-requests/{id} - Dettaglio richiesta
- PATCH /api/v1/quote-requests/{id} - Aggiorna richiesta (admin)

- POST /api/v1/orders - Crea ordine
- GET /api/v1/orders - Lista ordini
- GET /api/v1/orders/{id} - Dettaglio ordine
- PATCH /api/v1/orders/{id} - Aggiorna ordine (admin)

- GET /api/v1/cart - Visualizza carrello
- POST /api/v1/cart/items - Aggiungi al carrello
- PATCH /api/v1/cart/items/{service_id} - Aggiorna quantità
- DELETE /api/v1/cart/items/{service_id} - Rimuovi dal carrello
- DELETE /api/v1/cart - Svuota carrello

Note:
- Carrello salvato in sessione JWT per MVP (non persistente)
- Stripe Payment Intent creato al checkout
- Webhook Stripe per aggiornare status pagamento
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import get_current_active_user, require_admin
from app.core.database import get_async_db
from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
    QuoteRequest,
    QuoteRequestStatus,
)
from app.models.service import Service
from app.models.user import User, UserRole
from app.schemas.base import SuccessResponse
from app.schemas.order import (
    CartAddItem,
    CartResponse,
    CartUpdateItem,
    OrderCreate,
    OrderFilters,
    OrderItemResponse,
    OrderListResponse,
    OrderResponse,
    OrderUpdate,
    QuoteRequestCreate,
    QuoteRequestFilters,
    QuoteRequestResponse,
    QuoteRequestUpdate,
)

# Setup logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["orders"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def generate_order_number() -> str:
    """
    Genera numero ordine univoco.

    Format: ORD-YYYY-NNNNN
    Example: ORD-2026-00001
    """
    year = datetime.now(timezone.utc).year
    # In produzione, usare sequence o counter da DB
    random_num = str(uuid4().int)[:5]
    return f"ORD-{year}-{random_num}"


def generate_quote_request_number() -> str:
    """
    Genera numero richiesta preventivo univoco.

    Format: QR-YYYY-NNNNN
    Example: QR-2026-00001
    """
    year = datetime.now(timezone.utc).year
    random_num = str(uuid4().int)[:5]
    return f"QR-{year}-{random_num}"


def calculate_tax(subtotal: Decimal, tax_rate: Decimal = Decimal("22.00")) -> Decimal:
    """
    Calcola IVA.

    Args:
        subtotal: Importo senza IVA
        tax_rate: Aliquota IVA % (default 22%)

    Returns:
        Importo IVA arrotondato a 2 decimali
    """
    tax_amount = (subtotal * tax_rate / Decimal("100")).quantize(Decimal("0.01"))
    return tax_amount


async def get_service_or_404(db: AsyncSession, service_id: UUID) -> Service:
    """Recupera servizio o solleva 404"""
    result = await db.execute(select(Service).where(Service.id == service_id))
    service = result.scalar_one_or_none()

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Servizio {service_id} non trovato",
        )

    if not service.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Servizio {service.name} non disponibile",
        )

    return service


def get_user_billing_data(user: User) -> dict:
    """
    Estrae dati fatturazione da UserProfile.

    Returns:
        Dict con snapshot dati billing per ordine
    """
    if not user.profile:
        return {
            "first_name": None,
            "last_name": None,
            "company_name": None,
            "vat_number": None,
            "fiscal_code": None,
            "pec_email": None,
            "sdi_code": None,
            "address": None,
        }

    profile = user.profile
    return {
        "first_name": profile.first_name,
        "last_name": profile.last_name,
        "company_name": profile.company_name,
        "vat_number": profile.vat_number,
        "fiscal_code": profile.fiscal_code,
        "pec_email": profile.pec_email,
        "sdi_code": profile.sdi_code,
        "address": profile.billing_address,
    }


# =============================================================================
# QUOTE REQUESTS ENDPOINTS
# =============================================================================


@router.post(
    "/quote-requests",
    response_model=QuoteRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea richiesta preventivo",
    description="Permette a utenti (anche guest) di richiedere un preventivo personalizzato per un servizio",
)
async def create_quote_request(
    data: QuoteRequestCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[Optional[User], Depends(get_current_active_user)] = None,
):
    """
    Crea nuova richiesta preventivo.

    - Può essere usato da utenti registrati o guest
    - Se utente registrato, user_id viene popolato automaticamente
    - Genera numero richiesta univoco (QR-YYYY-NNNNN)
    - Status iniziale: NEW
    """
    logger.info(f"Creating quote request for service {data.service_id}")

    # Verifica che servizio esista e sia attivo
    service = await get_service_or_404(db, data.service_id)

    # Crea richiesta
    quote_request = QuoteRequest(
        request_number=generate_quote_request_number(),
        user_id=current_user.id if current_user else None,
        service_id=service.id,
        contact_name=data.contact_name,
        contact_email=data.contact_email,
        contact_phone=data.contact_phone,
        company_name=data.company_name,
        message=data.message,
        custom_fields=data.custom_fields,
        status=QuoteRequestStatus.NEW,
    )

    db.add(quote_request)
    await db.commit()
    await db.refresh(quote_request)

    logger.info(f"Quote request created: {quote_request.request_number}")

    return quote_request


@router.get(
    "/quote-requests",
    response_model=list[QuoteRequestResponse],
    summary="Lista richieste preventivo",
    description="Lista richieste preventivo con filtri. Utenti vedono solo le proprie, admin vedono tutte.",
)
async def list_quote_requests(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    filters: QuoteRequestFilters = Depends(),
):
    """
    Lista richieste preventivo con filtri.

    Permessi:
    - Customer: Solo proprie richieste
    - Admin/Super Admin: Tutte le richieste
    """
    logger.info(f"Listing quote requests for user {current_user.email}")

    query = select(QuoteRequest)

    # Filtro per utente (se non admin)
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        query = query.where(QuoteRequest.user_id == current_user.id)

    # Applica filtri
    if filters.status:
        query = query.where(QuoteRequest.status == filters.status)

    if filters.service_id:
        query = query.where(QuoteRequest.service_id == filters.service_id)

    if filters.from_date:
        query = query.where(QuoteRequest.created_at >= filters.from_date)

    if filters.to_date:
        query = query.where(QuoteRequest.created_at <= filters.to_date)

    # Ordinamento
    if filters.sort_order == "desc":
        query = query.order_by(desc(getattr(QuoteRequest, filters.sort_by)))
    else:
        query = query.order_by(getattr(QuoteRequest, filters.sort_by))

    # Paginazione
    query = query.offset(filters.skip).limit(filters.limit)

    result = await db.execute(query)
    quote_requests = result.scalars().all()

    return quote_requests


@router.get(
    "/quote-requests/{quote_request_id}",
    response_model=QuoteRequestResponse,
    summary="Dettaglio richiesta preventivo",
)
async def get_quote_request(
    quote_request_id: UUID,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Recupera dettaglio richiesta preventivo.

    Permessi:
    - Owner: Può vedere propria richiesta
    - Admin: Può vedere qualsiasi richiesta
    """
    result = await db.execute(
        select(QuoteRequest).where(QuoteRequest.id == quote_request_id)
    )
    quote_request = result.scalar_one_or_none()

    if not quote_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Richiesta preventivo non trovata",
        )

    # Verifica permessi
    is_owner = quote_request.user_id == current_user.id
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a visualizzare questa richiesta",
        )

    return quote_request


@router.patch(
    "/quote-requests/{quote_request_id}",
    response_model=QuoteRequestResponse,
    summary="Aggiorna richiesta preventivo (admin only)",
    dependencies=[Depends(require_admin)],
)
async def update_quote_request(
    quote_request_id: UUID,
    data: QuoteRequestUpdate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    """
    Aggiorna richiesta preventivo (solo admin).

    Permette di:
    - Cambiare status (es: NEW → QUOTED)
    - Impostare importo preventivo
    - Aggiungere note interne
    """
    result = await db.execute(
        select(QuoteRequest).where(QuoteRequest.id == quote_request_id)
    )
    quote_request = result.scalar_one_or_none()

    if not quote_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Richiesta preventivo non trovata",
        )

    # Aggiorna campi
    if data.status is not None:
        quote_request.status = data.status

    if data.quoted_amount is not None:
        quote_request.quoted_amount = data.quoted_amount
        quote_request.quoted_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(quote_request)

    logger.info(f"Quote request {quote_request.request_number} updated")

    return quote_request


# =============================================================================
# ORDERS ENDPOINTS
# =============================================================================


@router.post(
    "/orders",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea ordine",
    description="Crea ordine da carrello o da preventivo accettato",
)
async def create_order(
    data: OrderCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Crea nuovo ordine.

    Due modalità:
    1. Da carrello: fornire lista items
    2. Da preventivo: fornire quote_request_id

    Workflow:
    1. Valida servizi/preventivo
    2. Crea Order (status=PENDING)
    3. Crea OrderItems con snapshot prezzi
    4. Calcola totali con IVA
    5. Snapshot dati fatturazione utente

    Note:
    - Ordine creato ma non pagato (status=PENDING)
    - Cliente deve pagare tramite Stripe Payment Intent
    - Al pagamento, status → PAID
    """
    logger.info(f"Creating order for user {current_user.email}")

    # Ricarica utente con profile per evitare lazy loading issues
    result = await db.execute(
        select(User).options(selectinload(User.profile)).where(User.id == current_user.id)
    )
    user_with_profile = result.scalar_one()

    # Snapshot dati fatturazione
    billing_data = get_user_billing_data(user_with_profile)

    # Caso 1: Ordine da preventivo
    if data.quote_request_id:
        # Verifica preventivo esiste e appartiene a utente
        result = await db.execute(
            select(QuoteRequest).where(QuoteRequest.id == data.quote_request_id)
        )
        quote_request = result.scalar_one_or_none()

        if not quote_request:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Preventivo non trovato",
            )

        if quote_request.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Preventivo non appartiene a questo utente",
            )

        if quote_request.status != QuoteRequestStatus.QUOTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preventivo non ancora emesso o già accettato",
            )

        if not quote_request.quoted_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Preventivo senza importo",
            )

        # Recupera servizio
        service = await get_service_or_404(db, quote_request.service_id)

        # Crea ordine da preventivo
        order = Order(
            order_number=generate_order_number(),
            user_id=current_user.id,
            quote_request_id=quote_request.id,
            status=OrderStatus.PENDING,
            subtotal=Decimal("0.00"),  # Calcolato dopo
            tax_rate=Decimal("22.00"),
            tax_amount=Decimal("0.00"),  # Calcolato dopo
            total=Decimal("0.00"),  # Calcolato dopo
            currency="EUR",
            billing_data=billing_data,
            notes=data.notes,
        )
        db.add(order)
        await db.flush()  # Per ottenere order.id

        # Crea OrderItem dal preventivo
        subtotal = quote_request.quoted_amount
        tax_rate = Decimal("22.00")
        tax_amount = calculate_tax(subtotal, tax_rate)
        total = subtotal + tax_amount

        order_item = OrderItem(
            order_id=order.id,
            service_id=service.id,
            service_name=service.name,
            description=service.short_description,
            quantity=1,
            unit_price=quote_request.quoted_amount,
            tax_rate=tax_rate,
            total_price=total,
        )
        db.add(order_item)

        # Aggiorna totali ordine
        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.total = total

        # Aggiorna status preventivo
        quote_request.status = QuoteRequestStatus.ACCEPTED

    # Caso 2: Ordine da carrello (items)
    else:
        # Crea ordine
        order = Order(
            order_number=generate_order_number(),
            user_id=current_user.id,
            quote_request_id=None,
            status=OrderStatus.PENDING,
            subtotal=Decimal("0.00"),  # Calcolato dopo
            tax_rate=Decimal("22.00"),
            tax_amount=Decimal("0.00"),  # Calcolato dopo
            total=Decimal("0.00"),  # Calcolato dopo
            currency="EUR",
            billing_data=billing_data,
            notes=data.notes,
        )
        db.add(order)
        await db.flush()

        # Crea OrderItems
        subtotal = Decimal("0.00")
        order_items = []

        for item_data in data.items:
            # Recupera servizio
            service = await get_service_or_404(db, item_data.service_id)

            # Determina prezzo (custom o da servizio)
            if item_data.custom_price is not None:
                unit_price = item_data.custom_price
            elif service.price_min:
                unit_price = service.price_min
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Servizio {service.name} richiede prezzo custom",
                )

            # Calcola totale riga
            line_subtotal = unit_price * item_data.quantity
            line_tax_rate = Decimal("22.00")
            line_tax = calculate_tax(line_subtotal, line_tax_rate)
            line_total = line_subtotal + line_tax

            # Crea OrderItem
            order_item = OrderItem(
                order_id=order.id,
                service_id=service.id,
                service_name=service.name,
                description=service.short_description,
                quantity=item_data.quantity,
                unit_price=unit_price,
                tax_rate=line_tax_rate,
                total_price=line_total,
            )
            db.add(order_item)
            order_items.append(order_item)

            subtotal += line_subtotal

        # Calcola totali ordine
        tax_amount = calculate_tax(subtotal, Decimal("22.00"))
        total = subtotal + tax_amount

        order.subtotal = subtotal
        order.tax_amount = tax_amount
        order.total = total

    # Salva tutto
    await db.commit()

    # Ricarica con relationships
    await db.refresh(order)
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order.id)
    )
    order = result.scalar_one()

    logger.info(f"Order created: {order.order_number}, total: €{order.total}")

    return order


@router.get(
    "/orders",
    response_model=list[OrderListResponse],
    summary="Lista ordini",
)
async def list_orders(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    filters: OrderFilters = Depends(),
):
    """
    Lista ordini con filtri.

    Permessi:
    - Customer: Solo propri ordini
    - Admin: Tutti gli ordini (con filtro user_id opzionale)
    """
    logger.info(f"Listing orders for user {current_user.email}")

    query = select(Order).options(selectinload(Order.items))

    # Filtro per utente (se non admin)
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        query = query.where(Order.user_id == current_user.id)
    elif filters.user_id:
        # Admin può filtrare per user_id specifico
        query = query.where(Order.user_id == filters.user_id)

    # Applica filtri
    if filters.status:
        query = query.where(Order.status == filters.status)

    if filters.from_date:
        query = query.where(Order.created_at >= filters.from_date)

    if filters.to_date:
        query = query.where(Order.created_at <= filters.to_date)

    if filters.min_total:
        query = query.where(Order.total >= filters.min_total)

    if filters.max_total:
        query = query.where(Order.total <= filters.max_total)

    # Ordinamento
    if filters.sort_order == "desc":
        query = query.order_by(desc(getattr(Order, filters.sort_by)))
    else:
        query = query.order_by(getattr(Order, filters.sort_by))

    # Paginazione
    query = query.offset(filters.skip).limit(filters.limit)

    result = await db.execute(query)
    orders = result.scalars().all()

    # Converti a OrderListResponse con items_count
    response = []
    for order in orders:
        order_dict = {
            "id": order.id,
            "created_at": order.created_at,
            "updated_at": order.updated_at,
            "order_number": order.order_number,
            "status": order.status,
            "total": order.total,
            "currency": order.currency,
            "paid_at": order.paid_at,
            "items_count": len(order.items) if order.items else 0,
        }
        response.append(OrderListResponse(**order_dict))

    return response


@router.get(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Dettaglio ordine",
)
async def get_order(
    order_id: UUID,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    Recupera dettaglio ordine completo con items.

    Permessi:
    - Owner: Può vedere proprio ordine
    - Admin: Può vedere qualsiasi ordine
    """
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordine non trovato",
        )

    # Verifica permessi
    is_owner = order.user_id == current_user.id
    is_admin = current_user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]

    if not is_owner and not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Non autorizzato a visualizzare questo ordine",
        )

    return order


@router.patch(
    "/orders/{order_id}",
    response_model=OrderResponse,
    summary="Aggiorna ordine (admin only)",
    dependencies=[Depends(require_admin)],
)
async def update_order(
    order_id: UUID,
    data: OrderUpdate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
):
    """
    Aggiorna ordine (solo admin).

    Permette di:
    - Cambiare status workflow
    - Aggiungere/modificare note
    """
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ordine non trovato",
        )

    # Aggiorna campi
    if data.status is not None:
        old_status = order.status
        order.status = data.status

        # Aggiorna timestamp workflow
        if data.status == OrderStatus.PAID and old_status != OrderStatus.PAID:
            order.paid_at = datetime.now(timezone.utc)
        elif data.status == OrderStatus.COMPLETED and old_status != OrderStatus.COMPLETED:
            order.completed_at = datetime.now(timezone.utc)

    if data.notes is not None:
        order.notes = data.notes

    await db.commit()
    await db.refresh(order)

    logger.info(f"Order {order.order_number} updated")

    return order


# =============================================================================
# CART ENDPOINTS (Placeholder - Session based)
# =============================================================================
# TODO: Implementare cart management con session/cookie per MVP
# Per ora, frontend può gestire cart localmente e creare ordine direttamente


@router.get(
    "/cart",
    response_model=CartResponse,
    summary="Visualizza carrello (TODO)",
)
async def get_cart():
    """
    Recupera carrello corrente (session-based).

    TODO: Implementare storage carrello in sessione JWT o cookie
    Per MVP, frontend gestisce cart localmente
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Cart management in fase di implementazione. "
        "Usa direttamente POST /orders con lista items.",
    )


@router.post(
    "/cart/items",
    response_model=CartResponse,
    summary="Aggiungi al carrello (TODO)",
)
async def add_to_cart(item: CartAddItem):
    """Aggiungi item al carrello"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Cart management in fase di implementazione",
    )


@router.patch(
    "/cart/items/{service_id}",
    response_model=CartResponse,
    summary="Aggiorna quantità carrello (TODO)",
)
async def update_cart_item(service_id: UUID, update: CartUpdateItem):
    """Aggiorna quantità item nel carrello"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Cart management in fase di implementazione",
    )


@router.delete(
    "/cart/items/{service_id}",
    response_model=CartResponse,
    summary="Rimuovi dal carrello (TODO)",
)
async def remove_from_cart(service_id: UUID):
    """Rimuovi item dal carrello"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Cart management in fase di implementazione",
    )


@router.delete(
    "/cart",
    response_model=SuccessResponse,
    summary="Svuota carrello (TODO)",
)
async def clear_cart():
    """Svuota carrello"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Cart management in fase di implementazione",
    )


# =============================================================================
# PAYMENT ENDPOINTS (Placeholder - Stripe integration)
# =============================================================================
# TODO: Implementare Stripe Payment Intent creation e webhook handler


@router.post(
    "/payments/create-intent",
    summary="Crea Stripe Payment Intent (TODO)",
)
async def create_payment_intent(order_id: UUID):
    """
    Crea Stripe Payment Intent per ordine.

    TODO: Integrare Stripe SDK
    - Creare Payment Intent con order.total
    - Salvare stripe_payment_intent_id in Payment model
    - Ritornare client_secret per frontend
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Stripe integration in fase di implementazione",
    )


@router.post(
    "/payments/webhook",
    summary="Stripe webhook handler (TODO)",
)
async def stripe_webhook(request: Request):
    """
    Webhook per eventi Stripe.

    Eventi supportati:
    - payment_intent.succeeded → Order status = PAID
    - payment_intent.payment_failed → Log failure
    - charge.refunded → Order status = REFUNDED

    TODO: Implementare webhook signature verification
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Stripe webhook in fase di implementazione",
    )
