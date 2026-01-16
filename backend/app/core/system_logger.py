"""
System Logger Helper
Descrizione: Helper per registrare log di sistema nel database
Autore: Claude per Davide
Data: 2026-01-16
"""

import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request

from app.models.audit import SystemLog, LogLevel

logger = logging.getLogger(__name__)


class SystemLogger:
    """Helper class for logging system events to database"""

    @staticmethod
    async def log(
        db: AsyncSession,
        level: LogLevel,
        module: str,  # Cambiato da category a module
        message: str,
        user_id: Optional[UUID] = None,
        request: Optional[Request] = None,
        metadata: Optional[Dict[str, Any]] = None,
        exception: Optional[Exception] = None,
    ) -> SystemLog:
        """
        Log an event to the database

        Args:
            db: Database session
            level: Log level (debug, info, warning, error, critical)
            module: Module name (auth, order, payment, etc.)
            message: Log message
            user_id: User ID if applicable
            request: FastAPI Request object to extract IP
            metadata: Additional metadata as dict
            exception: Exception object if logging an error

        Returns:
            SystemLog: The created log entry
        """
        try:
            # Extract request info
            ip_address = None

            if request:
                # Get client IP (check for proxy headers first)
                ip_address = request.headers.get("X-Forwarded-For")
                if ip_address:
                    # Take first IP if multiple (proxy chain)
                    ip_address = ip_address.split(",")[0].strip()
                else:
                    ip_address = request.client.host if request.client else None

            # Extract exception info
            stack_trace = None

            if exception:
                stack_trace = "".join(traceback.format_exception(
                    type(exception), exception, exception.__traceback__
                ))

            # Enhance metadata with request info if available
            if request and metadata is None:
                metadata = {}

            if request:
                if metadata is not None:
                    metadata["request_method"] = request.method
                    metadata["request_path"] = str(request.url.path)
                    metadata["user_agent"] = request.headers.get("User-Agent")

            # Create log entry
            log_entry = SystemLog(
                level=level,
                module=module,
                message=message,
                user_id=user_id,
                ip_address=ip_address,
                context=metadata,  # Cambiato da extra_data a context
                stack_trace=stack_trace,
                created_at=datetime.utcnow(),
            )

            db.add(log_entry)
            await db.commit()
            await db.refresh(log_entry)

            return log_entry

        except Exception as e:
            # If logging fails, log to console but don't crash
            logger.error(f"Failed to log to database: {e}")
            await db.rollback()
            raise


# Convenience functions for common log levels

async def log_info(
    db: AsyncSession,
    module: str,  # Cambiato da category a module
    message: str,
    user_id: Optional[UUID] = None,
    request: Optional[Request] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Log an info message"""
    return await SystemLogger.log(
        db=db,
        level=LogLevel.INFO,
        module=module,
        message=message,
        user_id=user_id,
        request=request,
        metadata=metadata,
    )


async def log_warning(
    db: AsyncSession,
    module: str,
    message: str,
    user_id: Optional[UUID] = None,
    request: Optional[Request] = None,
    metadata: Optional[Dict[str, Any]] = None,
):
    """Log a warning message"""
    return await SystemLogger.log(
        db=db,
        level=LogLevel.WARNING,
        module=module,
        message=message,
        user_id=user_id,
        request=request,
        metadata=metadata,
    )


async def log_error(
    db: AsyncSession,
    module: str,
    message: str,
    user_id: Optional[UUID] = None,
    request: Optional[Request] = None,
    metadata: Optional[Dict[str, Any]] = None,
    exception: Optional[Exception] = None,
):
    """Log an error message"""
    return await SystemLogger.log(
        db=db,
        level=LogLevel.ERROR,
        module=module,
        message=message,
        user_id=user_id,
        request=request,
        metadata=metadata,
        exception=exception,
    )


async def log_critical(
    db: AsyncSession,
    module: str,
    message: str,
    user_id: Optional[UUID] = None,
    request: Optional[Request] = None,
    metadata: Optional[Dict[str, Any]] = None,
    exception: Optional[Exception] = None,
):
    """Log a critical message"""
    return await SystemLogger.log(
        db=db,
        level=LogLevel.CRITICAL,
        module=module,
        message=message,
        user_id=user_id,
        request=request,
        metadata=metadata,
        exception=exception,
    )
