"""
Seed Legal Pages
Descrizione: Popola le pagine legali (Cookie, Privacy, Termini)
Autore: Claude per Davide
Data: 2026-01-16
"""

import asyncio
import asyncpg
import uuid
from datetime import datetime, timezone


async def seed_legal_pages():
    """Crea le tre pagine legali nel database CMS"""

    conn = await asyncpg.connect(
        host='localhost',
        user='aistrategyhub',
        password='aistrategyhub_dev_password',
        database='aistrategyhub',
    )

    try:
        print("=" * 80)
        print("SEED LEGAL PAGES - AI Strategy Hub")
        print("=" * 80)

        # Get any user for the author
        user = await conn.fetchrow("""
            SELECT id FROM users
            ORDER BY created_at ASC
            LIMIT 1
        """)

        if not user:
            print("ERROR: Nessun utente trovato nel database.")
            print("SUGGERIMENTO: Crea un utente tramite registrazione o admin panel.")
            print("Le pagine verranno comunque mostrate con contenuto fallback.")
            return

        author_id = str(user['id'])
        now = datetime.now(timezone.utc)

        # ============================================================
        # 1. COOKIE POLICY
        # ============================================================

        cookie_id = str(uuid.uuid4())

        cookie_exists = await conn.fetchval(
            "SELECT id FROM pages WHERE slug = 'cookie'"
        )

        if cookie_exists:
            print("\n✓ Cookie Policy già esistente, skip...")
        else:
            await conn.execute("""
                INSERT INTO pages (
                    id, slug, title, page_type, status,
                    seo_title, seo_description,
                    content_blocks, created_by, updated_by,
                    published_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4::pagetype, $5::contentstatus, $6, $7, $8, $9, $10, $11, $12, $13)
            """,
                cookie_id,
                'cookie',
                'Cookie Policy',
                'custom',
                'published',
                'Cookie Policy - AI Strategy Hub',
                'Informativa sui cookie utilizzati da AI Strategy Hub',
                '[]',  # Empty JSON array for content_blocks
                uuid.UUID(author_id),
                uuid.UUID(author_id),
                now,
                now,
                now
            )
            print(f"\n✓ Cookie Policy creata con ID: {cookie_id}")

        # ============================================================
        # 2. PRIVACY POLICY
        # ============================================================

        privacy_id = str(uuid.uuid4())

        privacy_exists = await conn.fetchval(
            "SELECT id FROM pages WHERE slug = 'privacy'"
        )

        if privacy_exists:
            print("✓ Privacy Policy già esistente, skip...")
        else:
            await conn.execute("""
                INSERT INTO pages (
                    id, slug, title, page_type, status,
                    seo_title, seo_description,
                    content_blocks, created_by, updated_by,
                    published_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4::pagetype, $5::contentstatus, $6, $7, $8, $9, $10, $11, $12, $13)
            """,
                privacy_id,
                'privacy',
                'Privacy Policy',
                'custom',
                'published',
                'Privacy Policy - AI Strategy Hub',
                'Informativa sulla protezione dei dati personali secondo GDPR',
                '[]',
                uuid.UUID(author_id),
                uuid.UUID(author_id),
                now,
                now,
                now
            )
            print(f"✓ Privacy Policy creata con ID: {privacy_id}")

        # ============================================================
        # 3. TERMINI DI SERVIZIO
        # ============================================================

        terms_id = str(uuid.uuid4())

        terms_exists = await conn.fetchval(
            "SELECT id FROM pages WHERE slug = 'termini'"
        )

        if terms_exists:
            print("✓ Termini di Servizio già esistenti, skip...")
        else:
            await conn.execute("""
                INSERT INTO pages (
                    id, slug, title, page_type, status,
                    seo_title, seo_description,
                    content_blocks, created_by, updated_by,
                    published_at, created_at, updated_at
                ) VALUES ($1, $2, $3, $4::pagetype, $5::contentstatus, $6, $7, $8, $9, $10, $11, $12, $13)
            """,
                terms_id,
                'termini',
                'Termini di Servizio',
                'custom',
                'published',
                'Termini di Servizio - AI Strategy Hub',
                'Condizioni generali di utilizzo dei servizi',
                '[]',
                uuid.UUID(author_id),
                uuid.UUID(author_id),
                now,
                now,
                now
            )
            print(f"✓ Termini di Servizio creati con ID: {terms_id}")

        # ============================================================
        # VERIFICA FINALE
        # ============================================================

        print("\n" + "=" * 80)
        print("VERIFICA PAGINE LEGALI")
        print("=" * 80)

        pages = await conn.fetch("""
            SELECT slug, title, status, created_at
            FROM pages
            WHERE slug IN ('cookie', 'privacy', 'termini')
            ORDER BY slug
        """)

        for page in pages:
            print(f"\n✓ {page['title']}")
            print(f"  Slug: {page['slug']}")
            print(f"  Status: {page['status']}")
            print(f"  Creata: {page['created_at']}")

        print("\n" + "=" * 80)
        print("SEED COMPLETATO CON SUCCESSO!")
        print("=" * 80)
        print("\nLe pagine legali sono ora accessibili a:")
        print("  • http://localhost:3000/cookie")
        print("  • http://localhost:3000/privacy")
        print("  • http://localhost:3000/termini")
        print("\nNOTA: Le pagine useranno il contenuto fallback statico finché")
        print("non aggiungerai content_sections tramite il pannello admin.")
        print("=" * 80 + "\n")

    except Exception as e:
        print(f"\n❌ Errore durante il seed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_legal_pages())
