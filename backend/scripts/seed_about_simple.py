"""
Script semplice per popolare la pagina About con SQL raw
Esegui con: python scripts/seed_about_simple.py
"""

import asyncio
import asyncpg
from datetime import datetime
import uuid
import json


async def seed_about_page():
    """Popola il database con dati di esempio usando SQL raw"""

    print("=" * 60)
    print("🌱 Seeding About Page - SQL Raw")
    print("=" * 60)

    # Connessione al database
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="aistrategyhub",
        password="aistrategyhub_dev_password",
        database="aistrategyhub",
    )

    try:
        # 1. Elimina dati esistenti
        print("\n🗑️  Eliminando dati esistenti...")
        await conn.execute("DELETE FROM competence_sections")
        await conn.execute("DELETE FROM specialization_areas")
        await conn.execute("DELETE FROM about_pages")
        print("✅ Dati esistenti eliminati")

        # 2. Crea la pagina About
        print("\n📄 Creando pagina About...")
        about_page_id = str(uuid.uuid4())
        now = datetime.utcnow()

        await conn.execute(
            """
            INSERT INTO about_pages (
                id, profile_name, profile_title, profile_description,
                profile_image_url, profile_badges, is_published,
                created_at, updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            about_page_id,
            "Davide Botto",
            "Senior AI & Privacy Consultant",
            "Aiuto le aziende a innovare in sicurezza, trasformando la compliance in un asset strategico.",
            None,
            json.dumps(["ISO 27001 LA", "CIPP/E", "AI Ethics"]),
            True,
            now,
            now,
        )
        print(f"✅ Pagina About creata (ID: {about_page_id})")

        # 3. Crea aree di specializzazione
        print("\n📊 Creando aree di specializzazione...")
        specializations = [
            ("AI Governance", 95, 0),
            ("GDPR Compliance", 98, 1),
            ("Cybersecurity Audit", 90, 2),
            ("Risk Management", 92, 3),
        ]

        for name, percentage, order in specializations:
            await conn.execute(
                """
                INSERT INTO specialization_areas (
                    id, about_page_id, name, percentage, display_order,
                    created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                str(uuid.uuid4()),
                about_page_id,
                name,
                percentage,
                order,
                now,
                now,
            )
            print(f"  ✅ {name}: {percentage}%")

        # 4. Crea sezioni di competenza
        print("\n🎯 Creando sezioni di competenza...")

        competences = [
            {
                "title": "AI Governance & Ethics",
                "icon": "BookOpen",
                "description": "Con l'avvento dell'AI Act europeo, la governance dei sistemi di intelligenza artificiale non è più opzionale. Offro supporto completo per la classificazione dei sistemi AI, la valutazione d'impatto (FRIA) e la definizione di policy etiche.",
                "features": [
                    "Gap Analysis rispetto all'AI Act",
                    "Sviluppo di AI Policy aziendali",
                    "Valutazione dei rischi algoritmici",
                    "Formazione etica per team di sviluppo",
                    "Audit di sistemi AI ad alto rischio",
                    "Documentazione tecnica per la conformità",
                ],
                "display_order": 0,
            },
            {
                "title": "GDPR & Data Protection",
                "icon": "Shield",
                "description": "La protezione dei dati è il fondamento della fiducia digitale. Come DPO certificato, guido le organizzazioni attraverso le complessità del GDPR, garantendo che i dati siano trattati in modo lecito, corretto e trasparente.",
                "features": [
                    "Assunzione del ruolo di Data Protection Officer (DPO) esterno",
                    "Esecuzione di DPIA (Data Protection Impact Assessment)",
                    "Gestione dei registri dei trattamenti e delle nomine",
                    "Supporto in caso di Data Breach e rapporti con il Garante",
                    "Formazione GDPR per dipendenti e management",
                    "Audit di conformità e remediation plan",
                ],
                "display_order": 1,
            },
            {
                "title": "Cybersecurity & NIS2",
                "icon": "Lock",
                "description": "La Direttiva NIS2 richiede alle organizzazioni di adottare misure tecniche e organizzative adeguate per gestire i rischi di sicurezza. Supporto le aziende nell'implementazione di framework di cybersecurity conformi e resilienza operativa.",
                "features": [
                    "Gap Analysis rispetto alla Direttiva NIS2",
                    "Implementazione di Security Operations Center (SOC)",
                    "Business Continuity Planning e Disaster Recovery",
                    "Penetration Testing e Vulnerability Assessment",
                    "Security Awareness Training",
                    "Incident Response Planning",
                ],
                "display_order": 2,
            },
            {
                "title": "Consulenza Strategica",
                "icon": "TrendingUp",
                "description": "Oltre alla compliance normativa, offro supporto strategico per integrare AI e sicurezza informatica come leve competitive. Aiuto le aziende a costruire un ecosistema digitale sicuro, etico e scalabile.",
                "features": [
                    "AI Strategy & Roadmap",
                    "Digital Transformation Governance",
                    "Vendor Risk Management",
                    "Privacy by Design per nuovi prodotti",
                    "Compliance Automation con AI",
                    "Executive Advisory su AI & Privacy",
                ],
                "display_order": 3,
            },
        ]

        for comp in competences:
            await conn.execute(
                """
                INSERT INTO competence_sections (
                    id, about_page_id, title, icon, description, features,
                    display_order, created_at, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                str(uuid.uuid4()),
                about_page_id,
                comp["title"],
                comp["icon"],
                comp["description"],
                json.dumps(comp["features"]),
                comp["display_order"],
                now,
                now,
            )
            print(f"  ✅ {comp['title']} ({len(comp['features'])} features)")

        print("\n" + "=" * 60)
        print("✅ COMPLETATO! Pagina About popolata con successo!")
        print("=" * 60)
        print("\n📍 Profilo: Davide Botto")
        print("📍 Titolo: Senior AI & Privacy Consultant")
        print("📍 Badge: ISO 27001 LA, CIPP/E, AI Ethics")
        print(f"📍 Aree di specializzazione: {len(specializations)}")
        print(f"📍 Sezioni di competenza: {len(competences)}")
        print("📍 Pubblicata: Sì")
        print("\n🌐 Vai su http://localhost:3000/about per vedere la pagina!")
        print("⚙️  Vai su http://localhost:3000/admin/about per modificarla!")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(seed_about_page())
