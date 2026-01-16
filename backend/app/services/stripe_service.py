"""
Modulo: stripe_service.py
Descrizione: Servizio per integrazione Stripe Payment
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from typing import Optional
from decimal import Decimal

import stripe
from fastapi import HTTPException, status

from app.core.config import settings

logger = logging.getLogger(__name__)

# Configura Stripe API key
if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY
else:
    logger.warning("STRIPE_SECRET_KEY not configured - Stripe integration disabled")


class StripeService:
    """Servizio per operazioni Stripe"""

    @staticmethod
    async def create_payment_intent(
        amount: Decimal,
        currency: str = "eur",
        order_id: str = None,
        customer_email: str = None,
        metadata: Optional[dict] = None,
    ) -> dict:
        """
        Crea Stripe Payment Intent.

        Args:
            amount: Importo in formato decimal (es: 100.50)
            currency: Valuta (default: eur)
            order_id: ID ordine per metadata
            customer_email: Email cliente
            metadata: Metadata aggiuntivi

        Returns:
            Dict con client_secret e payment_intent_id

        Raises:
            HTTPException: Se Stripe non configurato o errore API
        """
        if not settings.STRIPE_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe payment not configured",
            )

        try:
            # Converti amount in centesimi (Stripe usa centesimi)
            amount_cents = int(amount * 100)

            # Prepara metadata
            payment_metadata = metadata or {}
            if order_id:
                payment_metadata["order_id"] = order_id

            # Crea Payment Intent
            intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency.lower(),
                receipt_email=customer_email,
                metadata=payment_metadata,
                automatic_payment_methods={"enabled": True},
            )

            logger.info(
                f"Created Payment Intent {intent.id} for order {order_id}: €{amount}"
            )

            return {
                "client_secret": intent.client_secret,
                "payment_intent_id": intent.id,
                "amount": amount,
                "currency": currency,
            }

        except stripe.error.CardError as e:
            # Errore carta
            logger.error(f"Stripe CardError: {e.user_message}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Errore carta: {e.user_message}",
            )

        except stripe.error.InvalidRequestError as e:
            # Parametri invalidi
            logger.error(f"Stripe InvalidRequestError: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parametri pagamento non validi",
            )

        except stripe.error.AuthenticationError as e:
            # API key non valida
            logger.error(f"Stripe AuthenticationError: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Errore configurazione pagamenti",
            )

        except stripe.error.APIConnectionError as e:
            # Errore di rete
            logger.error(f"Stripe APIConnectionError: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Servizio pagamenti temporaneamente non disponibile",
            )

        except stripe.error.StripeError as e:
            # Errore generico Stripe
            logger.error(f"Stripe Error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore durante la creazione del pagamento",
            )

        except Exception as e:
            # Errore imprevisto
            logger.error(f"Unexpected error creating Payment Intent: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore imprevisto durante la creazione del pagamento",
            )

    @staticmethod
    async def retrieve_payment_intent(payment_intent_id: str) -> dict:
        """
        Recupera Payment Intent da Stripe.

        Args:
            payment_intent_id: ID del Payment Intent

        Returns:
            Dict con dati Payment Intent

        Raises:
            HTTPException: Se non trovato o errore
        """
        if not settings.STRIPE_SECRET_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Stripe payment not configured",
            )

        try:
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            return {
                "id": intent.id,
                "status": intent.status,
                "amount": intent.amount / 100,  # Converti da centesimi
                "currency": intent.currency,
                "metadata": intent.metadata,
            }

        except stripe.error.InvalidRequestError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment Intent non trovato",
            )

        except Exception as e:
            logger.error(f"Error retrieving Payment Intent: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Errore durante il recupero del pagamento",
            )

    @staticmethod
    def construct_webhook_event(payload: bytes, sig_header: str):
        """
        Costruisce e verifica webhook event Stripe.

        Args:
            payload: Body della richiesta (bytes)
            sig_header: Header Stripe-Signature

        Returns:
            Stripe Event object

        Raises:
            ValueError: Se signature non valida
        """
        if not settings.STRIPE_WEBHOOK_SECRET:
            raise ValueError("STRIPE_WEBHOOK_SECRET not configured")

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
            return event

        except ValueError as e:
            # Invalid payload
            logger.error(f"Invalid webhook payload: {str(e)}")
            raise

        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            logger.error(f"Invalid webhook signature: {str(e)}")
            raise ValueError("Invalid signature")


# Istanza singleton
stripe_service = StripeService()
