"""
Script per popolare la pagina About con dati di esempio
Esegui con: python scripts/seed_about_page.py
"""

import asyncio
import sys
from pathlib import Path

# Aggiungi il path del backend al PYTHONPATH
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.about_page import AboutPage, SpecializationArea, CompetenceSection


async def seed_about_page():
    """Popola il database con dati di esempio per la pagina About"""

    async with AsyncSessionLocal() as db:
        # 1. Elimina eventuali dati esistenti
        print("🗑️  Eliminando dati esistenti...")

        # Elimina tutte le about pages (cascade cancellerà anche le relazioni)
        result = await db.execute(select(AboutPage))
        existing_pages = result.scalars().all()
        for page in existing_pages:
            await db.delete(page)

        await db.commit()
        print("✅ Dati esistenti eliminati")

        # 2. Crea la pagina About principale
        print("\n📄 Creando pagina About...")

        about_page = AboutPage(
            profile_name="Davide Botto",
            profile_title="Senior AI & Privacy Consultant",
            profile_description="Aiuto le aziende a innovare in sicurezza, trasformando la compliance in un asset strategico.",
            profile_image_url=None,  # Aggiungi poi l'URL della tua foto dall'admin
            profile_badges=["ISO 27001 LA", "CIPP/E", "AI Ethics"],
            is_published=True,
        )

        db.add(about_page)
        await db.flush()  # Per ottenere l'ID

        print(f"✅ Pagina About creata (ID: {about_page.id})")

        # 3. Crea le aree di specializzazione
        print("\n📊 Creando aree di specializzazione...")

        specialization_areas = [
            SpecializationArea(
                about_page_id=about_page.id,
                name="AI Governance",
                percentage=95,
                display_order=0,
            ),
            SpecializationArea(
                about_page_id=about_page.id,
                name="GDPR Compliance",
                percentage=98,
                display_order=1,
            ),
            SpecializationArea(
                about_page_id=about_page.id,
                name="Cybersecurity Audit",
                percentage=90,
                display_order=2,
            ),
            SpecializationArea(
                about_page_id=about_page.id,
                name="Risk Management",
                percentage=92,
                display_order=3,
            ),
        ]

        for area in specialization_areas:
            db.add(area)
            print(f"  ✅ {area.name}: {area.percentage}%")

        # 4. Crea le sezioni di competenza
        print("\n🎯 Creando sezioni di competenza...")

        competence_sections = [
            # AI Governance & Ethics
            CompetenceSection(
                about_page_id=about_page.id,
                title="AI Governance & Ethics",
                icon="BookOpen",
                description="Con l'avvento dell'AI Act europeo, la governance dei sistemi di intelligenza artificiale non è più opzionale. Offro supporto completo per la classificazione dei sistemi AI, la valutazione d'impatto (FRIA) e la definizione di policy etiche.",
                features=[
                    "Gap Analysis rispetto all'AI Act",
                    "Sviluppo di AI Policy aziendali",
                    "Valutazione dei rischi algoritmici",
                    "Formazione etica per team di sviluppo",
                    "Audit di sistemi AI ad alto rischio",
                    "Documentazione tecnica per la conformità",
                ],
                display_order=0,
            ),

            # GDPR & Data Protection
            CompetenceSection(
                about_page_id=about_page.id,
                title="GDPR & Data Protection",
                icon="Shield",
                description="La protezione dei dati è il fondamento della fiducia digitale. Come DPO certificato, guido le organizzazioni attraverso le complessità del GDPR, garantendo che i dati siano trattati in modo lecito, corretto e trasparente.",
                features=[
                    "Assunzione del ruolo di Data Protection Officer (DPO) esterno",
                    "Esecuzione di DPIA (Data Protection Impact Assessment)",
                    "Gestione dei registri dei trattamenti e delle nomine",
                    "Supporto in caso di Data Breach e rapporti con il Garante",
                    "Formazione GDPR per dipendenti e management",
                    "Audit di conformità e remediation plan",
                ],
                display_order=1,
            ),

            # Cybersecurity & NIS2
            CompetenceSection(
                about_page_id=about_page.id,
                title="Cybersecurity & NIS2",
                icon="Lock",
                description="La Direttiva NIS2 richiede alle organizzazioni di adottare misure tecniche e organizzative adeguate per gestire i rischi di sicurezza. Supporto le aziende nell'implementazione di framework di cybersecurity conformi e resilienza operativa.",
                features=[
                    "Gap Analysis rispetto alla Direttiva NIS2",
                    "Implementazione di Security Operations Center (SOC)",
                    "Business Continuity Planning e Disaster Recovery",
                    "Penetration Testing e Vulnerability Assessment",
                    "Security Awareness Training",
                    "Incident Response Planning",
                ],
                display_order=2,
            ),

            # Consulenza Strategica
            CompetenceSection(
                about_page_id=about_page.id,
                title="Consulenza Strategica",
                icon="TrendingUp",
                description="Oltre alla compliance normativa, offro supporto strategico per integrare AI e sicurezza informatica come leve competitive. Aiuto le aziende a costruire un ecosistema digitale sicuro, etico e scalabile.",
                features=[
                    "AI Strategy & Roadmap",
                    "Digital Transformation Governance",
                    "Vendor Risk Management",
                    "Privacy by Design per nuovi prodotti",
                    "Compliance Automation con AI",
                    "Executive Advisory su AI & Privacy",
                ],
                display_order=3,
            ),
        ]

        for section in competence_sections:
            db.add(section)
            print(f"  ✅ {section.title} ({len(section.features)} features)")

        # 5. Commit finale
        await db.commit()

        print("\n" + "="*60)
        print("✅ COMPLETATO! Pagina About popolata con successo!")
        print("="*60)
        print(f"\n📍 Profilo: {about_page.profile_name}")
        print(f"📍 Titolo: {about_page.profile_title}")
        print(f"📍 Badge: {', '.join(about_page.profile_badges)}")
        print(f"📍 Aree di specializzazione: {len(specialization_areas)}")
        print(f"📍 Sezioni di competenza: {len(competence_sections)}")
        print(f"📍 Pubblicata: {'Sì' if about_page.is_published else 'No'}")
        print("\n🌐 Vai su http://localhost:3000/about per vedere la pagina!")
        print("⚙️  Vai su http://localhost:3000/admin/about per modificarla!")


if __name__ == "__main__":
    print("="*60)
    print("🌱 Seeding About Page - Dati di esempio")
    print("="*60)
    asyncio.run(seed_about_page())
