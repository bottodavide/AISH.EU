"""
Modulo: knowledge_base.py
Descrizione: API endpoints per gestione Knowledge Base e RAG
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime
import io
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from pydantic import BaseModel, Field
from PyPDF2 import PdfReader

from app.core.database import get_db, get_async_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.knowledge_base import (
    KnowledgeBaseDocument,
    KnowledgeBaseChunk,
    DocumentType,
    DocumentTopic,
    ProcessingStatus,
)
from app.services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================


class DocumentCreateRequest(BaseModel):
    """Request for creating document"""

    title: str = Field(..., min_length=1, max_length=255)
    topic: str = Field(..., description="AI, GDPR, NIS2, CYBERSECURITY, GENERAL")
    description: Optional[str] = Field(None, max_length=1000)
    source_url: Optional[str] = Field(None)
    author: Optional[str] = Field(None, max_length=100)
    is_active: bool = Field(True)


class DocumentUpdateRequest(BaseModel):
    """Request for updating document"""

    title: Optional[str] = Field(None, min_length=1, max_length=255)
    topic: Optional[str] = Field(None)
    description: Optional[str] = Field(None, max_length=1000)
    source_url: Optional[str] = Field(None)
    author: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = Field(None)


class ChunkResponse(BaseModel):
    """Response for chunk"""

    id: UUID
    document_id: UUID
    chunk_index: int
    chunk_text: str
    token_count: int
    chunk_metadata: dict


class DocumentResponse(BaseModel):
    """Response for document"""

    id: UUID
    title: str
    document_type: str
    topic: str
    description: Optional[str]
    source_url: Optional[str]
    author: Optional[str]
    file_size: Optional[int]
    chunk_count: int
    processing_status: str
    is_active: bool
    created_at: datetime
    processed_at: Optional[datetime]


class DocumentDetailResponse(BaseModel):
    """Response for document with chunks"""

    id: UUID
    title: str
    document_type: str
    topic: str
    description: Optional[str]
    source_url: Optional[str]
    author: Optional[str]
    file_size: Optional[int]
    chunk_count: int
    processing_status: str
    is_active: bool
    created_at: datetime
    processed_at: Optional[datetime]
    chunks: List[ChunkResponse]


class DocumentListResponse(BaseModel):
    """Response for document list"""

    documents: List[DocumentResponse]
    total: int
    page: int
    page_size: int


class ProcessingResponse(BaseModel):
    """Response for processing status"""

    document_id: UUID
    status: str
    chunk_count: int
    message: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require SUPER_ADMIN, ADMIN or EDITOR role"""
    if current_user.role not in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.EDITOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or Editor role required",
        )
    return current_user


async def get_document_or_404(
    document_id: UUID, db: AsyncSession
) -> KnowledgeBaseDocument:
    """Get document or raise 404"""
    query = select(KnowledgeBaseDocument).where(KnowledgeBaseDocument.id == document_id)
    result = await db.execute(query)
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    return document


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post(
    "/knowledge-base/documents",
    response_model=DocumentResponse,
    tags=["Knowledge Base"],
    status_code=status.HTTP_201_CREATED,
)
async def create_document(
    title: str = Form(...),
    topic: str = Form(...),
    description: Optional[str] = Form(None),
    source_url: Optional[str] = Form(None),
    author: Optional[str] = Form(None),
    is_active: bool = Form(True),
    file: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Create new document in knowledge base.

    Admin/Editor only. Can upload file or provide source_url.

    Returns:
        Created document
    """
    try:
        # Validate topic
        try:
            topic_enum = DocumentTopic(topic.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid topic. Must be one of: {', '.join([t.value for t in DocumentTopic])}",
            )

        # Determine document type
        document_type = DocumentType.URL if source_url else DocumentType.TEXT
        file_path = None
        file_size = None
        content_text = None

        if file:
            # Handle file upload
            filename_lower = file.filename.lower()

            if filename_lower.endswith(".pdf"):
                document_type = DocumentType.PDF
            elif filename_lower.endswith((".txt", ".md")):
                document_type = DocumentType.TEXT
            elif filename_lower.endswith(".docx"):
                document_type = DocumentType.DOCX
            else:
                document_type = DocumentType.TEXT

            # Read file content
            content = await file.read()
            file_size = len(content)

            # Extract text based on file type
            if document_type == DocumentType.PDF:
                try:
                    # Extract text from PDF
                    pdf_file = io.BytesIO(content)
                    pdf_reader = PdfReader(pdf_file)

                    text_parts = []
                    for page in pdf_reader.pages:
                        text = page.extract_text()
                        if text:
                            text_parts.append(text)

                    content_text = "\n\n".join(text_parts)
                    logger.info(f"Extracted {len(content_text)} characters from PDF with {len(pdf_reader.pages)} pages")

                except Exception as e:
                    logger.error(f"Error extracting PDF text: {e}")
                    # Continue without text - can be processed later
                    content_text = None

            elif document_type == DocumentType.TEXT:
                # For text files, decode content
                try:
                    content_text = content.decode("utf-8")
                except UnicodeDecodeError:
                    # Try latin-1 as fallback
                    content_text = content.decode("latin-1")

            # Save file path (in production, save to storage)
            file_path = f"/uploads/knowledge_base/{file.filename}"

            logger.info(f"File uploaded: {file.filename} ({file_size} bytes)")

        # Create document
        document = KnowledgeBaseDocument(
            title=title,
            document_type=document_type,
            topic=topic_enum,
            description=description,
            source_url=source_url,
            author=author,
            file_path=file_path,
            file_size=file_size,
            content_text=content_text,
            processing_status=ProcessingStatus.PENDING,
            is_active=is_active,
            uploaded_by_user_id=current_user.id,
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        logger.info(f"Document created: {document.id} - {document.title}")

        return DocumentResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type.value,
            topic=document.topic.value,
            description=document.description,
            source_url=document.source_url,
            author=document.author,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            processing_status=document.processing_status.value,
            is_active=document.is_active,
            created_at=document.created_at,
            processed_at=document.processed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating document: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating document: {str(e)}",
        )


@router.post(
    "/knowledge-base/documents/{document_id}/process",
    response_model=ProcessingResponse,
    tags=["Knowledge Base"],
)
async def process_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Process document and generate embeddings.

    Admin/Editor only. Chunks text and creates vector embeddings.

    Returns:
        Processing status
    """
    try:
        document = await get_document_or_404(document_id, db)

        # Check if already processing or completed
        if document.processing_status == ProcessingStatus.PROCESSING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document is already being processed",
            )

        # Validate document has content or file
        if not document.content_text and not document.source_url and not document.file_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no content to process",
            )

        # Update status to processing
        document.processing_status = ProcessingStatus.PROCESSING
        await db.commit()

        # Get RAG service
        rag_service = get_rag_service()

        # Process document chunks
        text_to_process = document.content_text

        if not text_to_process:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text content available for processing. The document may not have been uploaded correctly or text extraction failed.",
            )

        logger.info(f"Processing document {document_id} - length: {len(text_to_process)}")

        # Generate chunks and embeddings
        chunks = await rag_service.process_document_chunks(
            db=db, document_id=str(document_id), text=text_to_process
        )

        # Update document
        document.chunk_count = len(chunks)
        document.processing_status = ProcessingStatus.COMPLETED
        document.processed_at = datetime.utcnow()

        await db.commit()

        logger.info(f"Document processed successfully: {document_id} - {len(chunks)} chunks")

        return ProcessingResponse(
            document_id=document_id,
            status=ProcessingStatus.COMPLETED.value,
            chunk_count=len(chunks),
            message=f"Document processed successfully with {len(chunks)} chunks",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {e}")

        # Update status to failed
        try:
            document.processing_status = ProcessingStatus.FAILED
            await db.commit()
        except:
            pass

        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}",
        )


@router.get(
    "/knowledge-base/documents",
    response_model=DocumentListResponse,
    tags=["Knowledge Base"],
)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    topic: Optional[str] = None,
    processing_status: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    List documents in knowledge base.

    Admin/Editor only. Supports filtering and pagination.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page
        topic: Filter by topic
        processing_status: Filter by processing status
        is_active: Filter by active status
        search: Search in title and description

    Returns:
        List of documents with pagination
    """
    try:
        # Build query
        query = select(KnowledgeBaseDocument)

        # Apply filters
        if topic:
            try:
                topic_enum = DocumentTopic(topic.upper())
                query = query.where(KnowledgeBaseDocument.topic == topic_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid topic",
                )

        if processing_status:
            try:
                status_enum = ProcessingStatus(processing_status.upper())
                query = query.where(KnowledgeBaseDocument.processing_status == status_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid processing status",
                )

        if is_active is not None:
            query = query.where(KnowledgeBaseDocument.is_active == is_active)

        if search:
            search_filter = f"%{search}%"
            query = query.where(
                (KnowledgeBaseDocument.title.ilike(search_filter))
                | (KnowledgeBaseDocument.description.ilike(search_filter))
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order_by(desc(KnowledgeBaseDocument.created_at)).offset(offset).limit(page_size)

        # Execute query
        result = await db.execute(query)
        documents = result.scalars().all()

        return DocumentListResponse(
            documents=[
                DocumentResponse(
                    id=doc.id,
                    title=doc.title,
                    document_type=doc.document_type.value,
                    topic=doc.topic.value,
                    description=doc.description,
                    source_url=doc.source_url,
                    author=doc.author,
                    file_size=doc.file_size,
                    chunk_count=doc.chunk_count,
                    processing_status=doc.processing_status.value,
                    is_active=doc.is_active,
                    created_at=doc.created_at,
                    processed_at=doc.processed_at,
                )
                for doc in documents
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}",
        )


@router.get(
    "/knowledge-base/documents/{document_id}",
    response_model=DocumentDetailResponse,
    tags=["Knowledge Base"],
)
async def get_document(
    document_id: UUID,
    include_chunks: bool = False,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Get document detail.

    Admin/Editor only. Optionally include chunks.

    Args:
        document_id: Document ID
        include_chunks: Include chunk data

    Returns:
        Document detail with optional chunks
    """
    try:
        document = await get_document_or_404(document_id, db)

        chunks = []
        if include_chunks:
            # Get chunks
            query = (
                select(KnowledgeBaseChunk)
                .where(KnowledgeBaseChunk.document_id == document_id)
                .order_by(KnowledgeBaseChunk.chunk_index)
            )
            result = await db.execute(query)
            chunk_list = result.scalars().all()

            chunks = [
                ChunkResponse(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    chunk_index=chunk.chunk_index,
                    chunk_text=chunk.chunk_text,
                    token_count=chunk.token_count,
                    chunk_metadata=chunk.chunk_metadata or {},
                )
                for chunk in chunk_list
            ]

        return DocumentDetailResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type.value,
            topic=document.topic.value,
            description=document.description,
            source_url=document.source_url,
            author=document.author,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            processing_status=document.processing_status.value,
            is_active=document.is_active,
            created_at=document.created_at,
            processed_at=document.processed_at,
            chunks=chunks,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting document: {str(e)}",
        )


@router.put(
    "/knowledge-base/documents/{document_id}",
    response_model=DocumentResponse,
    tags=["Knowledge Base"],
)
async def update_document(
    document_id: UUID,
    request: DocumentUpdateRequest,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Update document metadata.

    Admin/Editor only. Does not reprocess embeddings.

    Args:
        document_id: Document ID
        request: Update data

    Returns:
        Updated document
    """
    try:
        document = await get_document_or_404(document_id, db)

        # Update fields
        if request.title is not None:
            document.title = request.title

        if request.topic is not None:
            try:
                document.topic = DocumentTopic(request.topic.upper())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid topic",
                )

        if request.description is not None:
            document.description = request.description

        if request.source_url is not None:
            document.source_url = request.source_url

        if request.author is not None:
            document.author = request.author

        if request.is_active is not None:
            document.is_active = request.is_active

        await db.commit()
        await db.refresh(document)

        logger.info(f"Document updated: {document_id}")

        return DocumentResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type.value,
            topic=document.topic.value,
            description=document.description,
            source_url=document.source_url,
            author=document.author,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            processing_status=document.processing_status.value,
            is_active=document.is_active,
            created_at=document.created_at,
            processed_at=document.processed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating document: {str(e)}",
        )


@router.delete(
    "/knowledge-base/documents/{document_id}",
    tags=["Knowledge Base"],
)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Delete document and all its chunks.

    Admin/Editor only. Permanently deletes document and embeddings.

    Args:
        document_id: Document ID

    Returns:
        Success message
    """
    try:
        document = await get_document_or_404(document_id, db)

        # Delete all chunks
        query = select(KnowledgeBaseChunk).where(KnowledgeBaseChunk.document_id == document_id)
        result = await db.execute(query)
        chunks = result.scalars().all()

        for chunk in chunks:
            await db.delete(chunk)

        # Delete document
        await db.delete(document)
        await db.commit()

        logger.info(f"Document deleted: {document_id} ({len(chunks)} chunks)")

        return JSONResponse(
            content={
                "message": "Document deleted successfully",
                "document_id": str(document_id),
                "chunks_deleted": len(chunks),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}",
        )


@router.patch(
    "/knowledge-base/documents/{document_id}/toggle-active",
    response_model=DocumentResponse,
    tags=["Knowledge Base"],
)
async def toggle_document_active(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Toggle document active status.

    Admin/Editor only. Inactive documents are excluded from RAG retrieval.

    Args:
        document_id: Document ID

    Returns:
        Updated document
    """
    try:
        document = await get_document_or_404(document_id, db)

        # Toggle status
        document.is_active = not document.is_active
        await db.commit()
        await db.refresh(document)

        logger.info(f"Document active status toggled: {document_id} -> {document.is_active}")

        return DocumentResponse(
            id=document.id,
            title=document.title,
            document_type=document.document_type.value,
            topic=document.topic.value,
            description=document.description,
            source_url=document.source_url,
            author=document.author,
            file_size=document.file_size,
            chunk_count=document.chunk_count,
            processing_status=document.processing_status.value,
            is_active=document.is_active,
            created_at=document.created_at,
            processed_at=document.processed_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error toggling document status: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error toggling document status: {str(e)}",
        )


@router.get(
    "/knowledge-base/documents/{document_id}/chunks",
    response_model=List[ChunkResponse],
    tags=["Knowledge Base"],
)
async def get_document_chunks(
    document_id: UUID,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    """
    Get all chunks for a document.

    Admin/Editor only. Returns chunks in order.

    Args:
        document_id: Document ID

    Returns:
        List of chunks
    """
    try:
        # Verify document exists
        await get_document_or_404(document_id, db)

        # Get chunks
        query = (
            select(KnowledgeBaseChunk)
            .where(KnowledgeBaseChunk.document_id == document_id)
            .order_by(KnowledgeBaseChunk.chunk_index)
        )
        result = await db.execute(query)
        chunks = result.scalars().all()

        return [
            ChunkResponse(
                id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                chunk_text=chunk.chunk_text,
                token_count=chunk.token_count,
                chunk_metadata=chunk.chunk_metadata or {},
            )
            for chunk in chunks
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chunks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting chunks: {str(e)}",
        )


logger.debug("Knowledge base routes loaded")
