"""
Modulo: chat.py
Descrizione: Modelli SQLAlchemy per AI chatbot conversazioni
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from sqlalchemy import Column, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, UUIDMixin
import enum

logger = logging.getLogger(__name__)


class MessageRole(str, enum.Enum):
    """Ruolo messaggio nella conversazione"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class UserFeedback(str, enum.Enum):
    """Feedback utente sulla risposta AI"""
    THUMBS_UP = "thumbs_up"
    THUMBS_DOWN = "thumbs_down"
    NONE = "none"


class ChatConversation(Base, UUIDMixin, TimestampMixin):
    """Conversazione chatbot AI"""
    __tablename__ = "chat_conversations"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True, comment="NULL per guest")
    session_id = Column(String(255), nullable=False, index=True, comment="Browser session tracking")
    total_messages = Column(Integer, nullable=False, default=0)
    user_feedback = Column(Enum(UserFeedback), nullable=True, default=UserFeedback.NONE)
    ended_at = Column(TimestampMixin.created_at.__class__, nullable=True)

    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="ChatMessage.created_at")

    __table_args__ = (
        Index("ix_chat_conversations_user_session", "user_id", "session_id"),
        {"comment": "Conversazioni chatbot AI"},
    )


class ChatMessage(Base, UUIDMixin, TimestampMixin):
    """Singolo messaggio in conversazione"""
    __tablename__ = "chat_messages"

    conversation_id = Column(UUID(as_uuid=True), ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    retrieved_chunks = Column(JSONB, nullable=True, comment="Array chunk IDs usati per RAG")
    claude_message_id = Column(String(255), nullable=True, comment="Message ID da Claude API")
    token_count = Column(Integer, nullable=True)

    conversation = relationship("ChatConversation", back_populates="messages")

    __table_args__ = (
        Index("ix_chat_messages_conversation_created", "conversation_id", "created_at"),
        {"comment": "Messaggi conversazione AI"},
    )


class AIGuardrailConfig(Base, UUIDMixin, TimestampMixin):
    """Configurazione guardrail AI chatbot"""
    __tablename__ = "ai_guardrails_config"

    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="Chiave configurazione")
    config_value = Column(JSONB, nullable=False, comment="Valore configurazione (JSON)")
    description = Column(Text, nullable=True)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    updater = relationship("User")

    __table_args__ = ({"comment": "Configurazione guardrail AI chatbot"},)


logger.debug("Chat models loaded")
