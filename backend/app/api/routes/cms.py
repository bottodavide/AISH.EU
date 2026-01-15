"""
Modulo: cms.py
Descrizione: API routes per CMS (Pages, Blog, Media Library)
Autore: Claude per Davide
Data: 2026-01-15

Endpoints:
PAGES:
- GET    /api/v1/cms/pages - Lista pagine
- POST   /api/v1/cms/pages - Crea pagina
- GET    /api/v1/cms/pages/{id} - Dettaglio pagina
- PUT    /api/v1/cms/pages/{id} - Aggiorna pagina
- DELETE /api/v1/cms/pages/{id} - Elimina pagina
- POST   /api/v1/cms/pages/{id}/publish - Pubblica/Unpublish

BLOG CATEGORIES:
- GET    /api/v1/cms/blog/categories - Lista categorie
- POST   /api/v1/cms/blog/categories - Crea categoria
- PUT    /api/v1/cms/blog/categories/{id} - Aggiorna categoria
- DELETE /api/v1/cms/blog/categories/{id} - Elimina categoria

BLOG TAGS:
- GET    /api/v1/cms/blog/tags - Lista tags
- POST   /api/v1/cms/blog/tags - Crea tag
- DELETE /api/v1/cms/blog/tags/{id} - Elimina tag

BLOG POSTS:
- GET    /api/v1/cms/blog/posts - Lista posts
- POST   /api/v1/cms/blog/posts - Crea post
- GET    /api/v1/cms/blog/posts/{id} - Dettaglio post
- PUT    /api/v1/cms/blog/posts/{id} - Aggiorna post
- DELETE /api/v1/cms/blog/posts/{id} - Elimina post
- POST   /api/v1/cms/blog/posts/{id}/publish - Pubblica/Unpublish

MEDIA:
- GET    /api/v1/cms/media - Lista media files (usa /files endpoint esistente)

Note:
- Tutti gli endpoint richiedono autenticazione
- Solo ADMIN e EDITOR possono creare/modificare contenuti
- Pubblico può vedere solo contenuti published
"""

import logging
from datetime import datetime, timezone
from math import ceil
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_async_db
from app.core.dependencies import (
    get_current_active_user,
    get_current_user_optional,
    require_admin_or_editor,
)
from app.core.exceptions import (
    DuplicateResourceError,
    ResourceNotFoundError,
    ValidationError,
)
from app.models.audit import AuditAction, AuditLog
from app.models.cms import (
    BlogCategory,
    BlogPost,
    BlogTag,
    Page,
    ContentStatus,
)
from app.models.user import User
from app.schemas.base import SuccessResponse
from app.schemas.cms import (
    BlogCategoryCreate,
    BlogCategoryResponse,
    BlogCategoryUpdate,
    BlogPostCreate,
    BlogPostFilters,
    BlogPostListResponse,
    BlogPostResponse,
    BlogPostUpdate,
    BlogTagCreate,
    BlogTagResponse,
    PageCreate,
    PageFilters,
    PageListResponse,
    PageResponse,
    PageUpdate,
    PublishRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cms", tags=["CMS"])


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


async def get_page_or_404(db: AsyncSession, page_id: UUID) -> Page:
    """
    Recupera pagina per ID o raise 404.

    Args:
        db: Database session
        page_id: ID pagina

    Returns:
        Page: Pagina trovata

    Raises:
        ResourceNotFoundError: Se pagina non trovata
    """
    logger.debug(f"Fetching page {page_id}")

    result = await db.execute(select(Page).where(Page.id == page_id))
    page = result.scalar_one_or_none()

    if not page:
        logger.warning(f"Page not found: {page_id}")
        raise ResourceNotFoundError(f"Page with ID {page_id} not found")

    return page


async def get_blog_post_or_404(db: AsyncSession, post_id: UUID) -> BlogPost:
    """
    Recupera blog post per ID o raise 404.

    Args:
        db: Database session
        post_id: ID post

    Returns:
        BlogPost: Post trovato

    Raises:
        ResourceNotFoundError: Se post non trovato
    """
    logger.debug(f"Fetching blog post {post_id}")

    result = await db.execute(
        select(BlogPost)
        .options(
            selectinload(BlogPost.category), selectinload(BlogPost.tags)
        )
        .where(BlogPost.id == post_id)
    )
    post = result.scalar_one_or_none()

    if not post:
        logger.warning(f"Blog post not found: {post_id}")
        raise ResourceNotFoundError(f"Blog post with ID {post_id} not found")

    return post


async def create_audit_log(
    db: AsyncSession,
    user_id: UUID,
    action: AuditAction,
    entity_type: str,
    entity_id: UUID,
    details: Optional[dict] = None,
):
    """
    Crea audit log entry.

    Args:
        db: Database session
        user_id: ID utente che ha eseguito azione
        action: Tipo azione
        entity_type: Tipo entità (page, blog_post, etc.)
        entity_id: ID entità
        details: Dettagli opzionali
    """
    logger.debug(
        f"Creating audit log: user={user_id}, action={action}, entity={entity_type}:{entity_id}"
    )

    audit_entry = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details or {},
    )

    db.add(audit_entry)


# =============================================================================
# PAGES ENDPOINTS
# =============================================================================


@router.get("/pages", response_model=PageListResponse)
async def list_pages(
    filters: PageFilters = Depends(),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> PageListResponse:
    """
    Lista pagine con filtri e pagination.

    - **Pubblico**: Vede solo pagine pubblicate
    - **Admin/Editor**: Vede tutte le pagine

    Args:
        filters: Filtri di ricerca
        current_user: Utente corrente (opzionale)
        db: Database session

    Returns:
        PageListResponse: Lista pagine paginata
    """
    logger.info("Listing pages")

    # Build query
    query = select(Page)

    # Se non admin/editor, mostra solo published
    is_admin_or_editor = current_user and current_user.role in [
        "super_admin",
        "admin",
        "editor",
    ]
    if not is_admin_or_editor:
        query = query.where(Page.is_published == True)

    # Apply filters
    if filters.page_type:
        query = query.where(Page.page_type == filters.page_type)

    if filters.is_published is not None and is_admin_or_editor:
        query = query.where(Page.is_published == filters.is_published)

    if filters.search:
        search_pattern = f"%{filters.search}%"
        query = query.where(Page.title.ilike(search_pattern))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (filters.page - 1) * filters.page_size
    query = query.offset(offset).limit(filters.page_size)

    # Order by updated_at desc
    query = query.order_by(desc(Page.updated_at))

    # Execute query
    result = await db.execute(query)
    pages = result.scalars().all()

    logger.info(f"Found {total} pages, returning page {filters.page}")

    return PageListResponse(
        pages=[PageResponse.model_validate(page) for page in pages],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=ceil(total / filters.page_size) if total > 0 else 0,
    )


@router.get("/pages/{page_id}", response_model=PageResponse)
async def get_page(
    page_id: UUID,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> PageResponse:
    """
    Dettaglio pagina per ID.

    - **Pubblico**: Può vedere solo pagine pubblicate
    - **Admin/Editor**: Può vedere tutte le pagine

    Args:
        page_id: ID pagina
        current_user: Utente corrente (opzionale)
        db: Database session

    Returns:
        PageResponse: Dettaglio pagina

    Raises:
        ResourceNotFoundError: Se pagina non trovata o non accessibile
    """
    logger.info(f"Getting page {page_id}")

    page = await get_page_or_404(db, page_id)

    # Check access
    is_admin_or_editor = current_user and current_user.role in [
        "super_admin",
        "admin",
        "editor",
    ]

    if not page.is_published and not is_admin_or_editor:
        logger.warning(f"Unauthorized access to unpublished page {page_id}")
        raise ResourceNotFoundError(f"Page with ID {page_id} not found")

    return PageResponse.model_validate(page)


@router.post("/pages", response_model=PageResponse, status_code=status.HTTP_201_CREATED)
async def create_page(
    page_data: PageCreate,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> PageResponse:
    """
    Crea nuova pagina.

    **Richiede**: Admin o Editor

    Args:
        page_data: Dati pagina
        current_user: Utente corrente
        db: Database session

    Returns:
        PageResponse: Pagina creata

    Raises:
        DuplicateResourceError: Se slug già esistente
    """
    logger.info(f"Creating page: {page_data.title}")

    # Check slug unique
    result = await db.execute(select(Page).where(Page.slug == page_data.slug))
    if result.scalar_one_or_none():
        logger.warning(f"Duplicate slug: {page_data.slug}")
        raise DuplicateResourceError(f"Page with slug '{page_data.slug}' already exists")

    # Create page
    page = Page(
        slug=page_data.slug,
        title=page_data.title,
        page_type=page_data.page_type,
        content_sections={"sections": [s.model_dump() for s in page_data.content_sections]},
        meta_title=page_data.meta_title,
        meta_description=page_data.meta_description,
        meta_keywords=page_data.meta_keywords,
        og_image_url=str(page_data.og_image_url) if page_data.og_image_url else None,
        is_published=page_data.is_published,
        status=ContentStatus.PUBLISHED if page_data.is_published else ContentStatus.DRAFT,
        published_at=datetime.now(timezone.utc) if page_data.is_published else None,
    )

    db.add(page)
    await db.flush()

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="page",
        entity_id=page.id,
        details={"title": page.title, "slug": page.slug},
    )

    await db.commit()
    await db.refresh(page)

    logger.info(f"Page created: {page.id}")

    return PageResponse.model_validate(page)


@router.put("/pages/{page_id}", response_model=PageResponse)
async def update_page(
    page_id: UUID,
    page_data: PageUpdate,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> PageResponse:
    """
    Aggiorna pagina esistente.

    **Richiede**: Admin o Editor

    Args:
        page_id: ID pagina
        page_data: Dati aggiornati
        current_user: Utente corrente
        db: Database session

    Returns:
        PageResponse: Pagina aggiornata

    Raises:
        ResourceNotFoundError: Se pagina non trovata
        DuplicateResourceError: Se nuovo slug già esistente
    """
    logger.info(f"Updating page {page_id}")

    page = await get_page_or_404(db, page_id)

    # Check slug unique se changed
    if page_data.slug and page_data.slug != page.slug:
        result = await db.execute(select(Page).where(Page.slug == page_data.slug))
        if result.scalar_one_or_none():
            logger.warning(f"Duplicate slug: {page_data.slug}")
            raise DuplicateResourceError(f"Page with slug '{page_data.slug}' already exists")

    # Update fields
    update_data = page_data.model_dump(exclude_unset=True)

    if "content_sections" in update_data and update_data["content_sections"]:
        update_data["content_sections"] = {
            "sections": [s.model_dump() for s in page_data.content_sections]
        }

    if "og_image_url" in update_data and update_data["og_image_url"]:
        update_data["og_image_url"] = str(update_data["og_image_url"])

    for field, value in update_data.items():
        setattr(page, field, value)

    # Update status if published changed
    if page_data.is_published is not None:
        if page_data.is_published and not page.is_published:
            # Publishing
            page.status = ContentStatus.PUBLISHED
            page.published_at = datetime.now(timezone.utc)
        elif not page_data.is_published and page.is_published:
            # Unpublishing
            page.status = ContentStatus.DRAFT
            page.published_at = None

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="page",
        entity_id=page.id,
        details={"updated_fields": list(update_data.keys())},
    )

    await db.commit()
    await db.refresh(page)

    logger.info(f"Page updated: {page.id}")

    return PageResponse.model_validate(page)


@router.delete("/pages/{page_id}", response_model=SuccessResponse)
async def delete_page(
    page_id: UUID,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina pagina.

    **Richiede**: Admin o Editor

    Args:
        page_id: ID pagina
        current_user: Utente corrente
        db: Database session

    Returns:
        SuccessResponse: Conferma eliminazione

    Raises:
        ResourceNotFoundError: Se pagina non trovata
    """
    logger.info(f"Deleting page {page_id}")

    page = await get_page_or_404(db, page_id)

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="page",
        entity_id=page.id,
        details={"title": page.title, "slug": page.slug},
    )

    await db.delete(page)
    await db.commit()

    logger.info(f"Page deleted: {page_id}")

    return SuccessResponse(message="Page deleted successfully")


@router.post("/pages/{page_id}/publish", response_model=PageResponse)
async def toggle_publish_page(
    page_id: UUID,
    publish_data: PublishRequest,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> PageResponse:
    """
    Pubblica o unpublish pagina.

    **Richiede**: Admin o Editor

    Args:
        page_id: ID pagina
        publish_data: Action (publish o unpublish)
        current_user: Utente corrente
        db: Database session

    Returns:
        PageResponse: Pagina aggiornata

    Raises:
        ResourceNotFoundError: Se pagina non trovata
    """
    logger.info(f"Toggling publish for page {page_id}: publish={publish_data.publish}")

    page = await get_page_or_404(db, page_id)

    if publish_data.publish:
        # Publish
        page.is_published = True
        page.status = ContentStatus.PUBLISHED
        page.published_at = datetime.now(timezone.utc)
        action_type = "published"
    else:
        # Unpublish
        page.is_published = False
        page.status = ContentStatus.DRAFT
        page.published_at = None
        action_type = "unpublished"

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="page",
        entity_id=page.id,
        details={"action": action_type},
    )

    await db.commit()
    await db.refresh(page)

    logger.info(f"Page {action_type}: {page.id}")

    return PageResponse.model_validate(page)


# =============================================================================
# BLOG CATEGORIES ENDPOINTS
# =============================================================================


@router.get("/blog/categories", response_model=list[BlogCategoryResponse])
async def list_blog_categories(
    db: AsyncSession = Depends(get_async_db),
) -> list[BlogCategoryResponse]:
    """
    Lista tutte le categorie blog.

    **Pubblico**: Accessibile a tutti

    Returns:
        list[BlogCategoryResponse]: Lista categorie ordinate per sort_order
    """
    logger.info("Listing blog categories")

    result = await db.execute(select(BlogCategory).order_by(BlogCategory.sort_order))
    categories = result.scalars().all()

    logger.info(f"Found {len(categories)} blog categories")

    return [BlogCategoryResponse.model_validate(cat) for cat in categories]


@router.post(
    "/blog/categories",
    response_model=BlogCategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_blog_category(
    category_data: BlogCategoryCreate,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> BlogCategoryResponse:
    """
    Crea nuova categoria blog.

    **Richiede**: Admin o Editor

    Args:
        category_data: Dati categoria
        current_user: Utente corrente
        db: Database session

    Returns:
        BlogCategoryResponse: Categoria creata

    Raises:
        DuplicateResourceError: Se nome o slug già esistente
    """
    logger.info(f"Creating blog category: {category_data.name}")

    # Check unique name
    result = await db.execute(
        select(BlogCategory).where(BlogCategory.name == category_data.name)
    )
    if result.scalar_one_or_none():
        raise DuplicateResourceError(
            f"Category with name '{category_data.name}' already exists"
        )

    # Check unique slug
    result = await db.execute(
        select(BlogCategory).where(BlogCategory.slug == category_data.slug)
    )
    if result.scalar_one_or_none():
        raise DuplicateResourceError(
            f"Category with slug '{category_data.slug}' already exists"
        )

    # Create category
    category = BlogCategory(**category_data.model_dump())
    db.add(category)

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="blog_category",
        entity_id=category.id,
        details={"name": category.name},
    )

    await db.commit()
    await db.refresh(category)

    logger.info(f"Blog category created: {category.id}")

    return BlogCategoryResponse.model_validate(category)


@router.put("/blog/categories/{category_id}", response_model=BlogCategoryResponse)
async def update_blog_category(
    category_id: UUID,
    category_data: BlogCategoryUpdate,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> BlogCategoryResponse:
    """
    Aggiorna categoria blog.

    **Richiede**: Admin o Editor

    Args:
        category_id: ID categoria
        category_data: Dati aggiornati
        current_user: Utente corrente
        db: Database session

    Returns:
        BlogCategoryResponse: Categoria aggiornata

    Raises:
        ResourceNotFoundError: Se categoria non trovata
        DuplicateResourceError: Se nuovo nome/slug già esistente
    """
    logger.info(f"Updating blog category {category_id}")

    result = await db.execute(select(BlogCategory).where(BlogCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise ResourceNotFoundError(f"Category with ID {category_id} not found")

    # Check unique name if changed
    if category_data.name and category_data.name != category.name:
        result = await db.execute(
            select(BlogCategory).where(BlogCategory.name == category_data.name)
        )
        if result.scalar_one_or_none():
            raise DuplicateResourceError(
                f"Category with name '{category_data.name}' already exists"
            )

    # Check unique slug if changed
    if category_data.slug and category_data.slug != category.slug:
        result = await db.execute(
            select(BlogCategory).where(BlogCategory.slug == category_data.slug)
        )
        if result.scalar_one_or_none():
            raise DuplicateResourceError(
                f"Category with slug '{category_data.slug}' already exists"
            )

    # Update fields
    for field, value in category_data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="blog_category",
        entity_id=category.id,
    )

    await db.commit()
    await db.refresh(category)

    logger.info(f"Blog category updated: {category.id}")

    return BlogCategoryResponse.model_validate(category)


@router.delete("/blog/categories/{category_id}", response_model=SuccessResponse)
async def delete_blog_category(
    category_id: UUID,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina categoria blog.

    **Richiede**: Admin o Editor
    **Note**: Non può eliminare categoria con posts associati

    Args:
        category_id: ID categoria
        current_user: Utente corrente
        db: Database session

    Returns:
        SuccessResponse: Conferma eliminazione

    Raises:
        ResourceNotFoundError: Se categoria non trovata
        ValidationError: Se categoria ha posts associati
    """
    logger.info(f"Deleting blog category {category_id}")

    result = await db.execute(select(BlogCategory).where(BlogCategory.id == category_id))
    category = result.scalar_one_or_none()
    if not category:
        raise ResourceNotFoundError(f"Category with ID {category_id} not found")

    # Check if has posts
    posts_result = await db.execute(
        select(func.count(BlogPost.id)).where(BlogPost.category_id == category_id)
    )
    posts_count = posts_result.scalar()

    if posts_count > 0:
        raise ValidationError(
            f"Cannot delete category with {posts_count} associated posts. "
            "Please reassign or delete posts first."
        )

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="blog_category",
        entity_id=category.id,
        details={"name": category.name},
    )

    await db.delete(category)
    await db.commit()

    logger.info(f"Blog category deleted: {category_id}")

    return SuccessResponse(message="Category deleted successfully")


# =============================================================================
# BLOG TAGS ENDPOINTS
# =============================================================================


@router.get("/blog/tags", response_model=list[BlogTagResponse])
async def list_blog_tags(
    db: AsyncSession = Depends(get_async_db),
) -> list[BlogTagResponse]:
    """
    Lista tutti i tags blog.

    **Pubblico**: Accessibile a tutti

    Returns:
        list[BlogTagResponse]: Lista tags ordinati per nome
    """
    logger.info("Listing blog tags")

    result = await db.execute(select(BlogTag).order_by(BlogTag.name))
    tags = result.scalars().all()

    logger.info(f"Found {len(tags)} blog tags")

    return [BlogTagResponse.model_validate(tag) for tag in tags]


@router.post(
    "/blog/tags", response_model=BlogTagResponse, status_code=status.HTTP_201_CREATED
)
async def create_blog_tag(
    tag_data: BlogTagCreate,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> BlogTagResponse:
    """
    Crea nuovo tag blog.

    **Richiede**: Admin o Editor

    Args:
        tag_data: Dati tag
        current_user: Utente corrente
        db: Database session

    Returns:
        BlogTagResponse: Tag creato

    Raises:
        DuplicateResourceError: Se nome o slug già esistente
    """
    logger.info(f"Creating blog tag: {tag_data.name}")

    # Check unique name
    result = await db.execute(select(BlogTag).where(BlogTag.name == tag_data.name))
    if result.scalar_one_or_none():
        raise DuplicateResourceError(f"Tag with name '{tag_data.name}' already exists")

    # Check unique slug
    result = await db.execute(select(BlogTag).where(BlogTag.slug == tag_data.slug))
    if result.scalar_one_or_none():
        raise DuplicateResourceError(f"Tag with slug '{tag_data.slug}' already exists")

    # Create tag
    tag = BlogTag(**tag_data.model_dump())
    db.add(tag)

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="blog_tag",
        entity_id=tag.id,
        details={"name": tag.name},
    )

    await db.commit()
    await db.refresh(tag)

    logger.info(f"Blog tag created: {tag.id}")

    return BlogTagResponse.model_validate(tag)


@router.delete("/blog/tags/{tag_id}", response_model=SuccessResponse)
async def delete_blog_tag(
    tag_id: UUID,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina tag blog.

    **Richiede**: Admin o Editor
    **Note**: Rimuove associazioni con posts ma non elimina posts

    Args:
        tag_id: ID tag
        current_user: Utente corrente
        db: Database session

    Returns:
        SuccessResponse: Conferma eliminazione

    Raises:
        ResourceNotFoundError: Se tag non trovato
    """
    logger.info(f"Deleting blog tag {tag_id}")

    result = await db.execute(select(BlogTag).where(BlogTag.id == tag_id))
    tag = result.scalar_one_or_none()
    if not tag:
        raise ResourceNotFoundError(f"Tag with ID {tag_id} not found")

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="blog_tag",
        entity_id=tag.id,
        details={"name": tag.name},
    )

    await db.delete(tag)
    await db.commit()

    logger.info(f"Blog tag deleted: {tag_id}")

    return SuccessResponse(message="Tag deleted successfully")


# =============================================================================
# BLOG POSTS ENDPOINTS
# =============================================================================


@router.get("/blog/posts", response_model=BlogPostListResponse)
async def list_blog_posts(
    filters: BlogPostFilters = Depends(),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> BlogPostListResponse:
    """
    Lista blog posts con filtri e pagination.

    - **Pubblico**: Vede solo posts pubblicati
    - **Admin/Editor**: Vede tutti i posts

    Args:
        filters: Filtri di ricerca
        current_user: Utente corrente (opzionale)
        db: Database session

    Returns:
        BlogPostListResponse: Lista posts paginata
    """
    logger.info("Listing blog posts")

    # Build query
    query = select(BlogPost).options(
        selectinload(BlogPost.category), selectinload(BlogPost.tags)
    )

    # Se non admin/editor, mostra solo published
    is_admin_or_editor = current_user and current_user.role in [
        "super_admin",
        "admin",
        "editor",
    ]
    if not is_admin_or_editor:
        query = query.where(BlogPost.is_published == True)

    # Apply filters
    if filters.category_id:
        query = query.where(BlogPost.category_id == filters.category_id)

    if filters.tag_id:
        # Join with tags table
        query = query.join(BlogPost.tags).where(BlogTag.id == filters.tag_id)

    if filters.is_published is not None and is_admin_or_editor:
        query = query.where(BlogPost.is_published == filters.is_published)

    if filters.search:
        search_pattern = f"%{filters.search}%"
        query = query.where(
            or_(
                BlogPost.title.ilike(search_pattern),
                BlogPost.excerpt.ilike(search_pattern),
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Apply pagination
    offset = (filters.page - 1) * filters.page_size
    query = query.offset(offset).limit(filters.page_size)

    # Order by published_at/updated_at desc
    query = query.order_by(
        desc(BlogPost.published_at), desc(BlogPost.updated_at)
    )

    # Execute query
    result = await db.execute(query)
    posts = result.unique().scalars().all()

    logger.info(f"Found {total} blog posts, returning page {filters.page}")

    return BlogPostListResponse(
        posts=[
            {
                "id": post.id,
                "slug": post.slug,
                "title": post.title,
                "subtitle": post.subtitle,
                "excerpt": post.excerpt,
                "featured_image_url": post.featured_image_url,
                "category": BlogCategoryResponse.model_validate(post.category),
                "tags": [BlogTagResponse.model_validate(t) for t in post.tags],
                "author_id": post.author_id,
                "is_published": post.is_published,
                "published_at": post.published_at,
                "view_count": post.view_count,
                "created_at": post.created_at,
                "updated_at": post.updated_at,
            }
            for post in posts
        ],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
        total_pages=ceil(total / filters.page_size) if total > 0 else 0,
    )


@router.get("/blog/posts/{post_id}", response_model=BlogPostResponse)
async def get_blog_post(
    post_id: UUID,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_async_db),
) -> BlogPostResponse:
    """
    Dettaglio blog post per ID.

    - **Pubblico**: Può vedere solo posts pubblicati (incrementa view_count)
    - **Admin/Editor**: Può vedere tutti i posts (no increment view_count)

    Args:
        post_id: ID post
        current_user: Utente corrente (opzionale)
        db: Database session

    Returns:
        BlogPostResponse: Dettaglio post

    Raises:
        ResourceNotFoundError: Se post non trovato o non accessibile
    """
    logger.info(f"Getting blog post {post_id}")

    post = await get_blog_post_or_404(db, post_id)

    # Check access
    is_admin_or_editor = current_user and current_user.role in [
        "super_admin",
        "admin",
        "editor",
    ]

    if not post.is_published and not is_admin_or_editor:
        logger.warning(f"Unauthorized access to unpublished post {post_id}")
        raise ResourceNotFoundError(f"Blog post with ID {post_id} not found")

    # Increment view count se pubblico
    if not is_admin_or_editor and post.is_published:
        post.view_count += 1
        await db.commit()

    return BlogPostResponse.model_validate(post)


@router.post(
    "/blog/posts", response_model=BlogPostResponse, status_code=status.HTTP_201_CREATED
)
async def create_blog_post(
    post_data: BlogPostCreate,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> BlogPostResponse:
    """
    Crea nuovo blog post.

    **Richiede**: Admin o Editor

    Args:
        post_data: Dati post
        current_user: Utente corrente
        db: Database session

    Returns:
        BlogPostResponse: Post creato

    Raises:
        DuplicateResourceError: Se slug già esistente
        ResourceNotFoundError: Se category_id o tag_ids non esistenti
    """
    logger.info(f"Creating blog post: {post_data.title}")

    # Check slug unique
    result = await db.execute(select(BlogPost).where(BlogPost.slug == post_data.slug))
    if result.scalar_one_or_none():
        raise DuplicateResourceError(
            f"Blog post with slug '{post_data.slug}' already exists"
        )

    # Check category exists
    result = await db.execute(
        select(BlogCategory).where(BlogCategory.id == post_data.category_id)
    )
    if not result.scalar_one_or_none():
        raise ResourceNotFoundError(f"Category with ID {post_data.category_id} not found")

    # Check tags exist
    if post_data.tag_ids:
        result = await db.execute(select(BlogTag).where(BlogTag.id.in_(post_data.tag_ids)))
        tags = result.scalars().all()
        if len(tags) != len(post_data.tag_ids):
            raise ResourceNotFoundError("One or more tag IDs not found")
    else:
        tags = []

    # Create post
    post = BlogPost(
        slug=post_data.slug,
        title=post_data.title,
        subtitle=post_data.subtitle,
        excerpt=post_data.excerpt,
        content_html=post_data.content_html,
        featured_image_url=str(post_data.featured_image_url)
        if post_data.featured_image_url
        else None,
        meta_title=post_data.meta_title,
        meta_description=post_data.meta_description,
        meta_keywords=post_data.meta_keywords,
        og_image_url=str(post_data.og_image_url) if post_data.og_image_url else None,
        author_id=current_user.id,
        category_id=post_data.category_id,
        is_published=post_data.is_published,
        published_at=datetime.now(timezone.utc) if post_data.is_published else None,
        scheduled_publish_at=post_data.scheduled_publish_at,
    )

    # Add tags
    post.tags = tags

    db.add(post)
    await db.flush()

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.CREATE,
        entity_type="blog_post",
        entity_id=post.id,
        details={"title": post.title, "slug": post.slug},
    )

    await db.commit()
    await db.refresh(post)

    # Reload with relationships
    post = await get_blog_post_or_404(db, post.id)

    logger.info(f"Blog post created: {post.id}")

    return BlogPostResponse.model_validate(post)


@router.put("/blog/posts/{post_id}", response_model=BlogPostResponse)
async def update_blog_post(
    post_id: UUID,
    post_data: BlogPostUpdate,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> BlogPostResponse:
    """
    Aggiorna blog post esistente.

    **Richiede**: Admin o Editor

    Args:
        post_id: ID post
        post_data: Dati aggiornati
        current_user: Utente corrente
        db: Database session

    Returns:
        BlogPostResponse: Post aggiornato

    Raises:
        ResourceNotFoundError: Se post non trovato
        DuplicateResourceError: Se nuovo slug già esistente
    """
    logger.info(f"Updating blog post {post_id}")

    post = await get_blog_post_or_404(db, post_id)

    # Check slug unique se changed
    if post_data.slug and post_data.slug != post.slug:
        result = await db.execute(select(BlogPost).where(BlogPost.slug == post_data.slug))
        if result.scalar_one_or_none():
            raise DuplicateResourceError(
                f"Blog post with slug '{post_data.slug}' already exists"
            )

    # Check category exists se changed
    if post_data.category_id:
        result = await db.execute(
            select(BlogCategory).where(BlogCategory.id == post_data.category_id)
        )
        if not result.scalar_one_or_none():
            raise ResourceNotFoundError(
                f"Category with ID {post_data.category_id} not found"
            )

    # Check tags exist se provided
    if post_data.tag_ids is not None:
        if post_data.tag_ids:
            result = await db.execute(
                select(BlogTag).where(BlogTag.id.in_(post_data.tag_ids))
            )
            tags = result.scalars().all()
            if len(tags) != len(post_data.tag_ids):
                raise ResourceNotFoundError("One or more tag IDs not found")
            post.tags = tags
        else:
            # Clear tags
            post.tags = []

    # Update fields
    update_data = post_data.model_dump(exclude_unset=True, exclude={"tag_ids"})

    if "featured_image_url" in update_data and update_data["featured_image_url"]:
        update_data["featured_image_url"] = str(update_data["featured_image_url"])

    if "og_image_url" in update_data and update_data["og_image_url"]:
        update_data["og_image_url"] = str(update_data["og_image_url"])

    for field, value in update_data.items():
        setattr(post, field, value)

    # Update published_at if is_published changed
    if post_data.is_published is not None:
        if post_data.is_published and not post.is_published:
            # Publishing
            post.published_at = datetime.now(timezone.utc)
        elif not post_data.is_published and post.is_published:
            # Unpublishing
            post.published_at = None

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="blog_post",
        entity_id=post.id,
        details={"updated_fields": list(update_data.keys())},
    )

    await db.commit()
    await db.refresh(post)

    # Reload with relationships
    post = await get_blog_post_or_404(db, post.id)

    logger.info(f"Blog post updated: {post.id}")

    return BlogPostResponse.model_validate(post)


@router.delete("/blog/posts/{post_id}", response_model=SuccessResponse)
async def delete_blog_post(
    post_id: UUID,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> SuccessResponse:
    """
    Elimina blog post.

    **Richiede**: Admin o Editor

    Args:
        post_id: ID post
        current_user: Utente corrente
        db: Database session

    Returns:
        SuccessResponse: Conferma eliminazione

    Raises:
        ResourceNotFoundError: Se post non trovato
    """
    logger.info(f"Deleting blog post {post_id}")

    post = await get_blog_post_or_404(db, post_id)

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.DELETE,
        entity_type="blog_post",
        entity_id=post.id,
        details={"title": post.title, "slug": post.slug},
    )

    await db.delete(post)
    await db.commit()

    logger.info(f"Blog post deleted: {post_id}")

    return SuccessResponse(message="Blog post deleted successfully")


@router.post("/blog/posts/{post_id}/publish", response_model=BlogPostResponse)
async def toggle_publish_blog_post(
    post_id: UUID,
    publish_data: PublishRequest,
    current_user: User = Depends(require_admin_or_editor),
    db: AsyncSession = Depends(get_async_db),
) -> BlogPostResponse:
    """
    Pubblica o unpublish blog post.

    **Richiede**: Admin o Editor

    Args:
        post_id: ID post
        publish_data: Action (publish o unpublish)
        current_user: Utente corrente
        db: Database session

    Returns:
        BlogPostResponse: Post aggiornato

    Raises:
        ResourceNotFoundError: Se post non trovato
    """
    logger.info(f"Toggling publish for blog post {post_id}: publish={publish_data.publish}")

    post = await get_blog_post_or_404(db, post_id)

    if publish_data.publish:
        # Publish
        post.is_published = True
        post.published_at = datetime.now(timezone.utc)
        action_type = "published"
    else:
        # Unpublish
        post.is_published = False
        post.published_at = None
        action_type = "unpublished"

    # Audit log
    await create_audit_log(
        db=db,
        user_id=current_user.id,
        action=AuditAction.UPDATE,
        entity_type="blog_post",
        entity_id=post.id,
        details={"action": action_type},
    )

    await db.commit()
    await db.refresh(post)

    # Reload with relationships
    post = await get_blog_post_or_404(db, post.id)

    logger.info(f"Blog post {action_type}: {post.id}")

    return BlogPostResponse.model_validate(post)
