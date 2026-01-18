"""
Modulo: assertions.py
Descrizione: Utility functions per asserzioni personalizzate nei test
Autore: Claude per Davide
Data: 2026-01-18

Utility disponibili:
- assert_decimal_equal(): Confronto decimali con precisione
- assert_uuid_valid(): Validazione formato UUID
- assert_jwt_valid(): Validazione structure JWT token
- assert_email_format(): Validazione formato email
- assert_iban_format(): Validazione formato IBAN
- assert_vat_number(): Validazione P.IVA italiana
"""

import logging
import re
import uuid
from decimal import Decimal
from typing import Any, Dict, Optional

from jose import jwt, JWTError

from app.core.config import settings

logger = logging.getLogger(__name__)

# =============================================================================
# DECIMAL ASSERTIONS
# =============================================================================


def assert_decimal_equal(
    actual: Decimal,
    expected: Decimal,
    places: int = 2,
    msg: Optional[str] = None,
):
    """
    Assert che due Decimal siano uguali con precisione specificata.

    Args:
        actual: Valore attuale
        expected: Valore atteso
        places: Numero decimali per confronto (default: 2)
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se i valori non sono uguali

    Example:
        >>> assert_decimal_equal(Decimal("100.005"), Decimal("100.00"), places=2)
        # Passa (arrotondamento a 2 decimali)
    """
    # Arrotonda a precisione specificata
    actual_rounded = actual.quantize(Decimal(10) ** -places)
    expected_rounded = expected.quantize(Decimal(10) ** -places)

    if actual_rounded != expected_rounded:
        error_msg = (
            msg or
            f"Decimals not equal: {actual_rounded} != {expected_rounded} "
            f"(precision={places} places)"
        )
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.debug(f"Decimal assertion passed: {actual_rounded} == {expected_rounded}")


def assert_decimal_in_range(
    value: Decimal,
    min_value: Decimal,
    max_value: Decimal,
    msg: Optional[str] = None,
):
    """
    Assert che un Decimal sia in un range specificato.

    Args:
        value: Valore da verificare
        min_value: Valore minimo (incluso)
        max_value: Valore massimo (incluso)
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se valore fuori range
    """
    if not (min_value <= value <= max_value):
        error_msg = (
            msg or
            f"Value {value} not in range [{min_value}, {max_value}]"
        )
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.debug(f"Decimal range assertion passed: {min_value} <= {value} <= {max_value}")


# =============================================================================
# UUID ASSERTIONS
# =============================================================================


def assert_uuid_valid(value: Any, msg: Optional[str] = None):
    """
    Assert che un valore sia un UUID valido.

    Args:
        value: Valore da verificare (str o UUID)
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se non è un UUID valido

    Example:
        >>> assert_uuid_valid("123e4567-e89b-12d3-a456-426614174000")
        # Passa
        >>> assert_uuid_valid("not-a-uuid")
        # Fallisce
    """
    try:
        # Tenta conversione a UUID
        if isinstance(value, str):
            uuid.UUID(value)
        elif not isinstance(value, uuid.UUID):
            raise ValueError("Not a UUID type")

        logger.debug(f"UUID assertion passed: {value}")

    except (ValueError, AttributeError) as e:
        error_msg = msg or f"Invalid UUID format: {value}"
        logger.error(error_msg)
        raise AssertionError(error_msg) from e


# =============================================================================
# JWT ASSERTIONS
# =============================================================================


def assert_jwt_valid(
    token: str,
    expected_claims: Optional[Dict[str, Any]] = None,
    msg: Optional[str] = None,
):
    """
    Assert che un JWT token sia valido e contenga claims attesi.

    Args:
        token: JWT token string
        expected_claims: Claims attesi nel payload (opzionale)
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se token non valido o claims non corrispondono

    Example:
        >>> assert_jwt_valid(
        ...     token="eyJ0eXAiOiJKV1QiLCJhbGc...",
        ...     expected_claims={"sub": "user_id_123", "role": "admin"}
        ... )
    """
    try:
        # Decode JWT
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        logger.debug(f"JWT decoded successfully: {payload}")

        # Verifica expected claims se specificati
        if expected_claims:
            for key, expected_value in expected_claims.items():
                actual_value = payload.get(key)
                if actual_value != expected_value:
                    error_msg = (
                        f"JWT claim mismatch: {key}={actual_value}, "
                        f"expected {expected_value}"
                    )
                    logger.error(error_msg)
                    raise AssertionError(error_msg)

        logger.debug("JWT assertion passed with all expected claims")

    except JWTError as e:
        error_msg = msg or f"Invalid JWT token: {str(e)}"
        logger.error(error_msg)
        raise AssertionError(error_msg) from e


def assert_jwt_expired(token: str, msg: Optional[str] = None):
    """
    Assert che un JWT token sia scaduto.

    Args:
        token: JWT token string
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se token ancora valido
    """
    try:
        # Tenta decode (dovrebbe fallire per expiration)
        jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Se arriviamo qui, il token è ancora valido
        error_msg = msg or "JWT token is still valid (expected expired)"
        logger.error(error_msg)
        raise AssertionError(error_msg)

    except JWTError as e:
        # Verifica che sia errore di expiration
        if "expired" in str(e).lower():
            logger.debug("JWT expiration assertion passed")
        else:
            # Altro tipo di errore JWT
            error_msg = f"JWT error (not expiration): {str(e)}"
            logger.error(error_msg)
            raise AssertionError(error_msg) from e


# =============================================================================
# EMAIL ASSERTIONS
# =============================================================================


def assert_email_format(email: str, msg: Optional[str] = None):
    """
    Assert che una stringa sia un formato email valido.

    Args:
        email: Stringa email
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se formato email non valido

    Example:
        >>> assert_email_format("test@example.com")
        # Passa
        >>> assert_email_format("not-an-email")
        # Fallisce
    """
    # Regex semplice per validazione email
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(email_pattern, email):
        error_msg = msg or f"Invalid email format: {email}"
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.debug(f"Email format assertion passed: {email}")


# =============================================================================
# ITALIAN TAX CODE ASSERTIONS
# =============================================================================


def assert_vat_number(vat: str, msg: Optional[str] = None):
    """
    Assert che una P.IVA italiana sia valida.

    Formato: IT + 11 cifre (es: IT12345678901)

    Args:
        vat: Partita IVA
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se P.IVA non valida
    """
    # Pattern P.IVA italiana: IT + 11 cifre
    vat_pattern = r'^IT\d{11}$'

    if not re.match(vat_pattern, vat):
        error_msg = msg or f"Invalid Italian VAT number format: {vat}"
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.debug(f"VAT number assertion passed: {vat}")


def assert_fiscal_code(cf: str, msg: Optional[str] = None):
    """
    Assert che un Codice Fiscale italiano sia valido (formato base).

    Formato: 16 caratteri alfanumerici

    Args:
        cf: Codice Fiscale
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se CF non valido

    Note:
        Questa è una validazione semplice del formato.
        Per validazione completa con checksum, serve algoritmo più complesso.
    """
    # Pattern CF: 6 lettere + 2 cifre + 1 lettera + 2 cifre + 4 alfanumerici + 1 lettera
    cf_pattern = r'^[A-Z]{6}\d{2}[A-Z]\d{2}[A-Z\d]{4}[A-Z]$'

    if not re.match(cf_pattern, cf.upper()):
        error_msg = msg or f"Invalid Italian fiscal code format: {cf}"
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.debug(f"Fiscal code assertion passed: {cf}")


# =============================================================================
# IBAN ASSERTIONS
# =============================================================================


def assert_iban_format(iban: str, msg: Optional[str] = None):
    """
    Assert che un IBAN sia valido (formato base).

    Formato: 2 lettere (country) + 2 cifre (check) + fino a 30 alfanumerici

    Args:
        iban: IBAN code
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se IBAN non valido

    Note:
        Questa è una validazione semplice del formato.
        Per validazione completa con checksum, serve algoritmo specifico.
    """
    # Rimuovi spazi
    iban_clean = iban.replace(" ", "")

    # Pattern IBAN: 2 lettere + 2 cifre + fino a 30 alfanumerici
    iban_pattern = r'^[A-Z]{2}\d{2}[A-Z0-9]{1,30}$'

    if not re.match(iban_pattern, iban_clean.upper()):
        error_msg = msg or f"Invalid IBAN format: {iban}"
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.debug(f"IBAN format assertion passed: {iban_clean}")


# =============================================================================
# JSON RESPONSE ASSERTIONS
# =============================================================================


def assert_response_has_keys(
    response_data: Dict[str, Any],
    required_keys: list[str],
    msg: Optional[str] = None,
):
    """
    Assert che una response JSON contenga tutte le chiavi richieste.

    Args:
        response_data: Dizionario response
        required_keys: Lista chiavi richieste
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se mancano chiavi

    Example:
        >>> assert_response_has_keys(
        ...     {"id": 1, "name": "Test"},
        ...     ["id", "name", "email"]
        ... )
        # Fallisce perché manca "email"
    """
    missing_keys = [key for key in required_keys if key not in response_data]

    if missing_keys:
        error_msg = (
            msg or
            f"Response missing required keys: {missing_keys}. "
            f"Available keys: {list(response_data.keys())}"
        )
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.debug(f"Response keys assertion passed: all {len(required_keys)} keys present")


def assert_response_structure(
    response_data: Dict[str, Any],
    expected_structure: Dict[str, type],
    msg: Optional[str] = None,
):
    """
    Assert che una response JSON abbia la struttura attesa (chiavi + tipi).

    Args:
        response_data: Dizionario response
        expected_structure: Dict {key: expected_type}
        msg: Messaggio errore custom

    Raises:
        AssertionError: Se struttura non corrisponde

    Example:
        >>> assert_response_structure(
        ...     {"id": 1, "name": "Test", "active": True},
        ...     {"id": int, "name": str, "active": bool}
        ... )
        # Passa
    """
    errors = []

    for key, expected_type in expected_structure.items():
        if key not in response_data:
            errors.append(f"Missing key: {key}")
            continue

        actual_type = type(response_data[key])
        if actual_type != expected_type:
            errors.append(
                f"Key '{key}': expected type {expected_type.__name__}, "
                f"got {actual_type.__name__}"
            )

    if errors:
        error_msg = msg or f"Response structure errors: {'; '.join(errors)}"
        logger.error(error_msg)
        raise AssertionError(error_msg)

    logger.debug(f"Response structure assertion passed: {len(expected_structure)} fields validated")


logger.info("Test assertions loaded successfully")
