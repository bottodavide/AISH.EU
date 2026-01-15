"""
Modulo: env.py
Descrizione: Alembic migration environment configuration
Autore: Claude per Davide
Data: 2026-01-15

Questo modulo configura l'ambiente per le migrations Alembic:
- Carica la configurazione dal database
- Importa tutti i modelli SQLAlchemy
- Gestisce migrations online e offline
"""

import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Importa configurazione app per DATABASE_URL
import sys
import os
from pathlib import Path

# Aggiungi la directory backend al path per import
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.models.base import Base

# Importa TUTTI i modelli per auto-detection modifiche schema
# IMPORTANTE: Ogni nuovo modello deve essere importato qui!
from app.models.user import User, UserProfile, Session, LoginAttempt
from app.models.service import Service, ServiceContent, ServiceFAQ, ServiceImage
from app.models.order import Order, OrderItem, Payment, QuoteRequest
from app.models.invoice import Invoice, InvoiceLine, CreditNote
from app.models.cms import Page, PageVersion, BlogPost, BlogCategory, BlogTag, BlogPostTag, MediaLibrary
from app.models.newsletter import NewsletterSubscriber, EmailCampaign, EmailSend
from app.models.knowledge_base import KnowledgeBaseDocument, KnowledgeBaseChunk
from app.models.chat import ChatConversation, ChatMessage, AIGuardrailConfig
from app.models.support import SupportTicket, TicketMessage, TicketAttachment
from app.models.notification import Notification
from app.models.audit import AuditLog, SystemLog
from app.models.settings import SiteSetting

# Setup logger
logger = logging.getLogger(__name__)

# =============================================================================
# Alembic Config object
# =============================================================================
config = context.config

# Interpreta il file di configurazione per logging Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# =============================================================================
# Metadata per autogenerate
# =============================================================================
# Questo è l'oggetto MetaData che Alembic userà per confrontare
# lo schema attuale con quello desiderato
target_metadata = Base.metadata

# Log dei modelli importati per debugging
logger.info(f"Loaded {len(target_metadata.tables)} tables for migration")
for table_name in target_metadata.tables.keys():
    logger.debug(f"  - Table: {table_name}")


# =============================================================================
# Funzioni helper
# =============================================================================

def get_url():
    """
    Ottiene il DATABASE_URL dalla configurazione.

    Returns:
        str: Connection URL per database PostgreSQL
    """
    # Usa DATABASE_URL da settings
    url = settings.DATABASE_URL
    logger.info(f"Using database URL: {url.split('@')[1] if '@' in url else url}")
    return url


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Questo configura il context con solo un URL e non un Engine,
    anche se un Engine è disponibile.

    Chiama context.execute() per emettere le stringhe SQL
    nel file di output migration.

    In questa modalità, le migrations vengono scritte in un file SQL
    invece di essere eseguite direttamente sul database.
    """
    url = get_url()

    logger.info("Running migrations in OFFLINE mode")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Opzioni per confronto schema
        compare_type=True,  # Confronta tipi colonne
        compare_server_default=True,  # Confronta valori default
    )

    with context.begin_transaction():
        logger.info("Executing migration in offline transaction")
        context.run_migrations()
        logger.info("Offline migration completed")


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In questo scenario dobbiamo creare un Engine e associare
    una connection con il context.

    Questa modalità esegue le migrations direttamente sul database.
    """
    # Ottieni configurazione connection dal alembic.ini
    configuration = config.get_section(config.config_ini_section)

    # Override sqlalchemy.url con quello da settings
    configuration["sqlalchemy.url"] = get_url()

    logger.info("Running migrations in ONLINE mode")

    # Crea connectable (Engine)
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # Non usare connection pooling per migrations
    )

    with connectable.connect() as connection:
        logger.info("Database connection established")

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Opzioni per confronto schema
            compare_type=True,
            compare_server_default=True,
            # Include schemas (opzionale)
            # include_schemas=True,
        )

        with context.begin_transaction():
            logger.info("Executing migration in online transaction")

            try:
                context.run_migrations()
                logger.info("Online migration completed successfully")
            except Exception as e:
                logger.error(f"Migration failed: {str(e)}", exc_info=True)
                raise


# =============================================================================
# Main execution
# =============================================================================

if context.is_offline_mode():
    logger.info("Detected OFFLINE mode")
    run_migrations_offline()
else:
    logger.info("Detected ONLINE mode")
    run_migrations_online()
