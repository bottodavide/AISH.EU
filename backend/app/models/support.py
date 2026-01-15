"""
Modulo: support.py
Descrizione: Modelli SQLAlchemy per sistema ticket support
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, UUIDMixin
import enum

logger = logging.getLogger(__name__)


class TicketStatus(str, enum.Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, enum.Enum):
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SupportTicket(Base, UUIDMixin, TimestampMixin):
    """Ticket supporto cliente"""
    __tablename__ = "support_tickets"

    ticket_number = Column(String(50), unique=True, nullable=False, index=True, comment="TKT-2026-00001")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(Enum(TicketStatus), nullable=False, default=TicketStatus.NEW, index=True)
    priority = Column(Enum(TicketPriority), nullable=False, default=TicketPriority.MEDIUM, index=True)
    category = Column(String(100), nullable=True, index=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    first_response_at = Column(DateTime(timezone=True), nullable=True, comment="SLA tracking")

    user = relationship("User", foreign_keys=[user_id])
    assigned_user = relationship("User", foreign_keys=[assigned_to])
    messages = relationship("TicketMessage", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketMessage.created_at")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_support_tickets_status_priority", "status", "priority"),
        Index("ix_support_tickets_assigned_status", "assigned_to", "status"),
        {"comment": "Ticket supporto clienti"},
    )


class TicketMessage(Base, UUIDMixin, TimestampMixin):
    """Messaggio conversazione ticket"""
    __tablename__ = "ticket_messages"

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message = Column(Text, nullable=False)
    is_internal = Column(Boolean, nullable=False, default=False, comment="Note interne admin (non visibili a cliente)")

    ticket = relationship("SupportTicket", back_populates="messages")
    user = relationship("User")

    __table_args__ = (
        Index("ix_ticket_messages_ticket_created", "ticket_id", "created_at"),
        {"comment": "Messaggi conversazione ticket"},
    )


class TicketAttachment(Base, UUIDMixin, TimestampMixin):
    """Allegati ticket"""
    __tablename__ = "ticket_attachments"

    ticket_id = Column(UUID(as_uuid=True), ForeignKey("support_tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    message_id = Column(UUID(as_uuid=True), ForeignKey("ticket_messages.id", ondelete="SET NULL"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    ticket = relationship("SupportTicket", back_populates="attachments")
    message = relationship("TicketMessage")
    uploader = relationship("User")

    __table_args__ = ({"comment": "Allegati ticket support"},)


logger.debug("Support models loaded")
