"""
Modulo: invoice.py
Descrizione: Modelli SQLAlchemy per fatturazione elettronica italiana
Autore: Claude per Davide
Data: 2026-01-15

Modelli inclusi:
- Invoice: Fattura principale (XML PA + PDF)
- InvoiceLine: Righe fattura
- CreditNote: Note di credito

Note sulla Fatturazione Elettronica Italiana:
- Formato XML PA 1.2.1 (Sistema di Interscambio)
- Invio via PEC a SDI
- Tracking stati: Inviata → Accettata/Rifiutata
- Conservazione sostitutiva 10 anni
- Numerazione progressiva per anno fiscale

Compliance:
- D.Lgs. 127/2015 (fatturazione elettronica B2B)
- Conservazione digitale ex DMEF 17/06/2014
"""

import logging
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS
# =============================================================================

import enum


class InvoiceStatus(str, enum.Enum):
    """
    Status fattura nel workflow.

    Workflow:
    DRAFT → GENERATED → SENT → ACCEPTED/REJECTED
                                   ↓
                              DELIVERED (al cliente finale)
    """

    DRAFT = "draft"  # Bozza (non ancora generata XML)
    GENERATED = "generated"  # XML generato, non ancora inviato
    SENT = "sent"  # Inviata a SDI via PEC
    ACCEPTED = "accepted"  # Accettata da SDI
    REJECTED = "rejected"  # Rifiutata da SDI
    DELIVERED = "delivered"  # Consegnata al destinatario finale


class SDIStatus(str, enum.Enum):
    """
    Status notifiche Sistema di Interscambio (SDI).

    Basato su codici ricevute SDI:
    - MC: Mancata consegna
    - NS: Notifica di scarto
    - RC: Ricevuta di consegna
    - EC: Esito committente (accettazione/rifiuto)
    """

    PENDING = "pending"  # In attesa risposta SDI
    MC = "mc"  # Mancata consegna
    NS = "ns"  # Notificata scarto
    RC = "rc"  # Ricevuta consegna
    EC_ACCEPTED = "ec_accepted"  # Esito: accettata
    EC_REJECTED = "ec_rejected"  # Esito: rifiutata


# =============================================================================
# INVOICE MODEL
# =============================================================================


class Invoice(Base, UUIDMixin, TimestampMixin):
    """
    Fattura elettronica italiana.

    Features:
    - Numerazione progressiva per anno fiscale
    - Generazione XML PA formato 1.2.1
    - Generazione PDF per cliente
    - Invio automatico via PEC a SDI
    - Tracking ricevute SDI
    - Invio copia cortesia via PEC a cliente

    Relationships:
    - order: Order (one-to-one)
    - user: User (cliente)
    - lines: InvoiceLine[] (righe fattura)

    Compliance:
    - Tutti i dati obbligatori per XML PA
    - Split payment se applicabile
    - Ritenuta d'acconto se applicabile
    - Bollo virtuale se applicabile

    Note:
    - Conservazione 10 anni obbligatoria
    - Immutabilità dopo invio (solo note credito per correzioni)
    """

    __tablename__ = "invoices"

    # -------------------------------------------------------------------------
    # Numero Fattura
    # -------------------------------------------------------------------------

    invoice_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Numero fattura completo (es: 2026/00001)",
    )

    invoice_year = Column(
        Integer,
        nullable=False,
        index=True,
        comment="Anno fiscale",
    )

    invoice_progressive = Column(
        Integer,
        nullable=False,
        comment="Numero progressivo nell'anno",
    )

    # -------------------------------------------------------------------------
    # Foreign Keys
    # -------------------------------------------------------------------------

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
        index=True,
        comment="FK a orders (one-to-one, RESTRICT per sicurezza)",
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="FK a users (cliente)",
    )

    # -------------------------------------------------------------------------
    # Date
    # -------------------------------------------------------------------------

    issue_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Data emissione fattura",
    )

    due_date = Column(
        Date,
        nullable=True,
        comment="Data scadenza pagamento (opzionale)",
    )

    # -------------------------------------------------------------------------
    # Dati Cedente (Chi emette - AI Strategy Hub)
    # -------------------------------------------------------------------------
    # Snapshot da settings al momento emissione

    seller_name = Column(
        String(255),
        nullable=False,
        comment="Denominazione cedente",
    )

    seller_vat = Column(
        String(20),
        nullable=False,
        comment="Partita IVA cedente",
    )

    seller_fiscal_code = Column(
        String(16),
        nullable=True,
        comment="Codice Fiscale cedente (se diverso da P.IVA)",
    )

    seller_address = Column(
        JSONB,
        nullable=False,
        comment="Indirizzo cedente (JSON)",
    )

    seller_regime_fiscale = Column(
        String(10),
        nullable=False,
        comment="Regime fiscale cedente (es: RF01 per ordinario)",
    )

    # -------------------------------------------------------------------------
    # Dati Cessionario (Cliente)
    # -------------------------------------------------------------------------
    # Snapshot da UserProfile al momento emissione

    buyer_name = Column(
        String(255),
        nullable=False,
        comment="Denominazione cessionario",
    )

    buyer_vat = Column(
        String(20),
        nullable=True,
        comment="Partita IVA cessionario (B2B)",
    )

    buyer_fiscal_code = Column(
        String(16),
        nullable=True,
        comment="Codice Fiscale cessionario (B2C o se P.IVA mancante)",
    )

    buyer_pec = Column(
        String(255),
        nullable=True,
        comment="Email PEC cessionario per ricezione",
    )

    buyer_sdi_code = Column(
        String(7),
        nullable=True,
        comment="Codice SDI destinatario (7 caratteri)",
    )

    buyer_address = Column(
        JSONB,
        nullable=False,
        comment="Indirizzo cessionario (JSON)",
    )

    # -------------------------------------------------------------------------
    # Totali Fattura
    # -------------------------------------------------------------------------

    subtotal = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Imponibile totale (senza IVA)",
    )

    tax_amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="IVA totale",
    )

    total = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Totale fattura (imponibile + IVA)",
    )

    currency = Column(
        String(3),
        nullable=False,
        default="EUR",
        comment="Valuta (sempre EUR per Italia)",
    )

    # -------------------------------------------------------------------------
    # Status Fattura
    # -------------------------------------------------------------------------

    status = Column(
        Enum(InvoiceStatus),
        nullable=False,
        default=InvoiceStatus.DRAFT,
        index=True,
        comment="Status fattura nel workflow",
    )

    # -------------------------------------------------------------------------
    # File Generati
    # -------------------------------------------------------------------------

    pdf_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK a files (PDF fattura)",
    )

    xml_file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("files.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK a files (XML PA per SDI)",
    )

    pdf_url = Column(
        String(500),
        nullable=True,
        comment="URL file PDF per cliente (legacy/deprecated)",
    )

    xml_url = Column(
        String(500),
        nullable=True,
        comment="URL file XML PA (legacy/deprecated)",
    )

    xml_signed_url = Column(
        String(500),
        nullable=True,
        comment="URL file XML firmato digitalmente (opzionale)",
    )

    # -------------------------------------------------------------------------
    # Status SDI (Sistema di Interscambio)
    # -------------------------------------------------------------------------

    sdi_status = Column(
        Enum(SDIStatus),
        nullable=False,
        default=SDIStatus.PENDING,
        index=True,
        comment="Status notifiche SDI",
    )

    sdi_sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp invio a SDI via PEC",
    )

    sdi_accepted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp accettazione SDI",
    )

    sdi_rejection_reason = Column(
        Text,
        nullable=True,
        comment="Motivo rifiuto SDI (se rejected)",
    )

    # -------------------------------------------------------------------------
    # Status PEC (Invio copia cortesia a cliente)
    # -------------------------------------------------------------------------

    pec_sent = Column(
        Boolean,
        nullable=False,
        default=False,
        comment="Copia cortesia inviata via PEC a cliente",
    )

    pec_sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp invio PEC a cliente",
    )

    pec_delivery_receipt = Column(
        Text,
        nullable=True,
        comment="Ricevuta di consegna PEC (base64 o URL)",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    order = relationship("Order")
    user = relationship("User")

    lines = relationship(
        "InvoiceLine",
        back_populates="invoice",
        cascade="all, delete-orphan",
        order_by="InvoiceLine.line_number",
    )

    pdf_file = relationship("File", foreign_keys=[pdf_file_id])
    xml_file = relationship("File", foreign_keys=[xml_file_id])

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_invoices_year_progressive", "invoice_year", "invoice_progressive", unique=True),
        Index("ix_invoices_user_year", "user_id", "invoice_year"),
        Index("ix_invoices_issue_date", "issue_date"),
        Index("ix_invoices_status", "status"),
        Index("ix_invoices_sdi_status", "sdi_status"),
        {"comment": "Fatture elettroniche italiane (XML PA)"},
    )

    def __repr__(self) -> str:
        return f"<Invoice(number={self.invoice_number}, buyer={self.buyer_name}, total=€{self.total})>"


# =============================================================================
# INVOICE LINE MODEL
# =============================================================================


class InvoiceLine(Base, UUIDMixin, TimestampMixin):
    """
    Riga fattura.

    Ogni riga rappresenta:
    - Un servizio/prestazione
    - Quantità (es: 1 per servizio consulenza)
    - Prezzo unitario
    - Aliquota IVA
    - Totale riga

    Note:
    - Corrisponde a <DettaglioLinee> in XML PA
    - Supporta natura IVA particolare (N2, N3, etc.)
    """

    __tablename__ = "invoice_lines"

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    invoice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a invoices",
    )

    # -------------------------------------------------------------------------
    # Line Info
    # -------------------------------------------------------------------------

    line_number = Column(
        Integer,
        nullable=False,
        comment="Numero riga progressivo (per ordinamento)",
    )

    description = Column(
        Text,
        nullable=False,
        comment="Descrizione prestazione/servizio",
    )

    # -------------------------------------------------------------------------
    # Quantità e Prezzi
    # -------------------------------------------------------------------------

    quantity = Column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("1.00"),
        comment="Quantità (es: 1.00 per servizi)",
    )

    unit_price = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Prezzo unitario (imponibile) in EUR",
    )

    # -------------------------------------------------------------------------
    # IVA
    # -------------------------------------------------------------------------

    tax_rate = Column(
        Numeric(5, 2),
        nullable=False,
        comment="Aliquota IVA % (es: 22.00)",
    )

    tax_amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="IVA calcolata per questa riga",
    )

    total = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Totale riga (quantity * unit_price + IVA)",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    invoice = relationship("Invoice", back_populates="lines")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_invoice_lines_invoice_line", "invoice_id", "line_number", unique=True),
        {"comment": "Righe fattura"},
    )

    def __repr__(self) -> str:
        return f"<InvoiceLine(invoice_id={self.invoice_id}, line={self.line_number}, total=€{self.total})>"


# =============================================================================
# CREDIT NOTE MODEL
# =============================================================================


class CreditNote(Base, UUIDMixin, TimestampMixin):
    """
    Nota di credito.

    Usata per:
    - Annullare fattura errata
    - Storno parziale
    - Rimborso cliente

    Note:
    - Genera XML PA separato (tipo documento TD04)
    - Riferisce fattura originale
    - Stessa procedura invio SDI della fattura
    - Numerazione separata dalle fatture

    Compliance:
    - D.P.R. 633/72 art. 26
    """

    __tablename__ = "credit_notes"

    # -------------------------------------------------------------------------
    # Numero Nota Credito
    # -------------------------------------------------------------------------

    credit_note_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Numero nota credito (es: NC-2026-00001)",
    )

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    original_invoice_id = Column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
        comment="FK a invoices (fattura originale)",
    )

    # -------------------------------------------------------------------------
    # Date e Dati
    # -------------------------------------------------------------------------

    issue_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Data emissione nota credito",
    )

    reason = Column(
        Text,
        nullable=False,
        comment="Causale/motivazione nota credito",
    )

    amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Importo nota credito (positivo) in EUR",
    )

    # -------------------------------------------------------------------------
    # File Generati
    # -------------------------------------------------------------------------

    xml_url = Column(
        String(500),
        nullable=True,
        comment="URL file XML PA nota credito",
    )

    pdf_url = Column(
        String(500),
        nullable=True,
        comment="URL file PDF nota credito",
    )

    # -------------------------------------------------------------------------
    # Status SDI
    # -------------------------------------------------------------------------

    sdi_status = Column(
        Enum(SDIStatus),
        nullable=False,
        default=SDIStatus.PENDING,
        index=True,
        comment="Status notifiche SDI",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    original_invoice = relationship("Invoice")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_credit_notes_invoice_id", "original_invoice_id"),
        Index("ix_credit_notes_issue_date", "issue_date"),
        {"comment": "Note di credito (storno fatture)"},
    )

    def __repr__(self) -> str:
        return f"<CreditNote(number={self.credit_note_number}, invoice_id={self.original_invoice_id}, amount=€{self.amount})>"


# =============================================================================
# LOGGING
# =============================================================================

logger.debug("Invoice models loaded: Invoice, InvoiceLine, CreditNote")
