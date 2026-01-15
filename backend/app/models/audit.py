"""
Modulo: audit.py
Descrizione: Modelli SQLAlchemy per audit trail e system logs
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, UUIDMixin
import enum

logger = logging.getLogger(__name__)


class AuditAction(str, enum.Enum):
    """Azioni audit trail"""
    LOGIN = "login"
    LOGOUT = "logout"
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    IMPORT = "import"


class LogLevel(str, enum.Enum):
    """Livelli log sistema"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base, UUIDMixin):
    """Audit trail azioni utenti (compliance & security)"""
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(Enum(AuditAction), nullable=False, index=True, comment="Tipo azione eseguita")
    entity_type = Column(String(50), nullable=True, index=True, comment="orders, users, invoices, etc.")
    entity_id = Column(UUID(as_uuid=True), nullable=True, comment="ID entità modificata")
    changes = Column(JSONB, nullable=True, comment="Before/After values JSON")
    ip_address = Column(INET, nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False)

    user = relationship("User")

    __table_args__ = (
        Index("ix_audit_logs_user_created", "user_id", "created_at"),
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_action_created", "action", "created_at"),
        {"comment": "Audit trail azioni utenti"},
    )


class SystemLog(Base, UUIDMixin):
    """Log applicazione per debugging e monitoring"""
    __tablename__ = "system_logs"

    level = Column(Enum(LogLevel), nullable=False, index=True)
    module = Column(String(100), nullable=False, index=True, comment="auth, payment, email, cms, api, etc.")
    message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    context = Column(JSONB, nullable=True, comment="Extra metadata")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    ip_address = Column(INET, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, index=True)

    user = relationship("User")

    __table_args__ = (
        Index("ix_system_logs_level_created", "level", "created_at"),
        Index("ix_system_logs_module_created", "module", "created_at"),
        {"comment": "Log applicazione sistema"},
    )


logger.debug("Audit models loaded")
