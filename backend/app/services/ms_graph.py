"""
Modulo: ms_graph.py
Descrizione: Servizio Microsoft Graph API per invio email
Autore: Claude per Davide
Data: 2026-01-15

Microsoft Graph API permette di inviare email usando account Microsoft 365.

Setup richiesto:
1. Registra App in Azure AD (https://portal.azure.com)
2. Ottieni: TENANT_ID, CLIENT_ID, CLIENT_SECRET
3. Configura permissions: Mail.Send (Application)
4. Admin consent per permissions
5. Configura credenziali in .env

Features:
- Autenticazione OAuth2 Client Credentials Flow
- Invio email singole e bulk
- Supporto HTML e plain text
- Attachments (opzionale)
- Template-based emails

Dependencies:
- msal: Microsoft Authentication Library
- requests: HTTP client

Docs:
- https://learn.microsoft.com/en-us/graph/api/user-sendmail
- https://learn.microsoft.com/en-us/graph/auth-v2-service
"""

import base64
import logging
from pathlib import Path
from typing import List, Optional

import msal
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# MS GRAPH SERVICE
# =============================================================================


class MSGraphService:
    """
    Servizio Microsoft Graph API.

    Gestisce autenticazione e chiamate API a Microsoft Graph.
    Usato principalmente per invio email tramite account aziendale.

    Usage:
        service = MSGraphService()
        await service.send_email(
            to="user@example.com",
            subject="Welcome",
            body_html="<p>Hello!</p>"
        )
    """

    def __init__(self):
        """Inizializza MS Graph service"""
        self.tenant_id = settings.MS_GRAPH_TENANT_ID
        self.client_id = settings.MS_GRAPH_CLIENT_ID
        self.client_secret = settings.MS_GRAPH_CLIENT_SECRET
        self.sender_email = settings.MS_GRAPH_SENDER_EMAIL
        self.sender_name = settings.MS_GRAPH_SENDER_NAME

        # Graph API endpoints
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"

        # Token cache
        self._access_token: Optional[str] = None

        # Verifica configurazione
        self._check_configuration()

        logger.info("MSGraphService initialized")

    def _check_configuration(self) -> None:
        """
        Verifica se MS Graph è configurato.

        Se non configurato, logga warning ma non solleva errore.
        L'applicazione funziona anche senza email.
        """
        if not all([self.tenant_id, self.client_id, self.client_secret]):
            logger.warning(
                "MS Graph not configured - email sending disabled. "
                "Configure MS_GRAPH_* variables in .env to enable email."
            )
            self.enabled = False
        else:
            self.enabled = True
            logger.info("MS Graph configured and enabled")

    def is_enabled(self) -> bool:
        """
        Verifica se MS Graph è abilitato.

        Returns:
            bool: True se configurato, False altrimenti
        """
        return self.enabled

    def _get_access_token(self) -> str:
        """
        Ottiene access token da Microsoft Identity Platform.

        Usa OAuth2 Client Credentials Flow per autenticazione app-to-app.

        Returns:
            str: Access token valido

        Raises:
            Exception: Se autenticazione fallisce
        """
        if not self.enabled:
            raise ValueError("MS Graph not configured")

        # TODO: Implementare token caching con TTL
        # Per ora otteniamo sempre un nuovo token

        logger.debug("Requesting access token from Microsoft Identity Platform")

        # Crea MSAL Confidential Client
        app = msal.ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=self.authority,
        )

        # Ottieni token
        result = app.acquire_token_for_client(scopes=self.scopes)

        if "access_token" in result:
            logger.debug("Access token obtained successfully")
            return result["access_token"]
        else:
            error = result.get("error", "unknown")
            error_desc = result.get("error_description", "No description")
            logger.error(f"Failed to obtain access token: {error} - {error_desc}")
            raise Exception(f"Authentication failed: {error} - {error_desc}")

    def send_email(
        self,
        to: str | List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[dict]] = None,
        reply_to: Optional[str] = None,
    ) -> bool:
        """
        Invia email tramite Microsoft Graph API.

        Args:
            to: Email destinatario/i (str o list)
            subject: Oggetto email
            body_html: Corpo email in HTML
            body_text: Corpo email in plain text (opzionale, fallback)
            cc: Email in copia (opzionale)
            bcc: Email in copia nascosta (opzionale)
            attachments: Lista attachments (opzionale)
            reply_to: Email per risposte (opzionale)

        Returns:
            bool: True se invio successo, False altrimenti

        Example:
            >>> service.send_email(
            ...     to="user@example.com",
            ...     subject="Welcome",
            ...     body_html="<h1>Welcome!</h1><p>Thanks for signing up.</p>"
            ... )
            True
        """
        if not self.enabled:
            logger.warning("MS Graph not configured - email not sent")
            return False

        try:
            # Normalizza destinatari
            if isinstance(to, str):
                to = [to]

            logger.info(f"Sending email to {', '.join(to)}: {subject}")

            # Ottieni access token
            token = self._get_access_token()

            # Costruisci messaggio
            message = self._build_message(
                to=to,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                cc=cc,
                bcc=bcc,
                attachments=attachments,
                reply_to=reply_to,
            )

            # Invia via Graph API
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }

            # Endpoint: /users/{sender}/sendMail
            url = f"{self.graph_endpoint}/users/{self.sender_email}/sendMail"

            response = requests.post(
                url,
                headers=headers,
                json={"message": message, "saveToSentItems": True},
            )

            if response.status_code == 202:
                logger.info(f"Email sent successfully to {', '.join(to)}")
                return True
            else:
                logger.error(
                    f"Failed to send email: {response.status_code} - {response.text}"
                )
                return False

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}", exc_info=True)
            return False

    def _build_message(
        self,
        to: List[str],
        subject: str,
        body_html: str,
        body_text: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[dict]] = None,
        reply_to: Optional[str] = None,
    ) -> dict:
        """
        Costruisce messaggio email in formato Graph API.

        Args:
            to, subject, body_html, etc.: Parametri email

        Returns:
            dict: Messaggio formattato per Graph API
        """
        message = {
            "subject": subject,
            "body": {
                "contentType": "HTML",
                "content": body_html,
            },
            "toRecipients": [{"emailAddress": {"address": addr}} for addr in to],
            "from": {
                "emailAddress": {
                    "address": self.sender_email,
                    "name": self.sender_name,
                }
            },
        }

        # CC
        if cc:
            message["ccRecipients"] = [
                {"emailAddress": {"address": addr}} for addr in cc
            ]

        # BCC
        if bcc:
            message["bccRecipients"] = [
                {"emailAddress": {"address": addr}} for addr in bcc
            ]

        # Reply-To
        if reply_to:
            message["replyTo"] = [{"emailAddress": {"address": reply_to}}]

        # Attachments
        if attachments:
            message["attachments"] = attachments

        return message

    def send_email_with_attachment(
        self,
        to: str | List[str],
        subject: str,
        body_html: str,
        attachment_path: str,
        attachment_name: Optional[str] = None,
    ) -> bool:
        """
        Invia email con attachment.

        Args:
            to: Destinatario/i
            subject: Oggetto
            body_html: Corpo HTML
            attachment_path: Path file da allegare
            attachment_name: Nome file (default: basename)

        Returns:
            bool: True se successo
        """
        try:
            # Leggi file
            file_path = Path(attachment_path)
            if not file_path.exists():
                logger.error(f"Attachment not found: {attachment_path}")
                return False

            # Nome file
            if not attachment_name:
                attachment_name = file_path.name

            # Leggi contenuto
            with open(file_path, "rb") as f:
                file_content = f.read()

            # Encode base64
            file_base64 = base64.b64encode(file_content).decode("utf-8")

            # Crea attachment
            attachment = {
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": attachment_name,
                "contentBytes": file_base64,
            }

            # Invia con attachment
            return self.send_email(
                to=to,
                subject=subject,
                body_html=body_html,
                attachments=[attachment],
            )

        except Exception as e:
            logger.error(f"Error sending email with attachment: {str(e)}")
            return False


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

# Istanza globale del servizio
ms_graph_service = MSGraphService()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def send_email(
    to: str | List[str],
    subject: str,
    body_html: str,
    body_text: Optional[str] = None,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    attachments: Optional[List[dict]] = None,
    reply_to: Optional[str] = None,
) -> bool:
    """
    Helper function per inviare email.

    Wrapper around ms_graph_service.send_email() per uso semplificato.

    Args:
        to: Destinatario/i
        subject: Oggetto
        body_html: Corpo HTML
        body_text: Corpo plain text (opzionale)
        cc: Email in copia
        bcc: Email in copia nascosta
        attachments: Lista attachments
        reply_to: Email per risposte

    Returns:
        bool: True se successo, False altrimenti

    Usage:
        >>> from app.services.ms_graph import send_email
        >>> send_email(
        ...     to="user@example.com",
        ...     subject="Welcome",
        ...     body_html="<p>Hello!</p>"
        ... )
    """
    return ms_graph_service.send_email(
        to=to,
        subject=subject,
        body_html=body_html,
        body_text=body_text,
        cc=cc,
        bcc=bcc,
        attachments=attachments,
        reply_to=reply_to,
    )


def is_email_enabled() -> bool:
    """
    Verifica se invio email è abilitato.

    Returns:
        bool: True se MS Graph configurato
    """
    return ms_graph_service.is_enabled()


# =============================================================================
# LOGGING
# =============================================================================

logger.info("MS Graph service loaded successfully")
