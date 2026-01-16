"""
Modulo: knowledge_base.py
Descrizione: Modelli SQLAlchemy per knowledge base e RAG (AI chatbot)
Autore: Claude per Davide
Data: 2026-01-15

Usa pgvector per vector similarity search
"""

import logging
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, UUIDMixin
import enum

# Import pgvector type
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Fallback se pgvector non installato (per tests)
    Vector = None

logger = logging.getLogger(__name__)


class KnowledgeTopic(str, enum.Enum):
    """Topic per categorizzazione knowledge base"""
    AI = "AI"
    GDPR = "GDPR"
    NIS2 = "NIS2"
    CYBERSECURITY = "CYBERSECURITY"
    GENERAL = "GENERAL"


# Alias per compatibilità con routes
DocumentTopic = KnowledgeTopic


class DocumentType(str, enum.Enum):
    """Tipo di documento"""
    PDF = "PDF"
    TEXT = "TEXT"
    URL = "URL"
    DOCX = "DOCX"
    MD = "MD"


class ProcessingStatus(str, enum.Enum):
    """Stato processing documento"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class KnowledgeBaseDocument(Base, UUIDMixin, TimestampMixin):
    """
    Documenti caricati nella knowledge base.

    Supporta: PDF, DOCX, TXT, MD
    """
    __tablename__ = "knowledge_base_documents"

    title = Column(String(255), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False, default=DocumentType.TEXT)
    topic = Column(Enum(DocumentTopic), nullable=False, index=True)
    description = Column(Text, nullable=True)
    source_url = Column(String(500), nullable=True)
    author = Column(String(100), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True, comment="Size in bytes")
    content_text = Column(Text, nullable=True, comment="Estratto plain text")
    chunk_count = Column(Integer, nullable=False, default=0)
    processing_status = Column(Enum(ProcessingStatus), nullable=False, default=ProcessingStatus.PENDING)
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    processed_at = Column(DateTime, nullable=True)
    uploaded_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    uploader = relationship("User", foreign_keys=[uploaded_by_user_id])
    chunks = relationship("KnowledgeBaseChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_knowledge_base_docs_topic_active", "topic", "is_active"),
        {"comment": "Documenti knowledge base per RAG"},
    )


class KnowledgeBaseChunk(Base, UUIDMixin, TimestampMixin):
    """
    Chunks di testo con embeddings per RAG.

    Ogni documento viene diviso in chunks per vector search.
    """
    __tablename__ = "knowledge_base_chunks"

    document_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_base_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False, comment="Indice chunk nel documento")
    chunk_text = Column(Text, nullable=False, comment="Testo chunk")

    # Vector embedding (dimensione 1536 per OpenAI text-embedding-3-small)
    # O dimensione custom per altri modelli
    # Fallback to Text if pgvector not installed
    embedding = Column(
        Vector(1536) if Vector else Text,
        nullable=True,
        comment="Vector embedding per similarity search"
    )

    token_count = Column(Integer, nullable=True, comment="Numero token nel chunk")
    chunk_metadata = Column(JSONB, nullable=True, comment="Metadata aggiuntivi (page_number, section, etc.)")

    document = relationship("KnowledgeBaseDocument", back_populates="chunks")

    __table_args__ = (
        Index("ix_knowledge_base_chunks_doc_idx", "document_id", "chunk_index"),
        # Index per vector similarity search (ivfflat)
        # Creato manualmente nella migration con:
        # CREATE INDEX ON knowledge_base_chunks USING ivfflat (embedding vector_cosine_ops)
        {"comment": "Chunks con embeddings per RAG"},
    )


logger.debug("Knowledge base models loaded")
