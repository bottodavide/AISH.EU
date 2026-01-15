"""
Modulo: cms.py
Descrizione: Pydantic schemas per CMS (Pages, Blog, Media)
Autore: Claude per Davide
Data: 2026-01-15
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, field_validator

from app.models.cms import PageStatus, PageType


# =============================================================================
# PAGE SCHEMAS
# =============================================================================


class PageBase(BaseModel):
    """Base schema per Page"""

    slug: str = Field(..., max_length=255, description="URL-friendly slug")
    title: str = Field(..., max_length=255, description="Titolo pagina")
    page_type: PageType = Field(..., description="Tipo pagina")
    meta_title: Optional[str] = Field(None, max_length=255, description="SEO title")
    meta_description: Optional[str] = Field(
        None, max_length=500, description="SEO description"
    )
    meta_keywords: Optional[str] = Field(
        None, max_length=500, description="SEO keywords (comma separated)"
    )
    og_image_url: Optional[HttpUrl] = Field(None, description="Open Graph image URL")


class PageContentSection(BaseModel):
    """Schema per sezione di contenuto pagina"""

    section_type: str = Field(
        ..., max_length=50, description="Tipo sezione (hero, text, cta, etc.)"
    )
    content: dict = Field(..., description="Contenuto JSON flessibile")
    order: int = Field(..., ge=0, description="Ordinamento sezione")


class PageCreate(PageBase):
    """Schema per creazione Page"""

    content_sections: List[PageContentSection] = Field(
        default_factory=list, description="Sezioni contenuto"
    )
    is_published: bool = Field(default=False, description="Pubblica subito")


class PageUpdate(BaseModel):
    """Schema per update Page (campi opzionali)"""

    slug: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    page_type: Optional[PageType] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    og_image_url: Optional[HttpUrl] = None
    content_sections: Optional[List[PageContentSection]] = None
    is_published: Optional[bool] = None


class PageResponse(PageBase):
    """Schema per response Page"""

    id: UUID
    status: PageStatus
    is_published: bool
    published_at: Optional[datetime]
    content_sections: List[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PageListResponse(BaseModel):
    """Schema per lista Pages paginata"""

    pages: List[PageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# BLOG SCHEMAS
# =============================================================================


class BlogCategoryBase(BaseModel):
    """Base schema per BlogCategory"""

    name: str = Field(..., max_length=100, description="Nome categoria")
    slug: str = Field(..., max_length=100, description="URL slug")
    description: Optional[str] = Field(None, description="Descrizione categoria")
    sort_order: int = Field(default=0, description="Ordinamento")


class BlogCategoryCreate(BlogCategoryBase):
    """Schema per creazione BlogCategory"""

    pass


class BlogCategoryUpdate(BaseModel):
    """Schema per update BlogCategory"""

    name: Optional[str] = Field(None, max_length=100)
    slug: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    sort_order: Optional[int] = None


class BlogCategoryResponse(BlogCategoryBase):
    """Schema per response BlogCategory"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogTagBase(BaseModel):
    """Base schema per BlogTag"""

    name: str = Field(..., max_length=50, description="Nome tag")
    slug: str = Field(..., max_length=50, description="URL slug")


class BlogTagCreate(BlogTagBase):
    """Schema per creazione BlogTag"""

    pass


class BlogTagResponse(BlogTagBase):
    """Schema per response BlogTag"""

    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogPostBase(BaseModel):
    """Base schema per BlogPost"""

    slug: str = Field(..., max_length=255, description="URL slug")
    title: str = Field(..., max_length=255, description="Titolo post")
    subtitle: Optional[str] = Field(None, max_length=500, description="Sottotitolo")
    excerpt: Optional[str] = Field(None, max_length=500, description="Estratto")
    featured_image_url: Optional[HttpUrl] = Field(None, description="Immagine principale")
    meta_title: Optional[str] = Field(None, max_length=255, description="SEO title")
    meta_description: Optional[str] = Field(
        None, max_length=500, description="SEO description"
    )
    meta_keywords: Optional[str] = Field(
        None, max_length=500, description="SEO keywords"
    )
    og_image_url: Optional[HttpUrl] = Field(None, description="Open Graph image")


class BlogPostCreate(BlogPostBase):
    """Schema per creazione BlogPost"""

    content_html: str = Field(..., description="Contenuto HTML del post")
    category_id: UUID = Field(..., description="ID categoria")
    tag_ids: List[UUID] = Field(default_factory=list, description="IDs tags")
    is_published: bool = Field(default=False, description="Pubblica subito")
    scheduled_publish_at: Optional[datetime] = Field(
        None, description="Scheduling pubblicazione"
    )


class BlogPostUpdate(BaseModel):
    """Schema per update BlogPost"""

    slug: Optional[str] = Field(None, max_length=255)
    title: Optional[str] = Field(None, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=500)
    excerpt: Optional[str] = Field(None, max_length=500)
    content_html: Optional[str] = None
    featured_image_url: Optional[HttpUrl] = None
    category_id: Optional[UUID] = None
    tag_ids: Optional[List[UUID]] = None
    is_published: Optional[bool] = None
    scheduled_publish_at: Optional[datetime] = None
    meta_title: Optional[str] = Field(None, max_length=255)
    meta_description: Optional[str] = Field(None, max_length=500)
    meta_keywords: Optional[str] = Field(None, max_length=500)
    og_image_url: Optional[HttpUrl] = None


class BlogPostResponse(BlogPostBase):
    """Schema per response BlogPost"""

    id: UUID
    author_id: UUID
    category: BlogCategoryResponse
    tags: List[BlogTagResponse]
    content_html: str
    is_published: bool
    published_at: Optional[datetime]
    scheduled_publish_at: Optional[datetime]
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogPostListItem(BaseModel):
    """Schema per item in lista blog posts (senza content)"""

    id: UUID
    slug: str
    title: str
    subtitle: Optional[str]
    excerpt: Optional[str]
    featured_image_url: Optional[HttpUrl]
    category: BlogCategoryResponse
    tags: List[BlogTagResponse]
    author_id: UUID
    is_published: bool
    published_at: Optional[datetime]
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BlogPostListResponse(BaseModel):
    """Schema per lista BlogPosts paginata"""

    posts: List[BlogPostListItem]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# MEDIA LIBRARY SCHEMAS
# =============================================================================


class MediaFileBase(BaseModel):
    """Base schema per Media file (usa File model esistente)"""

    filename: str
    alt_text: Optional[str] = None
    title: Optional[str] = None


class MediaFileResponse(BaseModel):
    """Schema per response Media file"""

    id: UUID
    filename: str
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    file_type: str
    alt_text: Optional[str]
    title: Optional[str]
    thumbnail_path: Optional[str]
    url: str
    thumbnail_url: Optional[str]
    uploaded_by_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class MediaListResponse(BaseModel):
    """Schema per lista Media files paginata"""

    files: List[MediaFileResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# FILTERS SCHEMAS
# =============================================================================


class PageFilters(BaseModel):
    """Filtri per lista Pages"""

    page_type: Optional[PageType] = None
    is_published: Optional[bool] = None
    search: Optional[str] = Field(None, max_length=255, description="Search in title")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class BlogPostFilters(BaseModel):
    """Filtri per lista Blog Posts"""

    category_id: Optional[UUID] = None
    tag_id: Optional[UUID] = None
    is_published: Optional[bool] = None
    search: Optional[str] = Field(
        None, max_length=255, description="Search in title/excerpt"
    )
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class MediaFilters(BaseModel):
    """Filtri per lista Media"""

    file_type: Optional[str] = Field(
        None, description="Filter by type (image, document, etc.)"
    )
    search: Optional[str] = Field(None, max_length=255, description="Search in filename")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=100, description="Items per page")


# =============================================================================
# PUBLISH ACTION SCHEMAS
# =============================================================================


class PublishRequest(BaseModel):
    """Schema per pubblicazione immediata"""

    publish: bool = Field(..., description="True per pubblicare, False per unpublish")


class SchedulePublishRequest(BaseModel):
    """Schema per scheduling pubblicazione"""

    scheduled_publish_at: datetime = Field(..., description="Data/ora pubblicazione")

    @field_validator("scheduled_publish_at")
    @classmethod
    def validate_future_date(cls, v: datetime) -> datetime:
        """Valida che la data sia futura"""
        if v <= datetime.utcnow():
            raise ValueError("Scheduled publish date must be in the future")
        return v
