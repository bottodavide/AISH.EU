"""
Modulo: rag_service.py
Descrizione: Servizio RAG (Retrieval-Augmented Generation) con pgvector
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
import openai
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from app.core.config import get_settings
from app.models.knowledge_base import KnowledgeBaseChunk, KnowledgeBaseDocument

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGService:
    """
    Servizio RAG per embeddings e similarity search.

    Features:
    - Generate embeddings con OpenAI
    - Similarity search con pgvector
    - Document chunking
    - Context retrieval
    """

    def __init__(self):
        """Initialize OpenAI client for embeddings"""
        self.api_key = settings.OPENAI_API_KEY
        if not self.api_key:
            logger.warning("OPENAI_API_KEY not configured - RAG embeddings will not work")
            self.client = None
        else:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized for embeddings")

        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            List of floats (1536-dimensional vector)

        Raises:
            Exception: If embedding generation fails
        """
        if not self.client:
            raise Exception("OpenAI client not initialized - check OPENAI_API_KEY")

        try:
            logger.debug(f"Generating embedding for text length: {len(text)}")

            response = await self.client.embeddings.create(
                model=self.embedding_model, input=text
            )

            embedding = response.data[0].embedding

            logger.debug(f"Embedding generated - dimension: {len(embedding)}")
            return embedding

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    def chunk_text(
        self, text: str, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None
    ) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Text to chunk
            chunk_size: Size of each chunk in characters (default: self.chunk_size)
            chunk_overlap: Overlap between chunks (default: self.chunk_overlap)

        Returns:
            List of text chunks
        """
        chunk_size = chunk_size or self.chunk_size
        chunk_overlap = chunk_overlap or self.chunk_overlap

        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence end markers within last 100 chars
                search_start = max(start, end - 100)
                last_period = text.rfind(".", search_start, end)
                last_newline = text.rfind("\n", search_start, end)

                # Use the last sentence/paragraph boundary found
                boundary = max(last_period, last_newline)
                if boundary > start:
                    end = boundary + 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            # Move start with overlap
            start = end - chunk_overlap

        logger.debug(f"Text chunked into {len(chunks)} chunks")
        return chunks

    async def similarity_search(
        self,
        db: AsyncSession,
        query_embedding: List[float],
        top_k: int = 5,
        topic_filter: Optional[str] = None,
    ) -> List[Tuple[KnowledgeBaseChunk, float]]:
        """
        Perform similarity search on knowledge base.

        Args:
            db: Database session
            query_embedding: Query vector embedding
            top_k: Number of results to return
            topic_filter: Optional topic to filter by

        Returns:
            List of tuples (chunk, similarity_score)
        """
        try:
            # Build query with vector similarity
            # Using cosine distance (1 - cosine_similarity)
            query = select(
                KnowledgeBaseChunk,
                (1 - KnowledgeBaseChunk.embedding.cosine_distance(query_embedding)).label(
                    "similarity"
                ),
            ).join(KnowledgeBaseDocument)

            # Filter by active documents
            query = query.where(KnowledgeBaseDocument.is_active == True)

            # Optional topic filter
            if topic_filter:
                query = query.where(KnowledgeBaseDocument.topic == topic_filter)

            # Order by similarity and limit
            query = query.order_by(text("similarity DESC")).limit(top_k)

            result = await db.execute(query)
            results = result.all()

            logger.info(f"Similarity search returned {len(results)} results")

            return [(row[0], row[1]) for row in results]

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            raise

    async def retrieve_context(
        self,
        db: AsyncSession,
        query: str,
        top_k: int = 5,
        topic_filter: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context for query using RAG.

        Args:
            db: Database session
            query: User query text
            top_k: Number of chunks to retrieve
            topic_filter: Optional topic filter

        Returns:
            List of dicts with 'text', 'score', 'metadata'
        """
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)

            # Perform similarity search
            results = await self.similarity_search(
                db=db, query_embedding=query_embedding, top_k=top_k, topic_filter=topic_filter
            )

            # Format results
            context_items = []
            for chunk, score in results:
                context_items.append(
                    {
                        "text": chunk.chunk_text,
                        "score": float(score),
                        "chunk_id": str(chunk.id),
                        "document_id": str(chunk.document_id),
                        "metadata": chunk.chunk_metadata or {},
                    }
                )

            logger.info(f"Retrieved {len(context_items)} context items for query")
            return context_items

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            raise

    async def process_document_chunks(
        self, db: AsyncSession, document_id: str, text: str
    ) -> List[KnowledgeBaseChunk]:
        """
        Process document: chunk text and generate embeddings.

        Args:
            db: Database session
            document_id: Document ID
            text: Full document text

        Returns:
            List of created chunks
        """
        try:
            logger.info(f"Processing document {document_id} - length: {len(text)}")

            # Chunk text
            chunks_text = self.chunk_text(text)
            logger.info(f"Created {len(chunks_text)} chunks")

            # Create chunks with embeddings
            created_chunks = []

            for idx, chunk_text in enumerate(chunks_text):
                # Generate embedding
                embedding = await self.generate_embedding(chunk_text)

                # Create chunk
                chunk = KnowledgeBaseChunk(
                    document_id=document_id,
                    chunk_index=idx,
                    chunk_text=chunk_text,
                    embedding=embedding,
                    token_count=len(chunk_text) // 4,  # Rough estimate
                    chunk_metadata={"position": idx, "total_chunks": len(chunks_text)},
                )

                db.add(chunk)
                created_chunks.append(chunk)

                logger.debug(f"Created chunk {idx + 1}/{len(chunks_text)}")

            # Commit
            await db.commit()

            logger.info(f"Processed document {document_id} - {len(created_chunks)} chunks created")
            return created_chunks

        except Exception as e:
            logger.error(f"Error processing document chunks: {e}")
            await db.rollback()
            raise

    async def reprocess_document(
        self, db: AsyncSession, document_id: str, new_text: str
    ) -> List[KnowledgeBaseChunk]:
        """
        Reprocess document: delete old chunks and create new ones.

        Args:
            db: Database session
            document_id: Document ID
            new_text: Updated document text

        Returns:
            List of new chunks
        """
        try:
            # Delete old chunks
            query = select(KnowledgeBaseChunk).where(
                KnowledgeBaseChunk.document_id == document_id
            )
            result = await db.execute(query)
            old_chunks = result.scalars().all()

            for chunk in old_chunks:
                await db.delete(chunk)

            await db.commit()
            logger.info(f"Deleted {len(old_chunks)} old chunks")

            # Process new text
            new_chunks = await self.process_document_chunks(db, document_id, new_text)

            return new_chunks

        except Exception as e:
            logger.error(f"Error reprocessing document: {e}")
            await db.rollback()
            raise

    def format_context_for_prompt(self, context_items: List[Dict[str, Any]]) -> List[str]:
        """
        Format retrieved context items for LLM prompt.

        Args:
            context_items: List of context dicts from retrieve_context

        Returns:
            List of formatted context strings
        """
        formatted = []

        for idx, item in enumerate(context_items, 1):
            text = item["text"]
            score = item["score"]

            # Add source indicator
            formatted_text = f"[Fonte {idx} - Rilevanza: {score:.2f}]\n{text}"
            formatted.append(formatted_text)

        return formatted


# Singleton instance
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get singleton RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


logger.debug("RAG service module loaded")
