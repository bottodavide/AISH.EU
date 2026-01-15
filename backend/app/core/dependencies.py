"""
Modulo: dependencies.py
Descrizione: FastAPI dependencies per autenticazione e autorizzazione
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.security import decode_token
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)

# Security scheme per JWT Bearer token
security = HTTPBearer()
security_optional = HTTPBearer(auto_error=False)

# =============================================================================
# AUTHENTICATION DEPENDENCIES
# =============================================================================


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    """
    Ottiene utente corrente da JWT token.

    Args:
        credentials: HTTP Bearer token
        db: Database session

    Returns:
        User: Utente autenticato

    Raises:
        HTTPException: 401 se token invalido o utente non trovato

    Example:
        @app.get("/me")
        async def get_me(current_user: User = Depends(get_current_user)):
            return current_user
    """
    logger.debug("Authenticating user from JWT token")

    # Estrai token
    token = credentials.credentials

    # Decodifica token
    payload = decode_token(token)

    if not payload:
        logger.warning("Invalid JWT token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica tipo token
    token_type = payload.get("type")
    if token_type != "access":
        logger.warning(f"Wrong token type: {token_type}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Estrai user_id
    user_id_str = payload.get("sub")
    if not user_id_str:
        logger.warning("Token missing 'sub' claim")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        logger.warning(f"Invalid user_id format in token: {user_id_str}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Carica utente dal database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifica se utente è attivo
    if not user.is_active:
        logger.warning(f"Inactive user attempted login: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Verifica se email è verificata (opzionale, dipende dai requisiti)
    # if not user.is_email_verified:
    #     logger.warning(f"Unverified email attempted access: {user.email}")
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Email not verified",
    #     )

    logger.info(f"User authenticated: {user.email} (ID: {user.id})")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ottiene utente corrente ATTIVO.

    Args:
        current_user: Utente da get_current_user

    Returns:
        User: Utente attivo

    Raises:
        HTTPException: 403 se utente non attivo
    """
    if not current_user.is_active:
        logger.warning(f"Inactive user blocked: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ottiene utente corrente con EMAIL VERIFICATA.

    Args:
        current_user: Utente da get_current_user

    Returns:
        User: Utente con email verificata

    Raises:
        HTTPException: 403 se email non verificata
    """
    if not current_user.is_email_verified:
        logger.warning(f"Unverified user blocked: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )
    return current_user


# =============================================================================
# AUTHORIZATION DEPENDENCIES (RBAC)
# =============================================================================


class RoleChecker:
    """
    Dependency class per verificare ruoli utente (RBAC).

    Example:
        require_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN])

        @app.get("/admin/dashboard")
        async def dashboard(user: User = Depends(require_admin)):
            return {"message": "Admin dashboard"}
    """

    def __init__(self, allowed_roles: list[UserRole]):
        """
        Args:
            allowed_roles: Lista di ruoli autorizzati
        """
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Verifica se utente ha uno dei ruoli autorizzati.

        Args:
            current_user: Utente corrente

        Returns:
            User: Utente autorizzato

        Raises:
            HTTPException: 403 se utente non autorizzato
        """
        logger.debug(
            f"Checking role for user {current_user.email}: "
            f"{current_user.role.value} in {[r.value for r in self.allowed_roles]}"
        )

        if current_user.role not in self.allowed_roles:
            logger.warning(
                f"Access denied for user {current_user.email} "
                f"(role: {current_user.role.value}, required: {[r.value for r in self.allowed_roles]})"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        logger.debug(f"Role check passed for {current_user.email}")
        return current_user


# Dependency shortcuts per ruoli comuni
require_super_admin = RoleChecker([UserRole.SUPER_ADMIN])
require_admin = RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN])
require_admin_or_editor = RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.EDITOR])
require_editor = RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.EDITOR])
require_support = RoleChecker([UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.SUPPORT])
require_customer = RoleChecker([
    UserRole.SUPER_ADMIN,
    UserRole.ADMIN,
    UserRole.EDITOR,
    UserRole.SUPPORT,
    UserRole.CUSTOMER
])


# =============================================================================
# OWNERSHIP VERIFICATION
# =============================================================================


def verify_ownership_or_admin(resource_owner_id: UUID, current_user: User) -> bool:
    """
    Verifica se utente è owner della risorsa O admin.

    Args:
        resource_owner_id: ID owner della risorsa
        current_user: Utente corrente

    Returns:
        bool: True se autorizzato

    Raises:
        HTTPException: 403 se non autorizzato

    Example:
        order = await get_order(order_id)
        verify_ownership_or_admin(order.user_id, current_user)
    """
    is_owner = current_user.id == resource_owner_id
    is_admin = current_user.role in [UserRole.SUPER_ADMIN, UserRole.ADMIN]

    if not (is_owner or is_admin):
        logger.warning(
            f"Access denied: User {current_user.email} "
            f"tried to access resource owned by {resource_owner_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )

    logger.debug(
        f"Ownership verification passed for user {current_user.email} "
        f"(is_owner: {is_owner}, is_admin: {is_admin})"
    )
    return True


# =============================================================================
# OPTIONAL AUTHENTICATION
# =============================================================================


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_optional),
    db: AsyncSession = Depends(get_async_db),
) -> Optional[User]:
    """
    Ottiene utente corrente se autenticato, altrimenti None.

    Utile per endpoint che possono funzionare sia autenticati che non.

    Args:
        credentials: HTTP Bearer token (opzionale)
        db: Database session

    Returns:
        User: Utente autenticato, o None

    Example:
        @app.get("/services")
        async def list_services(
            current_user: Optional[User] = Depends(get_current_user_optional)
        ):
            # Mostra prezzi diversi se utente è loggato
            if current_user:
                return services_with_discount
            return services
    """
    if not credentials:
        logger.debug("No credentials provided, returning None")
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        logger.debug("Invalid credentials provided, returning None")
        return None


# =============================================================================
# PAGINATION DEPENDENCIES
# =============================================================================


async def get_pagination(
    skip: int = 0,
    limit: int = 100,
) -> dict[str, int]:
    """
    Dependency per parametri paginazione.

    Args:
        skip: Numero di record da saltare
        limit: Numero massimo di record da restituire

    Returns:
        dict: {"skip": int, "limit": int}

    Example:
        @app.get("/users")
        async def list_users(pagination: dict = Depends(get_pagination)):
            skip = pagination["skip"]
            limit = pagination["limit"]
            return await get_users(skip, limit)
    """
    # Valida limiti
    if skip < 0:
        logger.warning(f"Invalid skip value: {skip}, using 0")
        skip = 0

    if limit < 1:
        logger.warning(f"Invalid limit value: {limit}, using 1")
        limit = 1

    if limit > 1000:
        logger.warning(f"Limit too high: {limit}, capping at 1000")
        limit = 1000

    logger.debug(f"Pagination: skip={skip}, limit={limit}")
    return {"skip": skip, "limit": limit}


logger.info("Dependencies module initialized")
