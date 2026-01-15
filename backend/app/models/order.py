"""
Modulo: order.py
Descrizione: Modelli SQLAlchemy per ordini, pagamenti e quote
Autore: Claude per Davide
Data: 2026-01-15

Modelli inclusi:
- QuoteRequest: Richiesta preventivo personalizzato
- Order: Ordine principale
- OrderItem: Righe ordine (servizi acquistati)
- Payment: Transazioni pagamento Stripe

Note:
- NO prodotti fisici, solo servizi
- NO shipping, solo billing
- Stripe come payment gateway
- Workflow: QuoteRequest → Order → Payment → Invoice
"""

import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Column,
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


class QuoteRequestStatus(str, enum.Enum):
    """
    Status richiesta preventivo.

    Workflow:
    NEW → IN_REVIEW → QUOTED → ACCEPTED/REJECTED
    """

    NEW = "new"
    IN_REVIEW = "in_review"
    QUOTED = "quoted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class OrderStatus(str, enum.Enum):
    """
    Status ordine.

    Workflow:
    PENDING → AWAITING_PAYMENT → PAID → PROCESSING → COMPLETED
                                    ↓
                               CANCELLED/REFUNDED
    """

    PENDING = "pending"  # Ordine creato, non ancora pagato
    AWAITING_PAYMENT = "awaiting_payment"  # In attesa pagamento
    PAID = "paid"  # Pagamento ricevuto
    PROCESSING = "processing"  # In lavorazione
    COMPLETED = "completed"  # Completato
    CANCELLED = "cancelled"  # Annullato
    REFUNDED = "refunded"  # Rimborsato


class PaymentStatus(str, enum.Enum):
    """
    Status pagamento.

    Mappato su eventi Stripe webhook.
    """

    PENDING = "pending"  # In attesa
    SUCCEEDED = "succeeded"  # Successo
    FAILED = "failed"  # Fallito
    REFUNDED = "refunded"  # Rimborsato
    CANCELLED = "cancelled"  # Cancellato


# =============================================================================
# QUOTE REQUEST MODEL
# =============================================================================


class QuoteRequest(Base, UUIDMixin, TimestampMixin):
    """
    Richiesta preventivo personalizzato.

    Usato per servizi CUSTOM_QUOTE dove il prezzo va concordato.

    Workflow:
    1. Cliente compila form richiesta preventivo
    2. Admin rivede e genera preventivo
    3. Cliente riceve email con preventivo PDF
    4. Cliente accetta → crea Order

    Relationships:
    - user: User (nullable per guest)
    - service: Service
    - order: Order (se accettato)
    """

    __tablename__ = "quote_requests"

    # -------------------------------------------------------------------------
    # Numero Richiesta
    # -------------------------------------------------------------------------

    request_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Numero richiesta (es: QR-2026-00001)",
    )

    # -------------------------------------------------------------------------
    # Foreign Keys
    # -------------------------------------------------------------------------

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK a users (nullable per guest)",
    )

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a services",
    )

    # -------------------------------------------------------------------------
    # Contact Info (required anche per user registrati)
    # -------------------------------------------------------------------------

    contact_name = Column(
        String(255),
        nullable=False,
        comment="Nome contatto",
    )

    contact_email = Column(
        String(255),
        nullable=False,
        index=True,
        comment="Email contatto",
    )

    contact_phone = Column(
        String(20),
        nullable=True,
        comment="Telefono contatto",
    )

    company_name = Column(
        String(255),
        nullable=True,
        comment="Azienda (opzionale)",
    )

    # -------------------------------------------------------------------------
    # Request Details
    # -------------------------------------------------------------------------

    message = Column(
        Text,
        nullable=True,
        comment="Messaggio/descrizione esigenze",
    )

    custom_fields = Column(
        JSONB,
        nullable=True,
        comment="Risposte questionario custom (JSON key-value)",
    )
    # Example:
    # {
    #   "company_size": "50-100",
    #   "industry": "fintech",
    #   "urgency": "high"
    # }

    # -------------------------------------------------------------------------
    # Quote Status & Workflow
    # -------------------------------------------------------------------------

    status = Column(
        Enum(QuoteRequestStatus),
        nullable=False,
        default=QuoteRequestStatus.NEW,
        index=True,
        comment="Status richiesta",
    )

    quoted_amount = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Importo preventivo (EUR)",
    )

    quoted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp invio preventivo",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    user = relationship("User", foreign_keys=[user_id])
    service = relationship("Service")
    # TODO: order = relationship("Order", back_populates="quote_request")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_quote_requests_status_created", "status", "created_at"),
        Index("ix_quote_requests_email", "contact_email"),
        {"comment": "Richieste preventivo personalizzato"},
    )

    def __repr__(self) -> str:
        return f"<QuoteRequest(number={self.request_number}, status={self.status})>"


# =============================================================================
# ORDER MODEL
# =============================================================================


class Order(Base, UUIDMixin, TimestampMixin):
    """
    Ordine principale.

    Un ordine contiene:
    - Uno o più servizi (OrderItem)
    - Dati billing snapshot
    - Calcolo IVA italiana
    - Link a Payment e Invoice

    Workflow:
    1. Crea Order (status=PENDING)
    2. Cliente paga (Stripe) → status=PAID
    3. Genera Invoice automaticamente
    4. Processa servizio → status=PROCESSING
    5. Completa → status=COMPLETED

    Relationships:
    - user: User
    - quote_request: QuoteRequest (opzionale)
    - items: OrderItem[]
    - payment: Payment
    - invoice: Invoice (one-to-one)
    """

    __tablename__ = "orders"

    # -------------------------------------------------------------------------
    # Numero Ordine
    # -------------------------------------------------------------------------

    order_number = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Numero ordine (es: ORD-2026-00001)",
    )

    # -------------------------------------------------------------------------
    # Foreign Keys
    # -------------------------------------------------------------------------

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a users",
    )

    quote_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("quote_requests.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK a quote_requests (se da preventivo)",
    )

    # -------------------------------------------------------------------------
    # Status
    # -------------------------------------------------------------------------

    status = Column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
        index=True,
        comment="Status ordine",
    )

    # -------------------------------------------------------------------------
    # Totali (calcolati da OrderItems)
    # -------------------------------------------------------------------------

    subtotal = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Subtotale (senza IVA) in EUR",
    )

    tax_rate = Column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("22.00"),
        comment="Aliquota IVA % (es: 22.00 per IVA 22%)",
    )

    tax_amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Importo IVA calcolato in EUR",
    )

    total = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Totale ordine (subtotal + IVA) in EUR",
    )

    currency = Column(
        String(3),
        nullable=False,
        default="EUR",
        comment="Valuta (sempre EUR per Italia)",
    )

    # -------------------------------------------------------------------------
    # Billing Data (snapshot)
    # -------------------------------------------------------------------------

    billing_data = Column(
        JSONB,
        nullable=False,
        comment="Snapshot dati fatturazione (from UserProfile)",
    )
    # Example:
    # {
    #   "company_name": "Acme Corp",
    #   "vat_number": "IT12345678901",
    #   "address": {...},
    #   "pec_email": "...",
    #   "sdi_code": "..."
    # }

    # -------------------------------------------------------------------------
    # Notes
    # -------------------------------------------------------------------------

    notes = Column(
        Text,
        nullable=True,
        comment="Note aggiuntive (admin o cliente)",
    )

    # -------------------------------------------------------------------------
    # Timestamps Workflow
    # -------------------------------------------------------------------------

    paid_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp pagamento ricevuto",
    )

    completed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp completamento ordine",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    user = relationship("User")
    quote_request = relationship("QuoteRequest")

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
    )

    payment = relationship(
        "Payment",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # TODO: invoice = relationship("Invoice", back_populates="order", uselist=False)

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_orders_user_status", "user_id", "status"),
        Index("ix_orders_status_created", "status", "created_at"),
        Index("ix_orders_paid_at", "paid_at"),
        {"comment": "Ordini principali"},
    )

    def __repr__(self) -> str:
        return f"<Order(number={self.order_number}, status={self.status}, total=€{self.total})>"


# =============================================================================
# ORDER ITEM MODEL
# =============================================================================


class OrderItem(Base, UUIDMixin, TimestampMixin):
    """
    Riga ordine (servizio acquistato).

    Contiene:
    - Service snapshot (name, description)
    - Prezzo al momento acquisto
    - Quantità (solitamente 1 per servizi)
    - IVA per riga

    Note:
    - Snapshot fields per preservare dati anche se Service cambia
    - Quantity support per servizi ricorrenti/multipli
    """

    __tablename__ = "order_items"

    # -------------------------------------------------------------------------
    # Foreign Keys
    # -------------------------------------------------------------------------

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="FK a orders",
    )

    service_id = Column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="FK a services (nullable se service eliminato)",
    )

    # -------------------------------------------------------------------------
    # Service Snapshot
    # -------------------------------------------------------------------------

    service_name = Column(
        String(255),
        nullable=False,
        comment="Nome servizio (snapshot)",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Descrizione servizio (snapshot)",
    )

    # -------------------------------------------------------------------------
    # Pricing
    # -------------------------------------------------------------------------

    quantity = Column(
        Integer,
        nullable=False,
        default=1,
        comment="Quantità (solitamente 1 per servizi)",
    )

    unit_price = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Prezzo unitario (snapshot) in EUR",
    )

    tax_rate = Column(
        Numeric(5, 2),
        nullable=False,
        comment="Aliquota IVA % per questa riga",
    )

    total_price = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Totale riga (quantity * unit_price + IVA) in EUR",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    order = relationship("Order", back_populates="items")
    service = relationship("Service")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
        Index("ix_order_items_service_id", "service_id"),
        {"comment": "Righe ordine (servizi acquistati)"},
    )

    def __repr__(self) -> str:
        return f"<OrderItem(order_id={self.order_id}, service={self.service_name}, qty={self.quantity})>"


# =============================================================================
# PAYMENT MODEL
# =============================================================================


class Payment(Base, UUIDMixin, TimestampMixin):
    """
    Transazione pagamento Stripe.

    Traccia:
    - Payment Intent ID di Stripe
    - Status pagamento
    - Importo e valuta
    - Metodo pagamento (card, sepa, etc.)
    - Metadata per reconciliation

    Webhook Events:
    - payment_intent.succeeded → status=SUCCEEDED
    - payment_intent.payment_failed → status=FAILED
    - charge.refunded → status=REFUNDED

    Note:
    - One-to-one con Order
    - Stripe webhook aggiorna status
    """

    __tablename__ = "payments"

    # -------------------------------------------------------------------------
    # Foreign Key
    # -------------------------------------------------------------------------

    order_id = Column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="FK a orders (one-to-one)",
    )

    # -------------------------------------------------------------------------
    # Stripe Data
    # -------------------------------------------------------------------------

    stripe_payment_intent_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Stripe Payment Intent ID (pi_...)",
    )

    # -------------------------------------------------------------------------
    # Payment Info
    # -------------------------------------------------------------------------

    amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Importo pagamento in EUR",
    )

    currency = Column(
        String(3),
        nullable=False,
        default="EUR",
        comment="Valuta (sempre EUR)",
    )

    status = Column(
        Enum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.PENDING,
        index=True,
        comment="Status pagamento (da Stripe webhook)",
    )

    payment_method_type = Column(
        String(50),
        nullable=True,
        comment="Tipo metodo pagamento (card, sepa_debit, etc.)",
    )

    # -------------------------------------------------------------------------
    # Error Handling
    # -------------------------------------------------------------------------

    failure_reason = Column(
        Text,
        nullable=True,
        comment="Motivo fallimento pagamento (da Stripe)",
    )

    # -------------------------------------------------------------------------
    # Metadata
    # -------------------------------------------------------------------------

    payment_metadata = Column(
        JSONB,
        nullable=True,
        comment="Metadata Stripe e custom",
    )

    # -------------------------------------------------------------------------
    # Timestamps
    # -------------------------------------------------------------------------

    processed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp elaborazione pagamento",
    )

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------

    order = relationship("Order", back_populates="payment")

    # -------------------------------------------------------------------------
    # Indexes
    # -------------------------------------------------------------------------

    __table_args__ = (
        Index("ix_payments_stripe_id", "stripe_payment_intent_id"),
        Index("ix_payments_status_processed", "status", "processed_at"),
        {"comment": "Transazioni pagamento Stripe"},
    )

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, order_id={self.order_id}, status={self.status}, amount=€{self.amount})>"


# =============================================================================
# LOGGING
# =============================================================================

logger.debug("Order models loaded: QuoteRequest, Order, OrderItem, Payment")
