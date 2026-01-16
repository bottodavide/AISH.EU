"""
Seed per Banner Homepage
Popola database con banner di esempio per la homepage.
"""

import logging
from datetime import datetime, timedelta

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.homepage import HomepageBanner

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_banners():
    """Popola database con banner homepage di esempio."""

    # Connessione sync
    engine = create_engine(settings.DATABASE_URL)
    session = Session(engine)

    try:
        logger.info("=" * 80)
        logger.info("SEEDING HOMEPAGE BANNERS")
        logger.info("=" * 80)

        # 1. Pulisci banner esistenti
        logger.info("Cleaning existing banners...")
        session.execute(text("DELETE FROM homepage_banners"))
        session.commit()

        # 2. Crea banner hero principale
        logger.info("Creating hero banners...")

        banner1 = HomepageBanner(
            title="Innovazione AI in Sicurezza e Compliance",
            subtitle="Consulenza strategica per l'adozione responsabile dell'Intelligenza Artificiale",
            description="Aiutiamo le aziende a implementare soluzioni AI rispettando GDPR, NIS2 e normative di Cybersecurity",
            image_url="https://images.unsplash.com/photo-1677442136019-21780ecad995?q=80&w=2000",
            cta_text="Scopri i Servizi",
            cta_link="/servizi",
            cta_variant="primary",
            position="hero",
            display_order=0,
            background_color="",
            text_color="",
            is_active=True,
            start_date=None,
            end_date=None,
        )
        session.add(banner1)

        banner2 = HomepageBanner(
            title="AI Act & GDPR Compliance",
            subtitle="Ti prepariamo per le nuove normative europee sull'Intelligenza Artificiale",
            description="Consulenza specializzata per conformità AI Act, GDPR e valutazione rischi algoritmici",
            image_url="https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2000",
            cta_text="Richiedi Consulenza",
            cta_link="/contatti",
            cta_variant="primary",
            position="hero",
            display_order=1,
            background_color="",
            text_color="",
            is_active=True,
            start_date=None,
            end_date=None,
        )
        session.add(banner2)

        banner3 = HomepageBanner(
            title="Cybersecurity & NIS2",
            subtitle="Proteggi la tua infrastruttura critica con strategie avanzate di sicurezza",
            description="Implementazione NIS2, penetration testing e gestione incident response",
            image_url="https://images.unsplash.com/photo-1563986768609-322da13575f3?q=80&w=2000",
            cta_text="Scopri di Più",
            cta_link="/servizi",
            cta_variant="outline",
            position="hero",
            display_order=2,
            background_color="",
            text_color="",
            is_active=True,
            start_date=None,
            end_date=None,
        )
        session.add(banner3)

        # 3. Crea sezioni promozionali
        logger.info("Creating section banners...")

        promo1 = HomepageBanner(
            title="Webinar Gratuito: AI e Compliance 2026",
            subtitle="Iscriviti al nostro webinar gratuito sulle nuove normative AI",
            description="",
            image_url="https://images.unsplash.com/photo-1540575467063-178a50c2df87?q=80&w=1200",
            cta_text="Iscriviti Ora",
            cta_link="/blog",
            cta_variant="primary",
            position="section",
            display_order=0,
            background_color="primary",
            text_color="white",
            is_active=True,
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=30),
        )
        session.add(promo1)

        promo2 = HomepageBanner(
            title="Pacchetto Starter AI Compliance",
            subtitle="Valutazione iniziale + Roadmap strategica a prezzo promozionale",
            description="",
            image_url="https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=1200",
            cta_text="Scopri l'Offerta",
            cta_link="/servizi",
            cta_variant="secondary",
            position="section",
            display_order=1,
            background_color="muted",
            text_color="",
            is_active=True,
            start_date=None,
            end_date=None,
        )
        session.add(promo2)

        session.commit()
        logger.info("✅ Banner homepage created successfully!")
        logger.info(f"   - 3 Hero banners")
        logger.info(f"   - 2 Section banners")

        logger.info("=" * 80)
        logger.info("SEEDING COMPLETED")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        session.rollback()
        raise
    finally:
        session.close()
        engine.dispose()


if __name__ == "__main__":
    seed_banners()
    logger.info("\n🎉 Database seeded successfully!")
    logger.info("You can now view banners at http://localhost:3000")
    logger.info("Admin panel: http://localhost:3000/admin/banners")
