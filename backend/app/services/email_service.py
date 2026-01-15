"""
Modulo: email_service.py
Descrizione: Servizio invio email con templates Jinja2
Autore: Claude per Davide
Data: 2026-01-15

Servizio high-level per invio email template-based usando MS Graph API.

Features:
- Template Jinja2 per email HTML
- Integrazione con MS Graph per invio
- Helper functions per use cases comuni
- Fallback graceful se MS Graph non configurato

Templates disponibili:
- welcome.html: Email di benvenuto post-registrazione
- email_verification.html: Verifica email
- password_reset.html: Reset password
- order_confirmation.html: Conferma ordine
- invoice_ready.html: Fattura disponibile

Usage:
    from app.services.email_service import send_welcome_email

    await send_welcome_email(
        user_email="user@example.com",
        user_name="Mario Rossi",
        verification_link="https://..."
    )
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.services.ms_graph import ms_graph_service

logger = logging.getLogger(__name__)


# =============================================================================
# JINJA2 ENVIRONMENT
# =============================================================================

# Template directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "emails"

# Jinja2 environment
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

# Add settings to globals (per uso nei template)
jinja_env.globals["settings"] = settings


# =============================================================================
# EMAIL SERVICE
# =============================================================================


class EmailService:
    """
    Servizio invio email con templates.

    Gestisce rendering template Jinja2 e invio via MS Graph.
    """

    def __init__(self):
        """Inizializza email service"""
        self.ms_graph = ms_graph_service
        self.env = jinja_env
        logger.info("EmailService initialized")

    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Renderizza template email.

        Args:
            template_name: Nome template (es: "welcome.html")
            context: Context variables per template

        Returns:
            str: HTML renderizzato

        Raises:
            Exception: Se template non trovato
        """
        try:
            template = self.env.get_template(template_name)
            html = template.render(**context)
            return html
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            raise

    def send_templated_email(
        self,
        to: str,
        subject: str,
        template_name: str,
        context: Dict[str, Any],
    ) -> bool:
        """
        Invia email usando template.

        Args:
            to: Email destinatario
            subject: Oggetto email
            template_name: Nome template
            context: Context per template

        Returns:
            bool: True se successo
        """
        try:
            # Renderizza template
            html_body = self.render_template(template_name, context)

            # Invia email
            success = self.ms_graph.send_email(
                to=to,
                subject=subject,
                body_html=html_body,
            )

            if success:
                logger.info(f"Email sent to {to}: {subject}")
            else:
                logger.warning(f"Email not sent to {to}: {subject}")

            return success

        except Exception as e:
            logger.error(f"Error sending templated email: {str(e)}")
            return False


# =============================================================================
# SINGLETON
# =============================================================================

email_service = EmailService()


# =============================================================================
# HELPER FUNCTIONS - AUTHENTICATION
# =============================================================================


def send_welcome_email(
    user_email: str,
    user_name: str,
    verification_link: str,
) -> bool:
    """
    Invia email di benvenuto con link verifica.

    Args:
        user_email: Email utente
        user_name: Nome utente
        verification_link: Link verifica account

    Returns:
        bool: True se successo
    """
    context = {
        "subject": "Benvenuto su AI Strategy Hub!",
        "user_email": user_email,
        "user_name": user_name,
        "verification_link": verification_link,
        "expiry_hours": settings.EMAIL_VERIFICATION_EXPIRE_HOURS,
    }

    return email_service.send_templated_email(
        to=user_email,
        subject=context["subject"],
        template_name="welcome.html",
        context=context,
    )


def send_email_verification(
    user_email: str,
    user_name: str,
    verification_link: str,
) -> bool:
    """
    Invia email di verifica account.

    Args:
        user_email: Email utente
        user_name: Nome utente
        verification_link: Link verifica

    Returns:
        bool: True se successo
    """
    context = {
        "subject": "Verifica il tuo account - AI Strategy Hub",
        "user_email": user_email,
        "user_name": user_name,
        "verification_link": verification_link,
        "expiry_hours": settings.EMAIL_VERIFICATION_EXPIRE_HOURS,
    }

    return email_service.send_templated_email(
        to=user_email,
        subject=context["subject"],
        template_name="email_verification.html",
        context=context,
    )


def send_password_reset_email(
    user_email: str,
    user_name: str,
    reset_link: str,
) -> bool:
    """
    Invia email reset password.

    Args:
        user_email: Email utente
        user_name: Nome utente
        reset_link: Link reset password

    Returns:
        bool: True se successo
    """
    context = {
        "subject": "Reset Password - AI Strategy Hub",
        "user_name": user_name,
        "reset_link": reset_link,
        "expiry_hours": settings.PASSWORD_RESET_EXPIRE_HOURS,
    }

    return email_service.send_templated_email(
        to=user_email,
        subject=context["subject"],
        template_name="password_reset.html",
        context=context,
    )


# =============================================================================
# HELPER FUNCTIONS - ORDERS & INVOICES
# =============================================================================


def send_order_confirmation_email(
    user_email: str,
    user_name: str,
    order_number: str,
    order_date: str,
    order_items: list,
    order_subtotal: str,
    order_tax: str,
    order_total: str,
    order_url: str,
    dashboard_url: str,
) -> bool:
    """
    Invia email conferma ordine.

    Args:
        user_email: Email utente
        user_name: Nome utente
        order_number: Numero ordine
        order_date: Data ordine
        order_items: Lista item ordine
        order_subtotal: Subtotale
        order_tax: IVA
        order_total: Totale
        order_url: URL dettaglio ordine
        dashboard_url: URL dashboard

    Returns:
        bool: True se successo
    """
    context = {
        "subject": f"Conferma Ordine #{order_number} - AI Strategy Hub",
        "user_name": user_name,
        "order_number": order_number,
        "order_date": order_date,
        "order_items": order_items,
        "order_subtotal": order_subtotal,
        "order_tax": order_tax,
        "order_total": order_total,
        "order_url": order_url,
        "dashboard_url": dashboard_url,
    }

    return email_service.send_templated_email(
        to=user_email,
        subject=context["subject"],
        template_name="order_confirmation.html",
        context=context,
    )


def send_invoice_ready_email(
    user_email: str,
    user_name: str,
    invoice_number: str,
    invoice_date: str,
    invoice_subtotal: str,
    invoice_tax: str,
    invoice_total: str,
    invoice_pdf_url: str,
    dashboard_url: str,
    has_pec: bool = False,
) -> bool:
    """
    Invia email fattura disponibile.

    Args:
        user_email: Email utente
        user_name: Nome utente
        invoice_number: Numero fattura
        invoice_date: Data fattura
        invoice_subtotal: Imponibile
        invoice_tax: IVA
        invoice_total: Totale
        invoice_pdf_url: URL download PDF
        dashboard_url: URL dashboard
        has_pec: Se utente ha PEC configurata

    Returns:
        bool: True se successo
    """
    context = {
        "subject": f"Fattura {invoice_number} Disponibile - AI Strategy Hub",
        "user_name": user_name,
        "invoice_number": invoice_number,
        "invoice_date": invoice_date,
        "invoice_subtotal": invoice_subtotal,
        "invoice_tax": invoice_tax,
        "invoice_total": invoice_total,
        "invoice_pdf_url": invoice_pdf_url,
        "dashboard_url": dashboard_url,
        "has_pec": has_pec,
    }

    return email_service.send_templated_email(
        to=user_email,
        subject=context["subject"],
        template_name="invoice_ready.html",
        context=context,
    )


# =============================================================================
# HELPER FUNCTIONS - SUPPORT & NOTIFICATIONS
# =============================================================================


def send_support_ticket_created_email(
    user_email: str,
    user_name: str,
    ticket_id: str,
    ticket_subject: str,
    ticket_url: str,
) -> bool:
    """
    Invia email conferma creazione ticket supporto.

    Args:
        user_email: Email utente
        user_name: Nome utente
        ticket_id: ID ticket
        ticket_subject: Oggetto ticket
        ticket_url: URL ticket

    Returns:
        bool: True se successo
    """
    # TODO: Creare template support_ticket_created.html
    logger.warning("Support ticket email template not implemented yet")
    return False


def send_generic_notification_email(
    user_email: str,
    subject: str,
    message: str,
) -> bool:
    """
    Invia email notifica generica.

    Args:
        user_email: Email destinatario
        subject: Oggetto
        message: Messaggio (HTML)

    Returns:
        bool: True se successo
    """
    # Per notifiche generiche usiamo direttamente MS Graph
    return ms_graph_service.send_email(
        to=user_email,
        subject=subject,
        body_html=message,
    )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def is_email_enabled() -> bool:
    """
    Verifica se invio email è abilitato.

    Returns:
        bool: True se MS Graph configurato
    """
    return ms_graph_service.is_enabled()


def get_available_templates() -> list[str]:
    """
    Ottiene lista template disponibili.

    Returns:
        list[str]: Nomi template
    """
    templates = []
    for file in TEMPLATES_DIR.glob("*.html"):
        if file.name != "base.html":
            templates.append(file.name)
    return sorted(templates)


# =============================================================================
# LOGGING
# =============================================================================

logger.info(
    f"Email service loaded - Templates dir: {TEMPLATES_DIR} - "
    f"Email enabled: {is_email_enabled()}"
)

# Log available templates
available_templates = get_available_templates()
logger.info(f"Available email templates: {', '.join(available_templates)}")
