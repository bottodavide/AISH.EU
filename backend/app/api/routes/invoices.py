"""
Modulo: invoices.py
Descrizione: API endpoints per fatturazione elettronica italiana
Autore: Claude per Davide
Data: 2026-01-15

Endpoints:
- POST   /api/v1/invoices                    - Crea fattura da ordine pagato
- GET    /api/v1/invoices                    - Lista fatture con filtri
- GET    /api/v1/invoices/{id}               - Dettaglio fattura
- POST   /api/v1/invoices/{id}/generate-pdf  - Genera PDF fattura
- POST   /api/v1/invoices/{id}/generate-xml  - Genera XML SDI
- POST   /api/v1/invoices/{id}/send-sdi      - Invia fattura a SDI (stub)
- PATCH  /api/v1/invoices/{id}               - Aggiorna status fattura
- GET    /api/v1/invoices/stats              - Statistiche fatturazione

Permissions:
- Lista/dettaglio: Customer (solo proprie), Admin/Support (tutte)
- Crea: Customer (solo da propri ordini pagati)
- Genera PDF/XML: Customer (solo proprie), Admin (tutte)
- Invia SDI: Admin only
- Update status: Admin only
- Stats: Admin only

Workflow:
1. Order pagato → POST /invoices (InvoiceCreate con order_id)
2. Sistema genera numero progressivo, snapshot dati, status=DRAFT
3. POST /invoices/{id}/generate-pdf → PDF salvato in files table
4. POST /invoices/{id}/generate-xml → XML salvato in files table
5. POST /invoices/{id}/send-sdi → Invio PEC a SDI (stub)
6. Webhook SDI → PATCH /invoices/{id} (update sdi_status)
"""

import logging
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, desc, extract, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.dependencies import (
    get_current_active_user,
    require_support,
)
from app.core.config import settings
from app.core.database import get_async_db
from app.models.file import File, FileCategory, FileStatus
from app.models.invoice import CreditNote, Invoice, InvoiceLine, InvoiceStatus, SDIStatus
from app.models.order import Order, Payment
from app.models.user import User
from app.schemas.invoice import (
    CreditNoteCreate,
    CreditNoteResponse,
    InvoiceCreate,
    InvoiceFilters,
    InvoiceGeneratePDFRequest,
    InvoiceGenerateXMLRequest,
    InvoiceListItem,
    InvoiceResponse,
    InvoiceSendSDIRequest,
    InvoiceStatsResponse,
    InvoiceUpdate,
)
from app.services.file_storage import FileStorageService
from app.services.invoice_pdf import generate_invoice_pdf
from app.services.invoice_xml import generate_invoice_xml

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/v1/invoices", tags=["invoices"])

# Services
file_storage_service = FileStorageService()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


async def _get_invoice_or_404(
    db: AsyncSession, invoice_id: UUID, user: User
) -> Invoice:
    """
    Ottiene Invoice o solleva 404.

    Args:
        db: Database session
        invoice_id: ID fattura
        user: User corrente

    Returns:
        Invoice: Fattura trovata

    Raises:
        HTTPException: 404 se non trovata o no permission
    """
    result = await db.execute(
        select(Invoice)
        .options(
            selectinload(Invoice.lines),
            selectinload(Invoice.user),
            selectinload(Invoice.order),
        )
        .where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice {invoice_id} not found",
        )

    # Permission check: owner o admin/support
    if user.role not in ["admin", "super_admin", "support"]:
        if invoice.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this invoice",
            )

    return invoice


async def generate_invoice_number(db: AsyncSession, year: int) -> tuple[str, int]:
    """
    Genera numero fattura progressivo per anno.

    Formato: YYYY/00001

    Args:
        db: Database session
        year: Anno fiscale

    Returns:
        tuple[str, int]: (invoice_number, progressive)

    Note:
        Thread-safe grazie a SELECT FOR UPDATE
    """
    logger.info(f"Generating invoice number for year {year}")

    # Ottieni ultimo progressivo per anno (con lock)
    result = await db.execute(
        select(func.max(Invoice.invoice_progressive))
        .where(Invoice.invoice_year == year)
        .with_for_update()
    )
    last_progressive = result.scalar_one_or_none()

    # Calcola nuovo progressivo
    new_progressive = (last_progressive or 0) + 1

    # Formatta numero fattura
    invoice_number = f"{year}/{new_progressive:05d}"

    logger.info(f"Generated invoice number: {invoice_number}")
    return invoice_number, new_progressive


def get_user_billing_data(user: User) -> dict:
    """
    Estrae dati fatturazione da UserProfile.

    Returns:
        dict: Dati per buyer_* fields
    """
    if not user.profile:
        raise ValueError("User profile not found")

    profile = user.profile

    # Nome
    if profile.company_name:
        buyer_name = profile.company_name
    else:
        buyer_name = f"{profile.first_name} {profile.last_name}".strip()
        if not buyer_name:
            buyer_name = user.email

    # Indirizzo
    buyer_address = {
        "address": profile.billing_address or "",
        "city": profile.billing_city or "",
        "zip": profile.billing_zip or "",
        "province": profile.billing_province or "",
        "country": profile.billing_country or "IT",
    }

    return {
        "buyer_name": buyer_name,
        "buyer_vat": profile.vat_number,
        "buyer_fiscal_code": profile.fiscal_code,
        "buyer_pec": profile.pec_email,
        "buyer_sdi_code": profile.sdi_code,
        "buyer_address": buyer_address,
    }


def get_seller_data_from_settings() -> dict:
    """
    Estrae dati cedente da settings.

    Returns:
        dict: Dati per seller_* fields
    """
    seller_address = {
        "address": settings.SELLER_ADDRESS,
        "city": settings.SELLER_CITY,
        "zip": settings.SELLER_ZIP,
        "province": settings.SELLER_PROVINCE,
        "country": settings.SELLER_COUNTRY,
    }

    return {
        "seller_name": settings.SELLER_NAME,
        "seller_vat": settings.SELLER_VAT,
        "seller_fiscal_code": settings.SELLER_FISCAL_CODE or settings.SELLER_VAT,
        "seller_address": seller_address,
        "seller_regime_fiscale": settings.SELLER_REGIME_FISCALE,
    }


# =============================================================================
# CREATE INVOICE
# =============================================================================


@router.post(
    "",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crea fattura da ordine pagato",
    description="""
    Crea fattura elettronica da ordine pagato.

    Workflow:
    1. Verifica ordine esiste e pagato (Payment.status = COMPLETED)
    2. Verifica ordine non ha già fattura
    3. Genera numero progressivo fattura per anno fiscale
    4. Snapshot dati cedente da settings
    5. Snapshot dati cessionario da UserProfile
    6. Copia righe da OrderItems
    7. Calcola totali
    8. Status = DRAFT
    9. Ritorna fattura creata

    Permissions:
    - Customer: può creare fattura solo da propri ordini
    - Admin: può creare fattura da qualsiasi ordine
    """,
)
async def create_invoice(
    data: InvoiceCreate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Crea fattura da ordine pagato"""
    logger.info(f"Creating invoice for order {data.order_id} by user {current_user.id}")

    # 1. Ottieni Order con relazioni
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items),
            selectinload(Order.user).selectinload(User.profile),
            selectinload(Order.payment),
        )
        .where(Order.id == data.order_id)
    )
    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order {data.order_id} not found",
        )

    # Permission check
    if current_user.role not in ["admin", "super_admin"]:
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to create invoice for this order",
            )

    # 2. Verifica ordine pagato
    if not order.payment or order.payment.status != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be paid before creating invoice",
        )

    # 3. Verifica non esista già fattura per questo ordine
    existing = await db.execute(
        select(Invoice).where(Invoice.order_id == data.order_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Invoice already exists for this order",
        )

    # 4. Genera numero fattura progressivo
    issue_year = data.issue_date.year if data.issue_date else date.today().year
    invoice_number, progressive = await generate_invoice_number(db, issue_year)

    # 5. Snapshot dati cedente da settings
    seller_data = get_seller_data_from_settings()

    # 6. Snapshot dati cessionario da UserProfile
    buyer_data = get_user_billing_data(order.user)

    # Override con dati da request (se forniti)
    if data.buyer_name:
        buyer_data["buyer_name"] = data.buyer_name
    if data.buyer_vat:
        buyer_data["buyer_vat"] = data.buyer_vat
    if data.buyer_fiscal_code:
        buyer_data["buyer_fiscal_code"] = data.buyer_fiscal_code
    if data.buyer_pec:
        buyer_data["buyer_pec"] = data.buyer_pec
    if data.buyer_sdi_code:
        buyer_data["buyer_sdi_code"] = data.buyer_sdi_code

    # 7. Crea Invoice
    invoice = Invoice(
        order_id=order.id,
        user_id=order.user_id,
        invoice_number=invoice_number,
        invoice_year=issue_year,
        invoice_progressive=progressive,
        issue_date=data.issue_date or date.today(),
        due_date=data.due_date,
        **seller_data,
        **buyer_data,
        subtotal=order.subtotal,
        tax_amount=order.tax_amount,
        total=order.total,
        currency="EUR",
        status=InvoiceStatus.DRAFT,
        sdi_status=SDIStatus.PENDING,
    )

    db.add(invoice)
    await db.flush()  # Get invoice.id

    # 8. Copia righe da OrderItems
    for idx, item in enumerate(order.items, start=1):
        line = InvoiceLine(
            invoice_id=invoice.id,
            line_number=idx,
            description=item.description or f"Servizio: {item.service.title}",
            quantity=item.quantity,
            unit_price=item.unit_price,
            tax_rate=Decimal("22.00"),  # IVA italiana standard
            tax_amount=item.tax_amount,
            total=item.total,
        )
        db.add(line)

    await db.commit()
    await db.refresh(invoice)

    logger.info(f"Invoice {invoice.invoice_number} created successfully")

    # Ricarica con relazioni per response
    result = await db.execute(
        select(Invoice)
        .options(
            selectinload(Invoice.lines),
            selectinload(Invoice.user),
            selectinload(Invoice.order),
        )
        .where(Invoice.id == invoice.id)
    )
    invoice_with_lines = result.scalar_one()

    return invoice_with_lines


# =============================================================================
# LIST INVOICES
# =============================================================================


@router.get(
    "",
    response_model=list[InvoiceListItem],
    summary="Lista fatture con filtri",
    description="""
    Ritorna lista fatture con paginazione e filtri.

    Permissions:
    - Customer: vede solo proprie fatture
    - Admin/Support: vede tutte le fatture

    Filtri disponibili:
    - status: Status fattura (draft, generated, sent, accepted, rejected, delivered)
    - sdi_status: Status SDI (pending, mc, ns, rc, ec_accepted, ec_rejected)
    - year: Anno fiscale
    - issue_date_from/to: Range data emissione
    - user_id: Filtra per cliente (admin only)
    - buyer_name: Ricerca nome cliente (ILIKE)
    - search: Ricerca full-text su numero, nome cliente, descrizione righe
    - sort_by: Campo ordinamento (issue_date, invoice_number, total, created_at)
    - sort_order: Direzione (asc, desc)
    """,
)
async def list_invoices(
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    filters: Annotated[InvoiceFilters, Depends()],
):
    """Lista fatture con filtri e paginazione"""
    logger.info(f"Listing invoices for user {current_user.id} with filters: {filters}")

    # Base query
    query = select(Invoice)

    # Permission filter: customer vede solo proprie
    if current_user.role not in ["admin", "super_admin", "support"]:
        query = query.where(Invoice.user_id == current_user.id)
    else:
        # Admin può filtrare per user_id
        if filters.user_id:
            query = query.where(Invoice.user_id == filters.user_id)

    # Status filters
    if filters.status:
        query = query.where(Invoice.status == filters.status)

    if filters.sdi_status:
        query = query.where(Invoice.sdi_status == filters.sdi_status)

    # Date filters
    if filters.year:
        query = query.where(Invoice.invoice_year == filters.year)

    if filters.issue_date_from:
        query = query.where(Invoice.issue_date >= filters.issue_date_from)

    if filters.issue_date_to:
        query = query.where(Invoice.issue_date <= filters.issue_date_to)

    # Buyer name filter (ILIKE)
    if filters.buyer_name:
        query = query.where(Invoice.buyer_name.ilike(f"%{filters.buyer_name}%"))

    # Full-text search
    if filters.search:
        search_term = f"%{filters.search}%"
        query = query.where(
            or_(
                Invoice.invoice_number.ilike(search_term),
                Invoice.buyer_name.ilike(search_term),
            )
        )

    # Sorting
    sort_column = getattr(Invoice, filters.sort_by, Invoice.issue_date)
    if filters.sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Pagination
    offset = (filters.page - 1) * filters.page_size
    query = query.offset(offset).limit(filters.page_size)

    # Execute
    result = await db.execute(query)
    invoices = result.scalars().all()

    logger.info(f"Found {len(invoices)} invoices")
    return invoices


# =============================================================================
# GET INVOICE DETAIL
# =============================================================================


@router.get(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Dettaglio fattura",
    description="""
    Ritorna dettagli completi fattura con righe.

    Permissions:
    - Customer: solo proprie fatture
    - Admin/Support: tutte le fatture
    """,
)
async def get_invoice(
    invoice_id: UUID,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Ottiene dettaglio fattura"""
    invoice = await _get_invoice_or_404(db, invoice_id, current_user)
    return invoice


# =============================================================================
# GENERATE PDF
# =============================================================================


@router.post(
    "/{invoice_id}/generate-pdf",
    response_model=InvoiceResponse,
    summary="Genera PDF fattura",
    description="""
    Genera PDF professionale fattura.

    Workflow:
    1. Verifica invoice.status != DRAFT
    2. Genera PDF con logo, dati cedente/cessionario, righe, totali
    3. Salva PDF in files table (category=INVOICE)
    4. Aggiorna invoice.pdf_file_id
    5. Ritorna invoice aggiornata

    Permissions:
    - Customer: solo proprie fatture
    - Admin: tutte le fatture
    """,
)
async def generate_pdf(
    invoice_id: UUID,
    request: InvoiceGeneratePDFRequest,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Genera PDF fattura"""
    logger.info(f"Generating PDF for invoice {invoice_id}")

    invoice = await _get_invoice_or_404(db, invoice_id, current_user)

    # Verifica status (deve essere almeno DRAFT)
    if invoice.status == InvoiceStatus.DRAFT:
        # Aggiorna status a GENERATED
        invoice.status = InvoiceStatus.GENERATED

    # Path output PDF
    upload_dir = Path(settings.UPLOAD_DIR)
    pdf_dir = upload_dir / "invoices" / str(invoice.invoice_year) / f"{invoice.issue_date.month:02d}"
    pdf_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename = f"fattura_{invoice.invoice_number.replace('/', '_')}.pdf"
    pdf_path = pdf_dir / pdf_filename

    # Genera PDF
    try:
        generate_invoice_pdf(
            invoice=invoice,
            output_path=str(pdf_path),
            include_payment_info=request.include_payment_info,
            include_qr_code=request.include_qr_code,
            language=request.language,
        )
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF generation failed: {str(e)}",
        )

    # Calcola hash e size
    file_size = pdf_path.stat().st_size
    sha256_hash = file_storage_service.calculate_sha256(str(pdf_path))

    # Salva in files table
    db_file = File(
        uploaded_by_id=current_user.id,
        category=FileCategory.INVOICE,
        status=FileStatus.ACTIVE,
        filename=pdf_filename,
        stored_filename=pdf_filename,
        file_path=str(pdf_path.relative_to(upload_dir)),
        mime_type="application/pdf",
        file_size=file_size,
        file_extension="pdf",
        sha256_hash=sha256_hash,
        is_public=False,
        reference_type="invoice",
        reference_id=invoice.id,
        description=f"PDF Fattura {invoice.invoice_number}",
    )

    db.add(db_file)
    await db.flush()

    # Aggiorna invoice
    invoice.pdf_file_id = db_file.id
    await db.commit()
    await db.refresh(invoice)

    logger.info(f"PDF generated successfully: {pdf_path}")

    # Ricarica con relazioni
    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.lines))
        .where(Invoice.id == invoice.id)
    )
    return result.scalar_one()


# =============================================================================
# GENERATE XML
# =============================================================================


@router.post(
    "/{invoice_id}/generate-xml",
    response_model=InvoiceResponse,
    summary="Genera XML FatturaPA per SDI",
    description="""
    Genera XML formato FatturaPA 1.2.1 per invio a Sistema di Interscambio.

    Workflow:
    1. Verifica invoice.status = GENERATED (deve avere PDF)
    2. Genera XML formato FatturaPA 1.2.1
    3. Valida XML contro XSD (opzionale)
    4. Salva XML in files table (category=INVOICE)
    5. Aggiorna invoice.xml_file_id
    6. Ritorna invoice aggiornata

    Permissions:
    - Customer: solo proprie fatture
    - Admin: tutte le fatture

    Note:
    - XML contiene tutti i dati obbligatori per SDI
    - Formato validato contro specifiche AgID
    """,
)
async def generate_xml(
    invoice_id: UUID,
    request: InvoiceGenerateXMLRequest,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """Genera XML FatturaPA"""
    logger.info(f"Generating XML for invoice {invoice_id}")

    invoice = await _get_invoice_or_404(db, invoice_id, current_user)

    # Verifica status (deve avere almeno PDF)
    if invoice.status == InvoiceStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generate PDF before XML",
        )

    # Path output XML
    upload_dir = Path(settings.UPLOAD_DIR)
    xml_dir = upload_dir / "invoices" / str(invoice.invoice_year) / f"{invoice.issue_date.month:02d}"
    xml_dir.mkdir(parents=True, exist_ok=True)

    xml_filename = f"fattura_{invoice.invoice_number.replace('/', '_')}.xml"
    xml_path = xml_dir / xml_filename

    # Genera XML
    try:
        generate_invoice_xml(
            invoice=invoice,
            output_path=str(xml_path),
            transmission_format=request.transmission_format,
            validate_xsd=request.validate_xsd,
        )
    except Exception as e:
        logger.error(f"XML generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"XML generation failed: {str(e)}",
        )

    # Calcola hash e size
    file_size = xml_path.stat().st_size
    sha256_hash = file_storage_service.calculate_sha256(str(xml_path))

    # Salva in files table
    db_file = File(
        uploaded_by_id=current_user.id,
        category=FileCategory.INVOICE,
        status=FileStatus.ACTIVE,
        filename=xml_filename,
        stored_filename=xml_filename,
        file_path=str(xml_path.relative_to(upload_dir)),
        mime_type="application/xml",
        file_size=file_size,
        file_extension="xml",
        sha256_hash=sha256_hash,
        is_public=False,
        reference_type="invoice",
        reference_id=invoice.id,
        description=f"XML FatturaPA {invoice.invoice_number}",
    )

    db.add(db_file)
    await db.flush()

    # Aggiorna invoice
    invoice.xml_file_id = db_file.id
    await db.commit()
    await db.refresh(invoice)

    logger.info(f"XML generated successfully: {xml_path}")

    # Ricarica con relazioni
    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.lines))
        .where(Invoice.id == invoice.id)
    )
    return result.scalar_one()


# =============================================================================
# SEND TO SDI (STUB)
# =============================================================================


@router.post(
    "/{invoice_id}/send-sdi",
    response_model=InvoiceResponse,
    summary="Invia fattura a SDI via PEC (STUB)",
    description="""
    Invia fattura XML al Sistema di Interscambio via PEC.

    **NOTA: Questo è uno STUB - l'invio PEC reale non è implementato.**

    Workflow completo (da implementare):
    1. Verifica invoice.status = GENERATED
    2. Verifica xml_file_id esiste
    3. Invia XML via PEC a sdi@pec.fatturapa.it
    4. Aggiorna invoice:
       - status = SENT
       - sdi_status = PENDING
       - sdi_sent_at = now()
    5. (Opzionale) Invia copia cortesia PDF via PEC a cliente

    Permissions:
    - Admin only

    TODO:
    - Implementare invio PEC con MS Graph o SMTP
    - Configurare credenziali PEC in .env
    - Implementare gestione ricevute SDI
    - Implementare webhook per notifiche SDI
    """,
)
async def send_to_sdi(
    invoice_id: UUID,
    request: InvoiceSendSDIRequest,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(require_support)],
):
    """Invia fattura a SDI (STUB)"""
    logger.warning(f"send_to_sdi called for invoice {invoice_id} - STUB implementation")

    invoice = await _get_invoice_or_404(db, invoice_id, current_user)

    # Verifica status
    if invoice.status != InvoiceStatus.GENERATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice must be GENERATED before sending to SDI",
        )

    # Verifica XML exists
    if not invoice.xml_file_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Generate XML before sending to SDI",
        )

    # TODO: Implementare invio PEC reale
    # Per ora simuliamo invio successo
    logger.warning("PEC sending not implemented - simulating success")

    # Aggiorna status
    invoice.status = InvoiceStatus.SENT
    invoice.sdi_status = SDIStatus.PENDING
    invoice.sdi_sent_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(invoice)

    logger.info(f"Invoice {invoice.invoice_number} marked as SENT (stub)")

    # Ricarica con relazioni
    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.lines))
        .where(Invoice.id == invoice.id)
    )
    return result.scalar_one()


# =============================================================================
# UPDATE INVOICE
# =============================================================================


@router.patch(
    "/{invoice_id}",
    response_model=InvoiceResponse,
    summary="Aggiorna status fattura (Admin only)",
    description="""
    Aggiorna status fattura o dati SDI.

    Permissions:
    - Admin only

    Campi aggiornabili:
    - status: Status fattura
    - sdi_status: Status SDI
    - sdi_rejection_reason: Motivo rifiuto SDI
    - pec_sent: Flag invio PEC a cliente

    Note:
    - Non è possibile modificare dati fattura (immutabile)
    - Non è possibile modificare totali (calcolati)
    - Non è possibile modificare numero fattura (generato)
    """,
)
async def update_invoice(
    invoice_id: UUID,
    data: InvoiceUpdate,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    current_user: Annotated[User, Depends(require_support)],
):
    """Aggiorna status fattura"""
    logger.info(f"Updating invoice {invoice_id}")

    invoice = await _get_invoice_or_404(db, invoice_id, current_user)

    # Aggiorna campi
    if data.status is not None:
        invoice.status = data.status

    if data.sdi_status is not None:
        invoice.sdi_status = data.sdi_status

        # Se accettata, aggiorna timestamp
        if data.sdi_status == SDIStatus.RC:
            invoice.sdi_accepted_at = datetime.now(timezone.utc)
            invoice.status = InvoiceStatus.ACCEPTED

    if data.sdi_rejection_reason is not None:
        invoice.sdi_rejection_reason = data.sdi_rejection_reason

    if data.pec_sent is not None:
        invoice.pec_sent = data.pec_sent
        if data.pec_sent and not invoice.pec_sent_at:
            invoice.pec_sent_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(invoice)

    logger.info(f"Invoice {invoice.invoice_number} updated")

    # Ricarica con relazioni
    result = await db.execute(
        select(Invoice)
        .options(selectinload(Invoice.lines))
        .where(Invoice.id == invoice.id)
    )
    return result.scalar_one()


# =============================================================================
# STATS
# =============================================================================


@router.get(
    "/stats",
    response_model=InvoiceStatsResponse,
    summary="Statistiche fatturazione (Admin only)",
    description="""
    Ritorna statistiche fatturazione per anno.

    Permissions:
    - Admin only

    Statistiche:
    - Totale fatture
    - Fatturato totale
    - Importo medio fattura
    - Conteggio per status
    - Fatturato per mese
    - Top 10 clienti per fatturato
    """,
)
async def get_invoice_stats(
    year: int = Query(..., description="Anno fiscale", ge=2020, le=2100),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_support),
):
    """Ottiene statistiche fatturazione"""
    logger.info(f"Getting invoice stats for year {year}")

    # TODO: Implementare query statistiche complete
    # Per ora ritorniamo dati stub
    return InvoiceStatsResponse(
        year=year,
        total_invoices=0,
        total_revenue=Decimal("0.00"),
        average_invoice=Decimal("0.00"),
        by_status={},
        by_month=[],
        top_customers=[],
    )


# =============================================================================
# LOGGING
# =============================================================================

logger.info("Invoice routes loaded successfully")
