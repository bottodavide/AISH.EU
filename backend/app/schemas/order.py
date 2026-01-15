"""
Modulo: order.py
Descrizione: Pydantic schemas per ordini, preventivi e pagamenti
Autore: Claude per Davide
Data: 2026-01-15

Schemas inclusi:
- QuoteRequest: Richieste preventivo
- Order: Ordini
- OrderItem: Righe ordine
- Payment: Pagamenti
- Cart: Gestione carrello
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.order import OrderStatus, PaymentStatus, QuoteRequestStatus
from app.schemas.base import UUIDTimestampSchema


# =============================================================================
# QUOTE REQUEST SCHEMAS
# =============================================================================


class QuoteRequestCreate(BaseModel):
    """Schema per creare richiesta preventivo"""

    model_config = ConfigDict(from_attributes=True)

    service_id: UUID = Field(description="ID servizio per cui richiedere preventivo")
    contact_name: str = Field(min_length=2, max_length=255, description="Nome contatto")
    contact_email: EmailStr = Field(description="Email contatto")
    contact_phone: Optional[str] = Field(None, max_length=20, description="Telefono contatto")
    company_name: Optional[str] = Field(None, max_length=255, description="Nome azienda")
    message: Optional[str] = Field(None, max_length=2000, description="Messaggio con dettagli esigenze")
    custom_fields: Optional[dict] = Field(None, description="Campi custom questionario")


class QuoteRequestUpdate(BaseModel):
    """Schema per aggiornare richiesta preventivo (admin only)"""

    model_config = ConfigDict(from_attributes=True)

    status: Optional[QuoteRequestStatus] = Field(None, description="Nuovo status")
    quoted_amount: Optional[Decimal] = Field(None, ge=0, description="Importo preventivo (EUR)")
    notes: Optional[str] = Field(None, description="Note interne")


class QuoteRequestResponse(UUIDTimestampSchema):
    """Schema response richiesta preventivo"""

    request_number: str = Field(description="Numero richiesta (QR-2026-00001)")
    user_id: Optional[UUID] = Field(None, description="ID utente (se registrato)")
    service_id: UUID = Field(description="ID servizio")
    contact_name: str = Field(description="Nome contatto")
    contact_email: str = Field(description="Email contatto")
    contact_phone: Optional[str] = Field(None, description="Telefono contatto")
    company_name: Optional[str] = Field(None, description="Nome azienda")
    message: Optional[str] = Field(None, description="Messaggio cliente")
    custom_fields: Optional[dict] = Field(None, description="Campi custom")
    status: QuoteRequestStatus = Field(description="Status richiesta")
    quoted_amount: Optional[Decimal] = Field(None, description="Importo preventivo")
    quoted_at: Optional[datetime] = Field(None, description="Data invio preventivo")


# =============================================================================
# ORDER ITEM SCHEMAS
# =============================================================================


class OrderItemCreate(BaseModel):
    """Schema per creare riga ordine"""

    model_config = ConfigDict(from_attributes=True)

    service_id: UUID = Field(description="ID servizio da acquistare")
    quantity: int = Field(default=1, ge=1, le=100, description="Quantità (default 1)")
    custom_price: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Prezzo custom (es: da preventivo, altrimenti usa prezzo servizio)"
    )


class OrderItemResponse(UUIDTimestampSchema):
    """Schema response riga ordine"""

    order_id: UUID = Field(description="ID ordine")
    service_id: Optional[UUID] = Field(None, description="ID servizio originale")
    service_name: str = Field(description="Nome servizio (snapshot)")
    description: Optional[str] = Field(None, description="Descrizione servizio")
    quantity: int = Field(description="Quantità")
    unit_price: Decimal = Field(description="Prezzo unitario (EUR)")
    tax_rate: Decimal = Field(description="Aliquota IVA %")
    total_price: Decimal = Field(description="Totale riga con IVA (EUR)")


# =============================================================================
# ORDER SCHEMAS
# =============================================================================


class OrderCreate(BaseModel):
    """
    Schema per creare ordine.

    Due modalità:
    1. Ordine da carrello: fornire lista items
    2. Ordine da preventivo: fornire quote_request_id
    """

    model_config = ConfigDict(from_attributes=True)

    items: Optional[list[OrderItemCreate]] = Field(
        None,
        min_length=1,
        description="Lista servizi da ordinare (non usare con quote_request_id)"
    )
    quote_request_id: Optional[UUID] = Field(
        None,
        description="ID preventivo accettato (non usare con items)"
    )
    notes: Optional[str] = Field(None, max_length=1000, description="Note aggiuntive")

    @field_validator("items", "quote_request_id")
    @classmethod
    def validate_order_source(cls, v, info):
        """Valida che sia fornito items O quote_request_id, non entrambi"""
        # Questo validator viene chiamato per entrambi i campi
        # La validazione completa viene fatta nel root validator
        return v

    def model_post_init(self, __context):
        """Valida che esattamente uno tra items e quote_request_id sia fornito"""
        has_items = self.items is not None and len(self.items) > 0
        has_quote = self.quote_request_id is not None

        if not has_items and not has_quote:
            raise ValueError("Fornire 'items' oppure 'quote_request_id'")

        if has_items and has_quote:
            raise ValueError("Fornire 'items' OPPURE 'quote_request_id', non entrambi")


class OrderUpdate(BaseModel):
    """Schema per aggiornare ordine (admin only)"""

    model_config = ConfigDict(from_attributes=True)

    status: Optional[OrderStatus] = Field(None, description="Nuovo status")
    notes: Optional[str] = Field(None, max_length=1000, description="Note aggiuntive")


class OrderResponse(UUIDTimestampSchema):
    """Schema response ordine completo"""

    order_number: str = Field(description="Numero ordine (ORD-2026-00001)")
    user_id: UUID = Field(description="ID utente")
    quote_request_id: Optional[UUID] = Field(None, description="ID preventivo (se da preventivo)")
    status: OrderStatus = Field(description="Status ordine")

    # Totali
    subtotal: Decimal = Field(description="Subtotale senza IVA (EUR)")
    tax_rate: Decimal = Field(description="Aliquota IVA %")
    tax_amount: Decimal = Field(description="Importo IVA (EUR)")
    total: Decimal = Field(description="Totale con IVA (EUR)")
    currency: str = Field(default="EUR", description="Valuta")

    # Dati fatturazione
    billing_data: dict = Field(description="Snapshot dati fatturazione")
    notes: Optional[str] = Field(None, description="Note")

    # Timestamps workflow
    paid_at: Optional[datetime] = Field(None, description="Data pagamento")
    completed_at: Optional[datetime] = Field(None, description="Data completamento")

    # Relationships
    items: list[OrderItemResponse] = Field(default_factory=list, description="Righe ordine")


class OrderListResponse(UUIDTimestampSchema):
    """Schema response per lista ordini (versione leggera)"""

    order_number: str = Field(description="Numero ordine")
    status: OrderStatus = Field(description="Status ordine")
    total: Decimal = Field(description="Totale ordine (EUR)")
    currency: str = Field(description="Valuta")
    paid_at: Optional[datetime] = Field(None, description="Data pagamento")
    items_count: Optional[int] = Field(None, description="Numero servizi nell'ordine")


# =============================================================================
# PAYMENT SCHEMAS
# =============================================================================


class PaymentIntentCreate(BaseModel):
    """Schema per creare Stripe Payment Intent"""

    model_config = ConfigDict(from_attributes=True)

    order_id: UUID = Field(description="ID ordine da pagare")
    return_url: Optional[str] = Field(
        None,
        description="URL di ritorno dopo pagamento (default: frontend checkout success)"
    )


class PaymentIntentResponse(BaseModel):
    """Schema response Payment Intent"""

    model_config = ConfigDict(from_attributes=True)

    client_secret: str = Field(description="Client secret per Stripe.js")
    payment_intent_id: str = Field(description="ID Payment Intent Stripe")
    amount: Decimal = Field(description="Importo (EUR)")
    currency: str = Field(description="Valuta")
    order_id: UUID = Field(description="ID ordine")


class PaymentResponse(UUIDTimestampSchema):
    """Schema response pagamento"""

    order_id: UUID = Field(description="ID ordine")
    stripe_payment_intent_id: str = Field(description="ID Payment Intent Stripe")
    amount: Decimal = Field(description="Importo (EUR)")
    currency: str = Field(description="Valuta")
    status: PaymentStatus = Field(description="Status pagamento")
    payment_method_type: Optional[str] = Field(None, description="Tipo metodo pagamento")
    failure_reason: Optional[str] = Field(None, description="Motivo fallimento")
    processed_at: Optional[datetime] = Field(None, description="Data elaborazione")


# =============================================================================
# CART SCHEMAS (Session-based)
# =============================================================================


class CartItem(BaseModel):
    """Item nel carrello (sessione)"""

    model_config = ConfigDict(from_attributes=True)

    service_id: UUID = Field(description="ID servizio")
    quantity: int = Field(default=1, ge=1, le=100, description="Quantità")
    custom_price: Optional[Decimal] = Field(None, ge=0, description="Prezzo custom (opzionale)")


class CartResponse(BaseModel):
    """Response carrello completo"""

    model_config = ConfigDict(from_attributes=True)

    items: list[CartItem] = Field(default_factory=list, description="Items nel carrello")
    subtotal: Decimal = Field(default=Decimal("0.00"), description="Subtotale senza IVA")
    tax_rate: Decimal = Field(default=Decimal("22.00"), description="Aliquota IVA %")
    tax_amount: Decimal = Field(default=Decimal("0.00"), description="Importo IVA")
    total: Decimal = Field(default=Decimal("0.00"), description="Totale con IVA")
    items_count: int = Field(default=0, description="Numero totale items")


class CartAddItem(BaseModel):
    """Schema per aggiungere item al carrello"""

    model_config = ConfigDict(from_attributes=True)

    service_id: UUID = Field(description="ID servizio da aggiungere")
    quantity: int = Field(default=1, ge=1, le=100, description="Quantità")
    custom_price: Optional[Decimal] = Field(None, ge=0, description="Prezzo custom")


class CartUpdateItem(BaseModel):
    """Schema per aggiornare quantità item nel carrello"""

    model_config = ConfigDict(from_attributes=True)

    quantity: int = Field(ge=0, le=100, description="Nuova quantità (0 = rimuovi)")


# =============================================================================
# FILTERS
# =============================================================================


class OrderFilters(BaseModel):
    """Filtri per ricerca ordini"""

    model_config = ConfigDict(from_attributes=True)

    status: Optional[OrderStatus] = Field(None, description="Filtra per status")
    user_id: Optional[UUID] = Field(None, description="Filtra per utente (admin only)")
    from_date: Optional[datetime] = Field(None, description="Data inizio (created_at)")
    to_date: Optional[datetime] = Field(None, description="Data fine (created_at)")
    min_total: Optional[Decimal] = Field(None, ge=0, description="Importo minimo")
    max_total: Optional[Decimal] = Field(None, ge=0, description="Importo massimo")

    skip: int = Field(default=0, ge=0, description="Paginazione: skip")
    limit: int = Field(default=50, ge=1, le=100, description="Paginazione: limit")
    sort_by: str = Field(default="created_at", description="Campo ordinamento")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Direzione ordinamento")


class QuoteRequestFilters(BaseModel):
    """Filtri per ricerca richieste preventivo"""

    model_config = ConfigDict(from_attributes=True)

    status: Optional[QuoteRequestStatus] = Field(None, description="Filtra per status")
    service_id: Optional[UUID] = Field(None, description="Filtra per servizio")
    from_date: Optional[datetime] = Field(None, description="Data inizio")
    to_date: Optional[datetime] = Field(None, description="Data fine")

    skip: int = Field(default=0, ge=0, description="Paginazione: skip")
    limit: int = Field(default=50, ge=1, le=100, description="Paginazione: limit")
    sort_by: str = Field(default="created_at", description="Campo ordinamento")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="Direzione ordinamento")
