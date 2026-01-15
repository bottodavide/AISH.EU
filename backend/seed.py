"""
Modulo: seed.py
Descrizione: Script per popolare database con dati di esempio per testing
Autore: Claude per Davide
Data: 2026-01-15

Uso:
    python seed.py

Questo script crea:
- Utenti di test con tutti i ruoli (super_admin, admin, customer, etc.)
- Servizi di esempio per ogni categoria
- Ordini e quote di test
- Blog posts e pagine CMS
- Newsletter subscribers
- Support tickets
- Site settings
- Etc.

IMPORTANTE: Questo script è solo per ambiente di sviluppo/test!
NON eseguire in produzione!
"""

import asyncio
import logging
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import List

# Setup path per import
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from passlib.hash import argon2

from app.core.config import settings
from app.models.base import Base
from app.models.user import User, UserProfile, UserRole
from app.models.service import Service, ServiceCategory, ServiceContent, ServiceFAQ, PricingType
from app.models.order import Order, OrderItem, OrderStatus, QuoteRequest, QuoteRequestStatus, Payment, PaymentStatus
from app.models.invoice import Invoice, InvoiceLine, SDIStatus
from app.models.cms import Page, BlogPost, BlogCategory, BlogTag, BlogPostTag
from app.models.newsletter import NewsletterSubscriber, SubscriberStatus, EmailCampaign, CampaignStatus
from app.models.knowledge_base import KnowledgeBaseDocument, KnowledgeTopic
from app.models.chat import ChatConversation, ChatMessage, MessageRole, UserFeedback
from app.models.support import SupportTicket, TicketStatus, TicketPriority, TicketMessage
from app.models.notification import Notification
from app.models.audit import AuditLog, AuditAction, SystemLog, LogLevel
from app.models.settings import SiteSetting

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_db_engine():
    """
    Crea engine SQLAlchemy per connessione database.

    Returns:
        Engine: Engine SQLAlchemy
    """
    logger.info(f"Connecting to database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'}")
    engine = create_engine(settings.DATABASE_URL, echo=False)
    return engine


def seed_users(session: Session) -> dict:
    """
    Crea utenti di test con tutti i ruoli.

    Args:
        session: SQLAlchemy session

    Returns:
        dict: Dizionario con utenti creati per role
    """
    logger.info("=" * 80)
    logger.info("SEEDING USERS")
    logger.info("=" * 80)

    users = {}

    # Password hash per tutti gli utenti test: "Test123!"
    password_hash = argon2.hash("Test123!")

    # 1. Super Admin
    logger.info("Creating super admin user...")
    super_admin = User(
        email="admin@aistrategyhub.eu",
        password_hash=password_hash,
        role=UserRole.SUPER_ADMIN,
        is_active=True,
        is_email_verified=True,
    )
    session.add(super_admin)
    session.flush()

    super_admin_profile = UserProfile(
        user_id=super_admin.id,
        first_name="Davide",
        last_name="Botto",
        company_name="AI Strategy Hub",
        phone="+39 123 456 7890",
        vat_number="IT12345678901",
        billing_address={
            "street": "Via Roma 1",
            "city": "Milano",
            "province": "MI",
            "zip": "20100",
            "country": "IT"
        },
    )
    session.add(super_admin_profile)
    users['super_admin'] = super_admin
    logger.info(f"  ✓ Super Admin: {super_admin.email}")

    # 2. Admin
    logger.info("Creating admin user...")
    admin = User(
        email="editor@aistrategyhub.eu",
        password_hash=password_hash,
        role=UserRole.ADMIN,
        is_active=True,
        is_email_verified=True,
    )
    session.add(admin)
    session.flush()

    admin_profile = UserProfile(
        user_id=admin.id,
        first_name="Marco",
        last_name="Rossi",
        phone="+39 321 654 9870",
    )
    session.add(admin_profile)
    users['admin'] = admin
    logger.info(f"  ✓ Admin: {admin.email}")

    # 3. Support
    logger.info("Creating support user...")
    support = User(
        email="support@aistrategyhub.eu",
        password_hash=password_hash,
        role=UserRole.SUPPORT,
        is_active=True,
        is_email_verified=True,
    )
    session.add(support)
    session.flush()

    support_profile = UserProfile(
        user_id=support.id,
        first_name="Laura",
        last_name="Bianchi",
    )
    session.add(support_profile)
    users['support'] = support
    logger.info(f"  ✓ Support: {support.email}")

    # 4. Customer 1 (Business)
    logger.info("Creating customer users...")
    customer1 = User(
        email="mario.verdi@azienda.it",
        password_hash=password_hash,
        role=UserRole.CUSTOMER,
        is_active=True,
        is_email_verified=True,
    )
    session.add(customer1)
    session.flush()

    customer1_profile = UserProfile(
        user_id=customer1.id,
        first_name="Mario",
        last_name="Verdi",
        company_name="Verdi S.r.l.",
        phone="+39 345 678 9012",
        vat_number="IT98765432109",
        fiscal_code="VRDMRA80A01H501Z",
        sdi_code="ABCDEFG",
        billing_address={
            "street": "Corso Italia 45",
            "city": "Roma",
            "province": "RM",
            "zip": "00100",
            "country": "IT"
        },
    )
    session.add(customer1_profile)
    users['customer1'] = customer1
    logger.info(f"  ✓ Customer 1: {customer1.email}")

    # 5. Customer 2 (Individual)
    customer2 = User(
        email="giulia.neri@email.it",
        password_hash=password_hash,
        role=UserRole.CUSTOMER,
        is_active=True,
        is_email_verified=True,
    )
    session.add(customer2)
    session.flush()

    customer2_profile = UserProfile(
        user_id=customer2.id,
        first_name="Giulia",
        last_name="Neri",
        phone="+39 347 890 1234",
        fiscal_code="NREGLI85M50F205X",
        pec_email="giulia.neri@pec.it",
        billing_address={
            "street": "Via Garibaldi 12",
            "city": "Torino",
            "province": "TO",
            "zip": "10100",
            "country": "IT"
        },
    )
    session.add(customer2_profile)
    users['customer2'] = customer2
    logger.info(f"  ✓ Customer 2: {customer2.email}")

    # 6. Customer 3 (Not verified)
    customer3 = User(
        email="franco.blu@test.it",
        password_hash=password_hash,
        role=UserRole.CUSTOMER,
        is_active=True,
        is_email_verified=False,
        email_verification_token="test_token_123",
    )
    session.add(customer3)
    session.flush()

    customer3_profile = UserProfile(
        user_id=customer3.id,
        first_name="Franco",
        last_name="Blu",
    )
    session.add(customer3_profile)
    users['customer3'] = customer3
    logger.info(f"  ✓ Customer 3 (unverified): {customer3.email}")

    session.commit()
    logger.info(f"✓ Created {len(users)} users")
    return users


def seed_services(session: Session, users: dict) -> List[Service]:
    """
    Crea servizi di esempio per ogni categoria.

    Args:
        session: SQLAlchemy session
        users: Dizionario utenti creati

    Returns:
        List[Service]: Lista servizi creati
    """
    logger.info("=" * 80)
    logger.info("SEEDING SERVICES")
    logger.info("=" * 80)

    services = []

    # 1. AI Compliance
    logger.info("Creating AI compliance services...")
    ai_service = Service(
        slug="consulenza-ai-act-compliance",
        name="Consulenza AI Act Compliance",
        short_description="Supporto completo per conformità al Regolamento UE sull'Intelligenza Artificiale",
        category=ServiceCategory.AI_COMPLIANCE,
        pricing_type=PricingType.CUSTOM,
        base_price=None,
        currency="EUR",
        is_published=True,
        display_order=1,
        seo_title="Consulenza AI Act | Conformità Regolamento UE IA",
        seo_description="Servizio di consulenza professionale per la conformità al nuovo Regolamento UE sull'Intelligenza Artificiale (AI Act). Gap analysis, risk assessment e implementazione.",
    )
    session.add(ai_service)
    session.flush()

    # Aggiungi contenuti
    ai_content1 = ServiceContent(
        service_id=ai_service.id,
        section_type="description",
        title="Descrizione del servizio",
        content="""
Il nostro servizio di consulenza AI Act ti aiuta a navigare le complessità del nuovo Regolamento Europeo sull'Intelligenza Artificiale.

Offriamo un approccio completo che include:
- Gap analysis iniziale dei tuoi sistemi AI
- Classificazione dei sistemi secondo i livelli di rischio
- Roadmap di conformità personalizzata
- Supporto nell'implementazione dei requisiti
- Documentazione tecnica e compliance
- Audit e certificazione
        """,
        display_order=1,
    )
    session.add(ai_content1)

    ai_content2 = ServiceContent(
        service_id=ai_service.id,
        section_type="benefits",
        title="Benefici",
        content="""
- Conformità garantita al Regolamento UE
- Riduzione del rischio di sanzioni (fino a €35M o 7% fatturato globale)
- Maggiore fiducia da parte di clienti e stakeholder
- Competitive advantage nel mercato
- Processo strutturato e documentato
        """,
        display_order=2,
    )
    session.add(ai_content2)

    ai_faq1 = ServiceFAQ(
        service_id=ai_service.id,
        question="Quanto tempo richiede il processo di compliance?",
        answer="Il tempo varia in base alla complessità dei sistemi AI. Generalmente da 3 a 6 mesi per una compliance completa.",
        display_order=1,
    )
    session.add(ai_faq1)

    services.append(ai_service)
    logger.info(f"  ✓ Service: {ai_service.title}")

    # 2. Cybersecurity NIS2
    logger.info("Creating cybersecurity NIS2 services...")
    nis2_service = Service(
        slug="consulenza-nis2-cybersecurity",
        name="Consulenza NIS2 Cybersecurity",
        short_description="Conformità alla Direttiva NIS2 per operatori di servizi essenziali",
        category=ServiceCategory.CYBERSECURITY_NIS2,
        pricing_type=PricingType.CUSTOM,
        base_price=None,
        currency="EUR",
        is_published=True,
        display_order=2,
        seo_title="Consulenza NIS2 | Cybersecurity Compliance",
        seo_description="Servizi di consulenza per la conformità alla Direttiva NIS2. Risk assessment, implementazione misure di sicurezza e incident response.",
    )
    session.add(nis2_service)
    session.flush()

    nis2_content = ServiceContent(
        service_id=nis2_service.id,
        section_type="description",
        content="""
La Direttiva NIS2 impone nuovi obblighi di cybersecurity per operatori essenziali e importanti.

Il nostro servizio include:
- Assessment del perimetro di applicazione
- Gap analysis rispetto ai requisiti NIS2
- Implementazione misure tecniche e organizzative
- Procedure di incident response
- Formazione del personale
- Supporto nelle comunicazioni con CSIRT e autorità
        """,
        display_order=1,
    )
    session.add(nis2_content)

    services.append(nis2_service)
    logger.info(f"  ✓ Service: {nis2_service.title}")

    # 3. Toolkit & Formazione
    logger.info("Creating toolkit and training services...")
    toolkit_service = Service(
        slug="toolkit-gdpr-cybersecurity",
        name="Toolkit GDPR & Cybersecurity",
        short_description="Documenti e template pronti all'uso per compliance",
        category=ServiceCategory.TOOLKIT_FORMAZIONE,
        pricing_type=PricingType.FIXED,
        base_price=Decimal("497.00"),
        currency="EUR",
        is_published=True,
        display_order=3,
        seo_title="Toolkit GDPR | Template e Documenti Compliance",
        seo_description="Toolkit completo con template, checklist e documenti per GDPR e cybersecurity compliance. Immediatamente utilizzabili.",
    )
    session.add(toolkit_service)
    session.flush()

    toolkit_content = ServiceContent(
        service_id=toolkit_service.id,
        section_type="description",
        content="""
Toolkit completo con oltre 50 documenti pronti all'uso:

- Privacy Policy e Cookie Policy
- Informative GDPR
- Registro dei trattamenti
- DPIA template
- Policy di sicurezza IT
- Procedure incident response
- Checklist compliance
- Contract templates (DPA, Sub-processor agreement)

Tutti i documenti sono personalizzabili e conformi alle normative vigenti.
        """,
        display_order=1,
    )
    session.add(toolkit_content)

    services.append(toolkit_service)
    logger.info(f"  ✓ Service: {toolkit_service.title}")

    # 4. Servizio con pricing orario
    logger.info("Creating hourly consulting service...")
    hourly_service = Service(
        slug="consulenza-oraria-cybersecurity",
        name="Consulenza Oraria Cybersecurity",
        short_description="Supporto flessibile on-demand",
        category=ServiceCategory.CYBERSECURITY_NIS2,
        pricing_type=PricingType.HOURLY,
        base_price=Decimal("150.00"),
        currency="EUR",
        is_published=True,
        display_order=4,
    )
    session.add(hourly_service)
    services.append(hourly_service)
    logger.info(f"  ✓ Service: {hourly_service.title}")

    session.commit()
    logger.info(f"✓ Created {len(services)} services")
    return services


def seed_orders(session: Session, users: dict, services: List[Service]) -> List[Order]:
    """
    Crea ordini di esempio con diversi stati.

    Args:
        session: SQLAlchemy session
        users: Dizionario utenti
        services: Lista servizi

    Returns:
        List[Order]: Lista ordini creati
    """
    logger.info("=" * 80)
    logger.info("SEEDING ORDERS")
    logger.info("=" * 80)

    orders = []

    # 1. Ordine completato per customer1
    logger.info("Creating completed order...")
    order1 = Order(
        order_number="ORD-2026-00001",
        user_id=users['customer1'].id,
        status=OrderStatus.COMPLETED,
        subtotal=Decimal("497.00"),
        tax_rate=Decimal("22.00"),
        tax_amount=Decimal("109.34"),
        total=Decimal("606.34"),
        currency="EUR",
        billing_data={
            "company_name": "Verdi S.r.l.",
            "vat_number": "IT98765432109",
            "address": "Corso Italia 45, 00100 Roma (RM)"
        },
        completed_at=datetime.now() - timedelta(days=5),
    )
    session.add(order1)
    session.flush()

    order1_item = OrderItem(
        order_id=order1.id,
        service_id=services[2].id,  # Toolkit
        service_snapshot={
            "title": services[2].title,
            "pricing_type": "fixed",
            "base_price": "497.00"
        },
        quantity=1,
        unit_price=Decimal("497.00"),
        subtotal=Decimal("497.00"),
        tax_rate=Decimal("22.00"),
        tax_amount=Decimal("109.34"),
        total=Decimal("606.34"),
    )
    session.add(order1_item)

    # Payment
    payment1 = Payment(
        order_id=order1.id,
        amount=Decimal("606.34"),
        currency="EUR",
        payment_method_type="card",
        status=PaymentStatus.SUCCEEDED,
        stripe_payment_intent_id="pi_test_123456",
        paid_at=datetime.now() - timedelta(days=5),
    )
    session.add(payment1)

    orders.append(order1)
    logger.info(f"  ✓ Order {order1.order_number}: €{order1.total} - {order1.status.value}")

    # 2. Ordine in attesa di pagamento per customer2
    logger.info("Creating pending payment order...")
    order2 = Order(
        order_number="ORD-2026-00002",
        user_id=users['customer2'].id,
        status=OrderStatus.AWAITING_PAYMENT,
        subtotal=Decimal("1500.00"),
        tax_rate=Decimal("22.00"),
        tax_amount=Decimal("330.00"),
        total=Decimal("1830.00"),
        currency="EUR",
        billing_data={
            "name": "Giulia Neri",
            "tax_code": "NREGLI85M50F205X",
            "address": "Via Garibaldi 12, 10100 Torino (TO)"
        },
    )
    session.add(order2)
    session.flush()

    order2_item = OrderItem(
        order_id=order2.id,
        service_id=services[3].id,  # Hourly consulting
        service_snapshot={
            "title": services[3].title,
            "pricing_type": "hourly",
            "base_price": "150.00"
        },
        quantity=10,  # 10 ore
        unit_price=Decimal("150.00"),
        subtotal=Decimal("1500.00"),
        tax_rate=Decimal("22.00"),
        tax_amount=Decimal("330.00"),
        total=Decimal("1830.00"),
    )
    session.add(order2_item)

    payment2 = Payment(
        order_id=order2.id,
        amount=Decimal("1830.00"),
        currency="EUR",
        payment_method_type="card",
        status=PaymentStatus.PENDING,
    )
    session.add(payment2)

    orders.append(order2)
    logger.info(f"  ✓ Order {order2.order_number}: €{order2.total} - {order2.status.value}")

    # 3. Quote request
    logger.info("Creating quote request...")
    quote1 = QuoteRequest(
        request_number="QUO-2026-00001",
        user_id=users['customer1'].id,
        service_id=services[0].id,  # AI Act Compliance
        message="Abbiamo sviluppato un sistema di raccomandazione basato su ML e vorremmo una consulenza per la conformità AI Act.",
        requirements={
            "company_size": "50-100 dipendenti",
            "ai_systems": 2,
            "timeline": "3 mesi"
        },
        status=QuoteRequestStatus.QUOTED,
        admin_notes="Cliente interessato, follow-up previsto la prossima settimana",
        quoted_price=Decimal("8500.00"),
        quote_sent_at=datetime.now() - timedelta(days=2),
        quote_expires_at=datetime.now() + timedelta(days=28),
    )
    session.add(quote1)
    logger.info(f"  ✓ Quote {quote1.request_number}: €{quote1.quoted_price} - {quote1.status.value}")

    session.commit()
    logger.info(f"✓ Created {len(orders)} orders and 1 quote")
    return orders


def seed_invoices(session: Session, users: dict, orders: List[Order]):
    """
    Crea fatture per ordini completati.

    Args:
        session: SQLAlchemy session
        users: Dizionario utenti
        orders: Lista ordini
    """
    logger.info("=" * 80)
    logger.info("SEEDING INVOICES")
    logger.info("=" * 80)

    # Fattura per primo ordine (completato)
    completed_order = [o for o in orders if o.status == OrderStatus.COMPLETED][0]

    logger.info("Creating invoice...")
    invoice = Invoice(
        invoice_number="FAT-2026-00001",
        invoice_year=2026,
        invoice_progressive=1,
        order_id=completed_order.id,
        user_id=completed_order.user_id,
        invoice_date=datetime.now().date() - timedelta(days=5),
        due_date=datetime.now().date() + timedelta(days=25),
        seller_name="AI Strategy Hub di Davide Botto",
        seller_vat="IT12345678901",
        seller_address="Via Roma 1, 20100 Milano (MI)",
        buyer_name="Verdi S.r.l.",
        buyer_vat="IT98765432109",
        buyer_address="Corso Italia 45, 00100 Roma (RM)",
        buyer_sdi_code="ABCDEFG",
        subtotal=completed_order.subtotal,
        tax_rate=completed_order.tax_rate,
        tax_amount=completed_order.tax_amount,
        total=completed_order.total,
        currency="EUR",
        payment_method="Carta di credito (Stripe)",
        sdi_status=SDIStatus.ACCEPTED,
        sdi_transmission_id="123456789",
        sdi_sent_at=datetime.now() - timedelta(days=4),
        sdi_accepted_at=datetime.now() - timedelta(days=3),
    )
    session.add(invoice)
    session.flush()

    # Invoice lines
    invoice_line = InvoiceLine(
        invoice_id=invoice.id,
        line_number=1,
        description="Toolkit GDPR & Cybersecurity - Licenza singola",
        quantity=Decimal("1.000"),
        unit_price=Decimal("497.00"),
        subtotal=Decimal("497.00"),
        tax_rate=Decimal("22.00"),
        tax_amount=Decimal("109.34"),
        total=Decimal("606.34"),
    )
    session.add(invoice_line)

    session.commit()
    logger.info(f"  ✓ Invoice {invoice.invoice_number}: €{invoice.total} - SDI: {invoice.sdi_status.value}")
    logger.info("✓ Created 1 invoice")


def seed_cms_content(session: Session, users: dict):
    """
    Crea pagine CMS e blog posts di esempio.

    Args:
        session: SQLAlchemy session
        users: Dizionario utenti
    """
    logger.info("=" * 80)
    logger.info("SEEDING CMS CONTENT")
    logger.info("=" * 80)

    # 1. Pagine CMS
    logger.info("Creating CMS pages...")

    about_page = Page(
        slug="chi-siamo",
        title="Chi Siamo",
        content="""
# Chi Siamo

AI Strategy Hub è il punto di riferimento per la consulenza in AI Compliance, GDPR e Cybersecurity.

## La nostra missione

Aiutiamo le aziende a navigare le complessità delle normative tecnologiche europee, garantendo conformità e sicurezza.

## Il team

Il nostro team è composto da esperti certificati in:
- AI & Machine Learning
- Privacy e Data Protection (CIPP/E)
- Cybersecurity (CISSP, CEH)
- Risk Management (ISO 27001 Lead Auditor)
        """,
        is_published=True,
        published_at=datetime.now() - timedelta(days=30),
        author_id=users['admin'].id,
        seo_title="Chi Siamo | AI Strategy Hub",
        seo_description="Scopri AI Strategy Hub: consulenza specializzata in AI Act, GDPR e NIS2. Team di esperti certificati.",
    )
    session.add(about_page)
    logger.info(f"  ✓ Page: {about_page.title}")

    # 2. Blog categories
    logger.info("Creating blog categories...")

    cat_ai = BlogCategory(
        slug="intelligenza-artificiale",
        name="Intelligenza Artificiale",
        description="News e approfondimenti su AI, machine learning e regolamentazione",
        display_order=1,
    )
    session.add(cat_ai)

    cat_gdpr = BlogCategory(
        slug="gdpr-privacy",
        name="GDPR & Privacy",
        description="Tutto sul Regolamento Privacy e protezione dati",
        display_order=2,
    )
    session.add(cat_gdpr)

    cat_cyber = BlogCategory(
        slug="cybersecurity",
        name="Cybersecurity",
        description="Sicurezza informatica, NIS2 e gestione del rischio cyber",
        display_order=3,
    )
    session.add(cat_cyber)

    session.flush()
    logger.info("  ✓ Created 3 blog categories")

    # 3. Blog tags
    logger.info("Creating blog tags...")

    tag_ai_act = BlogTag(slug="ai-act", name="AI Act")
    tag_compliance = BlogTag(slug="compliance", name="Compliance")
    tag_nis2 = BlogTag(slug="nis2", name="NIS2")
    tag_gdpr = BlogTag(slug="gdpr", name="GDPR")

    session.add_all([tag_ai_act, tag_compliance, tag_nis2, tag_gdpr])
    session.flush()
    logger.info("  ✓ Created 4 blog tags")

    # 4. Blog posts
    logger.info("Creating blog posts...")

    post1 = BlogPost(
        slug="ai-act-guida-compliance-2026",
        title="AI Act: Guida Completa alla Compliance nel 2026",
        excerpt="Il Regolamento UE sull'Intelligenza Artificiale è entrato in vigore. Scopri cosa significa per la tua azienda e come prepararti.",
        content="""
# AI Act: Guida Completa alla Compliance nel 2026

Il Regolamento UE sull'Intelligenza Artificiale (AI Act) rappresenta la prima normativa organica al mondo per regolamentare l'uso dell'IA.

## Cosa prevede l'AI Act

Il regolamento introduce un approccio basato sul rischio, classificando i sistemi AI in quattro categorie:

### 1. Rischio Inaccettabile
Sistemi vietati che manipolano il comportamento umano o sfruttano vulnerabilità.

### 2. Alto Rischio
Sistemi che richiedono conformità rigorosa (es: sistemi per recruiting, scoring creditizio).

### 3. Rischio Limitato
Sistemi con obblighi di trasparenza (es: chatbot).

### 4. Rischio Minimo
Maggioranza dei sistemi AI, nessun obbligo specifico.

## Timeline di implementazione

- **2026**: Entrata in vigore per sistemi ad alto rischio
- **2027**: Estensione a tutti i sistemi

## Come prepararsi

1. **Gap Analysis**: Inventario dei sistemi AI utilizzati
2. **Risk Assessment**: Classificazione secondo l'AI Act
3. **Compliance Roadmap**: Piano di adeguamento
4. **Documentazione**: Technical file e conformità assessment

Contattaci per una consulenza personalizzata.
        """,
        category_id=cat_ai.id,
        author_id=users['admin'].id,
        is_published=True,
        published_at=datetime.now() - timedelta(days=7),
        view_count=245,
        reading_time_minutes=8,
        seo_title="AI Act 2026: Guida Completa alla Conformità",
        seo_description="Tutto quello che devi sapere sull'AI Act. Classificazione sistemi, timeline, obblighi di compliance e come prepararsi.",
    )
    session.add(post1)
    session.flush()

    # Associa tags al post
    session.add(BlogPostTag(blog_post_id=post1.id, blog_tag_id=tag_ai_act.id))
    session.add(BlogPostTag(blog_post_id=post1.id, blog_tag_id=tag_compliance.id))
    logger.info(f"  ✓ Blog post: {post1.title}")

    post2 = BlogPost(
        slug="nis2-obblighi-cybersecurity-2026",
        title="Direttiva NIS2: Nuovi Obblighi di Cybersecurity",
        excerpt="La Direttiva NIS2 estende gli obblighi di sicurezza informatica. Chi sono i soggetti obbligati e cosa devono fare.",
        content="""
# Direttiva NIS2: Nuovi Obblighi di Cybersecurity

La Direttiva NIS2 aggiorna e amplia il framework europeo per la cybersecurity.

## Chi è obbligato

- Operatori di Servizi Essenziali (OSE)
- Fornitori di Servizi Digitali (FSD)
- Settori aggiuntivi: sanità, energia, trasporti, pubbliche amministrazioni

## Obblighi principali

### Misure tecniche
- Risk management
- Business continuity
- Supply chain security
- Incident handling
- Crittografia

### Misure organizzative
- Governance della sicurezza
- Formazione del personale
- Controlli di accesso
- Human resource security

### Notifiche
- Incident notification entro 24 ore
- Report dettagliato entro 72 ore

## Sanzioni

Fino a €10M o 2% del fatturato globale annuo.

Contattaci per un assessment NIS2 della tua organizzazione.
        """,
        category_id=cat_cyber.id,
        author_id=users['admin'].id,
        is_published=True,
        published_at=datetime.now() - timedelta(days=3),
        view_count=178,
        reading_time_minutes=6,
    )
    session.add(post2)
    session.flush()

    session.add(BlogPostTag(blog_post_id=post2.id, blog_tag_id=tag_nis2.id))
    session.add(BlogPostTag(blog_post_id=post2.id, blog_tag_id=tag_compliance.id))
    logger.info(f"  ✓ Blog post: {post2.title}")

    session.commit()
    logger.info("✓ Created CMS content: 1 page, 3 categories, 4 tags, 2 blog posts")


def seed_support_and_notifications(session: Session, users: dict):
    """
    Crea ticket di supporto e notifiche di esempio.

    Args:
        session: SQLAlchemy session
        users: Dizionario utenti
    """
    logger.info("=" * 80)
    logger.info("SEEDING SUPPORT TICKETS & NOTIFICATIONS")
    logger.info("=" * 80)

    # 1. Support ticket
    logger.info("Creating support ticket...")

    ticket = SupportTicket(
        ticket_number="TKT-2026-00001",
        user_id=users['customer1'].id,
        subject="Domanda su toolkit GDPR",
        description="Ho acquistato il toolkit GDPR ma non riesco a scaricare il registro dei trattamenti. Potete aiutarmi?",
        status=TicketStatus.IN_PROGRESS,
        priority=TicketPriority.MEDIUM,
        category="technical",
        assigned_to=users['support'].id,
        first_response_at=datetime.now() - timedelta(hours=2),
    )
    session.add(ticket)
    session.flush()

    # Messaggi ticket
    msg1 = TicketMessage(
        ticket_id=ticket.id,
        user_id=users['customer1'].id,
        message="Ho provato a cliccare sul link di download ma ottengo errore 404.",
    )
    session.add(msg1)

    msg2 = TicketMessage(
        ticket_id=ticket.id,
        user_id=users['support'].id,
        message="Ciao Mario, grazie per la segnalazione. Ho verificato e il link è stato aggiornato. Ora dovrebbe funzionare correttamente. Fammi sapere se hai ancora problemi!",
    )
    session.add(msg2)
    logger.info(f"  ✓ Ticket {ticket.ticket_number}: {ticket.subject}")

    # 2. Notifiche
    logger.info("Creating notifications...")

    notif1 = Notification(
        user_id=users['customer1'].id,
        type="order_update",
        title="Ordine completato",
        message="Il tuo ordine ORD-2026-00001 è stato completato con successo!",
        action_url="/orders/ORD-2026-00001",
        is_read=True,
        read_at=datetime.now() - timedelta(days=4),
    )
    session.add(notif1)

    notif2 = Notification(
        user_id=users['customer2'].id,
        type="invoice_ready",
        title="Fattura disponibile",
        message="La fattura per il tuo ordine è disponibile per il download.",
        action_url="/invoices/FAT-2026-00001",
        is_read=False,
    )
    session.add(notif2)

    notif3 = Notification(
        user_id=users['customer1'].id,
        type="ticket_reply",
        title="Nuova risposta al ticket",
        message="Il supporto ha risposto al tuo ticket TKT-2026-00001",
        action_url="/support/tickets/TKT-2026-00001",
        is_read=False,
    )
    session.add(notif3)
    logger.info("  ✓ Created 3 notifications")

    session.commit()
    logger.info("✓ Created 1 ticket and 3 notifications")


def seed_site_settings(session: Session, users: dict):
    """
    Crea configurazioni sito di esempio.

    Args:
        session: SQLAlchemy session
        users: Dizionario utenti
    """
    logger.info("=" * 80)
    logger.info("SEEDING SITE SETTINGS")
    logger.info("=" * 80)

    settings_list = [
        {
            "key": "site_name",
            "value": "AI Strategy Hub",
            "type": "string",
            "description": "Nome del sito web",
            "category": "general",
            "is_public": True,
        },
        {
            "key": "site_tagline",
            "value": "Consulenza AI Compliance, GDPR e Cybersecurity",
            "type": "string",
            "description": "Tagline/sottotitolo del sito",
            "category": "general",
            "is_public": True,
        },
        {
            "key": "contact_email",
            "value": "info@aistrategyhub.eu",
            "type": "string",
            "description": "Email di contatto principale",
            "category": "general",
            "is_public": True,
        },
        {
            "key": "support_email",
            "value": "support@aistrategyhub.eu",
            "type": "string",
            "description": "Email supporto clienti",
            "category": "general",
            "is_public": True,
        },
        {
            "key": "max_file_upload_size_mb",
            "value": 10,
            "type": "number",
            "description": "Dimensione massima file upload (MB)",
            "category": "limits",
            "is_public": False,
        },
        {
            "key": "feature_ai_chat_enabled",
            "value": True,
            "type": "boolean",
            "description": "Abilita chatbot AI sul sito",
            "category": "feature_flags",
            "is_public": False,
        },
        {
            "key": "feature_newsletter_enabled",
            "value": True,
            "type": "boolean",
            "description": "Abilita iscrizione newsletter",
            "category": "feature_flags",
            "is_public": True,
        },
        {
            "key": "stripe_webhook_secret",
            "value": "whsec_test_secret_key_placeholder",
            "type": "encrypted",
            "description": "Stripe webhook secret",
            "category": "payment",
            "is_public": False,
            "is_encrypted": True,
        },
        {
            "key": "ai_chat_max_tokens",
            "value": 4096,
            "type": "number",
            "description": "Token massimi per risposta AI chatbot",
            "category": "ai",
            "is_public": False,
        },
        {
            "key": "ai_chat_model",
            "value": "claude-sonnet-4-5-20250929",
            "type": "string",
            "description": "Modello Claude da utilizzare per chatbot",
            "category": "ai",
            "is_public": False,
        },
    ]

    logger.info(f"Creating {len(settings_list)} site settings...")

    for s in settings_list:
        setting = SiteSetting(
            setting_key=s["key"],
            setting_value=s["value"],
            setting_type=s["type"],
            description=s["description"],
            category=s["category"],
            is_public=s["is_public"],
            is_encrypted=s.get("is_encrypted", False),
            updated_by=users['super_admin'].id,
        )
        session.add(setting)
        logger.info(f"  ✓ Setting: {s['key']} = {s['value']}")

    session.commit()
    logger.info(f"✓ Created {len(settings_list)} site settings")


def seed_audit_logs(session: Session, users: dict):
    """
    Crea alcuni audit logs di esempio.

    Args:
        session: SQLAlchemy session
        users: Dizionario utenti
    """
    logger.info("=" * 80)
    logger.info("SEEDING AUDIT LOGS")
    logger.info("=" * 80)

    logs = [
        AuditLog(
            user_id=users['super_admin'].id,
            action=AuditAction.LOGIN,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0...",
            created_at=datetime.now() - timedelta(days=1),
        ),
        AuditLog(
            user_id=users['admin'].id,
            action=AuditAction.CREATE,
            entity_type="services",
            entity_id=None,  # Would be actual service ID
            changes={"title": "New service created"},
            ip_address="192.168.1.2",
            created_at=datetime.now() - timedelta(hours=12),
        ),
        AuditLog(
            user_id=users['customer1'].id,
            action=AuditAction.READ,
            entity_type="orders",
            ip_address="192.168.1.100",
            created_at=datetime.now() - timedelta(hours=2),
        ),
    ]

    for log in logs:
        session.add(log)

    logger.info(f"  ✓ Created {len(logs)} audit logs")

    # System logs
    system_logs = [
        SystemLog(
            level=LogLevel.INFO,
            module="auth",
            message="User logged in successfully",
            context={"user_id": str(users['super_admin'].id), "method": "email"},
            created_at=datetime.now() - timedelta(days=1),
        ),
        SystemLog(
            level=LogLevel.WARNING,
            module="payment",
            message="Payment retry attempted",
            context={"order_id": "ORD-2026-00002", "attempt": 2},
            created_at=datetime.now() - timedelta(hours=6),
        ),
        SystemLog(
            level=LogLevel.ERROR,
            module="email",
            message="Failed to send email",
            stack_trace="ConnectionError: Unable to connect to SMTP server",
            context={"recipient": "test@example.com"},
            created_at=datetime.now() - timedelta(hours=1),
        ),
    ]

    for log in system_logs:
        session.add(log)

    logger.info(f"  ✓ Created {len(system_logs)} system logs")

    session.commit()
    logger.info(f"✓ Created audit and system logs")


def main():
    """
    Main function per eseguire seeding completo.
    """
    logger.info("=" * 80)
    logger.info("AI STRATEGY HUB - DATABASE SEEDING")
    logger.info("=" * 80)
    logger.info("")
    logger.info("ATTENZIONE: Questo script popola il database con dati di test.")
    logger.info("Assicurati di eseguirlo solo in ambiente di sviluppo!")
    logger.info("")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'localhost'}")
    logger.info("")

    # Safety check
    if settings.ENVIRONMENT == "production":
        logger.error("❌ ERRORE: Non puoi eseguire seed in produzione!")
        sys.exit(1)

    # Crea engine
    engine = create_db_engine()

    # Test connessione
    try:
        with engine.connect() as conn:
            logger.info("✓ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {str(e)}")
        sys.exit(1)

    # Crea session
    session = Session(engine)

    try:
        # Seed data
        users = seed_users(session)
        services = seed_services(session, users)
        orders = seed_orders(session, users, services)
        seed_invoices(session, users, orders)
        seed_cms_content(session, users)
        seed_support_and_notifications(session, users)
        seed_site_settings(session, users)
        seed_audit_logs(session, users)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✓ SEEDING COMPLETATO CON SUCCESSO!")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Dati creati:")
        logger.info(f"  - {len(users)} utenti")
        logger.info(f"  - {len(services)} servizi")
        logger.info(f"  - {len(orders)} ordini + 1 preventivo")
        logger.info("  - 1 fattura")
        logger.info("  - 1 pagina CMS + 2 blog posts")
        logger.info("  - 1 ticket supporto + 3 notifiche")
        logger.info("  - 10 site settings")
        logger.info("  - Audit e system logs")
        logger.info("")
        logger.info("Credenziali test:")
        logger.info("  Admin: admin@aistrategyhub.eu / Test123!")
        logger.info("  Customer: mario.verdi@azienda.it / Test123!")
        logger.info("")

    except Exception as e:
        logger.error(f"❌ Errore durante seeding: {str(e)}", exc_info=True)
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    main()
