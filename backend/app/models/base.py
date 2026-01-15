"""
Modulo: base.py
Descrizione: Base classes e utilities per modelli SQLAlchemy
Autore: Claude per Davide
Data: 2026-01-15

Questo modulo contiene:
- Classe Base per tutti i modelli
- Mixin per campi comuni (created_at, updated_at, etc.)
- Utilities per UUID generation
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class per tutti i modelli SQLAlchemy.

    Fornisce:
    - Configurazione comune
    - Metodi helper per serializzazione
    """

    # Disabilita automaticamente la generazione del __tablename__
    # Ogni modello deve definirlo esplicitamente
    __abstract__ = True

    def to_dict(self) -> dict[str, Any]:
        """
        Converte il modello in dizionario.

        Returns:
            dict: Rappresentazione dizionario del modello

        Note:
            - Utile per serializzazione JSON
            - Non include relationships per evitare loop infiniti
        """
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """
        Rappresentazione stringa del modello per debugging.

        Returns:
            str: Rappresentazione leggibile del modello
        """
        # Prendi i primi 3 campi per il repr
        attrs = []
        for column in list(self.__table__.columns)[:3]:
            value = getattr(self, column.name)
            attrs.append(f"{column.name}={value!r}")

        return f"{self.__class__.__name__}({', '.join(attrs)})"


class UUIDMixin:
    """
    Mixin che aggiunge campo ID con UUID.

    Fornisce:
    - Campo id (UUID) come primary key
    - Generazione automatica UUID v4
    """

    @declared_attr
    def id(cls):
        """
        Primary key UUID.

        Returns:
            Column: Colonna UUID primary key
        """
        return Column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid.uuid4,
            nullable=False,
            comment="Primary key UUID",
        )


class TimestampMixin:
    """
    Mixin che aggiunge campi timestamp per audit trail.

    Fornisce:
    - created_at: Timestamp creazione record
    - updated_at: Timestamp ultimo aggiornamento (auto-update)
    """

    @declared_attr
    def created_at(cls):
        """
        Timestamp creazione record.

        Returns:
            Column: Colonna datetime con default NOW()
        """
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=datetime.utcnow,
            comment="Timestamp creazione record",
        )

    @declared_attr
    def updated_at(cls):
        """
        Timestamp ultimo aggiornamento.

        Returns:
            Column: Colonna datetime con auto-update
        """
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            comment="Timestamp ultimo aggiornamento",
        )


class SoftDeleteMixin:
    """
    Mixin per soft delete (eliminazione logica).

    Fornisce:
    - deleted_at: Timestamp eliminazione (NULL se non eliminato)

    Note:
        - I record con deleted_at NOT NULL sono considerati eliminati
        - Query devono filtrare per deleted_at IS NULL per vedere solo record attivi
    """

    @declared_attr
    def deleted_at(cls):
        """
        Timestamp eliminazione logica.

        Returns:
            Column: Colonna datetime nullable
        """
        return Column(
            DateTime(timezone=True),
            nullable=True,
            default=None,
            comment="Timestamp eliminazione logica (NULL = attivo)",
        )

    @property
    def is_deleted(self) -> bool:
        """
        Check se il record è stato eliminato logicamente.

        Returns:
            bool: True se deleted_at is not None
        """
        return self.deleted_at is not None

    def soft_delete(self) -> None:
        """
        Elimina logicamente il record.

        Note:
            - Imposta deleted_at a NOW()
            - Non rimuove fisicamente il record dal database
        """
        self.deleted_at = datetime.utcnow()

    def restore(self) -> None:
        """
        Ripristina un record eliminato logicamente.

        Note:
            - Imposta deleted_at a None
        """
        self.deleted_at = None


def generate_uuid() -> uuid.UUID:
    """
    Genera un nuovo UUID v4.

    Returns:
        uuid.UUID: Nuovo UUID

    Note:
        - UUID v4 è random e non contiene informazioni temporali
        - Usato come default per primary keys
    """
    return uuid.uuid4()


# =============================================================================
# Utility Functions
# =============================================================================


def get_or_create_uuid_extension(connection) -> None:
    """
    Abilita l'estensione uuid-ossp in PostgreSQL se non già presente.

    Args:
        connection: Connessione SQLAlchemy

    Note:
        - Necessaria per funzioni UUID native in PostgreSQL
        - Chiamata automaticamente durante migrations
    """
    connection.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")


def get_or_create_pgvector_extension(connection) -> None:
    """
    Abilita l'estensione pgvector in PostgreSQL se non già presente.

    Args:
        connection: Connessione SQLAlchemy

    Note:
        - Necessaria per vector similarity search (RAG chatbot)
        - Deve essere installata nel sistema prima di essere creata
    """
    connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
