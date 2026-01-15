"""
Modulo: security.py
Descrizione: Utilities per sicurezza (password hashing, JWT, MFA)
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
import secrets
from datetime import datetime, timedelta
from typing import Any, Optional

import pyotp
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

# =============================================================================
# PASSWORD HASHING (Argon2)
# =============================================================================

# Context per password hashing con Argon2 (OWASP recommended)
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__memory_cost=65536,  # 64 MB
    argon2__time_cost=3,  # 3 iterations
    argon2__parallelism=4,  # 4 threads
)

logger.info("Password context initialized with Argon2")


def hash_password(password: str) -> str:
    """
    Crea hash di una password usando Argon2.

    Args:
        password: Password in chiaro

    Returns:
        str: Hash della password

    Example:
        >>> hashed = hash_password("MySecurePass123!")
        >>> print(hashed)
        $argon2id$v=19$m=65536,t=3,p=4$...
    """
    logger.debug("Hashing password")
    hashed = pwd_context.hash(password)
    logger.debug("Password hashed successfully")
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se una password corrisponde all'hash.

    Args:
        plain_password: Password in chiaro
        hashed_password: Hash da verificare

    Returns:
        bool: True se la password è corretta

    Example:
        >>> is_valid = verify_password("MyPass123", hashed)
        >>> print(is_valid)
        True
    """
    logger.debug("Verifying password")
    try:
        is_valid = pwd_context.verify(plain_password, hashed_password)
        if is_valid:
            logger.debug("Password verification: SUCCESS")
        else:
            logger.debug("Password verification: FAILED")
        return is_valid
    except Exception as e:
        logger.error(f"Password verification error: {str(e)}", exc_info=True)
        return False


# =============================================================================
# JWT TOKEN MANAGEMENT
# =============================================================================

def create_access_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[dict[str, Any]] = None,
) -> str:
    """
    Crea JWT access token.

    Args:
        subject: Subject del token (tipicamente user_id)
        expires_delta: Durata token (default da settings)
        additional_claims: Claims aggiuntivi (role, permissions, etc.)

    Returns:
        str: JWT token

    Example:
        >>> token = create_access_token(
        ...     subject=str(user.id),
        ...     additional_claims={"role": "admin"}
        ... )
    """
    logger.debug(f"Creating access token for subject: {subject}")

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # Claims JWT standard
    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "access",
    }

    # Aggiungi claims custom
    if additional_claims:
        to_encode.update(additional_claims)
        logger.debug(f"Added additional claims: {list(additional_claims.keys())}")

    # Crea token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    logger.info(f"Access token created for {subject}, expires at {expire}")
    return encoded_jwt


def create_refresh_token(subject: str) -> str:
    """
    Crea JWT refresh token (durata più lunga).

    Args:
        subject: Subject del token (user_id)

    Returns:
        str: JWT refresh token

    Example:
        >>> refresh_token = create_refresh_token(str(user.id))
    """
    logger.debug(f"Creating refresh token for subject: {subject}")

    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        "exp": expire,
        "sub": str(subject),
        "iat": datetime.utcnow(),
        "type": "refresh",
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    logger.info(f"Refresh token created for {subject}, expires at {expire}")
    return encoded_jwt


def decode_token(token: str) -> Optional[dict[str, Any]]:
    """
    Decodifica e valida JWT token.

    Args:
        token: JWT token da decodificare

    Returns:
        dict: Payload del token, None se invalido

    Example:
        >>> payload = decode_token(token)
        >>> if payload:
        ...     user_id = payload["sub"]
    """
    try:
        logger.debug("Decoding JWT token")
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        logger.debug(f"Token decoded successfully, subject: {payload.get('sub')}")
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}", exc_info=True)
        return None


# =============================================================================
# MFA (TOTP - Time-based One-Time Password)
# =============================================================================

def generate_mfa_secret() -> str:
    """
    Genera secret per TOTP (Google Authenticator, Authy, etc.).

    Returns:
        str: Base32 encoded secret

    Example:
        >>> secret = generate_mfa_secret()
        >>> print(secret)
        JBSWY3DPEHPK3PXP
    """
    logger.debug("Generating MFA secret")
    secret = pyotp.random_base32()
    logger.info("MFA secret generated")
    return secret


def verify_mfa_token(secret: str, token: str) -> bool:
    """
    Verifica TOTP token.

    Args:
        secret: MFA secret dell'utente
        token: 6-digit OTP fornito dall'utente

    Returns:
        bool: True se token valido

    Example:
        >>> is_valid = verify_mfa_token(user.mfa_secret, "123456")
    """
    logger.debug("Verifying MFA token")

    try:
        totp = pyotp.TOTP(secret)
        is_valid = totp.verify(token, valid_window=1)  # Accept 1 window before/after

        if is_valid:
            logger.info("MFA token verification: SUCCESS")
        else:
            logger.warning("MFA token verification: FAILED")

        return is_valid
    except Exception as e:
        logger.error(f"MFA verification error: {str(e)}", exc_info=True)
        return False


def get_mfa_provisioning_uri(secret: str, email: str) -> str:
    """
    Genera URI per QR code setup MFA.

    Args:
        secret: MFA secret
        email: Email utente

    Returns:
        str: otpauth:// URI per QR code

    Example:
        >>> uri = get_mfa_provisioning_uri(secret, "user@example.com")
        >>> # Generate QR code from this URI
    """
    logger.debug(f"Generating MFA provisioning URI for {email}")

    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(
        name=email,
        issuer_name=settings.PROJECT_NAME,
    )

    logger.debug("MFA provisioning URI generated")
    return uri


# =============================================================================
# BACKUP CODES (per MFA recovery)
# =============================================================================

def generate_backup_codes(count: int = 8) -> list[str]:
    """
    Genera backup codes per MFA recovery.

    Args:
        count: Numero di backup codes da generare

    Returns:
        list[str]: Lista di backup codes (plain text)

    Example:
        >>> codes = generate_backup_codes()
        >>> print(codes)
        ['A1B2C3D4', 'E5F6G7H8', ...]

    Note:
        I codes devono essere hashati prima di salvarli nel database!
    """
    logger.debug(f"Generating {count} backup codes")

    codes = []
    for _ in range(count):
        # Genera 8 caratteri alfanumerici maiuscoli
        code = secrets.token_hex(4).upper()
        codes.append(code)

    logger.info(f"Generated {count} backup codes")
    return codes


def hash_backup_codes(codes: list[str]) -> list[str]:
    """
    Hash backup codes prima di salvarli nel database.

    Args:
        codes: Lista di backup codes in chiaro

    Returns:
        list[str]: Lista di backup codes hashati

    Example:
        >>> plain_codes = generate_backup_codes()
        >>> hashed_codes = hash_backup_codes(plain_codes)
        >>> # Save hashed_codes to database
        >>> # Show plain_codes to user ONCE
    """
    logger.debug(f"Hashing {len(codes)} backup codes")

    hashed = [hash_password(code) for code in codes]

    logger.debug("Backup codes hashed successfully")
    return hashed


def verify_backup_code(plain_code: str, hashed_codes: list[str]) -> bool:
    """
    Verifica se un backup code è valido.

    Args:
        plain_code: Backup code fornito dall'utente
        hashed_codes: Lista di backup codes hashati dal database

    Returns:
        bool: True se il code è valido

    Example:
        >>> is_valid = verify_backup_code(user_input, user.backup_codes)
    """
    logger.debug("Verifying backup code")

    for hashed in hashed_codes:
        if verify_password(plain_code, hashed):
            logger.info("Backup code verification: SUCCESS")
            return True

    logger.warning("Backup code verification: FAILED")
    return False


# =============================================================================
# RANDOM TOKENS (email verification, password reset)
# =============================================================================

def generate_random_token(length: int = 32) -> str:
    """
    Genera token random sicuro.

    Args:
        length: Lunghezza del token in bytes (output sarà length*2 hex chars)

    Returns:
        str: Token hexadecimal

    Example:
        >>> token = generate_random_token()
        >>> print(len(token))
        64
    """
    logger.debug(f"Generating random token ({length} bytes)")
    token = secrets.token_hex(length)
    logger.debug("Random token generated")
    return token


# =============================================================================
# API KEY GENERATION
# =============================================================================

def generate_api_key() -> str:
    """
    Genera API key per integrazioni esterne.

    Returns:
        str: API key con prefisso 'ash_' (AI Strategy Hub)

    Example:
        >>> api_key = generate_api_key()
        >>> print(api_key)
        ash_1a2b3c4d5e6f...
    """
    logger.debug("Generating API key")

    # Prefisso per identificare API keys
    prefix = "ash_"

    # 32 bytes random = 64 hex chars
    random_part = secrets.token_hex(32)

    api_key = f"{prefix}{random_part}"

    logger.info("API key generated")
    return api_key


logger.info("Security module initialized")
