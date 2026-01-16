"""
Modulo: errors.py
Descrizione: API routes per error reporting e notifiche
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user_optional
from app.models.user import User
from app.schemas.error import ErrorReportRequest, ErrorReportResponse
from app.services.email_service import send_error_notification_email

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/errors", tags=["Errors"])


@router.post("/report", response_model=ErrorReportResponse)
async def report_error(
    error: ErrorReportRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> ErrorReportResponse:
    """
    Segnala un errore che è stato catturato nel frontend.
    Invia email di notifica all'amministratore.

    - **Pubblico**: Accessibile a tutti (anche utenti non autenticati)

    Args:
        error: Dettagli errore
        request: Richiesta HTTP
        current_user: Utente corrente (opzionale)
        db: Database session

    Returns:
        ErrorReportResponse: Conferma invio notifica
    """
    logger.warning(
        f"Error reported from frontend: {error.error_code} - {error.error_message}"
    )

    # Email utente (se autenticato)
    user_email = current_user.email if current_user else None

    # Invia email di notifica all'amministratore
    try:
        email_sent = send_error_notification_email(
            error_code=error.error_code,
            error_message=error.error_message,
            error_details=error.error_details,
            user_email=user_email,
            request_path=error.request_path,
            request_method="FRONTEND",
            stack_trace=error.stack_trace,
        )

        if email_sent:
            logger.info(f"Error notification email sent for {error.error_code}")
            return ErrorReportResponse(
                success=True, message="Error notification sent successfully"
            )
        else:
            logger.warning(
                f"Failed to send error notification email for {error.error_code}"
            )
            return ErrorReportResponse(
                success=False,
                message="Error notification could not be sent (email service unavailable)",
            )

    except Exception as e:
        logger.error(f"Exception while sending error notification: {e}")
        return ErrorReportResponse(
            success=False, message=f"Error notification failed: {str(e)}"
        )
