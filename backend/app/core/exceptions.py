"""
Modulo: exceptions.py
Descrizione: Custom exceptions per API
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import Any, Optional

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


# =============================================================================
# CUSTOM EXCEPTIONS
# =============================================================================


class AIStrategyHubException(Exception):
    """Base exception per AI Strategy Hub"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[dict[str, Any]] = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(AIStrategyHubException):
    """Errore di autenticazione"""

    def __init__(self, message: str = "Authentication failed", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            details=details,
        )


class AuthorizationError(AIStrategyHubException):
    """Errore di autorizzazione (permessi insufficienti)"""

    def __init__(self, message: str = "Not enough permissions", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details,
        )


class ResourceNotFoundError(AIStrategyHubException):
    """Risorsa non trovata"""

    def __init__(
        self,
        resource_type: str,
        resource_id: Any,
        details: Optional[dict] = None,
    ):
        message = f"{resource_type} with id {resource_id} not found"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details or {"resource_type": resource_type, "resource_id": str(resource_id)},
        )


class DuplicateResourceError(AIStrategyHubException):
    """Risorsa duplicata (violazione unique constraint)"""

    def __init__(
        self,
        resource_type: str,
        field: str,
        value: Any,
        details: Optional[dict] = None,
    ):
        message = f"{resource_type} with {field}={value} already exists"
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details or {"resource_type": resource_type, "field": field, "value": str(value)},
        )


class ValidationError(AIStrategyHubException):
    """Errore di validazione dati"""

    def __init__(self, message: str, errors: Optional[list] = None, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details or {"validation_errors": errors or []},
        )


class BusinessLogicError(AIStrategyHubException):
    """Errore di business logic"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


class ExternalServiceError(AIStrategyHubException):
    """Errore servizio esterno (Stripe, MS Graph, Claude API, etc.)"""

    def __init__(
        self,
        service_name: str,
        message: str,
        details: Optional[dict] = None,
    ):
        full_message = f"External service error ({service_name}): {message}"
        super().__init__(
            message=full_message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            details=details or {"service": service_name},
        )


class RateLimitError(AIStrategyHubException):
    """Rate limit superato"""

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[dict] = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details=details or {"retry_after": retry_after},
        )


class MFARequiredError(AIStrategyHubException):
    """MFA richiesto ma non fornito"""

    def __init__(self, message: str = "MFA verification required", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details or {"mfa_required": True},
        )


class EmailNotVerifiedError(AIStrategyHubException):
    """Email non verificata"""

    def __init__(self, message: str = "Email not verified", details: Optional[dict] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details=details or {"email_verified": False},
        )


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================


async def aistrategyhub_exception_handler(
    request: Request,
    exc: AIStrategyHubException,
) -> JSONResponse:
    """
    Handler per custom exceptions AI Strategy Hub.

    Args:
        request: FastAPI request
        exc: Custom exception

    Returns:
        JSONResponse: Response con error details
    """
    logger.error(
        f"AIStrategyHubException: {exc.message}",
        extra={
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "path": request.url.path,
        },
    )


async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """
    Handler per HTTPException standard FastAPI.

    Args:
        request: FastAPI request
        exc: HTTPException

    Returns:
        JSONResponse: Response con error details
    """
    logger.warning(
        f"HTTPException: {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "path": request.url.path,
        },
        headers=exc.headers,
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Handler per eccezioni generiche non gestite.

    Args:
        request: FastAPI request
        exc: Generic exception

    Returns:
        JSONResponse: Response con error message
    """
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
        },
    )

    # Non esporre dettagli dell'errore in production
    message = "Internal server error"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": message,
            "path": request.url.path,
        },
    )


logger.info("Exceptions module initialized")
