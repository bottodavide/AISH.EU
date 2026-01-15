"""
Modulo: notification.py
Descrizione: Modelli SQLAlchemy per notifiche in-app
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, UUIDMixin

logger = logging.getLogger(__name__)


class Notification(Base, UUIDMixin, TimestampMixin):
    """Notifiche in-app per utenti"""
    __tablename__ = "notifications"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True, comment="order_update, invoice_ready, ticket_reply, blog_new, etc.")
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    action_url = Column(String(500), nullable=True, comment="URL per azione (es: /orders/123)")
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    read_at = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User")

    __table_args__ = (
        Index("ix_notifications_user_read", "user_id", "is_read"),
        Index("ix_notifications_user_created", "user_id", "created_at"),
        {"comment": "Notifiche in-app utenti"},
    )


logger.debug("Notification model loaded")
