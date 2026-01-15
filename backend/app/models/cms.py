"""
Modulo: cms.py
Descrizione: Modelli SQLAlchemy per CMS headless (pagine, blog, media)
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin, UUIDMixin
import enum

logger = logging.getLogger(__name__)


class PageType(str, enum.Enum):
    HOMEPAGE = "homepage"
    SERVICE = "service"
    ABOUT = "about"
    CONTACT = "contact"
    CUSTOM = "custom"


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Page(Base, UUIDMixin, TimestampMixin):
    """Pagine CMS modificabili (Homepage, About, Contact, etc.)"""
    __tablename__ = "pages"

    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    page_type = Column(Enum(PageType), nullable=False, index=True)
    content_blocks = Column(JSONB, nullable=True, comment="Array blocchi content JSON")
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)
    seo_keywords = Column(Text, nullable=True)
    og_image = Column(String(500), nullable=True)
    status = Column(Enum(ContentStatus), nullable=False, default=ContentStatus.DRAFT, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    versions = relationship("PageVersion", back_populates="page", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_pages_status_published", "status", "published_at"),
        {"comment": "Pagine CMS"},
    )


class PageVersion(Base, UUIDMixin, TimestampMixin):
    """Versioning pagine per rollback"""
    __tablename__ = "page_versions"

    page_id = Column(UUID(as_uuid=True), ForeignKey("pages.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content_snapshot = Column(JSONB, nullable=False, comment="Snapshot completo contenuto")
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    page = relationship("Page", back_populates="versions")

    __table_args__ = (
        Index("ix_page_versions_page_version", "page_id", "version_number", unique=True),
        {"comment": "Versioni pagine per rollback"},
    )


class BlogPost(Base, UUIDMixin, TimestampMixin):
    """Post blog con rich text editor"""
    __tablename__ = "blog_posts"

    slug = Column(String(255), unique=True, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    excerpt = Column(Text, nullable=True)
    content = Column(Text, nullable=False, comment="HTML da rich text editor")
    featured_image = Column(String(500), nullable=True)
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("blog_categories.id"), nullable=True, index=True)
    status = Column(Enum(ContentStatus), nullable=False, default=ContentStatus.DRAFT, index=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    scheduled_publish_at = Column(DateTime(timezone=True), nullable=True, index=True)
    view_count = Column(Integer, nullable=False, default=0)
    seo_title = Column(String(255), nullable=True)
    seo_description = Column(Text, nullable=True)

    author = relationship("User")
    category = relationship("BlogCategory")
    tags = relationship("BlogTag", secondary="blog_post_tags", back_populates="posts")

    __table_args__ = (
        Index("ix_blog_posts_published", "status", "published_at"),
        {"comment": "Post blog"},
    )


class BlogCategory(Base, UUIDMixin, TimestampMixin):
    """Categorie blog"""
    __tablename__ = "blog_categories"

    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    sort_order = Column(Integer, nullable=False, default=0)

    __table_args__ = ({"comment": "Categorie blog"},)


class BlogTag(Base, UUIDMixin, TimestampMixin):
    """Tag blog"""
    __tablename__ = "blog_tags"

    name = Column(String(50), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)

    posts = relationship("BlogPost", secondary="blog_post_tags", back_populates="tags")

    __table_args__ = ({"comment": "Tag blog"},)


class BlogPostTag(Base):
    """Many-to-many blog posts <-> tags"""
    __tablename__ = "blog_post_tags"

    blog_post_id = Column(UUID(as_uuid=True), ForeignKey("blog_posts.id", ondelete="CASCADE"), primary_key=True)
    blog_tag_id = Column(UUID(as_uuid=True), ForeignKey("blog_tags.id", ondelete="CASCADE"), primary_key=True)

    __table_args__ = ({"comment": "Relazione blog posts - tags"},)


class MediaLibrary(Base, UUIDMixin, TimestampMixin):
    """Media library per upload immagini/file"""
    __tablename__ = "media_library"

    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_url = Column(String(500), nullable=False)
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False, comment="Size in bytes")
    width = Column(Integer, nullable=True, comment="Per immagini")
    height = Column(Integer, nullable=True, comment="Per immagini")
    alt_text = Column(String(255), nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    folder = Column(String(255), nullable=False, default="/", comment="Organizzazione virtuale")

    uploader = relationship("User")

    __table_args__ = (
        Index("ix_media_library_folder", "folder"),
        Index("ix_media_library_mime", "mime_type"),
        {"comment": "Media library per upload files"},
    )


logger.debug("CMS models loaded")
