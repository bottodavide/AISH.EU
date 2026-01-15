"""
Modulo: invoice.py
Descrizione: Pydantic schemas per fatturazione elettronica italiana
Autore: Claude per Davide
Data: 2026-01-15

Schemas inclusi:
- InvoiceLineResponse: Riga fattura
- InvoiceResponse: Fattura completa con righe
- InvoiceListItem: Item leggero per lista fatture
- InvoiceCreate: Creazione fattura da ordine
- InvoiceUpdate: Aggiornamento status/metadata
- InvoiceFilters: Filtri ricerca fatture
- CreditNoteCreate/Response: Note di credito
- InvoiceStatsResponse: Statistiche fatturazione

Workflow:
1. Order pagato → POST /invoices (InvoiceCreate)
2. Sistema genera numero progressivo
3. Status = DRAFT
4. POST /invoices/{id}/generate-pdf → PDF generato
5. POST /invoices/{id}/generate-xml → XML PA generato
6. POST /invoices/{id}/send-sdi → Invio PEC a SDI
7. Webhook/polling SDI → Update status

Compliance:
- Formato XML PA 1.2.1
- Regime fiscale RF01 (ordinario)
- IVA 22% standard
- Numerazione progressiva per anno
- Conservazione 10 anni
"""

import logging
from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.invoice import InvoiceStatus, SDIStatus

logger = logging.getLogger(__name__)


# =============================================================================
# INVOICE LINE SCHEMAS
# =============================================================================


class InvoiceLineResponse(BaseModel):
    """
    Response schema per riga fattura.

    Contiene tutti i dettagli della riga:
    - Descrizione servizio
    - Quantità e prezzo unitario
    - Aliquota IVA e importo IVA
    - Totale riga
    """

    model_config = ConfigDict(from_attributes=True)

    # IDs
    id: UUID = Field(..., description="ID univoco riga")
    invoice_id: UUID = Field(..., description="ID fattura parent")

    # Line info
    line_number: int = Field(..., description="Numero riga progressivo", ge=1)
    description: str = Field(..., description="Descrizione prestazione/servizio")

    # Quantità e prezzi
    quantity: Decimal = Field(..., description="Quantità", ge=0)
    unit_price: Decimal = Field(..., description="Prezzo unitario (imponibile) €", ge=0)

    # IVA
    tax_rate: Decimal = Field(..., description="Aliquota IVA %", ge=0, le=100)
    tax_amount: Decimal = Field(..., description="IVA calcolata €", ge=0)

    # Totale
    total: Decimal = Field(..., description="Totale riga (con IVA) €", ge=0)

    # Timestamps
    created_at: datetime = Field(..., description="Data creazione")
    updated_at: datetime = Field(..., description="Data ultimo aggiornamento")


# =============================================================================
# INVOICE SCHEMAS
# =============================================================================


class InvoiceResponse(BaseModel):
    """
    Response schema completo per fattura.

    Include tutti i dati fattura + righe + file generati.
    Usato per GET /invoices/{id}
    """

    model_config = ConfigDict(from_attributes=True)

    # IDs
    id: UUID = Field(..., description="ID univoco fattura")
    order_id: UUID = Field(..., description="ID ordine collegato")
    user_id: UUID = Field(..., description="ID cliente")

    # Numero fattura
    invoice_number: str = Field(..., description="Numero fattura (es: 2026/00001)")
    invoice_year: int = Field(..., description="Anno fiscale")
    invoice_progressive: int = Field(..., description="Numero progressivo nell'anno")

    # Date
    issue_date: date = Field(..., description="Data emissione fattura")
    due_date: Optional[date] = Field(None, description="Data scadenza pagamento")

    # Dati Cedente (AI Strategy Hub)
    seller_name: str = Field(..., description="Denominazione cedente")
    seller_vat: str = Field(..., description="Partita IVA cedente")
    seller_fiscal_code: Optional[str] = Field(None, description="Codice Fiscale cedente")
    seller_address: dict = Field(..., description="Indirizzo cedente (JSON)")
    seller_regime_fiscale: str = Field(..., description="Regime fiscale (es: RF01)")

    # Dati Cessionario (Cliente)
    buyer_name: str = Field(..., description="Denominazione cessionario")
    buyer_vat: Optional[str] = Field(None, description="Partita IVA cessionario")
    buyer_fiscal_code: Optional[str] = Field(None, description="Codice Fiscale cessionario")
    buyer_pec: Optional[str] = Field(None, description="Email PEC cessionario")
    buyer_sdi_code: Optional[str] = Field(None, description="Codice SDI destinatario")
    buyer_address: dict = Field(..., description="Indirizzo cessionario (JSON)")

    # Totali
    subtotal: Decimal = Field(..., description="Imponibile totale €", ge=0)
    tax_amount: Decimal = Field(..., description="IVA totale €", ge=0)
    total: Decimal = Field(..., description="Totale fattura €", ge=0)
    currency: str = Field(default="EUR", description="Valuta")

    # Status
    status: InvoiceStatus = Field(..., description="Status fattura")

    # File generati
    pdf_file_id: Optional[UUID] = Field(None, description="ID file PDF")
    xml_file_id: Optional[UUID] = Field(None, description="ID file XML PA")
    pdf_url: Optional[str] = Field(None, description="URL PDF (legacy)")
    xml_url: Optional[str] = Field(None, description="URL XML (legacy)")

    # Status SDI
    sdi_status: SDIStatus = Field(..., description="Status Sistema di Interscambio")
    sdi_sent_at: Optional[datetime] = Field(None, description="Timestamp invio SDI")
    sdi_accepted_at: Optional[datetime] = Field(None, description="Timestamp accettazione SDI")
    sdi_rejection_reason: Optional[str] = Field(None, description="Motivo rifiuto SDI")

    # Status PEC
    pec_sent: bool = Field(default=False, description="Copia cortesia inviata via PEC")
    pec_sent_at: Optional[datetime] = Field(None, description="Timestamp invio PEC cliente")

    # Righe fattura
    lines: list[InvoiceLineResponse] = Field(default_factory=list, description="Righe fattura")

    # Timestamps
    created_at: datetime = Field(..., description="Data creazione")
    updated_at: datetime = Field(..., description="Data ultimo aggiornamento")


class InvoiceListItem(BaseModel):
    """
    Schema leggero per lista fatture.

    Contiene solo i campi essenziali per rendering lista.
    Usato per GET /invoices (senza righe)
    """

    model_config = ConfigDict(from_attributes=True)

    # IDs
    id: UUID
    order_id: UUID
    user_id: UUID

    # Numero fattura
    invoice_number: str
    invoice_year: int
    invoice_progressive: int

    # Date
    issue_date: date
    due_date: Optional[date] = None

    # Cliente
    buyer_name: str
    buyer_vat: Optional[str] = None
    buyer_fiscal_code: Optional[str] = None

    # Totali
    subtotal: Decimal
    tax_amount: Decimal
    total: Decimal
    currency: str = "EUR"

    # Status
    status: InvoiceStatus
    sdi_status: SDIStatus

    # File
    pdf_file_id: Optional[UUID] = None
    xml_file_id: Optional[UUID] = None

    # Timestamps
    created_at: datetime
    updated_at: datetime


# =============================================================================
# CREATE / UPDATE SCHEMAS
# =============================================================================


class InvoiceCreate(BaseModel):
    """
    Schema per creazione fattura da ordine pagato.

    Workflow:
    1. Order pagato → Payment.status = COMPLETED
    2. POST /invoices con order_id
    3. Sistema:
       - Genera numero progressivo
       - Snapshot dati cedente da settings
       - Snapshot dati cessionario da UserProfile
       - Copia righe da OrderItems
       - Calcola totali
       - Status = DRAFT
    4. Ritorna InvoiceResponse

    Validation:
    - Order deve esistere
    - Order deve essere pagato (Payment.status = COMPLETED)
    - Order non deve avere già una fattura
    - UserProfile deve avere dati completi per fatturazione
    """

    order_id: UUID = Field(..., description="ID ordine da fatturare")

    # Opzionale: override date
    issue_date: Optional[date] = Field(
        None,
        description="Data emissione (default: oggi)",
    )

    due_date: Optional[date] = Field(
        None,
        description="Data scadenza pagamento (opzionale)",
    )

    # Opzionale: override dati cliente (se diversi da UserProfile)
    buyer_name: Optional[str] = Field(None, max_length=255)
    buyer_vat: Optional[str] = Field(None, max_length=20)
    buyer_fiscal_code: Optional[str] = Field(None, max_length=16)
    buyer_pec: Optional[str] = Field(None, max_length=255)
    buyer_sdi_code: Optional[str] = Field(None, max_length=7)

    @field_validator("buyer_sdi_code")
    @classmethod
    def validate_sdi_code(cls, v: Optional[str]) -> Optional[str]:
        """Valida codice SDI (7 caratteri alfanumerici)"""
        if v is not None:
            v = v.strip().upper()
            if len(v) != 7:
                raise ValueError("Codice SDI deve essere 7 caratteri")
            if not v.isalnum():
                raise ValueError("Codice SDI deve contenere solo lettere e numeri")
        return v

    @field_validator("buyer_fiscal_code")
    @classmethod
    def validate_fiscal_code(cls, v: Optional[str]) -> Optional[str]:
        """Valida codice fiscale (16 caratteri alfanumerici)"""
        if v is not None:
            v = v.strip().upper()
            if len(v) != 16:
                raise ValueError("Codice Fiscale deve essere 16 caratteri")
            if not v.isalnum():
                raise ValueError("Codice Fiscale deve contenere solo lettere e numeri")
        return v


class InvoiceUpdate(BaseModel):
    """
    Schema per aggiornamento fattura (admin only).

    Permette di aggiornare solo:
    - Status (workflow manuale)
    - SDI status/dates (se integrazione SDI fallisce)
    - PEC status/dates

    NON permette di modificare:
    - Dati fattura (immutabile dopo invio)
    - Totali (calcolati)
    - Numero fattura (generato)
    """

    # Status update
    status: Optional[InvoiceStatus] = Field(
        None,
        description="Nuovo status fattura",
    )

    # SDI update (se integrazione fallisce)
    sdi_status: Optional[SDIStatus] = Field(None)
    sdi_rejection_reason: Optional[str] = Field(None, max_length=1000)

    # PEC update
    pec_sent: Optional[bool] = Field(None)

    # Note: Non permettiamo di modificare date o dati fattura
    # per garantire immutabilità dopo emissione


# =============================================================================
# FILTER SCHEMAS
# =============================================================================


class InvoiceFilters(BaseModel):
    """
    Schema per filtri ricerca fatture.

    Usato per GET /invoices?status=...&year=...

    Filtri disponibili:
    - Status fattura
    - Anno fiscale
    - Range date emissione
    - Cliente (user_id o nome)
    - SDI status
    - Ricerca full-text su numero/cliente
    """

    # Pagination
    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=100)] = 20

    # Filtri status
    status: Optional[InvoiceStatus] = Field(
        None,
        description="Filtra per status fattura",
    )

    sdi_status: Optional[SDIStatus] = Field(
        None,
        description="Filtra per status SDI",
    )

    # Filtri temporali
    year: Optional[int] = Field(
        None,
        description="Anno fiscale",
        ge=2020,
        le=2100,
    )

    issue_date_from: Optional[date] = Field(
        None,
        description="Data emissione da (inclusa)",
    )

    issue_date_to: Optional[date] = Field(
        None,
        description="Data emissione a (inclusa)",
    )

    # Filtri cliente
    user_id: Optional[UUID] = Field(
        None,
        description="Filtra per ID cliente",
    )

    buyer_name: Optional[str] = Field(
        None,
        description="Ricerca per nome cliente (ILIKE)",
        max_length=255,
    )

    # Ricerca full-text
    search: Optional[str] = Field(
        None,
        description="Ricerca in numero fattura, nome cliente, descrizione righe",
        max_length=255,
    )

    # Ordinamento
    sort_by: Annotated[str, Field()] = Field(
        default="issue_date",
        description="Campo per ordinamento (issue_date, invoice_number, total, created_at)",
    )

    sort_order: Annotated[str, Field()] = Field(
        default="desc",
        description="Direzione ordinamento (asc, desc)",
    )

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str) -> str:
        """Valida campo ordinamento"""
        allowed = ["issue_date", "invoice_number", "total", "created_at", "invoice_year"]
        if v not in allowed:
            raise ValueError(f"sort_by deve essere uno di: {', '.join(allowed)}")
        return v

    @field_validator("sort_order")
    @classmethod
    def validate_sort_order(cls, v: str) -> str:
        """Valida direzione ordinamento"""
        v = v.lower()
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order deve essere 'asc' o 'desc'")
        return v


# =============================================================================
# GENERATION SCHEMAS
# =============================================================================


class InvoiceGeneratePDFRequest(BaseModel):
    """
    Request per generazione PDF fattura.

    POST /invoices/{id}/generate-pdf

    Genera PDF professionale con:
    - Header con logo AI Strategy Hub
    - Dati cedente e cessionario
    - Tabella righe fattura
    - Totali (imponibile, IVA, totale)
    - Footer con info bancarie
    - QR code per pagamento (opzionale)

    Il PDF viene salvato in files table con:
    - category = INVOICE
    - reference_type = "invoice"
    - reference_id = invoice.id
    """

    # Opzioni generazione
    include_payment_info: bool = Field(
        default=True,
        description="Includi info pagamento e IBAN nel footer",
    )

    include_qr_code: bool = Field(
        default=False,
        description="Includi QR code PagoPA (se configurato)",
    )

    language: str = Field(
        default="it",
        description="Lingua PDF (it, en)",
    )


class InvoiceGenerateXMLRequest(BaseModel):
    """
    Request per generazione XML PA per SDI.

    POST /invoices/{id}/generate-xml

    Genera XML formato FatturaPA 1.2.1 con:
    - FatturaElettronicaHeader (cedente + cessionario)
    - FatturaElettronicaBody (dati fattura + righe)
    - Formato validato contro XSD ufficiale

    Il XML viene salvato in files table con:
    - category = INVOICE
    - reference_type = "invoice"
    - reference_id = invoice.id
    """

    # Opzioni generazione
    transmission_format: str = Field(
        default="FPR12",
        description="Formato trasmissione (FPR12 = FatturaPA 1.2.1)",
    )

    validate_xsd: bool = Field(
        default=True,
        description="Valida XML contro XSD ufficiale",
    )


class InvoiceSendSDIRequest(BaseModel):
    """
    Request per invio fattura a SDI via PEC.

    POST /invoices/{id}/send-sdi

    Workflow:
    1. Verifica invoice.status = GENERATED
    2. Verifica pdf_file_id e xml_file_id esistono
    3. Invia XML via PEC a SDI (sdi@pec.fatturapa.it)
    4. Aggiorna invoice:
       - status = SENT
       - sdi_status = PENDING
       - sdi_sent_at = now()
    5. Invia copia cortesia PDF via PEC a cliente (opzionale)
    """

    send_copy_to_buyer: bool = Field(
        default=True,
        description="Invia copia cortesia PDF al cliente via PEC",
    )

    buyer_pec_override: Optional[str] = Field(
        None,
        description="Override PEC cliente (se diversa da invoice.buyer_pec)",
        max_length=255,
    )


# =============================================================================
# CREDIT NOTE SCHEMAS
# =============================================================================


class CreditNoteCreate(BaseModel):
    """
    Schema per creazione nota di credito.

    Usata per:
    - Annullare fattura errata
    - Storno parziale
    - Rimborso cliente

    Genera XML PA separato (tipo documento TD04)
    """

    original_invoice_id: UUID = Field(
        ...,
        description="ID fattura originale da stornare",
    )

    reason: str = Field(
        ...,
        description="Causale/motivazione nota credito",
        min_length=10,
        max_length=500,
    )

    amount: Decimal = Field(
        ...,
        description="Importo nota credito (positivo) €",
        gt=0,
    )

    issue_date: Optional[date] = Field(
        None,
        description="Data emissione (default: oggi)",
    )


class CreditNoteResponse(BaseModel):
    """Response schema per nota di credito"""

    model_config = ConfigDict(from_attributes=True)

    # IDs
    id: UUID
    original_invoice_id: UUID

    # Numero
    credit_note_number: str

    # Date e dati
    issue_date: date
    reason: str
    amount: Decimal

    # File
    xml_url: Optional[str] = None
    pdf_url: Optional[str] = None

    # Status SDI
    sdi_status: SDIStatus

    # Timestamps
    created_at: datetime
    updated_at: datetime


# =============================================================================
# STATS SCHEMAS
# =============================================================================


class InvoiceStatsResponse(BaseModel):
    """
    Response schema per statistiche fatturazione.

    GET /invoices/stats?year=2026

    Ritorna:
    - Totale fatturato per anno/mese
    - Conteggio fatture per status
    - Media importo fattura
    - Top clienti per fatturato
    """

    year: int = Field(..., description="Anno statistiche")

    # Totali
    total_invoices: int = Field(..., description="Numero fatture totali")
    total_revenue: Decimal = Field(..., description="Fatturato totale €")
    average_invoice: Decimal = Field(..., description="Importo medio fattura €")

    # Per status
    by_status: dict[str, int] = Field(
        ...,
        description="Conteggio fatture per status",
    )

    # Per mese
    by_month: list[dict] = Field(
        ...,
        description="Fatturato per mese [{month: 1, revenue: 1500.00, count: 5}, ...]",
    )

    # Top clienti
    top_customers: list[dict] = Field(
        ...,
        description="Top 10 clienti per fatturato [{name, revenue, count}, ...]",
    )


# =============================================================================
# LOGGING
# =============================================================================

logger.debug("Invoice schemas loaded successfully")
