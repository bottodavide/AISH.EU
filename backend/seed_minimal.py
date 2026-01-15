"""
Seed Minimalista per Test Rapidi
Popola database con dati essenziali per testing.
"""

import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from passlib.hash import argon2

from app.core.config import settings
from app.models.user import User, UserProfile, UserRole
from app.models.service import Service, ServiceCategory, PricingType, ServiceType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Password per tutti gli utenti test
TEST_PASSWORD = "Test123!"
TEST_PASSWORD_HASH = argon2.hash(TEST_PASSWORD)


def seed_database():
    """Popola database con dati test minimali."""

    # Connessione sync
    engine = create_engine(settings.DATABASE_URL)
    session = Session(engine)

    try:
        logger.info("=" * 80)
        logger.info("SEEDING DATABASE - Minimal Version")
        logger.info("=" * 80)

        # 1. Pulisci dati esistenti (per evitare duplicati)
        logger.info("Cleaning existing test data...")
        session.execute(text("DELETE FROM user_profiles"))
        session.execute(text("""
            DELETE FROM users
            WHERE email LIKE '%@example.com'
               OR email LIKE '%@test.%'
               OR email = 'admin@aistrategyhub.eu'
               OR email = 'mario.verdi@azienda.it'
               OR email = 'giulia.neri@email.it'
        """))
        session.execute(text("DELETE FROM services"))
        session.commit()
        logger.info("✓ Cleaned")

        # 2. Crea utenti
        logger.info("\nCreating users...")

        # Admin
        admin = User(
            email="admin@aistrategyhub.eu",
            password_hash=TEST_PASSWORD_HASH,
            role=UserRole.SUPER_ADMIN,
            is_active=True,
            is_email_verified=True,
        )
        session.add(admin)
        session.flush()

        admin_profile = UserProfile(
            user_id=admin.id,
            first_name="Davide",
            last_name="Botto",
            company_name="AI Strategy Hub",
        )
        session.add(admin_profile)
        logger.info(f"  ✓ Admin: admin@aistrategyhub.eu (password: {TEST_PASSWORD})")

        # Customer 1
        customer1 = User(
            email="mario.verdi@azienda.it",
            password_hash=TEST_PASSWORD_HASH,
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
            vat_number="IT98765432109",
            billing_address={
                "street": "Corso Italia 45",
                "city": "Roma",
                "province": "RM",
                "zip": "00100",
                "country": "IT"
            }
        )
        session.add(customer1_profile)
        logger.info(f"  ✓ Customer: mario.verdi@azienda.it (password: {TEST_PASSWORD})")

        # Customer 2
        customer2 = User(
            email="giulia.neri@email.it",
            password_hash=TEST_PASSWORD_HASH,
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
        )
        session.add(customer2_profile)
        logger.info(f"  ✓ Customer: giulia.neri@email.it (password: {TEST_PASSWORD})")

        session.commit()
        logger.info(f"✓ Created 3 users (password for all: {TEST_PASSWORD})")

        # 3. Crea servizi
        logger.info("\nCreating services...")

        # Servizio 1: AI Act Compliance
        service1 = Service(
            slug="consulenza-ai-act-compliance",
            name="Consulenza AI Act Compliance",
            short_description="Supporto completo per conformità al Regolamento UE sull'Intelligenza Artificiale",
            category=ServiceCategory.AI_COMPLIANCE,
            type=ServiceType.CUSTOM_QUOTE,
            pricing_type=PricingType.CUSTOM,
            currency="EUR",
            is_active=True,
            is_featured=True,
            published_at=datetime.utcnow(),
        )
        session.add(service1)
        logger.info("  ✓ AI Act Compliance Service")

        # Servizio 2: NIS2 Cybersecurity
        service2 = Service(
            slug="consulenza-nis2-cybersecurity",
            name="Consulenza NIS2 Cybersecurity",
            short_description="Conformità alla Direttiva NIS2 per operatori di servizi essenziali",
            category=ServiceCategory.CYBERSECURITY_NIS2,
            type=ServiceType.CUSTOM_QUOTE,
            pricing_type=PricingType.CUSTOM,
            currency="EUR",
            is_active=True,
            is_featured=True,
            published_at=datetime.utcnow(),
        )
        session.add(service2)
        logger.info("  ✓ NIS2 Cybersecurity Service")

        # Servizio 3: Toolkit (con prezzo fisso)
        service3 = Service(
            slug="toolkit-gdpr-cybersecurity",
            name="Toolkit GDPR & Cybersecurity",
            short_description="Documenti e template pronti all'uso per compliance",
            category=ServiceCategory.TOOLKIT_FORMAZIONE,
            type=ServiceType.PACCHETTO_FISSO,
            pricing_type=PricingType.FIXED,
            price_min=Decimal("497.00"),
            currency="EUR",
            is_active=True,
            is_featured=False,
            published_at=datetime.utcnow(),
        )
        session.add(service3)
        logger.info("  ✓ Toolkit Service (€497)")

        # Servizio 4: Consulenza Oraria
        service4 = Service(
            slug="consulenza-oraria-cybersecurity",
            name="Consulenza Oraria Cybersecurity",
            short_description="Supporto flessibile on-demand",
            category=ServiceCategory.CYBERSECURITY_NIS2,
            type=ServiceType.PACCHETTO_FISSO,
            pricing_type=PricingType.RANGE,
            price_min=Decimal("150.00"),
            price_max=Decimal("250.00"),
            currency="EUR",
            is_active=True,
            is_featured=False,
            published_at=datetime.utcnow(),
        )
        session.add(service4)
        logger.info("  ✓ Hourly Consulting Service (€150-250/h)")

        session.commit()
        logger.info("✓ Created 4 services")

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("DATABASE SEEDING COMPLETED!")
        logger.info("=" * 80)
        logger.info(f"\nLogin Credentials (password for all): {TEST_PASSWORD}")
        logger.info("  - admin@aistrategyhub.eu (Super Admin)")
        logger.info("  - mario.verdi@azienda.it (Customer)")
        logger.info("  - giulia.neri@email.it (Customer)")
        logger.info("  - test@example.com (Customer - already registered)")
        logger.info("\nServices created: 4")
        logger.info("  - 2 Custom Quote services")
        logger.info("  - 1 Fixed Price service (€497)")
        logger.info("  - 1 Hourly service (€150-250/h)")
        logger.info("\nAPI Docs: http://localhost:8000/docs")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ Error during seeding: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()
