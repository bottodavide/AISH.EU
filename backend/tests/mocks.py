"""
Modulo: mocks.py
Descrizione: Mock classes per servizi esterni
Autore: Claude per Davide
Data: 2026-01-18

Mock services disponibili:
- MockStripeService: Mock Stripe API (Payment Intents, webhooks)
- MockMSGraphService: Mock Microsoft Graph email service
- MockClaudeService: Mock Claude API service
"""

import logging
from decimal import Decimal
from typing import Any, Dict, Optional
from unittest.mock import Mock
import uuid

logger = logging.getLogger(__name__)

# =============================================================================
# STRIPE MOCK SERVICE
# =============================================================================


class MockStripeService:
    """
    Mock service per Stripe API.

    Simula operazioni Stripe senza chiamare API reale:
    - create_payment_intent()
    - retrieve_payment_intent()
    - construct_webhook_event()
    - refund_payment()
    """

    def __init__(self):
        """Inizializza mock service con storage interno."""
        self.payment_intents: Dict[str, Dict[str, Any]] = {}
        self.events: Dict[str, Dict[str, Any]] = {}
        logger.info("MockStripeService initialized")

    def create_payment_intent(
        self,
        amount: int,
        currency: str = "eur",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Mock creazione Payment Intent.

        Args:
            amount: Importo in centesimi (es: 10000 = €100.00)
            currency: Valuta (default: eur)
            metadata: Metadata custom

        Returns:
            dict: Mock Payment Intent object
        """
        pi_id = f"pi_test_{uuid.uuid4().hex[:16]}"
        client_secret = f"{pi_id}_secret_{uuid.uuid4().hex[:8]}"

        payment_intent = {
            "id": pi_id,
            "object": "payment_intent",
            "amount": amount,
            "currency": currency,
            "status": "requires_payment_method",
            "client_secret": client_secret,
            "metadata": metadata or {},
            "created": 1234567890,
            "payment_method_types": ["card"],
        }

        # Salva in storage interno
        self.payment_intents[pi_id] = payment_intent

        logger.debug(f"Mock Payment Intent created: {pi_id} (amount={amount})")
        return payment_intent

    def retrieve_payment_intent(self, payment_intent_id: str) -> Dict[str, Any]:
        """
        Mock retrieve Payment Intent.

        Args:
            payment_intent_id: ID Payment Intent

        Returns:
            dict: Mock Payment Intent object

        Raises:
            ValueError: Se Payment Intent non trovato
        """
        if payment_intent_id not in self.payment_intents:
            raise ValueError(f"Payment Intent not found: {payment_intent_id}")

        logger.debug(f"Mock Payment Intent retrieved: {payment_intent_id}")
        return self.payment_intents[payment_intent_id]

    def update_payment_intent_status(
        self,
        payment_intent_id: str,
        status: str,
    ) -> Dict[str, Any]:
        """
        Mock update status Payment Intent.

        Args:
            payment_intent_id: ID Payment Intent
            status: Nuovo status (succeeded, failed, etc.)

        Returns:
            dict: Payment Intent aggiornato
        """
        if payment_intent_id not in self.payment_intents:
            raise ValueError(f"Payment Intent not found: {payment_intent_id}")

        self.payment_intents[payment_intent_id]["status"] = status

        logger.debug(f"Mock Payment Intent status updated: {payment_intent_id} -> {status}")
        return self.payment_intents[payment_intent_id]

    def construct_webhook_event(
        self,
        event_type: str,
        payment_intent_id: str,
        signature: str = "mock_signature",
    ) -> Dict[str, Any]:
        """
        Mock costruzione webhook event.

        Args:
            event_type: Tipo evento (es: payment_intent.succeeded)
            payment_intent_id: ID Payment Intent
            signature: Mock signature (non verificata)

        Returns:
            dict: Mock Stripe Event object
        """
        if payment_intent_id not in self.payment_intents:
            raise ValueError(f"Payment Intent not found: {payment_intent_id}")

        event_id = f"evt_test_{uuid.uuid4().hex[:16]}"
        payment_intent = self.payment_intents[payment_intent_id]

        event = {
            "id": event_id,
            "object": "event",
            "type": event_type,
            "data": {
                "object": payment_intent,
            },
            "created": 1234567890,
        }

        # Salva evento
        self.events[event_id] = event

        logger.debug(f"Mock Webhook Event created: {event_id} (type={event_type})")
        return event

    def refund_payment(
        self,
        payment_intent_id: str,
        amount: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Mock refund pagamento.

        Args:
            payment_intent_id: ID Payment Intent
            amount: Importo da rimborsare in centesimi (None = full refund)

        Returns:
            dict: Mock Refund object
        """
        if payment_intent_id not in self.payment_intents:
            raise ValueError(f"Payment Intent not found: {payment_intent_id}")

        pi = self.payment_intents[payment_intent_id]
        refund_amount = amount if amount is not None else pi["amount"]

        refund = {
            "id": f"re_test_{uuid.uuid4().hex[:16]}",
            "object": "refund",
            "amount": refund_amount,
            "currency": pi["currency"],
            "payment_intent": payment_intent_id,
            "status": "succeeded",
            "created": 1234567890,
        }

        # Aggiorna status Payment Intent
        self.payment_intents[payment_intent_id]["status"] = "refunded"

        logger.debug(f"Mock Refund created: {refund['id']} (amount={refund_amount})")
        return refund


# =============================================================================
# MS GRAPH MOCK SERVICE
# =============================================================================


class MockMSGraphService:
    """
    Mock service per Microsoft Graph API.

    Simula invio email senza chiamare API reale:
    - send_email()
    - send_template_email()
    """

    def __init__(self):
        """Inizializza mock service con storage email inviate."""
        self.sent_emails: list[Dict[str, Any]] = []
        logger.info("MockMSGraphService initialized")

    def send_email(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        from_email: str = "noreply@aistrategyhub.eu",
    ) -> bool:
        """
        Mock invio email.

        Args:
            to_email: Destinatario
            subject: Oggetto email
            body_html: Body HTML
            from_email: Mittente (default: noreply)

        Returns:
            bool: True (sempre successo nel mock)
        """
        email = {
            "id": uuid.uuid4().hex,
            "from": from_email,
            "to": to_email,
            "subject": subject,
            "body_html": body_html,
            "sent_at": "2026-01-18T12:00:00Z",
        }

        self.sent_emails.append(email)

        logger.debug(f"Mock Email sent: to={to_email}, subject={subject}")
        return True

    def send_template_email(
        self,
        to_email: str,
        template_name: str,
        template_data: Dict[str, Any],
    ) -> bool:
        """
        Mock invio email con template.

        Args:
            to_email: Destinatario
            template_name: Nome template
            template_data: Dati per template

        Returns:
            bool: True (sempre successo nel mock)
        """
        email = {
            "id": uuid.uuid4().hex,
            "from": "noreply@aistrategyhub.eu",
            "to": to_email,
            "template_name": template_name,
            "template_data": template_data,
            "sent_at": "2026-01-18T12:00:00Z",
        }

        self.sent_emails.append(email)

        logger.debug(f"Mock Template Email sent: to={to_email}, template={template_name}")
        return True

    def get_sent_emails(self, to_email: Optional[str] = None) -> list[Dict[str, Any]]:
        """
        Recupera email inviate (per asserzioni nei test).

        Args:
            to_email: Filtra per destinatario (opzionale)

        Returns:
            list: Lista email inviate
        """
        if to_email:
            return [email for email in self.sent_emails if email["to"] == to_email]
        return self.sent_emails

    def clear_sent_emails(self):
        """Cancella tutte le email inviate (cleanup tra test)."""
        self.sent_emails = []
        logger.debug("Mock sent emails cleared")


# =============================================================================
# CLAUDE MOCK SERVICE
# =============================================================================


class MockClaudeService:
    """
    Mock service per Claude API.

    Simula interazioni con Claude API senza chiamare API reale:
    - chat_completion()
    - stream_completion()
    """

    def __init__(self):
        """Inizializza mock service."""
        self.conversations: list[Dict[str, Any]] = []
        logger.info("MockClaudeService initialized")

    def chat_completion(
        self,
        messages: list[Dict[str, str]],
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Mock chat completion.

        Args:
            messages: Lista messaggi conversazione
            system_prompt: System prompt (opzionale)
            max_tokens: Max tokens output

        Returns:
            dict: Mock response da Claude
        """
        conversation_id = uuid.uuid4().hex

        response = {
            "id": f"msg_test_{conversation_id[:16]}",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "This is a mock response from Claude API. "
                           "In a real scenario, this would contain AI-generated content.",
                }
            ],
            "model": "claude-sonnet-4-5-20250929",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": len(str(messages)) // 4,  # Rough estimate
                "output_tokens": 50,
            },
        }

        # Salva conversazione
        self.conversations.append({
            "conversation_id": conversation_id,
            "messages": messages,
            "response": response,
        })

        logger.debug(f"Mock Claude completion: conv_id={conversation_id}")
        return response

    def stream_completion(
        self,
        messages: list[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ):
        """
        Mock streaming completion.

        Args:
            messages: Lista messaggi conversazione
            system_prompt: System prompt (opzionale)

        Yields:
            dict: Mock chunks di response
        """
        # Simula streaming con chunks
        chunks = [
            "This ",
            "is ",
            "a ",
            "mock ",
            "streaming ",
            "response.",
        ]

        for chunk in chunks:
            yield {
                "type": "content_block_delta",
                "delta": {
                    "type": "text_delta",
                    "text": chunk,
                },
            }

        # Final chunk
        yield {
            "type": "message_stop",
            "usage": {
                "input_tokens": 20,
                "output_tokens": 10,
            },
        }

        logger.debug("Mock Claude streaming completed")

    def get_conversations(self) -> list[Dict[str, Any]]:
        """
        Recupera conversazioni salvate (per asserzioni nei test).

        Returns:
            list: Lista conversazioni
        """
        return self.conversations

    def clear_conversations(self):
        """Cancella tutte le conversazioni (cleanup tra test)."""
        self.conversations = []
        logger.debug("Mock conversations cleared")


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================


def create_mock_stripe() -> MockStripeService:
    """
    Crea istanza MockStripeService.

    Returns:
        MockStripeService: Mock service pronto all'uso
    """
    return MockStripeService()


def create_mock_ms_graph() -> MockMSGraphService:
    """
    Crea istanza MockMSGraphService.

    Returns:
        MockMSGraphService: Mock service pronto all'uso
    """
    return MockMSGraphService()


def create_mock_claude() -> MockClaudeService:
    """
    Crea istanza MockClaudeService.

    Returns:
        MockClaudeService: Mock service pronto all'uso
    """
    return MockClaudeService()


logger.info("Test mocks loaded successfully")
