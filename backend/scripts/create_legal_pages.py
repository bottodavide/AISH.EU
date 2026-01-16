"""
Create Legal Pages using SQLAlchemy ORM
Descrizione: Crea le pagine legali nel CMS usando ORM
Autore: Claude per Davide
Data: 2026-01-16
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models.cms import Page, PageType, ContentStatus
from datetime import datetime, timezone


async def create_legal_pages():
    """Crea le 3 pagine legali nel database"""

    print("=" * 80)
    print("CREATE LEGAL PAGES - AI Strategy Hub")
    print("=" * 80)

    async with AsyncSessionLocal() as db:
        try:
            # Get first user for created_by/updated_by using raw query to avoid relationship issues
            result = await db.execute(text("SELECT id, email FROM users ORDER BY created_at ASC LIMIT 1"))
            user_row = result.fetchone()

            if not user_row:
                print("\n❌ Nessun utente trovato nel database.")
                print("Crea prima un utente tramite registrazione.")
                return

            user_id = user_row[0]
            user_email = user_row[1]
            print(f"\n✓ Utente trovato: {user_email}")
            now = datetime.now(timezone.utc)

            # ========================================
            # 1. COOKIE POLICY
            # ========================================
            result = await db.execute(select(Page).where(Page.slug == "cookie"))
            existing = result.scalar_one_or_none()

            if existing:
                print("\n✓ Cookie Policy già esistente, skip...")
            else:
                cookie_page = Page(
                    slug="cookie",
                    title="Cookie Policy",
                    page_type=PageType.CUSTOM,
                    status=ContentStatus.PUBLISHED,
                    seo_title="Cookie Policy - AI Strategy Hub",
                    seo_description="Informativa sui cookie utilizzati da AI Strategy Hub",
                    content_blocks=[],
                    created_by=user_id,
                    updated_by=user_id,
                    published_at=now,
                )
                db.add(cookie_page)
                print("\n✓ Cookie Policy creata")

            # ========================================
            # 2. PRIVACY POLICY
            # ========================================
            result = await db.execute(select(Page).where(Page.slug == "privacy"))
            existing = result.scalar_one_or_none()

            if existing:
                print("✓ Privacy Policy già esistente, skip...")
            else:
                privacy_page = Page(
                    slug="privacy",
                    title="Privacy Policy",
                    page_type=PageType.CUSTOM,
                    status=ContentStatus.PUBLISHED,
                    seo_title="Privacy Policy - AI Strategy Hub",
                    seo_description="Informativa sulla protezione dei dati personali secondo GDPR",
                    content_blocks=[],
                    created_by=user_id,
                    updated_by=user_id,
                    published_at=now,
                )
                db.add(privacy_page)
                print("✓ Privacy Policy creata")

            # ========================================
            # 3. TERMINI DI SERVIZIO
            # ========================================
            result = await db.execute(select(Page).where(Page.slug == "termini"))
            existing = result.scalar_one_or_none()

            if existing:
                print("✓ Termini di Servizio già esistenti, skip...")
            else:
                terms_page = Page(
                    slug="termini",
                    title="Termini di Servizio",
                    page_type=PageType.CUSTOM,
                    status=ContentStatus.PUBLISHED,
                    seo_title="Termini di Servizio - AI Strategy Hub",
                    seo_description="Condizioni generali di utilizzo dei servizi",
                    content_blocks=[],
                    created_by=user_id,
                    updated_by=user_id,
                    published_at=now,
                )
                db.add(terms_page)
                print("✓ Termini di Servizio creati")

            # Commit all changes
            await db.commit()

            # ========================================
            # VERIFICA
            # ========================================
            print("\n" + "=" * 80)
            print("VERIFICA PAGINE CREATE")
            print("=" * 80)

            result = await db.execute(
                select(Page).where(Page.slug.in_(["cookie", "privacy", "termini"]))
            )
            pages = result.scalars().all()

            for page in pages:
                print(f"\n✓ {page.title}")
                print(f"  Slug: {page.slug}")
                print(f"  Status: {page.status.value}")
                print(f"  Created: {page.created_at}")

            print("\n" + "=" * 80)
            print("✅ COMPLETATO CON SUCCESSO!")
            print("=" * 80)
            print("\nLe pagine sono ora accessibili:")
            print("  • http://localhost:8000/api/v1/cms/pages/slug/cookie")
            print("  • http://localhost:8000/api/v1/cms/pages/slug/privacy")
            print("  • http://localhost:8000/api/v1/cms/pages/slug/termini")
            print("\n  • http://localhost:3000/cookie")
            print("  • http://localhost:3000/privacy")
            print("  • http://localhost:3000/termini")
            print("\nNOTA: Le pagine hanno content_blocks vuoti, quindi il frontend")
            print("userà comunque il contenuto fallback statico.")
            print("Puoi modificare i content_blocks tramite /admin/pages")
            print("=" * 80 + "\n")

        except Exception as e:
            print(f"\n❌ Errore: {e}")
            import traceback
            traceback.print_exc()
            await db.rollback()


if __name__ == "__main__":
    asyncio.run(create_legal_pages())
