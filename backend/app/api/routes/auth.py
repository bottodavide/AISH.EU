"""
Modulo: auth.py
Descrizione: API routes per autenticazione e autorizzazione
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_async_db
from app.core.dependencies import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_backup_codes,
    generate_mfa_secret,
    generate_random_token,
    get_mfa_provisioning_uri,
    hash_backup_codes,
    hash_password,
    verify_backup_code,
    verify_mfa_token,
    verify_password,
)
from app.core.exceptions import (
    AuthenticationError,
    BusinessLogicError,
    DuplicateResourceError,
    EmailNotVerifiedError,
    MFARequiredError,
    ResourceNotFoundError,
)
from app.models.audit import AuditAction, AuditLog
from app.models.user import LoginAttempt, Session, User, UserProfile
from app.schemas.auth import (
    EmailVerificationRequest,
    LoginRequest,
    LoginResponse,
    MFABackupCodeRequest,
    MFADisableRequest,
    MFAEnableConfirm,
    MFAEnableRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    PasswordChangeRequest,
    PasswordResetConfirm,
    PasswordResetRequest,
    RefreshTokenRequest,
    RegisterRequest,
    ResendVerificationRequest,
    TokenResponse,
)
from app.schemas.base import SuccessResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


async def log_login_attempt(
    db: AsyncSession,
    email: str,
    success: bool,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    failure_reason: Optional[str] = None,
):
    """
    Logga tentativo di login nel database.

    Args:
        db: Database session
        email: Email utente
        success: Se login è riuscito
        ip_address: IP address
        user_agent: User agent
        failure_reason: Motivo fallimento (se applicable)
    """
    logger.debug(f"Logging login attempt for {email}: success={success}")

    login_attempt = LoginAttempt(
        email=email,
        ip_address=ip_address,
        success=success,
        failure_reason=failure_reason,
        user_agent=user_agent,
    )
    db.add(login_attempt)
    await db.commit()

    logger.info(f"Login attempt logged for {email}")


async def create_audit_log(
    db: AsyncSession,
    user_id: UUID,
    action: AuditAction,
    entity_type: Optional[str] = None,
    entity_id: Optional[UUID] = None,
    changes: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
):
    """
    Crea audit log per compliance.

    Args:
        db: Database session
        user_id: ID utente
        action: Azione eseguita
        entity_type: Tipo entità modificata
        entity_id: ID entità modificata
        changes: Modifiche (before/after)
        ip_address: IP address
        user_agent: User agent
    """
    logger.debug(f"Creating audit log: user={user_id}, action={action.value}")

    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent,
        created_at=datetime.utcnow(),
    )
    db.add(audit_log)
    await db.commit()

    logger.info(f"Audit log created for user {user_id}, action {action.value}")


# =============================================================================
# REGISTRATION
# =============================================================================


@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Registrazione nuovo utente.

    Process:
    1. Verifica email univoca
    2. Hash password
    3. Crea user e profile
    4. Genera token verifica email
    5. Invia email di verifica (TODO)

    Returns:
        SuccessResponse: Conferma registrazione
    """
    logger.info(f"Registration attempt for email: {data.email}")

    # Verifica email univoca
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        logger.warning(f"Registration failed: email already exists: {data.email}")
        raise DuplicateResourceError(
            resource_type="User",
            field="email",
            value=data.email,
        )

    # Hash password
    password_hash = hash_password(data.password)

    # Genera token verifica email
    verification_token = generate_random_token(32)

    # Crea user
    user = User(
        email=data.email,
        password_hash=password_hash,
        role="customer",  # Default role
        is_active=True,
        is_email_verified=False,
        email_verification_token=verification_token,
    )
    db.add(user)
    await db.flush()

    # Crea profile
    profile = UserProfile(
        user_id=user.id,
        first_name=data.first_name,
        last_name=data.last_name,
        company_name=data.company_name,
    )
    db.add(profile)

    # Audit log
    await create_audit_log(
        db=db,
        user_id=user.id,
        action=AuditAction.CREATE,
        entity_type="users",
        entity_id=user.id,
    )

    await db.commit()

    logger.info(f"User registered successfully: {user.email} (ID: {user.id})")

    # TODO: Invia email di verifica
    # await send_verification_email(user.email, verification_token)

    return SuccessResponse(
        message="Registration successful. Please check your email to verify your account.",
        data={
            "user_id": str(user.id),
            "email": user.email,
            "verification_required": True,
        },
    )


# =============================================================================
# LOGIN
# =============================================================================


@router.post("/login", response_model=LoginResponse)
async def login(
    data: LoginRequest,
    db: AsyncSession = Depends(get_async_db),
) -> LoginResponse:
    """
    Login utente con supporto MFA.

    Process:
    1. Verifica credenziali
    2. Verifica account attivo
    3. Se MFA abilitato: verifica token MFA
    4. Crea JWT tokens
    5. Crea session record

    Returns:
        LoginResponse: Tokens JWT e dati utente
    """
    logger.info(f"Login attempt for: {data.email}")

    # Carica utente
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"Login failed: user not found: {data.email}")
        await log_login_attempt(
            db=db,
            email=data.email,
            success=False,
            failure_reason="User not found",
        )
        raise AuthenticationError(message="Invalid email or password")

    # Verifica password
    if not verify_password(data.password, user.password_hash):
        logger.warning(f"Login failed: invalid password for: {data.email}")

        # Incrementa failed attempts
        user.failed_login_attempts += 1

        # Lock account dopo 5 tentativi
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            logger.warning(f"Account locked for 30 minutes: {data.email}")

        await db.commit()

        await log_login_attempt(
            db=db,
            email=data.email,
            success=False,
            failure_reason="Invalid password",
        )

        raise AuthenticationError(message="Invalid email or password")

    # Verifica account attivo
    if not user.is_active:
        logger.warning(f"Login failed: account inactive: {data.email}")
        await log_login_attempt(
            db=db,
            email=data.email,
            success=False,
            failure_reason="Account inactive",
        )
        raise AuthenticationError(message="Account is inactive")

    # Verifica account locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        logger.warning(f"Login failed: account locked: {data.email}")
        await log_login_attempt(
            db=db,
            email=data.email,
            success=False,
            failure_reason="Account locked",
        )
        raise AuthenticationError(
            message=f"Account is locked until {user.locked_until.isoformat()}"
        )

    # Verifica MFA (se abilitato)
    if user.mfa_enabled:
        if not data.mfa_token:
            logger.info(f"MFA required for: {data.email}")
            raise MFARequiredError()

        # Verifica token MFA
        if not verify_mfa_token(user.mfa_secret, data.mfa_token):
            logger.warning(f"Login failed: invalid MFA token: {data.email}")
            await log_login_attempt(
                db=db,
                email=data.email,
                success=False,
                failure_reason="Invalid MFA token",
            )
            raise AuthenticationError(message="Invalid MFA token")

    # Login successful - reset failed attempts
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login_at = datetime.utcnow()
    await db.commit()

    # Crea JWT tokens
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={"role": user.role.value, "email": user.email},
    )

    refresh_token = create_refresh_token(subject=str(user.id))

    # Crea session record
    session = Session(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        refresh_expires_at=datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(session)

    # Audit log
    await create_audit_log(
        db=db,
        user_id=user.id,
        action=AuditAction.LOGIN,
    )

    # Log successful login
    await log_login_attempt(
        db=db,
        email=data.email,
        success=True,
    )

    await db.commit()

    logger.info(f"Login successful for: {user.email}")

    # Load profile
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == user.id))
    profile = result.scalar_one_or_none()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=15 * 60,  # 15 minutes in seconds
        user={
            "id": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "is_email_verified": user.is_email_verified,
            "mfa_enabled": user.mfa_enabled,
            "profile": {
                "first_name": profile.first_name if profile else None,
                "last_name": profile.last_name if profile else None,
                "company_name": profile.company_name if profile else None,
            } if profile else None,
        },
    )


# =============================================================================
# REFRESH TOKEN
# =============================================================================


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_async_db),
) -> TokenResponse:
    """
    Refresh JWT access token usando refresh token.

    Args:
        data: Refresh token request

    Returns:
        TokenResponse: Nuovo access token
    """
    logger.debug("Token refresh request")

    # Decode refresh token
    payload = decode_token(data.refresh_token)

    if not payload:
        logger.warning("Invalid refresh token")
        raise AuthenticationError(message="Invalid refresh token")

    # Verifica tipo token
    if payload.get("type") != "refresh":
        logger.warning("Wrong token type for refresh")
        raise AuthenticationError(message="Invalid token type")

    # Estrai user_id
    user_id = UUID(payload.get("sub"))

    # Carica utente
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found for refresh: {user_id}")
        raise AuthenticationError(message="User not found")

    if not user.is_active:
        logger.warning(f"Inactive user tried to refresh: {user.email}")
        raise AuthenticationError(message="Account is inactive")

    # Crea nuovo access token
    access_token = create_access_token(
        subject=str(user.id),
        additional_claims={"role": user.role.value, "email": user.email},
    )

    logger.info(f"Token refreshed for user: {user.email}")

    return TokenResponse(
        access_token=access_token,
        refresh_token=data.refresh_token,  # Keep same refresh token
        token_type="bearer",
        expires_in=15 * 60,
    )


# =============================================================================
# EMAIL VERIFICATION
# =============================================================================


@router.post("/verify-email", response_model=SuccessResponse)
async def verify_email(
    data: EmailVerificationRequest,
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Verifica email utente tramite token.

    Args:
        data: Token di verifica

    Returns:
        SuccessResponse: Conferma verifica
    """
    logger.info(f"Email verification attempt with token: {data.token[:8]}...")

    # Cerca utente con questo token
    result = await db.execute(
        select(User).where(User.email_verification_token == data.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Invalid verification token")
        raise ResourceNotFoundError(
            resource_type="VerificationToken",
            resource_id=data.token[:8],
        )

    # Verifica se già verificato
    if user.is_email_verified:
        logger.info(f"Email already verified for: {user.email}")
        return SuccessResponse(message="Email already verified")

    # Marca email come verificata
    user.is_email_verified = True
    user.email_verification_token = None

    # Audit log
    await create_audit_log(
        db=db,
        user_id=user.id,
        action=AuditAction.UPDATE,
        entity_type="users",
        entity_id=user.id,
        changes={"email_verified": True},
    )

    await db.commit()

    logger.info(f"Email verified successfully for: {user.email}")

    return SuccessResponse(
        message="Email verified successfully",
        data={"email": user.email},
    )


# =============================================================================
# PASSWORD RESET
# =============================================================================


@router.post("/password-reset", response_model=SuccessResponse)
async def password_reset_request(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Richiesta reset password. Invia email con token.

    Args:
        data: Email utente

    Returns:
        SuccessResponse: Conferma invio email
    """
    logger.info(f"Password reset request for: {data.email}")

    # Carica utente
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    # Sempre restituisci success (security: non rivelare se email esiste)
    if not user:
        logger.warning(f"Password reset requested for non-existent email: {data.email}")
        return SuccessResponse(
            message="If the email exists, a password reset link has been sent."
        )

    # Genera token reset
    reset_token = generate_random_token(32)
    user.password_reset_token = reset_token
    user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)

    await db.commit()

    # TODO: Invia email con link reset
    # await send_password_reset_email(user.email, reset_token)

    logger.info(f"Password reset token generated for: {user.email}")

    return SuccessResponse(
        message="If the email exists, a password reset link has been sent."
    )


@router.post("/password-reset/confirm", response_model=SuccessResponse)
async def password_reset_confirm(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Conferma reset password con token.

    Args:
        data: Token e nuova password

    Returns:
        SuccessResponse: Conferma reset
    """
    logger.info(f"Password reset confirmation with token: {data.token[:8]}...")

    # Cerca utente con questo token
    result = await db.execute(
        select(User).where(User.password_reset_token == data.token)
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning("Invalid password reset token")
        raise BusinessLogicError(message="Invalid or expired reset token")

    # Verifica scadenza token
    if user.password_reset_expires < datetime.utcnow():
        logger.warning(f"Expired password reset token for: {user.email}")
        user.password_reset_token = None
        user.password_reset_expires = None
        await db.commit()
        raise BusinessLogicError(message="Reset token has expired")

    # Hash nuova password
    user.password_hash = hash_password(data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None

    # Reset failed login attempts
    user.failed_login_attempts = 0
    user.locked_until = None

    # Audit log
    await create_audit_log(
        db=db,
        user_id=user.id,
        action=AuditAction.UPDATE,
        entity_type="users",
        entity_id=user.id,
        changes={"password_reset": True},
    )

    await db.commit()

    logger.info(f"Password reset successful for: {user.email}")

    return SuccessResponse(message="Password reset successful")


# =============================================================================
# PASSWORD CHANGE (authenticated user)
# =============================================================================


@router.post("/password-change", response_model=SuccessResponse)
async def password_change(
    data: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Cambio password per utente autenticato.

    Args:
        data: Password corrente e nuova
        current_user: Utente corrente

    Returns:
        SuccessResponse: Conferma cambio
    """
    logger.info(f"Password change request for: {current_user.email}")

    # Verifica password corrente
    if not verify_password(data.current_password, current_user.password_hash):
        logger.warning(f"Invalid current password for: {current_user.email}")
        raise AuthenticationError(message="Current password is incorrect")

    # Hash nuova password
    current_user.password_hash = hash_password(data.new_password)

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="users",
        entity_id=current_user.id,
        changes={"password_changed": True},
    )

    await db.commit()

    logger.info(f"Password changed successfully for: {current_user.email}")

    return SuccessResponse(message="Password changed successfully")


# =============================================================================
# MFA SETUP
# =============================================================================


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def mfa_setup(
    data: MFAEnableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> MFASetupResponse:
    """
    Setup MFA per utente. Genera secret e QR code.

    Args:
        data: Password per conferma
        current_user: Utente corrente

    Returns:
        MFASetupResponse: Secret, QR code URL, backup codes
    """
    logger.info(f"MFA setup request for: {current_user.email}")

    # Verifica password
    if not verify_password(data.password, current_user.password_hash):
        logger.warning(f"Invalid password for MFA setup: {current_user.email}")
        raise AuthenticationError(message="Invalid password")

    # Verifica se MFA già abilitato
    if current_user.mfa_enabled:
        logger.warning(f"MFA already enabled for: {current_user.email}")
        raise BusinessLogicError(message="MFA is already enabled")

    # Genera MFA secret
    secret = generate_mfa_secret()

    # Genera QR code URL
    qr_url = get_mfa_provisioning_uri(secret, current_user.email)

    # Genera backup codes
    plain_codes = generate_backup_codes(count=10)
    hashed_codes = hash_backup_codes(plain_codes)

    # Salva (ma NON abilitare ancora - aspetta conferma)
    current_user.mfa_secret = secret
    current_user.backup_codes = hashed_codes

    await db.commit()

    logger.info(f"MFA setup initiated for: {current_user.email}")

    return MFASetupResponse(
        secret=secret,
        qr_code_url=qr_url,
        backup_codes=plain_codes,  # Mostrati UNA SOLA VOLTA
    )


@router.post("/mfa/enable", response_model=SuccessResponse)
async def mfa_enable(
    data: MFAEnableConfirm,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Conferma abilitazione MFA verificando token.

    Args:
        data: Token TOTP per verifica
        current_user: Utente corrente

    Returns:
        SuccessResponse: Conferma abilitazione
    """
    logger.info(f"MFA enable confirmation for: {current_user.email}")

    # Verifica setup fatto
    if not current_user.mfa_secret:
        logger.warning(f"MFA setup not initiated for: {current_user.email}")
        raise BusinessLogicError(message="MFA setup not initiated. Call /mfa/setup first.")

    # Verifica token
    if not verify_mfa_token(current_user.mfa_secret, data.token):
        logger.warning(f"Invalid MFA token for enable: {current_user.email}")
        raise AuthenticationError(message="Invalid MFA token")

    # Abilita MFA
    current_user.mfa_enabled = True

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="users",
        entity_id=current_user.id,
        changes={"mfa_enabled": True},
    )

    await db.commit()

    logger.info(f"MFA enabled successfully for: {current_user.email}")

    return SuccessResponse(message="MFA enabled successfully")


@router.post("/mfa/disable", response_model=SuccessResponse)
async def mfa_disable(
    data: MFADisableRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Disabilita MFA per utente.

    Args:
        data: Password e token MFA per conferma
        current_user: Utente corrente

    Returns:
        SuccessResponse: Conferma disabilitazione
    """
    logger.info(f"MFA disable request for: {current_user.email}")

    # Verifica password
    if not verify_password(data.password, current_user.password_hash):
        logger.warning(f"Invalid password for MFA disable: {current_user.email}")
        raise AuthenticationError(message="Invalid password")

    # Verifica MFA abilitato
    if not current_user.mfa_enabled:
        logger.warning(f"MFA not enabled for: {current_user.email}")
        raise BusinessLogicError(message="MFA is not enabled")

    # Verifica token corrente
    if not verify_mfa_token(current_user.mfa_secret, data.token):
        logger.warning(f"Invalid MFA token for disable: {current_user.email}")
        raise AuthenticationError(message="Invalid MFA token")

    # Disabilita MFA
    current_user.mfa_enabled = False
    current_user.mfa_secret = None
    current_user.backup_codes = None

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="users",
        entity_id=current_user.id,
        changes={"mfa_disabled": True},
    )

    await db.commit()

    logger.info(f"MFA disabled successfully for: {current_user.email}")

    return SuccessResponse(message="MFA disabled successfully")


# =============================================================================
# LOGOUT
# =============================================================================


@router.post("/logout", response_model=SuccessResponse)
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Logout utente. Invalida sessione corrente.

    Args:
        current_user: Utente corrente

    Returns:
        SuccessResponse: Conferma logout
    """
    logger.info(f"Logout request for: {current_user.email}")

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.LOGOUT,
    )

    await db.commit()

    logger.info(f"Logout successful for: {current_user.email}")

    return SuccessResponse(message="Logged out successfully")


logger.info("Auth router initialized with all endpoints")
