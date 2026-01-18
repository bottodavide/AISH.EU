"""
Modulo: factories.py
Descrizione: Factory functions per creare oggetti di test
Autore: Claude per Davide
Data: 2026-01-18

Factory functions disponibili:
- UserFactory: Crea user con profile
- ServiceFactory: Crea servizio
- OrderFactory: Crea order con items
- OrderItemFactory: Crea singolo order item
- PaymentFactory: Crea payment per order
- InvoiceFactory: Crea invoice da order
- QuoteRequestFactory: Crea quote request
"""

import logging
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.order import (
    Order,
    OrderItem,
    OrderStatus,
    Payment,
    PaymentStatus,
    QuoteRequest,
    QuoteRequestStatus,
)
from app.models.user import User, UserProfile, UserRole

logger = logging.getLogger(__name__)

# =============================================================================
# USER FACTORIES
# =============================================================================


class UserFactory:
    """Factory per creare User e UserProfile per test."""

    @staticmethod
    async def create(
        db: AsyncSession,
        email: Optional[str] = None,
        password: str = "TestPassword123!",
        role: UserRole = UserRole.CUSTOMER,
        is_active: bool = True,
        is_email_verified: bool = True,
        mfa_enabled: bool = False,
        with_profile: bool = True,
    ) -> User:
        """
        Crea user per test.

        Args:
            db: AsyncSession database
            email: Email user (default: random)
            password: Password in chiaro (default: TestPassword123!)
            role: UserRole (default: CUSTOMER)
            is_active: Account attivo (default: True)
            is_email_verified: Email verificata (default: True)
            mfa_enabled: MFA abilitato (default: False)
            with_profile: Crea anche UserProfile (default: True)

        Returns:
            User: User creato
        """
        if email is None:
            email = f"test_{uuid.uuid4().hex[:8]}@example.com"

        user = User(
            id=uuid.uuid4(),
            email=email,
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
            is_email_verified=is_email_verified,
            mfa_enabled=mfa_enabled,
        )

        db.add(user)
        await db.flush()

        if with_profile:
            profile = UserProfile(
                user_id=user.id,
                first_name="Test",
                last_name="User",
                company_name="Test Company",
                vat_number="IT12345678901",
                fiscal_code="TESTFC00A01H501Z",
                address_street="Via Test 123",
                address_city="Rome",
                address_province="RM",
                address_postal_code="00100",
                address_country="IT",
                phone="+39 06 12345678",
            )
            db.add(profile)

        await db.commit()
        await db.refresh(user)

        logger.debug(f"User created: {user.email} (role={user.role})")
        return user


# =============================================================================
# SERVICE FACTORIES
# =============================================================================


class ServiceFactory:
    """Factory per creare Service per test."""

    @staticmethod
    async def create(
        db: AsyncSession,
        name: Optional[str] = None,
        slug: Optional[str] = None,
        category: str = "consulting",
        base_price: Decimal = Decimal("1000.00"),
        is_active: bool = True,
    ):
        """
        Crea service per test.

        Args:
            db: AsyncSession database
            name: Nome servizio (default: random)
            slug: Slug URL (default: from name)
            category: Categoria (default: consulting)
            base_price: Prezzo base in EUR (default: 1000.00)
            is_active: Servizio attivo (default: True)

        Returns:
            Service: Service creato

        Note:
            Importa Service localmente per evitare circular import
        """
        from app.models.service import Service, ServiceType

        if name is None:
            name = f"Test Service {uuid.uuid4().hex[:8]}"

        if slug is None:
            slug = name.lower().replace(" ", "-")

        service = Service(
            id=uuid.uuid4(),
            name=name,
            slug=slug,
            category=category,
            service_type=ServiceType.FIXED_PRICE,
            short_description="Test service description",
            base_price=base_price,
            is_active=is_active,
        )

        db.add(service)
        await db.commit()
        await db.refresh(service)

        logger.debug(f"Service created: {service.name} (price=€{service.base_price})")
        return service


# =============================================================================
# ORDER FACTORIES
# =============================================================================


class OrderItemFactory:
    """Factory per creare OrderItem per test."""

    @staticmethod
    async def create(
        db: AsyncSession,
        order_id: uuid.UUID,
        service_id: Optional[uuid.UUID] = None,
        service_name: str = "Test Service",
        quantity: int = 1,
        unit_price: Decimal = Decimal("1000.00"),
        tax_rate: Decimal = Decimal("22.00"),
    ) -> OrderItem:
        """
        Crea order item per test.

        Args:
            db: AsyncSession database
            order_id: UUID order parent
            service_id: UUID servizio (opzionale)
            service_name: Nome servizio
            quantity: Quantità (default: 1)
            unit_price: Prezzo unitario (default: 1000.00)
            tax_rate: Aliquota IVA % (default: 22.00)

        Returns:
            OrderItem: Item creato
        """
        # Calcola total_price (unit_price * quantity + IVA)
        subtotal = unit_price * quantity
        tax_amount = subtotal * (tax_rate / 100)
        total_price = subtotal + tax_amount

        item = OrderItem(
            id=uuid.uuid4(),
            order_id=order_id,
            service_id=service_id,
            service_name=service_name,
            description=f"Description for {service_name}",
            quantity=quantity,
            unit_price=unit_price,
            tax_rate=tax_rate,
            total_price=total_price,
        )

        db.add(item)
        await db.flush()

        logger.debug(
            f"OrderItem created: {item.service_name} x{item.quantity} = €{item.total_price}"
        )
        return item


class OrderFactory:
    """Factory per creare Order con items per test."""

    @staticmethod
    async def create(
        db: AsyncSession,
        user_id: uuid.UUID,
        status: OrderStatus = OrderStatus.PENDING,
        num_items: int = 1,
        base_price_per_item: Decimal = Decimal("1000.00"),
        tax_rate: Decimal = Decimal("22.00"),
        with_payment: bool = False,
    ) -> Order:
        """
        Crea order completo con items per test.

        Args:
            db: AsyncSession database
            user_id: UUID user proprietario
            status: OrderStatus (default: PENDING)
            num_items: Numero di items da creare (default: 1)
            base_price_per_item: Prezzo base per item (default: 1000.00)
            tax_rate: Aliquota IVA % (default: 22.00)
            with_payment: Crea anche Payment (default: False)

        Returns:
            Order: Order creato con items
        """
        # Genera numero ordine unico
        order_number = f"ORD-TEST-{uuid.uuid4().hex[:8].upper()}"

        # Calcola totali
        subtotal = base_price_per_item * num_items
        tax_amount = subtotal * (tax_rate / 100)
        total = subtotal + tax_amount

        # Crea order
        order = Order(
            id=uuid.uuid4(),
            order_number=order_number,
            user_id=user_id,
            status=status,
            subtotal=subtotal,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            total=total,
            currency="EUR",
            billing_data={
                "company_name": "Test Company",
                "vat_number": "IT12345678901",
                "address": "Via Test 123, 00100 Rome, IT",
            },
        )

        db.add(order)
        await db.flush()

        # Crea items
        for i in range(num_items):
            await OrderItemFactory.create(
                db=db,
                order_id=order.id,
                service_name=f"Test Service {i+1}",
                quantity=1,
                unit_price=base_price_per_item,
                tax_rate=tax_rate,
            )

        # Crea payment se richiesto
        if with_payment:
            await PaymentFactory.create(
                db=db,
                order_id=order.id,
                amount=total,
            )

        await db.commit()
        await db.refresh(order)

        logger.debug(
            f"Order created: {order.order_number} (items={num_items}, total=€{order.total})"
        )
        return order


# =============================================================================
# PAYMENT FACTORIES
# =============================================================================


class PaymentFactory:
    """Factory per creare Payment per test."""

    @staticmethod
    async def create(
        db: AsyncSession,
        order_id: uuid.UUID,
        amount: Optional[Decimal] = None,
        status: PaymentStatus = PaymentStatus.PENDING,
        stripe_payment_intent_id: Optional[str] = None,
        stripe_client_secret: Optional[str] = None,
    ) -> Payment:
        """
        Crea payment per test.

        Args:
            db: AsyncSession database
            order_id: UUID order associato
            amount: Importo in EUR (default: da order)
            status: PaymentStatus (default: PENDING)
            stripe_payment_intent_id: Stripe PI ID (default: random)
            stripe_client_secret: Stripe client secret (default: random)

        Returns:
            Payment: Payment creato
        """
        if stripe_payment_intent_id is None:
            stripe_payment_intent_id = f"pi_test_{uuid.uuid4().hex[:16]}"

        if stripe_client_secret is None:
            stripe_client_secret = f"{stripe_payment_intent_id}_secret_{uuid.uuid4().hex[:8]}"

        # Se amount non specificato, recupera da order
        if amount is None:
            from sqlalchemy import select
            result = await db.execute(select(Order).where(Order.id == order_id))
            order = result.scalar_one()
            amount = order.total

        payment = Payment(
            id=uuid.uuid4(),
            order_id=order_id,
            stripe_payment_intent_id=stripe_payment_intent_id,
            stripe_client_secret=stripe_client_secret,
            amount=amount,
            currency="EUR",
            status=status,
            payment_method_type="card",
        )

        db.add(payment)
        await db.commit()
        await db.refresh(payment)

        logger.debug(
            f"Payment created: {payment.stripe_payment_intent_id} (status={payment.status}, amount=€{payment.amount})"
        )
        return payment


# =============================================================================
# INVOICE FACTORIES
# =============================================================================


class InvoiceFactory:
    """Factory per creare Invoice per test."""

    @staticmethod
    async def create(
        db: AsyncSession,
        order_id: uuid.UUID,
        invoice_number: Optional[str] = None,
        issue_date: Optional[datetime] = None,
    ):
        """
        Crea invoice da order per test.

        Args:
            db: AsyncSession database
            order_id: UUID order associato
            invoice_number: Numero fattura (default: random)
            issue_date: Data emissione (default: oggi)

        Returns:
            Invoice: Invoice creato

        Note:
            Importa Invoice localmente per evitare circular import
        """
        from app.models.invoice import Invoice, InvoiceStatus

        if invoice_number is None:
            invoice_number = f"INV-TEST-{uuid.uuid4().hex[:8].upper()}"

        if issue_date is None:
            issue_date = datetime.utcnow()

        # Recupera order per dati
        from sqlalchemy import select
        result = await db.execute(select(Order).where(Order.id == order_id))
        order = result.scalar_one()

        invoice = Invoice(
            id=uuid.uuid4(),
            invoice_number=invoice_number,
            order_id=order_id,
            user_id=order.user_id,
            issue_date=issue_date,
            due_date=issue_date + timedelta(days=30),
            status=InvoiceStatus.DRAFT,
            subtotal=order.subtotal,
            tax_amount=order.tax_amount,
            total=order.total,
            currency="EUR",
            billing_data=order.billing_data,
        )

        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)

        logger.debug(f"Invoice created: {invoice.invoice_number} (total=€{invoice.total})")
        return invoice


# =============================================================================
# QUOTE REQUEST FACTORIES
# =============================================================================


class QuoteRequestFactory:
    """Factory per creare QuoteRequest per test."""

    @staticmethod
    async def create(
        db: AsyncSession,
        service_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None,
        contact_email: Optional[str] = None,
        status: QuoteRequestStatus = QuoteRequestStatus.NEW,
    ) -> QuoteRequest:
        """
        Crea quote request per test.

        Args:
            db: AsyncSession database
            service_id: UUID servizio
            user_id: UUID user (opzionale per guest)
            contact_email: Email contatto (default: random)
            status: QuoteRequestStatus (default: NEW)

        Returns:
            QuoteRequest: Quote request creato
        """
        if contact_email is None:
            contact_email = f"quote_{uuid.uuid4().hex[:8]}@example.com"

        request_number = f"QR-TEST-{uuid.uuid4().hex[:8].upper()}"

        quote = QuoteRequest(
            id=uuid.uuid4(),
            request_number=request_number,
            user_id=user_id,
            service_id=service_id,
            contact_name="Test Contact",
            contact_email=contact_email,
            contact_phone="+39 06 12345678",
            company_name="Test Company",
            message="This is a test quote request message.",
            status=status,
        )

        db.add(quote)
        await db.commit()
        await db.refresh(quote)

        logger.debug(f"QuoteRequest created: {quote.request_number} (status={quote.status})")
        return quote


logger.info("Test factories loaded successfully")
