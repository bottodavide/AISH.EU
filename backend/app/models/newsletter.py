"""
Modulo: newsletter.py
Descrizione: Modelli SQLAlchemy per newsletter e email campaigns
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


class SubscriberStatus(str, enum.Enum):
    PENDING = "pending"  # In attesa double opt-in
    ACTIVE = "active"  # Confermato e attivo
    UNSUBSCRIBED = "unsubscribed"  # Disiscritto
    BOUNCED = "bounced"  # Email bounced


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"


class EmailType(str, enum.Enum):
    TRANSACTIONAL = "transactional"  # Order confirmation, password reset, etc.
    NEWSLETTER = "newsletter"  # Newsletter periodica
    NOTIFICATION = "notification"  # System notifications


class EmailStatus(str, enum.Enum):
    QUEUED = "queued"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    BOUNCED = "bounced"


class NewsletterSubscriber(Base, UUIDMixin, TimestampMixin):
    """Iscritti newsletter"""
    __tablename__ = "newsletter_subscribers"

    email = Column(String(255), unique=True, nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    status = Column(Enum(SubscriberStatus), nullable=False, default=SubscriberStatus.PENDING, index=True)
    subscribed_at = Column(DateTime(timezone=True), nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    unsubscribed_at = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(100), nullable=True, comment="web_form, manual, import")
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    confirmation_token = Column(String(255), nullable=True, unique=True, index=True)

    user = relationship("User")

    __table_args__ = (
        Index("ix_newsletter_subscribers_status", "status"),
        {"comment": "Iscritti newsletter"},
    )


class EmailCampaign(Base, UUIDMixin, TimestampMixin):
    """Campagne email newsletter"""
    __tablename__ = "email_campaigns"

    name = Column(String(255), nullable=False, comment="Nome interno campagna")
    subject = Column(String(255), nullable=False)
    from_name = Column(String(255), nullable=False)
    from_email = Column(String(255), nullable=False)
    html_content = Column(Text, nullable=False)
    text_content = Column(Text, nullable=True)
    status = Column(Enum(CampaignStatus), nullable=False, default=CampaignStatus.DRAFT, index=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    total_recipients = Column(Integer, nullable=False, default=0)
    total_sent = Column(Integer, nullable=False, default=0)
    total_opened = Column(Integer, nullable=False, default=0)
    total_clicked = Column(Integer, nullable=False, default=0)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    creator = relationship("User")
    sends = relationship("EmailSend", back_populates="campaign", cascade="all, delete-orphan")

    __table_args__ = ({"comment": "Campagne email newsletter"},)


class EmailSend(Base, UUIDMixin, TimestampMixin):
    """Log invii email (tracking)"""
    __tablename__ = "email_sends"

    campaign_id = Column(UUID(as_uuid=True), ForeignKey("email_campaigns.id", ondelete="CASCADE"), nullable=True, index=True)
    subscriber_id = Column(UUID(as_uuid=True), ForeignKey("newsletter_subscribers.id", ondelete="SET NULL"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    email_to = Column(String(255), nullable=False, index=True)
    email_type = Column(Enum(EmailType), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    status = Column(Enum(EmailStatus), nullable=False, default=EmailStatus.QUEUED, index=True)
    ms_graph_message_id = Column(String(255), nullable=True, comment="Message ID da MS Graph API")
    opened_at = Column(DateTime(timezone=True), nullable=True, comment="Timestamp apertura email")
    clicked_at = Column(DateTime(timezone=True), nullable=True, comment="Timestamp click link")
    error_message = Column(Text, nullable=True)
    queued_at = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)

    campaign = relationship("EmailCampaign", back_populates="sends")
    subscriber = relationship("NewsletterSubscriber")
    user = relationship("User")

    __table_args__ = (
        Index("ix_email_sends_status_queued", "status", "queued_at"),
        Index("ix_email_sends_campaign_status", "campaign_id", "status"),
        {"comment": "Log invii email con tracking"},
    )


logger.debug("Newsletter models loaded")
