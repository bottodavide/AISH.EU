"""
Modulo: contact.py
Descrizione: API routes per contact form
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_db
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.schemas.contact import ContactFormRequest, ContactFormResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/contact", tags=["Contact"])


@router.post("", response_model=ContactFormResponse)
async def submit_contact_form(
    data: ContactFormRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> ContactFormResponse:
    """
    Invio contact form.

    - **Pubblico**: Accessibile a tutti

    Args:
        data: Dati form
        request: Request object
        current_user: Utente corrente (opzionale)
        db: Database session

    Returns:
        ContactFormResponse: Conferma invio
    """
    logger.info(f"Contact form submission from: {data.email}")

    # Genera reference ID
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    reference_id = f"CONT-{timestamp}"

    # TODO: Salvare nel database (tabella contact_messages o support_tickets)
    # message_record = ContactMessage(
    #     reference_id=reference_id,
    #     name=data.name,
    #     email=data.email,
    #     subject=data.subject,
    #     message=data.message,
    #     user_id=current_user.id if current_user else None,
    #     ip_address=request.client.host if request.client else None,
    #     user_agent=request.headers.get("user-agent"),
    # )
    # db.add(message_record)
    # await db.commit()

    # Invia email all'admin/supporto
    try:
        # TODO: Implementare send_contact_form_email
        from app.services.email_service import ms_graph_service

        # Email HTML per admin
        admin_email_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; }}
                .content {{ padding: 20px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #64748b; }}
                .value {{ margin-top: 5px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>📧 Nuovo Messaggio dal Contact Form</h2>
            </div>
            <div class="content">
                <div class="field">
                    <div class="label">ID Riferimento:</div>
                    <div class="value">{reference_id}</div>
                </div>
                <div class="field">
                    <div class="label">Nome:</div>
                    <div class="value">{data.name}</div>
                </div>
                <div class="field">
                    <div class="label">Email:</div>
                    <div class="value"><a href="mailto:{data.email}">{data.email}</a></div>
                </div>
                {f'<div class="field"><div class="label">Azienda:</div><div class="value">{data.company}</div></div>' if data.company else ''}
                {f'<div class="field"><div class="label">Ruolo:</div><div class="value">{data.role}</div></div>' if data.role else ''}
                <div class="field">
                    <div class="label">Oggetto:</div>
                    <div class="value">{data.subject}</div>
                </div>
                <div class="field">
                    <div class="label">Messaggio:</div>
                    <div class="value" style="white-space: pre-wrap;">{data.message}</div>
                </div>
                <div class="field">
                    <div class="label">Data:</div>
                    <div class="value">{datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}</div>
                </div>
                {f'<div class="field"><div class="label">Utente Registrato:</div><div class="value">Sì (ID: {current_user.id})</div></div>' if current_user else ''}
            </div>
        </body>
        </html>
        """

        # Invia a admin
        admin_email = settings.ADMIN_EMAIL or "davide@davidebotto.com"
        ms_graph_service.send_email(
            to=admin_email,
            subject=f"[Contact Form] {data.subject}",
            body_html=admin_email_body,
        )

        logger.info(f"Contact form email sent to admin: {admin_email}")

        # Email di conferma al mittente
        user_email_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 30px; }}
                .footer {{ background-color: #f1f5f9; padding: 20px; text-align: center; margin-top: 30px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>✓ Messaggio Ricevuto</h2>
            </div>
            <div class="content">
                <p>Ciao <strong>{data.name}</strong>,</p>

                <p>Abbiamo ricevuto il tuo messaggio e ti ringraziamo per averci contattato.</p>

                <p>Il nostro team esaminerà la tua richiesta e ti risponderà al più presto all'indirizzo email fornito.</p>

                <div style="background-color: #f1f5f9; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <p style="margin: 0;"><strong>ID Riferimento:</strong> {reference_id}</p>
                    <p style="margin: 10px 0 0 0;"><small>Conserva questo codice per eventuali comunicazioni future.</small></p>
                </div>

                <p><strong>Riepilogo della tua richiesta:</strong></p>
                <p><strong>Oggetto:</strong> {data.subject}</p>
                <p><strong>Messaggio:</strong></p>
                <p style="white-space: pre-wrap; background-color: #f9fafb; padding: 15px; border-left: 4px solid #3b82f6;">{data.message}</p>
            </div>
            <div class="footer">
                <p><strong>AI Strategy Hub</strong></p>
                <p>Consulenza AI, GDPR e Cybersecurity</p>
                <p><a href="mailto:info@aistrategyhub.eu">info@aistrategyhub.eu</a></p>
            </div>
        </body>
        </html>
        """

        ms_graph_service.send_email(
            to=data.email,
            subject="Conferma ricezione messaggio - AI Strategy Hub",
            body_html=user_email_body,
        )

        logger.info(f"Confirmation email sent to: {data.email}")

    except Exception as e:
        logger.error(f"Failed to send contact form emails: {e}")
        # Non bloccare la response anche se email fallisce

    return ContactFormResponse(
        success=True,
        message="Grazie per averci contattato! Riceverai una conferma via email e ti risponderemo al più presto.",
        reference_id=reference_id,
    )
