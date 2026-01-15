"""
Modulo: chat.py
Descrizione: API endpoints per AI chatbot con RAG
Autore: Claude per Davide
Data: 2026-01-15
"""

import logging
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user_optional
from app.models.user import User
from app.models.chat import ChatConversation, ChatMessage, MessageRole, UserFeedback
from app.services.claude_service import get_claude_service
from app.services.rag_service import get_rag_service
from app.services.guardrails_service import get_guardrails_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================


class ChatMessageRequest(BaseModel):
    """Request for sending chat message"""

    conversation_id: Optional[UUID] = Field(None, description="Existing conversation ID (or null for new)")
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    session_id: str = Field(..., description="Browser session ID for guest tracking")
    use_rag: bool = Field(True, description="Use RAG context retrieval")
    topic_filter: Optional[str] = Field(None, description="Filter knowledge base by topic")


class ChatMessageResponse(BaseModel):
    """Response for chat message"""

    conversation_id: UUID
    message_id: UUID
    role: str
    content: str
    created_at: datetime


class ConversationResponse(BaseModel):
    """Response for conversation"""

    id: UUID
    user_id: Optional[UUID]
    session_id: str
    total_messages: int
    user_feedback: str
    created_at: datetime
    ended_at: Optional[datetime]


class ConversationDetailResponse(BaseModel):
    """Response for conversation with messages"""

    id: UUID
    user_id: Optional[UUID]
    session_id: str
    total_messages: int
    user_feedback: str
    created_at: datetime
    ended_at: Optional[datetime]
    messages: List[ChatMessageResponse]


class FeedbackRequest(BaseModel):
    """Request for conversation feedback"""

    conversation_id: UUID
    feedback: str = Field(..., description="thumbs_up or thumbs_down")


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.post("/chat/message", response_model=ChatMessageResponse, tags=["Chat"])
async def send_chat_message(
    request: ChatMessageRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Send message to AI chatbot and get response.

    Features:
    - RAG context retrieval from knowledge base
    - Guest support (no auth required)
    - Session tracking
    - Conversation history

    Returns:
        Assistant response message
    """
    try:
        claude_service = get_claude_service()
        rag_service = get_rag_service()
        guardrails_service = get_guardrails_service()

        # Load guardrails config
        guardrails_config = await guardrails_service.load_config(db)

        # Check rate limit
        identifier = str(current_user.id) if current_user else request.session_id
        rate_limit_check = guardrails_service.check_rate_limit(
            identifier=identifier,
            config=guardrails_config,
        )

        if not rate_limit_check["allowed"]:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=rate_limit_check["reason"],
                headers={"Retry-After": str(rate_limit_check["retry_after"])},
            )

        # Validate input
        input_validation = guardrails_service.validate_input(
            user_input=request.message,
            config=guardrails_config,
        )

        if not input_validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=input_validation["reason"],
            )

        # Use filtered input
        filtered_message = input_validation["filtered_input"]

        # Validate topic filter (if provided)
        if request.topic_filter:
            topic_validation = guardrails_service.validate_topic(
                topic=request.topic_filter,
                config=guardrails_config,
            )

            if not topic_validation["valid"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=topic_validation["reason"],
                )

        # Get or create conversation
        conversation = None
        if request.conversation_id:
            query = select(ChatConversation).where(
                ChatConversation.id == request.conversation_id
            )
            result = await db.execute(query)
            conversation = result.scalar_one_or_none()

            if not conversation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
                )
        else:
            # Create new conversation
            conversation = ChatConversation(
                user_id=current_user.id if current_user else None,
                session_id=request.session_id,
                total_messages=0,
            )
            db.add(conversation)
            await db.flush()
            logger.info(f"Created new conversation {conversation.id}")

        # Save user message (use filtered message)
        user_message = ChatMessage(
            conversation_id=conversation.id,
            role=MessageRole.USER,
            content=filtered_message,
        )
        db.add(user_message)
        conversation.total_messages += 1

        # Retrieve context with RAG (if enabled)
        context_chunks = []
        retrieved_chunk_ids = []

        if request.use_rag:
            context_items = await rag_service.retrieve_context(
                db=db,
                query=filtered_message,
                top_k=5,
                topic_filter=request.topic_filter,
            )

            if context_items:
                context_chunks = rag_service.format_context_for_prompt(context_items)
                retrieved_chunk_ids = [item["chunk_id"] for item in context_items]
                logger.info(f"Retrieved {len(context_chunks)} context chunks for RAG")

        # Build conversation history
        query = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation.id)
            .order_by(ChatMessage.created_at)
        )
        result = await db.execute(query)
        history = result.scalars().all()

        messages = []
        for msg in history:
            messages.append({"role": msg.role.value, "content": msg.content})

        # Build system prompt with RAG context and guardrails
        guardrails_instructions = guardrails_service.get_system_instructions(guardrails_config)
        base_instructions = (
            "Sei un assistente esperto di AI Strategy Hub, specializzato in "
            "Intelligenza Artificiale, GDPR, Cybersecurity e NIS2. "
            "Rispondi in italiano in modo professionale, chiaro e accurato. "
            "Se non conosci la risposta, dillo onestamente. "
            f"{guardrails_instructions}"
        )

        system_prompt = claude_service.build_rag_system_prompt(
            context_chunks=context_chunks,
            base_instructions=base_instructions,
        )

        # Call Claude API
        response = await claude_service.create_chat_completion(
            messages=messages,
            system_prompt=system_prompt,
            max_tokens=2048,
            temperature=0.7,
        )

        # Validate output
        output_validation = guardrails_service.validate_output(
            ai_output=response["content"],
            config=guardrails_config,
        )

        if not output_validation["valid"]:
            logger.error(f"Output validation failed: {output_validation['reason']}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Response validation failed",
            )

        # Use filtered output
        filtered_content = output_validation["filtered_output"]

        # Save assistant message (use filtered content)
        assistant_message = ChatMessage(
            conversation_id=conversation.id,
            role=MessageRole.ASSISTANT,
            content=filtered_content,
            retrieved_chunks=retrieved_chunk_ids if retrieved_chunk_ids else None,
            claude_message_id=response["id"],
            token_count=response["usage"]["output_tokens"],
        )
        db.add(assistant_message)
        conversation.total_messages += 1

        await db.commit()
        await db.refresh(assistant_message)

        logger.info(
            f"Chat message processed - Conversation: {conversation.id}, "
            f"Tokens: {response['usage']['input_tokens']} in / {response['usage']['output_tokens']} out"
        )

        return ChatMessageResponse(
            conversation_id=conversation.id,
            message_id=assistant_message.id,
            role=assistant_message.role.value,
            content=assistant_message.content,
            created_at=assistant_message.created_at,
        )

    except Exception as e:
        logger.error(f"Error in chat message: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat message: {str(e)}",
        )


@router.get("/chat/conversations", response_model=List[ConversationResponse], tags=["Chat"])
async def list_conversations(
    session_id: Optional[str] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    List user's conversations.

    Args:
        session_id: Optional session ID for guest users
        limit: Max conversations to return

    Returns:
        List of conversations
    """
    try:
        query = select(ChatConversation).order_by(desc(ChatConversation.created_at)).limit(limit)

        # Filter by user or session
        if current_user:
            query = query.where(ChatConversation.user_id == current_user.id)
        elif session_id:
            query = query.where(ChatConversation.session_id == session_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide session_id or authenticate",
            )

        result = await db.execute(query)
        conversations = result.scalars().all()

        return [
            ConversationResponse(
                id=conv.id,
                user_id=conv.user_id,
                session_id=conv.session_id,
                total_messages=conv.total_messages,
                user_feedback=conv.user_feedback.value,
                created_at=conv.created_at,
                ended_at=conv.ended_at,
            )
            for conv in conversations
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing conversations: {str(e)}",
        )


@router.get(
    "/chat/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    tags=["Chat"],
)
async def get_conversation(
    conversation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Get conversation with all messages.

    Args:
        conversation_id: Conversation ID

    Returns:
        Conversation with messages
    """
    try:
        query = select(ChatConversation).where(ChatConversation.id == conversation_id)
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        # Check access
        if current_user and conversation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        # Get messages
        query = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == conversation_id)
            .order_by(ChatMessage.created_at)
        )
        result = await db.execute(query)
        messages = result.scalars().all()

        return ConversationDetailResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            session_id=conversation.session_id,
            total_messages=conversation.total_messages,
            user_feedback=conversation.user_feedback.value,
            created_at=conversation.created_at,
            ended_at=conversation.ended_at,
            messages=[
                ChatMessageResponse(
                    conversation_id=msg.conversation_id,
                    message_id=msg.id,
                    role=msg.role.value,
                    content=msg.content,
                    created_at=msg.created_at,
                )
                for msg in messages
            ],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting conversation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting conversation: {str(e)}",
        )


@router.post("/chat/feedback", tags=["Chat"])
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """
    Submit feedback for conversation.

    Args:
        request: Feedback request with conversation_id and feedback

    Returns:
        Success message
    """
    try:
        query = select(ChatConversation).where(ChatConversation.id == request.conversation_id)
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found"
            )

        # Validate feedback
        if request.feedback not in ["thumbs_up", "thumbs_down"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid feedback value"
            )

        # Update feedback
        conversation.user_feedback = UserFeedback(request.feedback)
        await db.commit()

        logger.info(f"Feedback submitted for conversation {conversation.id}: {request.feedback}")

        return {"message": "Feedback submitted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting feedback: {str(e)}",
        )


logger.debug("Chat routes loaded")
