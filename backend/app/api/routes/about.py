"""
About Page Routes
Descrizione: Endpoint per gestione pagina Chi Siamo
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import get_async_db
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.about_page import AboutPage, SpecializationArea, CompetenceSection
from app.schemas.about import (
    AboutPageResponse,
    AboutPageCreate,
    AboutPageUpdate,
)
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter()


# ========== Public Endpoints ==========

@router.get("", response_model=AboutPageResponse)
async def get_about_page(
    db: AsyncSession = Depends(get_async_db),
) -> AboutPageResponse:
    """
    GET /about
    Ottiene la pagina About pubblicata (endpoint pubblico)
    """
    try:
        # Query pagina About pubblicata con relazioni
        stmt = (
            select(AboutPage)
            .options(
                selectinload(AboutPage.specialization_areas),
                selectinload(AboutPage.competence_sections)
            )
            .where(AboutPage.is_published == True)
        )
        result = await db.execute(stmt)
        about_page = result.scalar_one_or_none()

        if not about_page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagina About non trovata o non pubblicata"
            )

        logger.info("Pagina About recuperata con successo")
        return AboutPageResponse.model_validate(about_page)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Errore recupero pagina About: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante il recupero della pagina About"
        )


# ========== Admin Endpoints ==========

@router.get("/admin", response_model=AboutPageResponse)
async def admin_get_about_page(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
) -> AboutPageResponse:
    """
    GET /about/admin
    Ottiene la pagina About (anche non pubblicata) per amministratori
    """
    try:
        logger.info("Admin " + current_user.email + " recupera pagina About")

        # Query pagina About (anche se non pubblicata) con relazioni
        stmt = (
            select(AboutPage)
            .options(
                selectinload(AboutPage.specialization_areas),
                selectinload(AboutPage.competence_sections)
            )
        )
        result = await db.execute(stmt)
        about_page = result.scalar_one_or_none()

        if not about_page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Pagina About non trovata. Creala prima."
            )

        return AboutPageResponse.model_validate(about_page)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Errore recupero pagina About admin: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante il recupero della pagina About"
        )


@router.put("/admin", response_model=AboutPageResponse)
async def admin_update_or_create_about_page(
    data: AboutPageUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
) -> AboutPageResponse:
    """
    PUT /about/admin
    Crea o aggiorna la pagina About (singleton)
    Se non esiste, la crea. Se esiste, la aggiorna.
    """
    try:
        logger.info("Admin " + current_user.email + " aggiorna pagina About")

        # Cerca se esiste già una pagina About
        stmt = (
            select(AboutPage)
            .options(
                selectinload(AboutPage.specialization_areas),
                selectinload(AboutPage.competence_sections)
            )
        )
        result = await db.execute(stmt)
        about_page = result.scalar_one_or_none()

        # Se non esiste, la crea
        if not about_page:
            logger.info("Creazione nuova pagina About")

            # Crea la pagina base
            about_page = AboutPage(
                profile_name=data.profile_name or "Nome Professionista",
                profile_title=data.profile_title or "Titolo Professionale",
                profile_description=data.profile_description or "Descrizione profilo",
                profile_image_url=data.profile_image_url,
                profile_badges=data.profile_badges or [],
                is_published=data.is_published if data.is_published is not None else False,
            )
            db.add(about_page)
            await db.flush()  # Per ottenere l'ID

            # Aggiungi aree di specializzazione se fornite
            if data.specialization_areas:
                for spec_data in data.specialization_areas:
                    spec = SpecializationArea(
                        about_page_id=about_page.id,
                        name=spec_data.name,
                        percentage=spec_data.percentage,
                        display_order=spec_data.display_order,
                    )
                    db.add(spec)

            # Aggiungi sezioni di competenza se fornite
            if data.competence_sections:
                for comp_data in data.competence_sections:
                    comp = CompetenceSection(
                        about_page_id=about_page.id,
                        title=comp_data.title,
                        icon=comp_data.icon,
                        description=comp_data.description,
                        features=comp_data.features,
                        display_order=comp_data.display_order,
                    )
                    db.add(comp)

            await db.commit()
            await db.refresh(about_page)

            logger.info("Pagina About creata con successo: " + str(about_page.id))

        # Se esiste, la aggiorna
        else:
            logger.info("Aggiornamento pagina About esistente: " + str(about_page.id))

            # Aggiorna campi base
            if data.profile_name is not None:
                about_page.profile_name = data.profile_name
            if data.profile_title is not None:
                about_page.profile_title = data.profile_title
            if data.profile_description is not None:
                about_page.profile_description = data.profile_description
            if data.profile_image_url is not None:
                about_page.profile_image_url = data.profile_image_url
            if data.profile_badges is not None:
                about_page.profile_badges = data.profile_badges
            if data.is_published is not None:
                about_page.is_published = data.is_published

            # Aggiorna aree di specializzazione se fornite
            if data.specialization_areas is not None:
                # Rimuovi tutte le aree esistenti
                await db.execute(
                    select(SpecializationArea)
                    .where(SpecializationArea.about_page_id == about_page.id)
                )
                for spec in about_page.specialization_areas:
                    await db.delete(spec)

                # Aggiungi le nuove
                for spec_data in data.specialization_areas:
                    spec = SpecializationArea(
                        about_page_id=about_page.id,
                        name=spec_data.name,
                        percentage=spec_data.percentage,
                        display_order=spec_data.display_order,
                    )
                    db.add(spec)

            # Aggiorna sezioni di competenza se fornite
            if data.competence_sections is not None:
                # Rimuovi tutte le sezioni esistenti
                await db.execute(
                    select(CompetenceSection)
                    .where(CompetenceSection.about_page_id == about_page.id)
                )
                for comp in about_page.competence_sections:
                    await db.delete(comp)

                # Aggiungi le nuove
                for comp_data in data.competence_sections:
                    comp = CompetenceSection(
                        about_page_id=about_page.id,
                        title=comp_data.title,
                        icon=comp_data.icon,
                        description=comp_data.description,
                        features=comp_data.features,
                        display_order=comp_data.display_order,
                    )
                    db.add(comp)

            await db.commit()
            await db.refresh(about_page)

            logger.info("Pagina About aggiornata con successo")

        # Ricarica con tutte le relazioni
        stmt = (
            select(AboutPage)
            .options(
                selectinload(AboutPage.specialization_areas),
                selectinload(AboutPage.competence_sections)
            )
            .where(AboutPage.id == about_page.id)
        )
        result = await db.execute(stmt)
        about_page = result.scalar_one()

        return AboutPageResponse.model_validate(about_page)

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("Errore aggiornamento pagina About: " + str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Errore durante l'aggiornamento della pagina About"
        )
