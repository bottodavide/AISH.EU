"""
Modulo: admin.py
Descrizione: API routes per amministrazione sistema
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import require_admin, get_current_user
from app.core.exceptions import ResourceNotFoundError, BusinessLogicError
from app.core.system_logger import log_info, log_warning
from app.models.user import User, UserRole, UserProfile
from app.models.cms import BlogPost, BlogCategory, BlogTag
from app.models.service import Service
from app.models.order import Order, OrderStatus
from app.models.invoice import Invoice, InvoiceStatus
from app.models.audit import SystemLog, LogLevel
from app.schemas.base import SuccessResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# =============================================================================
# SCHEMAS
# =============================================================================

class AdminStats(BaseModel):
    """Statistiche admin dashboard"""
    total_users: int = Field(description="Totale utenti registrati")
    total_orders: int = Field(description="Totale ordini")
    total_revenue: float = Field(description="Fatturato totale")
    total_services: int = Field(description="Totale servizi")
    total_blog_posts: int = Field(description="Totale articoli blog")
    pending_orders: int = Field(description="Ordini in attesa")
    unpaid_invoices: int = Field(description="Fatture non pagate")
    total_categories: int = Field(description="Totale categorie blog")
    total_tags: int = Field(description="Totale tag blog")
    users_last_30_days: int = Field(description="Nuovi utenti ultimi 30 giorni")
    posts_last_30_days: int = Field(description="Nuovi post ultimi 30 giorni")


class UserListItem(BaseModel):
    """User item in list"""
    id: str
    email: str
    role: str
    is_active: bool
    is_email_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None


class UserListResponse(BaseModel):
    """Response for user list"""
    users: list[UserListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


class UserUpdateRequest(BaseModel):
    """Request to update user"""
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_email_verified: Optional[bool] = None


class LogEntry(BaseModel):
    """System log entry"""
    id: str
    timestamp: str
    level: str  # debug, info, warning, error, critical
    category: str
    message: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    ip_address: Optional[str] = None
    request_path: Optional[str] = None
    metadata: Optional[dict] = None


class LogStats(BaseModel):
    """Log statistics"""
    total_logs: int
    info_count: int
    warning_count: int
    error_count: int
    critical_count: int


# =============================================================================
# ADMIN STATS
# =============================================================================

@router.get("/stats", response_model=AdminStats)
async def get_admin_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> AdminStats:
    """
    Get admin dashboard statistics.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} requesting stats")

    # Calculate date for last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    # Total users
    total_users_query = select(func.count()).select_from(User)
    total_users_result = await db.execute(total_users_query)
    total_users = total_users_result.scalar() or 0

    # Users last 30 days
    users_30d_query = select(func.count()).select_from(User).where(
        User.created_at >= thirty_days_ago
    )
    users_30d_result = await db.execute(users_30d_query)
    users_last_30_days = users_30d_result.scalar() or 0

    # Total blog posts
    total_posts_query = select(func.count()).select_from(BlogPost)
    total_posts_result = await db.execute(total_posts_query)
    total_blog_posts = total_posts_result.scalar() or 0

    # Posts last 30 days
    posts_30d_query = select(func.count()).select_from(BlogPost).where(
        BlogPost.created_at >= thirty_days_ago
    )
    posts_30d_result = await db.execute(posts_30d_query)
    posts_last_30_days = posts_30d_result.scalar() or 0

    # Total services
    total_services_query = select(func.count()).select_from(Service)
    total_services_result = await db.execute(total_services_query)
    total_services = total_services_result.scalar() or 0

    # Total categories
    total_categories_query = select(func.count()).select_from(BlogCategory)
    total_categories_result = await db.execute(total_categories_query)
    total_categories = total_categories_result.scalar() or 0

    # Total tags
    total_tags_query = select(func.count()).select_from(BlogTag)
    total_tags_result = await db.execute(total_tags_query)
    total_tags = total_tags_result.scalar() or 0

    # Total orders
    total_orders_query = select(func.count()).select_from(Order)
    total_orders_result = await db.execute(total_orders_query)
    total_orders = total_orders_result.scalar() or 0

    # Pending orders (PENDING status)
    pending_orders_query = select(func.count()).select_from(Order).where(
        Order.status == OrderStatus.PENDING
    )
    pending_orders_result = await db.execute(pending_orders_query)
    pending_orders = pending_orders_result.scalar() or 0

    # Total revenue (sum of completed orders)
    revenue_query = select(func.sum(Order.total)).where(
        Order.status == OrderStatus.COMPLETED
    )
    revenue_result = await db.execute(revenue_query)
    total_revenue = float(revenue_result.scalar() or 0)

    # Unpaid invoices - temporarily disabled due to enum issue
    # TODO: Fix invoice status enum query
    unpaid_invoices = 0

    return AdminStats(
        total_users=total_users,
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_services=total_services,
        total_blog_posts=total_blog_posts,
        pending_orders=pending_orders,
        unpaid_invoices=unpaid_invoices,
        total_categories=total_categories,
        total_tags=total_tags,
        users_last_30_days=users_last_30_days,
        posts_last_30_days=posts_last_30_days,
    )


# =============================================================================
# USER MANAGEMENT
# =============================================================================

@router.get("/users", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    role: Optional[UserRole] = Query(None),
    is_active: Optional[bool] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|email|last_login)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> UserListResponse:
    """
    List all users with filtering and pagination.

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} listing users")

    # Build base query
    query = select(User).outerjoin(UserProfile, User.id == UserProfile.user_id)

    # Apply filters
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                User.email.ilike(search_pattern),
                UserProfile.first_name.ilike(search_pattern),
                UserProfile.last_name.ilike(search_pattern),
                UserProfile.company_name.ilike(search_pattern),
            )
        )

    if role:
        query = query.where(User.role == role)

    if is_active is not None:
        query = query.where(User.is_active == is_active)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply sorting
    if sort_by == "email":
        order_col = User.email
    elif sort_by == "last_login":
        order_col = User.last_login
    else:  # created_at
        order_col = User.created_at

    if sort_order == "asc":
        query = query.order_by(order_col.asc())
    else:
        query = query.order_by(order_col.desc())

    # Apply pagination
    query = query.limit(page_size).offset((page - 1) * page_size)

    # Execute query
    result = await db.execute(query)
    users = result.scalars().all()

    # Load profiles for each user
    user_items = []
    for user in users:
        # Always load profile explicitly to avoid lazy loading issues
        profile_result = await db.execute(
            select(UserProfile).where(UserProfile.user_id == user.id)
        )
        profile = profile_result.scalar_one_or_none()

        user_items.append(UserListItem(
            id=str(user.id),
            email=user.email,
            role=user.role.value,
            is_active=user.is_active,
            is_email_verified=user.is_email_verified,
            created_at=user.created_at,
            last_login=user.last_login,
            first_name=profile.first_name if profile else None,
            last_name=profile.last_name if profile else None,
            company_name=profile.company_name if profile else None,
        ))

    total_pages = (total + page_size - 1) // page_size

    return UserListResponse(
        users=user_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/users/{user_id}")
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
):
    """Get specific user details"""
    logger.info(f"Admin {current_user.email} getting user {user_id}")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise ResourceNotFoundError(resource_type="User", resource_id=str(user_id))

    # Load profile
    profile_result = await db.execute(
        select(UserProfile).where(UserProfile.user_id == user_id)
    )
    profile = profile_result.scalar_one_or_none()

    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_email_verified": user.is_email_verified,
        "mfa_enabled": user.mfa_enabled,
        "created_at": user.created_at,
        "last_login": user.last_login,
        "profile": {
            "first_name": profile.first_name if profile else None,
            "last_name": profile.last_name if profile else None,
            "company_name": profile.company_name if profile else None,
            "phone": profile.phone if profile else None,
        } if profile else None,
    }


@router.put("/users/{user_id}", response_model=SuccessResponse)
async def update_user(
    user_id: UUID,
    data: UserUpdateRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Update user (role, active status, etc.)

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} updating user {user_id}")

    # Load user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise ResourceNotFoundError(resource_type="User", resource_id=str(user_id))

    # Can't modify super admin unless you're super admin
    if user.role == UserRole.SUPER_ADMIN and current_user.role != UserRole.SUPER_ADMIN:
        raise BusinessLogicError(
            message="Only super admins can modify super admin users"
        )

    # Update fields
    if data.role is not None:
        user.role = data.role

    if data.is_active is not None:
        user.is_active = data.is_active

    if data.is_email_verified is not None:
        user.is_email_verified = data.is_email_verified

    await db.commit()

    logger.info(f"User {user_id} updated successfully")

    # Log user update
    changes = {}
    if data.role is not None:
        changes["role"] = data.role.value
    if data.is_active is not None:
        changes["is_active"] = data.is_active
    if data.is_email_verified is not None:
        changes["is_email_verified"] = data.is_email_verified

    await log_info(
        db=db,
        module="admin",
        message=f"Admin {current_user.email} updated user {user.email}",
        user_id=current_user.id,
        metadata={
            "target_user_id": str(user_id),
            "target_user_email": user.email,
            "changes": changes,
        },
    )

    return SuccessResponse(
        message="User updated successfully",
        data={"user_id": str(user_id)},
    )


@router.delete("/users/{user_id}", response_model=SuccessResponse)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Delete user (soft delete by setting is_active=False)

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} deleting user {user_id}")

    # Load user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise ResourceNotFoundError(resource_type="User", resource_id=str(user_id))

    # Can't delete super admin
    if user.role == UserRole.SUPER_ADMIN:
        raise BusinessLogicError(message="Cannot delete super admin users")

    # Can't delete yourself
    if user.id == current_user.id:
        raise BusinessLogicError(message="Cannot delete your own account")

    # Soft delete
    user.is_active = False

    await db.commit()

    logger.info(f"User {user_id} deleted (soft delete)")

    # Log user deletion
    await log_warning(
        db=db,
        module="admin",
        message=f"Admin {current_user.email} deleted user {user.email} (soft delete)",
        user_id=current_user.id,
        metadata={
            "target_user_id": str(user_id),
            "target_user_email": user.email,
            "action": "soft_delete",
        },
    )

    return SuccessResponse(
        message="User deleted successfully",
        data={"user_id": str(user_id)},
    )


# =============================================================================
# SYSTEM LOGS
# =============================================================================

@router.get("/logs", response_model=list[LogEntry])
async def get_system_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=500),
    level: Optional[str] = Query(None, description="Filter by log level"),
    category: Optional[str] = Query(None, description="Filter by module/category"),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> list[LogEntry]:
    """
    Get system logs from database

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} requesting logs (level: {level}, module: {category}, page: {page})")

    # Build query
    query = select(SystemLog).order_by(desc(SystemLog.created_at))

    # Apply filters
    if level and level != 'all':
        try:
            log_level = LogLevel(level)
            # Use string comparison to avoid enum type issues
            query = query.where(SystemLog.level == log_level.value)
        except ValueError:
            pass  # Invalid level, ignore filter

    if category:
        # Filter by module (string match)
        query = query.where(SystemLog.module == category)

    # Pagination
    offset = (page - 1) * page_size
    query = query.limit(page_size).offset(offset)

    # Execute query with user relationship
    result = await db.execute(
        query.options(selectinload(SystemLog.user))
    )
    logs = result.scalars().all()

    # Convert to response model
    log_entries = []
    for log in logs:
        # Extract request_path from context if available
        request_path = None
        if log.context and isinstance(log.context, dict):
            request_path = log.context.get("request_path")

        log_entries.append(
            LogEntry(
                id=str(log.id),
                timestamp=log.created_at.isoformat(),
                level=log.level.value,
                category=log.module,  # Use module as category
                message=log.message,
                user_id=str(log.user_id) if log.user_id else None,
                user_email=log.user.email if log.user else None,
                ip_address=str(log.ip_address) if log.ip_address else None,
                request_path=request_path,
                metadata=log.context,  # Use context as metadata
            )
        )

    return log_entries


@router.get("/logs/stats", response_model=LogStats)
async def get_log_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db),
) -> LogStats:
    """
    Get log statistics from database

    Requires: admin or super_admin role
    """
    logger.info(f"Admin {current_user.email} requesting log stats")

    # Count total logs
    total_result = await db.execute(
        select(func.count(SystemLog.id))
    )
    total_logs = total_result.scalar() or 0

    # Count by level - use .value to avoid enum type casting issues
    info_result = await db.execute(
        select(func.count(SystemLog.id)).where(SystemLog.level == LogLevel.INFO.value)
    )
    info_count = info_result.scalar() or 0

    warning_result = await db.execute(
        select(func.count(SystemLog.id)).where(SystemLog.level == LogLevel.WARNING.value)
    )
    warning_count = warning_result.scalar() or 0

    error_result = await db.execute(
        select(func.count(SystemLog.id)).where(SystemLog.level == LogLevel.ERROR.value)
    )
    error_count = error_result.scalar() or 0

    critical_result = await db.execute(
        select(func.count(SystemLog.id)).where(SystemLog.level == LogLevel.CRITICAL.value)
    )
    critical_count = critical_result.scalar() or 0

    stats = LogStats(
        total_logs=int(total_logs),
        info_count=int(info_count),
        warning_count=int(warning_count),
        error_count=int(error_count),
        critical_count=int(critical_count),
    )

    return stats


logger.info("Admin router initialized")
