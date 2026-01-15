"""
Modulo: users.py
Descrizione: API routes per gestione users
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import (
    get_current_user,
    require_admin,
    verify_ownership_or_admin,
)
from app.core.exceptions import (
    BusinessLogicError,
    DuplicateResourceError,
    ResourceNotFoundError,
)
from app.core.security import hash_password
from app.models.audit import AuditAction
from app.models.user import User, UserProfile, UserRole
from app.schemas.base import SuccessResponse
from app.schemas.user import (
    CurrentUserResponse,
    UpdateCurrentUserRequest,
    UserCreate,
    UserDetailResponse,
    UserFilters,
    UserListResponse,
    UserProfileResponse,
    UserProfileUpdate,
    UserResponse,
    UserRoleChangeRequest,
    UserStatistics,
    UserUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["Users"])


# =============================================================================
# CURRENT USER (ME)
# =============================================================================


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> CurrentUserResponse:
    """
    Ottiene informazioni utente corrente.

    Args:
        current_user: Utente autenticato

    Returns:
        CurrentUserResponse: Dati utente corrente con profile
    """
    logger.info(f"Getting current user info for: {current_user.email}")

    # Load profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    response_data = {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
        "is_email_verified": current_user.is_email_verified,
        "mfa_enabled": current_user.mfa_enabled,
        "last_login_at": current_user.last_login_at,
        "email_verification_sent_at": current_user.email_verification_sent_at,
        "failed_login_attempts": current_user.failed_login_attempts,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
        "profile": profile,
    }

    return CurrentUserResponse(**response_data)


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    data: UpdateCurrentUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> UserResponse:
    """
    Aggiorna informazioni utente corrente.

    Note: Cambio email richiede re-verifica.

    Args:
        data: Dati da aggiornare
        current_user: Utente autenticato

    Returns:
        UserResponse: Utente aggiornato
    """
    logger.info(f"Updating current user: {current_user.email}")

    changes = {}

    # Update email (richiede re-verifica)
    if data.email and data.email != current_user.email:
        # Verifica email univoca
        result = await db.execute(select(User).where(User.email == data.email))
        existing = result.scalar_one_or_none()

        if existing:
            logger.warning(f"Email already exists: {data.email}")
            raise DuplicateResourceError(
                resource_type="User",
                field="email",
                value=data.email,
            )

        changes["email"] = {"old": current_user.email, "new": data.email}
        current_user.email = data.email
        current_user.is_email_verified = False  # Richiede re-verifica
        # TODO: Invia email verifica

    await db.commit()
    await db.refresh(current_user)

    logger.info(f"User updated: {current_user.email}")

    # Load profile
    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
        is_email_verified=current_user.is_email_verified,
        mfa_enabled=current_user.mfa_enabled,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
        profile=profile,
    )


@router.get("/me/profile", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> UserProfileResponse:
    """
    Ottiene profilo utente corrente.

    Args:
        current_user: Utente autenticato

    Returns:
        UserProfileResponse: Profilo utente
    """
    logger.info(f"Getting profile for: {current_user.email}")

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        logger.warning(f"Profile not found for user: {current_user.id}")
        raise ResourceNotFoundError(
            resource_type="UserProfile",
            resource_id=current_user.id,
        )

    return UserProfileResponse.model_validate(profile)


@router.put("/me/profile", response_model=UserProfileResponse)
async def update_current_user_profile(
    data: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> UserProfileResponse:
    """
    Aggiorna profilo utente corrente.

    Args:
        data: Dati profilo da aggiornare
        current_user: Utente autenticato

    Returns:
        UserProfileResponse: Profilo aggiornato
    """
    logger.info(f"Updating profile for: {current_user.email}")

    result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()

    if not profile:
        # Crea profile se non esiste
        logger.info(f"Creating profile for user: {current_user.id}")
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    logger.info(f"Profile updated for: {current_user.email}")

    return UserProfileResponse.model_validate(profile)


# =============================================================================
# USER MANAGEMENT (ADMIN)
# =============================================================================


@router.get("", response_model=UserListResponse)
async def list_users(
    filters: UserFilters = Depends(),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UserListResponse:
    """
    Lista users con filtri (solo admin).

    Args:
        filters: Filtri di ricerca
        current_user: Admin autenticato

    Returns:
        UserListResponse: Lista users paginata
    """
    logger.info(f"Listing users (requested by {current_user.email})")

    # Build query
    query = select(User)

    # Apply filters
    if filters.email:
        query = query.where(User.email.ilike(f"%{filters.email}%"))

    if filters.role is not None:
        query = query.where(User.role == filters.role)

    if filters.is_active is not None:
        query = query.where(User.is_active == filters.is_active)

    if filters.is_email_verified is not None:
        query = query.where(User.is_email_verified == filters.is_email_verified)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    query = query.offset(filters.skip).limit(filters.limit)

    # Execute
    result = await db.execute(query)
    users = result.scalars().all()

    # Load profiles
    user_responses = []
    for user in users:
        profile_result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
        profile = profile_result.scalar_one_or_none()

        user_responses.append(
            UserResponse(
                id=user.id,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                is_email_verified=user.is_email_verified,
                mfa_enabled=user.mfa_enabled,
                last_login_at=user.last_login_at,
                created_at=user.created_at,
                updated_at=user.updated_at,
                profile=profile,
            )
        )

    logger.info(f"Found {len(users)} users (total: {total})")

    return UserListResponse(
        users=user_responses,
        total=total,
        skip=filters.skip,
        limit=filters.limit,
    )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UserResponse:
    """
    Crea nuovo user (solo admin).

    Args:
        data: Dati nuovo user
        current_user: Admin autenticato

    Returns:
        UserResponse: User creato
    """
    logger.info(f"Creating user: {data.email} (by {current_user.email})")

    # Verifica email univoca
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()

    if existing:
        logger.warning(f"Email already exists: {data.email}")
        raise DuplicateResourceError(
            resource_type="User",
            field="email",
            value=data.email,
        )

    # Hash password
    password_hash = hash_password(data.password)

    # Crea user
    user = User(
        email=data.email,
        password_hash=password_hash,
        role=data.role,
        is_active=data.is_active,
        is_email_verified=data.is_email_verified,
    )
    db.add(user)
    await db.flush()

    # Crea profile vuoto
    profile = UserProfile(user_id=user.id)
    db.add(profile)

    await db.commit()
    await db.refresh(user)

    logger.info(f"User created: {user.email} (ID: {user.id})")

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        mfa_enabled=user.mfa_enabled,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile=profile,
    )


@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db),
) -> UserDetailResponse:
    """
    Ottiene dettaglio user.

    Accessibile da:
    - Admin: tutti gli users
    - User: solo se stesso

    Args:
        user_id: ID user
        current_user: Utente autenticato

    Returns:
        UserDetailResponse: Dettaglio user
    """
    logger.info(f"Getting user {user_id} (requested by {current_user.email})")

    # Verifica ownership o admin
    verify_ownership_or_admin(user_id, current_user)

    # Load user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found: {user_id}")
        raise ResourceNotFoundError(
            resource_type="User",
            resource_id=user_id,
        )

    # Load profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()

    return UserDetailResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        mfa_enabled=user.mfa_enabled,
        last_login_at=user.last_login_at,
        failed_login_attempts=user.failed_login_attempts,
        locked_until=user.locked_until,
        last_login_ip=str(user.last_login_ip) if user.last_login_ip else None,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile=profile,
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UserResponse:
    """
    Aggiorna user (solo admin).

    Args:
        user_id: ID user
        data: Dati da aggiornare
        current_user: Admin autenticato

    Returns:
        UserResponse: User aggiornato
    """
    logger.info(f"Updating user {user_id} (by {current_user.email})")

    # Load user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found: {user_id}")
        raise ResourceNotFoundError(
            resource_type="User",
            resource_id=user_id,
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] != user.email:
        # Verifica email univoca
        result = await db.execute(
            select(User).where(User.email == update_data["email"])
        )
        existing = result.scalar_one_or_none()

        if existing:
            logger.warning(f"Email already exists: {update_data['email']}")
            raise DuplicateResourceError(
                resource_type="User",
                field="email",
                value=update_data["email"],
            )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    logger.info(f"User updated: {user.email}")

    # Load profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        mfa_enabled=user.mfa_enabled,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile=profile,
    )


@router.delete("/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina user (solo admin).

    Args:
        user_id: ID user
        current_user: Admin autenticato

    Returns:
        SuccessResponse: Conferma eliminazione
    """
    logger.info(f"Deleting user {user_id} (by {current_user.email})")

    # Load user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found: {user_id}")
        raise ResourceNotFoundError(
            resource_type="User",
            resource_id=user_id,
        )

    # Non permettere auto-eliminazione
    if user.id == current_user.id:
        logger.warning(f"User tried to delete themselves: {current_user.email}")
        raise BusinessLogicError(message="Cannot delete your own account")

    # Non permettere eliminazione super admin
    if user.role == UserRole.SUPER_ADMIN:
        logger.warning(f"Attempted to delete super admin: {user.email}")
        raise BusinessLogicError(message="Cannot delete super admin account")

    await db.delete(user)
    await db.commit()

    logger.info(f"User deleted: {user.email}")

    return SuccessResponse(
        message="User deleted successfully",
        data={"user_id": str(user_id)},
    )


@router.put("/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: UUID,
    data: UserRoleChangeRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UserResponse:
    """
    Cambia ruolo user (solo admin).

    Args:
        user_id: ID user
        data: Nuovo ruolo
        current_user: Admin autenticato

    Returns:
        UserResponse: User aggiornato
    """
    logger.info(f"Changing role for user {user_id} to {data.role.value} (by {current_user.email})")

    # Load user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        logger.warning(f"User not found: {user_id}")
        raise ResourceNotFoundError(
            resource_type="User",
            resource_id=user_id,
        )

    # Non permettere cambio ruolo a se stessi
    if user.id == current_user.id:
        logger.warning(f"User tried to change their own role: {current_user.email}")
        raise BusinessLogicError(message="Cannot change your own role")

    old_role = user.role
    user.role = data.role

    await db.commit()
    await db.refresh(user)

    logger.info(f"Role changed for {user.email}: {old_role.value} -> {data.role.value}")

    # Load profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user.id)
    )
    profile = profile_result.scalar_one_or_none()

    return UserResponse(
        id=user.id,
        email=user.email,
        role=user.role,
        is_active=user.is_active,
        is_email_verified=user.is_email_verified,
        mfa_enabled=user.mfa_enabled,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
        profile=profile,
    )


# =============================================================================
# STATISTICS (ADMIN)
# =============================================================================


@router.get("/statistics/overview", response_model=UserStatistics)
async def get_user_statistics(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UserStatistics:
    """
    Ottiene statistiche users (solo admin).

    Args:
        current_user: Admin autenticato

    Returns:
        UserStatistics: Statistiche users
    """
    logger.info(f"Getting user statistics (by {current_user.email})")

    # Total users
    total_result = await db.execute(select(func.count(User.id)))
    total_users = total_result.scalar()

    # Active users
    active_result = await db.execute(
        select(func.count(User.id)).where(User.is_active == True)
    )
    active_users = active_result.scalar()

    # Inactive users
    inactive_users = total_users - active_users

    # Verified users
    verified_result = await db.execute(
        select(func.count(User.id)).where(User.is_email_verified == True)
    )
    verified_users = verified_result.scalar()

    # Unverified users
    unverified_users = total_users - verified_users

    # Users with MFA
    mfa_result = await db.execute(
        select(func.count(User.id)).where(User.mfa_enabled == True)
    )
    users_with_mfa = mfa_result.scalar()

    # Users by role
    role_result = await db.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    )
    users_by_role = {role.value: count for role, count in role_result.all()}

    # New users last 30 days
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_users_result = await db.execute(
        select(func.count(User.id)).where(User.created_at >= thirty_days_ago)
    )
    new_users_last_30_days = new_users_result.scalar()

    logger.info(f"Statistics: {total_users} total users, {active_users} active")

    return UserStatistics(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        verified_users=verified_users,
        unverified_users=unverified_users,
        users_with_mfa=users_with_mfa,
        users_by_role=users_by_role,
        new_users_last_30_days=new_users_last_30_days,
    )


logger.info("Users router initialized with all endpoints")
