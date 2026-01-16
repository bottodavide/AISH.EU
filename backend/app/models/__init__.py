"""
Models package - Imports all models for Alembic auto-detection
"""

from app.models.base import Base
from app.models.homepage import HomepageBanner

# Import tutti i modelli per alembic (senza esportarli in __all__)
import app.models.user
import app.models.service
import app.models.order
import app.models.invoice
import app.models.cms
import app.models.chat
import app.models.knowledge_base
import app.models.newsletter
import app.models.file

__all__ = [
    "Base",
    "HomepageBanner",
]
